"""Core scraping engine for Y5 Solutions websites."""

import logging
import random
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

import config

logger = logging.getLogger(__name__)


class HttpClient:
    """HTTP client with automatic fallback from requests to cloudscraper."""

    def __init__(self):
        self.session = None
        self.transport_mode = None
        self._init_session()

    def _init_session(self):
        """Try plain requests first; fall back to cloudscraper on 403."""
        # Try plain requests with realistic headers
        session = requests.Session()
        session.headers.update(config.REQUEST_HEADERS)

        test_url = config.TARGET_SITES["y5solutions"]["base_url"] + "/"
        try:
            resp = session.get(test_url, timeout=config.REQUEST_TIMEOUT)
            if resp.status_code not in (403, 503):
                self.session = session
                self.transport_mode = "requests"
                logger.info("Using plain requests (status %d)", resp.status_code)
                return
            logger.info(
                "Plain requests got status %d, switching to cloudscraper",
                resp.status_code,
            )
        except requests.RequestException as e:
            logger.warning("Plain requests failed: %s, switching to cloudscraper", e)

        # Fall back to cloudscraper
        try:
            import cloudscraper

            self.session = cloudscraper.create_scraper(
                browser={"browser": "chrome", "platform": "windows", "mobile": False}
            )
            self.transport_mode = "cloudscraper"
            logger.info("Using cloudscraper transport")
        except ImportError:
            logger.error("cloudscraper not installed, falling back to plain requests")
            self.session = session
            self.transport_mode = "requests"

    def get(self, url):
        """Fetch a URL with retry and exponential backoff.

        Returns the response object or None on failure.
        """
        for attempt in range(1, config.MAX_RETRIES + 1):
            try:
                resp = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
                if resp.status_code == 429:
                    wait = 2**attempt
                    logger.warning("Rate limited (429) on %s, waiting %ds", url, wait)
                    time.sleep(wait)
                    continue
                return resp
            except requests.RequestException as e:
                wait = 2**attempt
                logger.warning(
                    "Request failed (attempt %d/%d) for %s: %s",
                    attempt,
                    config.MAX_RETRIES,
                    url,
                    e,
                )
                if attempt < config.MAX_RETRIES:
                    time.sleep(wait)
        return None


class PageScraper:
    """Extracts structured data from a parsed HTML page."""

    def __init__(self, soup, source_url):
        self.soup = soup
        self.source_url = source_url

    def extract_metadata(self):
        """Extract page title, meta description, and Open Graph tags."""
        metadata = {}

        title_tag = self.soup.find("title")
        if title_tag:
            metadata["title"] = title_tag.get_text(strip=True)

        desc = self.soup.find("meta", attrs={"name": "description"})
        if desc and desc.get("content"):
            metadata["description"] = desc["content"]

        keywords = self.soup.find("meta", attrs={"name": "keywords"})
        if keywords and keywords.get("content"):
            metadata["keywords"] = keywords["content"]

        # Open Graph tags
        for og_prop in ("og:title", "og:description", "og:image", "og:type"):
            tag = self.soup.find("meta", attrs={"property": og_prop})
            if tag and tag.get("content"):
                metadata[og_prop] = tag["content"]

        return metadata

    def extract_text_content(self):
        """Extract visible text content, excluding scripts/styles/nav."""
        # Remove non-content elements
        for tag in self.soup.find_all(["script", "style", "noscript", "iframe"]):
            tag.decompose()

        # Try semantic content containers first
        content_area = (
            self.soup.find("main")
            or self.soup.find("article")
            or self.soup.find("div", {"role": "main"})
            or self.soup.find("div", {"id": "content"})
        )

        if not content_area:
            content_area = self.soup.find("body") or self.soup

        # Get text, collapse whitespace
        lines = []
        for element in content_area.find_all(
            ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "td", "th", "span", "div", "a"]
        ):
            text = element.get_text(strip=True)
            if text and len(text) > 1:
                lines.append(text)

        # Deduplicate consecutive identical lines
        deduped = []
        for line in lines:
            if not deduped or line != deduped[-1]:
                deduped.append(line)

        return "\n".join(deduped)

    def extract_links(self):
        """Extract all links, resolving relative URLs."""
        links = []
        seen = set()
        for a_tag in self.soup.find_all("a", href=True):
            url = urljoin(self.source_url, a_tag["href"])
            text = a_tag.get_text(strip=True)
            if url not in seen:
                seen.add(url)
                links.append({"text": text, "url": url})
        return links

    def extract_images(self):
        """Extract all images with alt text."""
        images = []
        seen = set()
        for img in self.soup.find_all("img", src=True):
            src = urljoin(self.source_url, img["src"])
            if src not in seen:
                seen.add(src)
                images.append({"alt": img.get("alt", ""), "src": src})
        return images

    def extract_headings(self):
        """Extract all headings (h1-h6) with their level."""
        headings = []
        for level in range(1, 7):
            for h in self.soup.find_all(f"h{level}"):
                text = h.get_text(strip=True)
                if text:
                    headings.append({"level": level, "text": text})
        return headings

    def to_dict(self):
        """Aggregate all extracted data into a single dictionary."""
        return {
            "metadata": self.extract_metadata(),
            "headings": self.extract_headings(),
            "text_content": self.extract_text_content(),
            "links": self.extract_links(),
            "images": self.extract_images(),
        }


class SiteScraper:
    """Scrapes all pages from configured target sites."""

    def __init__(self, http_client):
        self.client = http_client

    def scrape_site(self, site_name, base_url, pages):
        """Scrape all known pages for a single site."""
        results = []
        total = len(pages)

        for i, path in enumerate(pages, 1):
            url = base_url.rstrip("/") + path
            logger.info("[%s] Scraping [%d/%d]: %s", site_name, i, total, url)

            page_data = {"url": url, "path": path, "success": False}

            try:
                resp = self.client.get(url)
                if resp is None:
                    page_data["error"] = "Request failed after retries"
                    logger.warning("Failed to fetch: %s", url)
                elif resp.status_code != 200:
                    page_data["status_code"] = resp.status_code
                    page_data["error"] = f"HTTP {resp.status_code}"
                    logger.warning("HTTP %d for: %s", resp.status_code, url)
                else:
                    page_data["status_code"] = 200
                    soup = BeautifulSoup(resp.text, "lxml")
                    scraper = PageScraper(soup, url)
                    page_data.update(scraper.to_dict())
                    page_data["success"] = True
                    logger.info("Successfully scraped: %s", url)
            except Exception as e:
                page_data["error"] = str(e)
                logger.error("Error scraping %s: %s", url, e)

            results.append(page_data)

            # Polite delay between requests
            if i < total:
                delay = random.uniform(*config.REQUEST_DELAY)
                time.sleep(delay)

        return results

    def scrape_all(self):
        """Scrape all configured target sites."""
        from datetime import datetime, timezone

        all_data = {
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "transport_mode": self.client.transport_mode,
            "sites": {},
        }

        for site_name, site_config in config.TARGET_SITES.items():
            logger.info("Starting scrape of %s (%s)", site_name, site_config["base_url"])
            pages = self.scrape_site(
                site_name, site_config["base_url"], site_config["pages"]
            )
            all_data["sites"][site_name] = pages

            success_count = sum(1 for p in pages if p["success"])
            logger.info(
                "Completed %s: %d/%d pages successful",
                site_name,
                success_count,
                len(pages),
            )

        return all_data
