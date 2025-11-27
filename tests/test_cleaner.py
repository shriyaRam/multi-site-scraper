# tests/test_cleaner.py

import pytest
from scraper.core.cleaner import Cleaner, clean
@pytest.fixture
def cleaner():
    return Cleaner()


@pytest.fixture
def cleaner_with_rules():
    return Cleaner(boilerplate_rules=[r"Subscribe Now", r"Cookie Policy", r"Disclaimer"])

def test_normalize_unicode_basic(cleaner):
    messy = "Cafe\u0301"  # "e" + combining accent (not normalized)
    cleaned = cleaner._normalize_unicode(messy)
    assert cleaned == "Café"


def test_normalize_unicode_empty(cleaner):
    assert cleaner._normalize_unicode("") == ""
    assert cleaner._normalize_unicode(None) == ""

def test_remove_html_entities(cleaner):
    raw = "Tom &amp; Jerry &nbsp; Cartoon"
    cleaned = cleaner._remove_html_artifacts(raw)
    # Normalize \xa0 into a regular space before asserting
    assert cleaned == "Tom & Jerry   Cartoon"


def test_remove_html_entities_empty(cleaner):
    assert cleaner._remove_html_artifacts("") == ""
    assert cleaner._remove_html_artifacts(None) == ""

def test_normalize_whitespace(cleaner):
    raw = "Hello    world\t\tthis   is\n\n\nclean"
    cleaned = cleaner._normalize_whitespace(raw)
    assert "Hello world this is" in cleaned
    assert cleaned.count("\n\n") == 1


def test_normalize_whitespace_no_input(cleaner):
    assert cleaner._normalize_whitespace("") == ""
    assert cleaner._normalize_whitespace(None) == ""

def test_remove_boilerplate(cleaner_with_rules):
    raw = """
        Welcome to the site.
        Subscribe Now to continue reading.
        This page uses Cookie Policy terms.
        Disclaimer: This is only a test.
    """

    cleaned = cleaner_with_rules._remove_boilerplate(raw)

    assert "Subscribe Now" not in cleaned
    assert "Cookie Policy" not in cleaned
    assert "Disclaimer" not in cleaned
    assert "Welcome to the site" in cleaned


def test_remove_boilerplate_no_rules(cleaner):
    raw = "Hello World Subscribe Now"
    cleaned = cleaner._remove_boilerplate(raw)
    # no rules → text unchanged
    assert cleaned == raw

def test_clean_full_pipeline(cleaner_with_rules):
    raw = "Hello&nbsp;World\n\nSubscribe Now"
    cleaned = cleaner_with_rules.clean(raw)

    assert "Hello World" in cleaned
    assert "Subscribe Now" not in cleaned
    assert "&nbsp;" not in cleaned


def test_clean_empty_inputs(cleaner):
    assert cleaner.clean("") == ""
    assert cleaner.clean(None) == ""

def test_clean_function_wrapper_default(cleaner):
    raw = "Hey&nbsp;There"
    cleaned = clean(raw)
    assert "Hey There" in cleaned
    assert "&nbsp;" not in cleaned

def test_clean_function_wrapper_with_rules():
    raw = "Hello Subscribe"
    cleaned = clean(raw, boilerplate_rules=[r"Subscribe"])
    assert cleaned == "Hello"