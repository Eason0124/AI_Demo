"""Generates company reports from scraped data and background info."""

import json
import logging
import os
import re

import config

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Transforms raw scraped data into Markdown and JSON reports."""

    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.background = config.COMPANY_BACKGROUND
        self.pages_by_category = self._categorize_pages()

    def _categorize_pages(self):
        """Group scraped pages by topic based on URL patterns."""
        categories = {
            "homepage": [],
            "about": [],
            "vision": [],
            "platform": [],
            "services": [],
            "contact": [],
            "customers": [],
            "other": [],
        }

        url_patterns = {
            "about": ["our-story", "about-us", "about"],
            "vision": ["our-vision", "vision"],
            "platform": ["our-platform", "platform", "software", "products"],
            "contact": ["contact"],
            "customers": ["shipper", "carrier", "logistics-provider"],
            "services": [
                "ocean-shipping",
                "port-drayage",
                "customs-brokerage",
                "warehousing",
                "air-freight",
                "ground-transportation",
            ],
        }

        for site_pages in self.raw_data.get("sites", {}).values():
            for page in site_pages:
                if not page.get("success"):
                    continue

                url = page.get("url", "")
                path = page.get("path", "")

                if path == "/":
                    categories["homepage"].append(page)
                    continue

                categorized = False
                for category, patterns in url_patterns.items():
                    if any(p in path.lower() for p in patterns):
                        categories[category].append(page)
                        categorized = True
                        break

                if not categorized:
                    categories["other"].append(page)

        return categories

    def _get_text_from_pages(self, category):
        """Get combined text content from pages in a category."""
        texts = []
        for page in self.pages_by_category.get(category, []):
            text = page.get("text_content", "").strip()
            if text:
                texts.append(text)
        return "\n\n".join(texts)

    def _extract_contact_info(self):
        """Scan all pages for contact information using regex."""
        all_text = ""
        for site_pages in self.raw_data.get("sites", {}).values():
            for page in site_pages:
                if page.get("success"):
                    all_text += " " + page.get("text_content", "")

        contact = {}

        # Phone numbers
        phones = re.findall(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", all_text)
        if phones:
            contact["phone"] = list(set(phones))

        # Email addresses
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", all_text)
        if emails:
            contact["email"] = list(set(emails))

        return contact

    def _get_scrape_summary(self):
        """Summarize scraping results."""
        summary = {"total_pages": 0, "successful": 0, "failed": 0, "sites": {}}
        for site_name, pages in self.raw_data.get("sites", {}).items():
            success = sum(1 for p in pages if p.get("success"))
            summary["sites"][site_name] = {
                "total": len(pages),
                "successful": success,
                "failed": len(pages) - success,
            }
            summary["total_pages"] += len(pages)
            summary["successful"] += success
            summary["failed"] += len(pages) - success
        return summary

    def generate_markdown(self):
        """Generate a comprehensive Markdown company report."""
        bg = self.background
        scraped_contact = self._extract_contact_info()
        scrape_summary = self._get_scrape_summary()

        sections = []

        # Title
        sections.append(f"# {bg['name']} - Company Report\n")

        # Company Overview
        sections.append("## 1. Company Overview\n")
        sections.append(f"| Item | Detail |")
        sections.append(f"|------|--------|")
        sections.append(f"| **Company Name** | {bg['name']} |")
        sections.append(f"| **Founded** | {bg['founded']} |")
        sections.append(f"| **Industry** | {bg['industry']} |")
        sections.append(f"| **Type** | {bg['company_type']} |")
        hq = bg["headquarters"]
        sections.append(
            f"| **Headquarters** | {hq['address']}, {hq['city']}, {hq['state']} {hq['zip']} |"
        )
        sections.append(f"| **Revenue** | {bg['revenue']} |")
        sections.append(f"| **Websites** | {', '.join(bg['websites'])} |")
        sections.append("")

        # Leadership
        sections.append("### Leadership\n")
        for leader in bg["leadership"]:
            sections.append(f"- **{leader['title']}**: {leader['name']}")
        sections.append("")

        # Office Locations
        sections.append("### Office Locations\n")
        for office in bg["offices"]:
            sections.append(f"- {office}")
        sections.append("")

        # Company Description
        sections.append("## 2. About the Company\n")
        sections.append(bg["description"])
        sections.append("")

        # Scraped about content
        about_text = self._get_text_from_pages("about")
        if about_text:
            sections.append("### Company Story (from website)\n")
            sections.append(about_text)
            sections.append("")

        # Homepage content
        homepage_text = self._get_text_from_pages("homepage")
        if homepage_text:
            sections.append("### Website Homepage Content\n")
            sections.append(homepage_text)
            sections.append("")

        # Vision & Mission
        sections.append("## 3. Vision & Mission\n")
        sections.append(bg["vision"])
        sections.append("")

        vision_text = self._get_text_from_pages("vision")
        if vision_text:
            sections.append("### From Website\n")
            sections.append(vision_text)
            sections.append("")

        # Services
        sections.append("## 4. Services\n")
        sections.append(
            "Y5 Solutions offers a comprehensive range of logistics services:\n"
        )
        for service in bg["services"]:
            sections.append(f"- **{service}**")
        sections.append("")

        services_text = self._get_text_from_pages("services")
        if services_text:
            sections.append("### Service Details (from website)\n")
            sections.append(services_text)
            sections.append("")

        # Technology Platform
        sections.append("## 5. Technology Platform\n")
        tech = bg["technology"]
        sections.append(tech["description"])
        sections.append("")

        sections.append("### Integrated Systems\n")
        for system in tech["systems"]:
            sections.append(f"- {system}")
        sections.append("")

        sections.append("### Key Features\n")
        for feature in tech["features"]:
            sections.append(f"- {feature}")
        sections.append("")

        platform_text = self._get_text_from_pages("platform")
        if platform_text:
            sections.append("### Platform Details (from website)\n")
            sections.append(platform_text)
            sections.append("")

        # Target Customers
        sections.append("## 6. Target Customers\n")
        for customer in bg["target_customers"]:
            sections.append(f"### {customer['type']}\n")
            sections.append(customer["description"])
            sections.append("")

        customers_text = self._get_text_from_pages("customers")
        if customers_text:
            sections.append("### Customer Details (from website)\n")
            sections.append(customers_text)
            sections.append("")

        # Contact Information
        sections.append("## 7. Contact Information\n")
        hq = bg["headquarters"]
        sections.append(
            f"**Address:** {hq['address']}, {hq['city']}, {hq['state']} {hq['zip']}, {hq['country']}"
        )
        sections.append("")

        if scraped_contact.get("phone"):
            sections.append(f"**Phone:** {', '.join(scraped_contact['phone'])}")
            sections.append("")
        else:
            sections.append("**Phone:** (310) 997-0045")
            sections.append("")

        if scraped_contact.get("email"):
            sections.append(f"**Email:** {', '.join(scraped_contact['email'])}")
            sections.append("")

        contact_text = self._get_text_from_pages("contact")
        if contact_text:
            sections.append("### Contact Details (from website)\n")
            sections.append(contact_text)
            sections.append("")

        # Web Presence
        sections.append("## 8. Web Presence\n")
        for url in bg["websites"]:
            sections.append(f"- {url}")
        sections.append("- LinkedIn: https://www.linkedin.com/company/y5-solutions-inc")
        sections.append("")

        # Data Sources
        sections.append("## 9. Data Sources\n")
        sections.append(
            f"**Scrape Date:** {self.raw_data.get('scraped_at', 'N/A')}"
        )
        sections.append(
            f"**Transport Mode:** {self.raw_data.get('transport_mode', 'N/A')}"
        )
        sections.append(
            f"**Pages Attempted:** {scrape_summary['total_pages']}"
        )
        sections.append(
            f"**Pages Successful:** {scrape_summary['successful']}"
        )
        sections.append(
            f"**Pages Failed:** {scrape_summary['failed']}"
        )
        sections.append("")

        sections.append("### Pages Scraped\n")
        for site_name, pages in self.raw_data.get("sites", {}).items():
            sections.append(f"**{site_name}:**")
            for page in pages:
                status = "OK" if page.get("success") else page.get("error", "Failed")
                sections.append(f"- {page['url']} - {status}")
            sections.append("")

        return "\n".join(sections)

    def generate_json(self):
        """Generate a structured JSON report."""
        bg = self.background
        scraped_contact = self._extract_contact_info()
        scrape_summary = self._get_scrape_summary()

        report = {
            "company": {
                "name": bg["name"],
                "founded": bg["founded"],
                "headquarters": bg["headquarters"],
                "offices": bg["offices"],
                "leadership": bg["leadership"],
                "revenue": bg["revenue"],
                "company_type": bg["company_type"],
                "industry": bg["industry"],
                "description": bg["description"],
                "vision": bg["vision"],
            },
            "services": bg["services"],
            "technology": bg["technology"],
            "target_customers": bg["target_customers"],
            "contact": {
                "address": bg["headquarters"],
                "phone": scraped_contact.get("phone", ["(310) 997-0045"]),
                "email": scraped_contact.get("email", []),
            },
            "web_presence": {
                "websites": bg["websites"],
                "linkedin": "https://www.linkedin.com/company/y5-solutions-inc",
            },
            "scraped_content": {},
            "scrape_metadata": {
                "scraped_at": self.raw_data.get("scraped_at"),
                "transport_mode": self.raw_data.get("transport_mode"),
                "summary": scrape_summary,
            },
        }

        # Add scraped text content organized by category
        for category, pages in self.pages_by_category.items():
            if pages:
                report["scraped_content"][category] = [
                    {
                        "url": p["url"],
                        "title": p.get("metadata", {}).get("title", ""),
                        "text": p.get("text_content", "")[:2000],  # Trim for JSON
                    }
                    for p in pages
                ]

        return report

    def save_reports(self, output_dir):
        """Write both Markdown and JSON reports to the output directory."""
        os.makedirs(output_dir, exist_ok=True)

        # Save raw data
        raw_path = os.path.join(output_dir, config.RAW_DATA_FILE)
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(self.raw_data, f, indent=2, ensure_ascii=False)
        logger.info("Raw data saved to %s", raw_path)

        # Save Markdown report
        md_path = os.path.join(output_dir, config.REPORT_MD_FILE)
        md_content = self.generate_markdown()
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        logger.info("Markdown report saved to %s", md_path)

        # Save JSON report
        json_path = os.path.join(output_dir, config.REPORT_JSON_FILE)
        json_content = self.generate_json()
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_content, f, indent=2, ensure_ascii=False)
        logger.info("JSON report saved to %s", json_path)

        return {
            "raw_data": raw_path,
            "markdown_report": md_path,
            "json_report": json_path,
        }
