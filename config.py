"""Configuration for Y5 Solutions web scraper."""

# Target websites and their known pages
TARGET_SITES = {
    "y5solutions": {
        "base_url": "https://www.y5solutions.com",
        "pages": [
            "/",
            "/logistics-solutions-our-story",
            "/logistics-solutions-our-vision",
            "/logistics-solutions-our-platform",
            "/logistics-solutions-contact-us",
            "/logistics-solutions-ocean-shipping",
            "/logistics-solutions-shipper",
            "/logistics-solutions-carrier",
            "/logistics-solutions-logistics-provider",
            "/logistics-solutions-port-drayage",
            "/logistics-solutions-customs-brokerage",
            "/logistics-solutions-login",
        ],
    },
    "y5logistics": {
        "base_url": "https://www.y5logistics.com",
        "pages": [
            "/",
            "/logistics-solutions",
            "/transport-management-software-in-los-angeles-california",
            "/logistics-about-us/contact-us",
            "/logistics-products",
            "/logistics-management-in-los-angeles-california/warehousing",
            "/logistics-software",
        ],
    },
}

# HTTP request configuration
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

REQUEST_TIMEOUT = 30  # seconds
REQUEST_DELAY = (1, 3)  # random delay range between requests (seconds)
MAX_RETRIES = 3

# Output configuration
OUTPUT_DIR = "output"
RAW_DATA_FILE = "raw_pages.json"
REPORT_MD_FILE = "company_report.md"
REPORT_JSON_FILE = "company_report.json"

# Pre-gathered company background data (from web search)
# This ensures the report is comprehensive even if scraping fails
COMPANY_BACKGROUND = {
    "name": "Y5 Solutions, Inc.",
    "founded": 2008,
    "headquarters": {
        "address": "24328 S Vermont Ave, Suite 230",
        "city": "Harbor City",
        "state": "CA",
        "zip": "90710",
        "country": "USA",
    },
    "offices": ["Los Angeles, California, USA", "Shanghai, China"],
    "leadership": [
        {"name": "Andy Ho", "title": "CEO"},
        {"name": "Jennifer Ho", "title": "COO"},
    ],
    "revenue": "~$5M (2025)",
    "company_type": "NVOCC (Non-Vessel Operating Common Carrier)",
    "industry": "Logistics & Supply Chain",
    "websites": [
        "https://www.y5solutions.com",
        "https://www.y5logistics.com",
    ],
    "services": [
        "Ocean Shipping / Ocean Freight",
        "Air Freight",
        "Ground Transportation",
        "Customs Brokerage",
        "Warehousing",
        "Port Drayage",
    ],
    "technology": {
        "description": (
            "Proprietary cloud-based logistics platform with integrated "
            "ERP, CRM, SRM, and WMS systems. AI-driven end-to-end logistics "
            "solution with SCLM (Supply Chain Logistics Management) software."
        ),
        "systems": ["ERP", "CRM", "SRM", "WMS", "TMS"],
        "features": [
            "Real-time shipment tracking and dashboard",
            "Allocation management technology",
            "AI-powered logistics optimization",
            "Online booking with instant confirmation",
            "Android & Apple mobile apps",
            "EDI integration",
            "Customer Portal System",
            "Digital Depot System",
            "Transportation Management System (TMS)",
        ],
    },
    "target_customers": [
        {
            "type": "Shippers",
            "description": (
                "Quick quotes, market-based rates with online booking, "
                "manage all shipments under one platform"
            ),
        },
        {
            "type": "Carriers",
            "description": (
                "User-friendly technology, quick pay options, "
                "address hauling needs efficiently"
            ),
        },
        {
            "type": "Logistics Providers",
            "description": (
                "Seamless integration with existing tools, "
                "real-time operations management"
            ),
        },
    ],
    "vision": (
        "Y5 Solutions believes that with their operation system, a tech "
        "innovation platform can seamlessly connect global trade with every "
        "single supply chain."
    ),
    "description": (
        "Y5 Solutions, Inc. is a logistics solutions provider based near "
        "Long Beach Port, established in 2008. The company is dedicated to "
        "engaging complete cloud-based solutions supported by their own "
        "in-house custom-made cloud-based software system. They offer a "
        "comprehensive range of services including ocean shipping, air freight, "
        "ground transportation, customs brokerage, warehousing, and port "
        "drayage. Y5 Solutions aims to deliver efficient logistics processes "
        "tailored to customer needs, leveraging advanced technology and "
        "standardized operations. Their AI-driven end-to-end logistics solution "
        "is dedicated to simplifying the shipping experience."
    ),
}
