# scraper/core/cleaner.py

import re
import unicodedata
import html

class Cleaner:
    """
    Text cleaning utility:
    Provides unicode normalization, HTML entity decoding,
    whitespace normalization, boilerplate removal
    """

    def __init__(self, boilerplate_rules=None):
        """
        Initialize cleaner with optional boilerplate removal rules
        boilerplate_rules: list of regex patterns to remove
        """
        self.boilerplate_rules = boilerplate_rules or []

    def _normalize_unicode(self, text):
        """Normalize unicode characters to NFC standard form"""
        if not text:
            return ""
        return unicodedata.normalize("NFC", text)

    def _remove_html_artifacts(self, text):
        """Decode HTML entities and turn non-breaking spaces into regular spaces."""
        if not text:
            return ""
        decoded = html.unescape(text)
        return decoded.replace("\xa0", " ")

    def _normalize_whitespace(self, text):
        """Collapse repeated whitespace and blank lines"""
        if not text:
            return ""
        # replace tab-spaces with single spaces
        text = re.sub(r"[ \t]{2,}", " ", text)      
        # remove blank lines with double newlines    
        text = re.sub(r"\n\s*\n", "\n\n", text)         
        return text.strip()

    def _remove_boilerplate(self, text):
        """Remove regex-based boilerplate patterns (optional)"""
        if not text:
            return ""

        if not self.boilerplate_rules:
            return text

        for pattern in self.boilerplate_rules:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)

        return text
    
    def clean(self, text):
        """Apply all cleaning steps in sequence"""
        if not text:
            return ""

        text = self._normalize_unicode(text)
        text = self._remove_html_artifacts(text)
        text = self._remove_boilerplate(text)
        text = self._normalize_whitespace(text)

        return text


# Convenience function for users who still import clean()
_default_cleaner = Cleaner()

def clean(text, boilerplate_rules=None):
    """
    Backward-compatible functional interface.
    Uses a temporary Cleaner instance if boilerplate_rules are provided.
    """
    if boilerplate_rules:
        return Cleaner(boilerplate_rules).clean(text)
    return _default_cleaner.clean(text)