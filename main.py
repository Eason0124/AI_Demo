"""Entry point for the Y5 Solutions company info scraper."""

import argparse
import logging
import sys

import config
from report_generator import ReportGenerator
from scraper import HttpClient, SiteScraper


def setup_logging():
    """Configure logging to stdout."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main():
    parser = argparse.ArgumentParser(
        description="Scrape Y5 Solutions websites and generate company reports"
    )
    parser.add_argument(
        "--output-dir",
        default=config.OUTPUT_DIR,
        help=f"Output directory for reports (default: {config.OUTPUT_DIR})",
    )
    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Y5 Solutions Company Info Scraper")
    logger.info("=" * 60)

    # Phase 1: Scrape
    logger.info("Phase 1: Initializing HTTP client...")
    client = HttpClient()
    logger.info("Transport mode: %s", client.transport_mode)

    logger.info("Phase 1: Scraping target websites...")
    scraper = SiteScraper(client)
    raw_data = scraper.scrape_all()

    # Summary
    total_pages = 0
    total_success = 0
    for site_name, pages in raw_data["sites"].items():
        success = sum(1 for p in pages if p["success"])
        total_pages += len(pages)
        total_success += success
        logger.info("  %s: %d/%d pages scraped", site_name, success, len(pages))

    logger.info("Total: %d/%d pages scraped successfully", total_success, total_pages)

    # Phase 2: Generate reports
    logger.info("Phase 2: Generating reports...")
    generator = ReportGenerator(raw_data)
    output_files = generator.save_reports(args.output_dir)

    # Final summary
    logger.info("=" * 60)
    logger.info("Scraping complete!")
    logger.info("Output files:")
    for name, path in output_files.items():
        logger.info("  %s: %s", name, path)
    logger.info("=" * 60)

    # Exit code: 0 if at least some pages scraped OR background data available
    if total_success == 0:
        logger.warning(
            "No pages were scraped successfully. "
            "Reports generated from background data only."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
