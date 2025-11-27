import pytest
from scraper.core.parser import Parser
from scraper.core.cleaner import Cleaner
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

@pytest.fixture
def complex_html():
    path = os.path.join(os.path.dirname(__file__), "data", "test_data.html")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def config():
    return {
        "selectors": {
            "title": "h1",
            "description": "meta[name='description']",
            "content_containers": [".main-content"],
            "content_tags": ["p", "li"]
        }
    }


@pytest.fixture
def parser(config):
    return Parser(config)

def test_extract_links(parser, complex_html):
    base = "https://example.com/base/page"
    links = parser.extract_links(complex_html, base)

    assert urljoin(base, "/relative/link") in links
    assert "https://example.com/absolute/link" in links

    assert not any("javascript:" in l for l in links)
    assert not any("mailto:" in l for l in links)
    assert not any("tel:" in l for l in links)

def test_extract_title(parser, complex_html):
    soup = BeautifulSoup(complex_html, "html.parser")
    assert parser._extract_title(soup) == "Test Heading"

def test_extract_description(parser, complex_html):
    soup = BeautifulSoup(complex_html, "html.parser")
    desc = parser._extract_description(soup)
    assert desc == "This is a sample description for testing."

def test_extract_main_content(parser, complex_html):
    soup = BeautifulSoup(complex_html, "html.parser")
    text = parser._extract_main_content(soup)

    assert "First paragraph with" in text
    assert "Second paragraph" in text
    assert "Nested paragraph" in text
    assert "List item one" in text
    assert "Article paragraph inside" in text

    assert "Sidebar content" not in text
    assert "Footer information" not in text
    assert "&nbsp;" not in text

def test_parse_page(parser, complex_html):
    url = "https://example.com/test"
    result = parser.parse(complex_html, url)

    assert result["url"] == url
    assert result["title"] == "Test Heading"
    assert result["description"] == "This is a sample description for testing."
    assert "First paragraph" in result["body_text"]
    assert "Article paragraph inside" in result["body_text"]