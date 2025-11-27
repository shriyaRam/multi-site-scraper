# scraper/core/crawler.py

import time
from urllib.parse import urljoin, urlparse
import requests
from collections import deque
from scraper.core.logger import Logger


class Crawler:
    def __init__(self, config):
        self.allowed_domains = config["allowed_domains"]
        self.exclude_patterns = config["crawl"].get("exclude_patterns", [])
        self.include_patterns = config["crawl"].get("include_patterns", [""])
        self.min_depth = config["crawl"].get("min_depth", 0)
        self.max_depth = config["crawl"].get("max_depth", 1)
        self.max_pages = config["crawl"].get("max_pages", 100)
        self.logger = Logger(__name__).get()
        self.visited = set()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "multi-site-scraper/1.0 (+https://github.com/shriyaRam/multi-site-scraper)"
        })

    def _allowed_domain(self, url):
        """Check if URL belongs to allowed domains"""
        hostname = urlparse(url).hostname or ""
        return any(domain in hostname for domain in self.allowed_domains)

    def _excluded(self, url):
        """Check patterns that are not allowed in the URL"""
        return any(pattern in url for pattern in self.exclude_patterns)

    def _included(self, url):
        """Check if pattern matches the explicitly listed URL patterns
        (optional, can restrict scraping to only certain endpoints)"""
        return any(keyword in url for keyword in self.include_patterns)

    def fetch(self, url, retries=3):
        """Fetch HTML with retries and throttling"""
        for attempt in range(1, retries + 1):
            try:
                resp = self.session.get(url, timeout=10)
                resp.raise_for_status()
                #polite delay to avoid overloading the server and risk being blocked
                time.sleep(0.7)  
                return resp.text
            except Exception as e:
                self.logger.error(f"Fetch failed ({attempt}/{retries}) for {url}: {e}")
                time.sleep(1)

        return None

    def extract_links(self, html, base_url, selector_fn):
        """
        Extract links using the parser's link extractor
        selector_fn: a function that extracts links from a tags in the HTML using BeautifulSoup
        """
        try:
            return selector_fn(html, base_url)
        except Exception as e:
            self.logger.error(f"Link extraction error: {e}")
            return set()

    def crawl(self, start_urls, link_extractor):
        """
        BFS crawl starting from start_url(s)
        link_extractor: function that extracts links from HTML
        Returns a dict of {url: html}
        """
        queue = deque([(url, 0) for url in start_urls])
        results = {}

        while queue and len(results) < self.max_pages:
            url, depth = queue.popleft()

            if url in self.visited:
                continue

            if depth > self.max_depth:
                continue

            if not self._allowed_domain(url):
                continue
            if self._excluded(url):
                continue
            if not self._included(url):
                continue

            self.logger.info(f"Crawling: {url} (depth {depth})")

            html = self.fetch(url)
            if not html:
                continue

            if depth >= self.min_depth:
                results[url] = html
            self.visited.add(url)

            # Extract links for crawling
            if depth < self.max_depth:
                discovered_links = self.extract_links(html, url, link_extractor)
                for link in discovered_links:
                    if link not in self.visited:
                        queue.append((link, depth + 1))

        return results