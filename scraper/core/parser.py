# scraper/core/parser.py

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from scraper.core.cleaner import Cleaner
import re


class Parser:
    """
    Encapsulates all parsing utilities:
    - link extraction
    - title/description extraction
    - main content extraction
    - full page parsing
    """

    def __init__(self, config):
        self.config = config
        self.selectors = config.get("selectors", {})
        self.cleaner = Cleaner()


    def extract_links(self, html, base_url):
        """
        Extract all internal <a href=""> links from an HTML document
        """
        soup = BeautifulSoup(html, "html.parser")
        links = set()

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()

            # Ignore javascript:, mailto:, tel:
            if href.startswith(("javascript:", "mailto:", "tel:")):
                continue

            # Convert relative → absolute URL
            absolute_url = urljoin(base_url, href)
            links.add(absolute_url)

        return links

    def _extract_title(self, soup):
        """Extract title using selector or fallback to <title>"""
        selector = self.selectors.get("title")

        if selector:
            el = soup.select_one(selector)
            if el and el.get_text(strip=True):
                return el.get_text(strip=True)

        # fallback: page <title>
        if soup.title and soup.title.string:
            return soup.title.string.strip()

        return None

    def _extract_description(self, soup):
        """Extract description from meta tags or selector"""
        selector = self.selectors.get("description")

        if selector:
            meta = soup.select_one(selector)
            if meta and meta.get("content"):
                return meta["content"].strip()

        # fallback: generic meta description
        generic = soup.find("meta", attrs={"name": "description"})
        if generic and generic.get("content"):
            return generic["content"].strip()

        return None

    def _extract_main_content(self, soup):
        """
        Extract main text content using:
        - content_containers (outer wrappers)
        - content_tags (inner tags)
        """
        content_blocks = []

        containers = self.selectors.get("content_containers", [])
        tags = self.selectors.get("content_tags", ["p"])

        # Extract from configured containers
        for container_selector in containers:
            for container in soup.select(container_selector):
                for tag in container.find_all(tags):
                    text = tag.get_text(" ", strip=True)
                    if text:
                        content_blocks.append(text)

        # fallback: all <p> tags if nothing extracted
        if not content_blocks:
            for tag in soup.find_all("p"):
                text = tag.get_text(" ", strip=True)
                if text:
                    content_blocks.append(text)

        full_text = "\n".join(content_blocks)
        return self.cleaner.clean(full_text)

    def parse(self, html, url):
        """
        Parse HTML page into JSON
        {
            "url": "",
            "title": "",
            "description": "",
            "body_text": "",
        }
        """
        soup = BeautifulSoup(html, "html.parser")

        return {
            "url": url,
            "title": self._extract_title(soup),
            "description": self._extract_description(soup),
            "body_text": self._extract_main_content(soup),
        }