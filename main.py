# main.py

import argparse
import json
import os

from scraper.core.crawler import Crawler
from scraper.core.parser import Parser
from scraper.core.enricher import Enricher
from scraper.core.writer import JSONLWriter
from scraper.core.logger import Logger

logger = Logger(__name__).get()


def load_config(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_pipeline(config_path, output_path):
    # Load config
    config = load_config(config_path)
    logger.info(f"Loaded config for site: {config.get('site_name')}")

    # Initialize crawler
    crawler = Crawler(config)
    #Initialize the parser
    parser = Parser(config)
    
    start_urls = config.get("start_urls", [])
    max_pages = config["crawl"].get("max_pages")

    logger.info(f"Starting crawl: {start_urls} (max_pages={max_pages})")

    # Execute crawl
    crawled_pages = crawler.crawl(
        start_urls=start_urls,
        link_extractor=parser.extract_links,
    )
    logger.info(f"Crawl completed. Pages collected: {len(crawled_pages)}")

    # Initialize writer
    writer = JSONLWriter(output_path, overwrite=False)

    #Initialize enricher for AI relevant signal
    enricher = Enricher(config)

    # Parse - Enrich - Write
    for url, html in crawled_pages.items():
        try:
            parsed = parser.parse(html, url)
            enriched = enricher.enrich(parsed)
            writer.write(enriched)
        except Exception as e:
            logger.error(f"Pipeline error on {url}: {e}")

    writer.close()
    logger.info(f"Pipeline complete. Output saved to: {output_path}")


def cli():
    arg_parser = argparse.ArgumentParser(
        description="Multi-site scraping pipeline"
    )

    arg_parser.add_argument(
        "--config",
        required=True,
        help="Path to JSON config file for the target site (e.g., configs/medlineplus.json)",
    )

    arg_parser.add_argument(
        "--output",
        required=True,
        help="Output .jsonl file (e.g., output/medlineplus.jsonl)",
    )

    args = arg_parser.parse_args()
    run_pipeline(args.config, args.output)


if __name__ == "__main__":
    cli()