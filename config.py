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
    "services_zh": [
        "海運 (Ocean Shipping / Ocean Freight)",
        "空運 (Air Freight)",
        "陸運 (Ground Transportation)",
        "報關服務 (Customs Brokerage)",
        "倉儲管理 (Warehousing)",
        "港口拖車 (Port Drayage)",
    ],
    "technology": {
        "description": (
            "Proprietary cloud-based logistics platform with integrated "
            "ERP, CRM, SRM, and WMS systems. AI-driven end-to-end logistics "
            "solution with SCLM (Supply Chain Logistics Management) software."
        ),
        "description_zh": (
            "自主研發的雲端物流平台，整合了 ERP、CRM、SRM 和 WMS 系統。"
            "搭載 AI 驅動的端到端物流解決方案，配備 SCLM（供應鏈物流管理）軟體。"
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
        "features_zh": [
            "即時貨運追蹤與管理儀表板",
            "艙位分配管理技術",
            "AI 智能物流優化",
            "線上訂艙與即時確認",
            "Android 及 Apple 行動應用程式",
            "EDI 電子資料交換整合",
            "客戶入口系統 (Customer Portal)",
            "數位倉儲系統 (Digital Depot)",
            "運輸管理系統 (TMS)",
        ],
    },
    "target_customers": [
        {
            "type": "Shippers",
            "type_zh": "託運人 (Shippers)",
            "description": (
                "Quick quotes, market-based rates with online booking, "
                "manage all shipments under one platform"
            ),
            "description_zh": (
                "快速報價、市場導向的運費費率與線上訂艙確認，"
                "在單一平台上管理所有貨運"
            ),
        },
        {
            "type": "Carriers",
            "type_zh": "承運人 (Carriers)",
            "description": (
                "User-friendly technology, quick pay options, "
                "address hauling needs efficiently"
            ),
            "description_zh": (
                "使用者友善的技術介面、快速付款選項，"
                "高效滿足運輸需求"
            ),
        },
        {
            "type": "Logistics Providers",
            "type_zh": "物流服務商 (Logistics Providers)",
            "description": (
                "Seamless integration with existing tools, "
                "real-time operations management"
            ),
            "description_zh": (
                "與現有工具無縫整合，"
                "即時營運管理"
            ),
        },
    ],
    "vision": (
        "Y5 Solutions believes that with their operation system, a tech "
        "innovation platform can seamlessly connect global trade with every "
        "single supply chain."
    ),
    "vision_zh": (
        "Y5 Solutions 深信透過其營運系統，技術創新平台能夠無縫連接全球貿易與每一條供應鏈。"
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
    "description_zh": (
        "Y5 Solutions, Inc. 是一家位於美國加州長灘港附近的物流解決方案供應商，"
        "成立於 2008 年。公司致力於提供完整的雲端物流解決方案，並以自主研發的雲端"
        "軟體系統為核心支撐。其服務範圍涵蓋海運、空運、陸運、報關、倉儲及港口拖車"
        "等全方位物流服務。Y5 Solutions 以先進技術和標準化營運流程為基礎，為客戶量身"
        "打造高效的物流方案。公司的 AI 驅動端到端物流解決方案，致力於簡化整體運輸體驗。"
    ),
    "industry_zh": "物流與供應鏈",
    "company_type_zh": "NVOCC（無船承運人）",
    "offices_zh": ["美國加州洛杉磯", "中國上海"],
}
