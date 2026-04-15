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
        """Generate a comprehensive Markdown company report in Chinese."""
        bg = self.background
        scraped_contact = self._extract_contact_info()
        scrape_summary = self._get_scrape_summary()

        sections = []

        # Title
        sections.append(f"# {bg['name']} - 公司報告\n")

        # Company Overview
        sections.append("## 1. 公司概覽\n")
        sections.append("| 項目 | 詳細資訊 |")
        sections.append("|------|----------|")
        sections.append(f"| **公司名稱** | {bg['name']} |")
        sections.append(f"| **成立年份** | {bg['founded']} 年 |")
        sections.append(f"| **產業類別** | {bg.get('industry_zh', bg['industry'])} |")
        sections.append(f"| **公司類型** | {bg.get('company_type_zh', bg['company_type'])} |")
        hq = bg["headquarters"]
        sections.append(
            f"| **總部地址** | {hq['address']}, {hq['city']}, {hq['state']} {hq['zip']} |"
        )
        sections.append(f"| **年營收** | {bg['revenue']} |")
        sections.append(f"| **官方網站** | {', '.join(bg['websites'])} |")
        sections.append("")

        # Leadership
        title_zh = {"CEO": "執行長", "COO": "營運長", "CTO": "技術長", "CFO": "財務長"}
        sections.append("### 管理團隊\n")
        for leader in bg["leadership"]:
            zh = title_zh.get(leader["title"], "")
            label = f"{leader['title']}（{zh}）" if zh else leader["title"]
            sections.append(f"- **{label}**: {leader['name']}")
        sections.append("")

        # Office Locations
        sections.append("### 辦公地點\n")
        for office in bg.get("offices_zh", bg["offices"]):
            sections.append(f"- {office}")
        sections.append("")

        # Company Description
        sections.append("## 2. 公司簡介\n")
        sections.append(bg.get("description_zh", bg["description"]))
        sections.append("")

        # Scraped about content
        about_text = self._get_text_from_pages("about")
        if about_text:
            sections.append("### 公司故事（網站內容）\n")
            sections.append(about_text)
            sections.append("")

        # Homepage content
        homepage_text = self._get_text_from_pages("homepage")
        if homepage_text:
            sections.append("### 網站首頁內容\n")
            sections.append(homepage_text)
            sections.append("")

        # Vision & Mission
        sections.append("## 3. 願景與使命\n")
        sections.append(bg.get("vision_zh", bg["vision"]))
        sections.append("")

        vision_text = self._get_text_from_pages("vision")
        if vision_text:
            sections.append("### 網站內容\n")
            sections.append(vision_text)
            sections.append("")

        # Services
        sections.append("## 4. 服務項目\n")
        sections.append("Y5 Solutions 提供全方位的物流服務：\n")
        for service in bg.get("services_zh", bg["services"]):
            sections.append(f"- **{service}**")
        sections.append("")

        services_text = self._get_text_from_pages("services")
        if services_text:
            sections.append("### 服務詳情（網站內容）\n")
            sections.append(services_text)
            sections.append("")

        # Technology Platform
        sections.append("## 5. 技術平台\n")
        tech = bg["technology"]
        sections.append(tech.get("description_zh", tech["description"]))
        sections.append("")

        sections.append("### 整合系統\n")
        for system in tech["systems"]:
            sections.append(f"- {system}")
        sections.append("")

        sections.append("### 核心功能\n")
        for feature in tech.get("features_zh", tech["features"]):
            sections.append(f"- {feature}")
        sections.append("")

        platform_text = self._get_text_from_pages("platform")
        if platform_text:
            sections.append("### 平台詳情（網站內容）\n")
            sections.append(platform_text)
            sections.append("")

        # Target Customers
        sections.append("## 6. 目標客戶\n")
        for customer in bg["target_customers"]:
            sections.append(f"### {customer.get('type_zh', customer['type'])}\n")
            sections.append(customer.get("description_zh", customer["description"]))
            sections.append("")

        customers_text = self._get_text_from_pages("customers")
        if customers_text:
            sections.append("### 客戶詳情（網站內容）\n")
            sections.append(customers_text)
            sections.append("")

        # Contact Information
        sections.append("## 7. 聯絡資訊\n")
        hq = bg["headquarters"]
        sections.append(
            f"**地址：** {hq['address']}, {hq['city']}, {hq['state']} {hq['zip']}, {hq['country']}"
        )
        sections.append("")

        if scraped_contact.get("phone"):
            sections.append(f"**電話：** {', '.join(scraped_contact['phone'])}")
            sections.append("")
        else:
            sections.append("**電話：** (310) 997-0045")
            sections.append("")

        if scraped_contact.get("email"):
            sections.append(f"**電子郵件：** {', '.join(scraped_contact['email'])}")
            sections.append("")

        contact_text = self._get_text_from_pages("contact")
        if contact_text:
            sections.append("### 聯絡詳情（網站內容）\n")
            sections.append(contact_text)
            sections.append("")

        # Web Presence
        sections.append("## 8. 網路資源\n")
        for url in bg["websites"]:
            sections.append(f"- {url}")
        sections.append("- LinkedIn: https://www.linkedin.com/company/y5-solutions-inc")
        sections.append("")

        # Data Sources
        sections.append("## 9. 資料來源\n")
        sections.append(
            f"**爬取日期：** {self.raw_data.get('scraped_at', 'N/A')}"
        )
        sections.append(
            f"**傳輸模式：** {self.raw_data.get('transport_mode', 'N/A')}"
        )
        sections.append(
            f"**嘗試頁面數：** {scrape_summary['total_pages']}"
        )
        sections.append(
            f"**成功頁面數：** {scrape_summary['successful']}"
        )
        sections.append(
            f"**失敗頁面數：** {scrape_summary['failed']}"
        )
        sections.append("")

        sections.append("### 爬取頁面清單\n")
        for site_name, pages in self.raw_data.get("sites", {}).items():
            sections.append(f"**{site_name}：**")
            for page in pages:
                status = "成功" if page.get("success") else page.get("error", "失敗")
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
                "offices_zh": bg.get("offices_zh", bg["offices"]),
                "leadership": bg["leadership"],
                "revenue": bg["revenue"],
                "company_type": bg["company_type"],
                "company_type_zh": bg.get("company_type_zh", ""),
                "industry": bg["industry"],
                "industry_zh": bg.get("industry_zh", ""),
                "description": bg["description"],
                "description_zh": bg.get("description_zh", ""),
                "vision": bg["vision"],
                "vision_zh": bg.get("vision_zh", ""),
            },
            "services": bg["services"],
            "services_zh": bg.get("services_zh", []),
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
