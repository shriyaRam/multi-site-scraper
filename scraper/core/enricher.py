# scraper/core/enricher.py

import time
import re
import hashlib
import tldextract
from collections import Counter
from langdetect import detect, LangDetectException
import yake
class Enricher:
    """
    Enrich parsed page data with AI-friendly metadata such as
    language, keywords, summary, readability, and domain signals
    """

    def __init__(self, config):
        self.cfg = config.get("enrichment", {})
        self.top_k = self.cfg.get("topk_keyword_count", 10)
        self.content_type = self.cfg.get("content_type", "generic")
        self.topic_labels = self.cfg.get("topic_labels", ["general"])


    def _safe_lang(self, text, default="en"):
        """Detect language with fallback"""
        try:
            return detect(text) if len(text) > 25 else default
        except LangDetectException:
            return default

    def _sentence_count(self, text):
        """Approximate sentence count using punctuation splits"""
        parts = re.split(r"[.!?]+", text)
        return max(1, len([p for p in parts if p.strip()]))

    def _extract_domain(self, url):
        """Return root domain for the URL"""
        ext = tldextract.extract(url)
        return f"{ext.domain}.{ext.suffix}"

    def _redundancy_penalty(self, text):
        """Compute fraction of repeated paragraphs"""
        paras = [p.strip() for p in text.split("\n") if p.strip()]
        if not paras:
            return 0.0
        counts = Counter(paras)
        repeats = sum(v - 1 for v in counts.values() if v > 1)
        return repeats / len(paras)

    def _readability(self, text):
        """
        Readability heuristic using:
        avg sentence length, avg word length, redundancy penalty
        Lower score = easier to read, higher score = more complex
        """
        words = re.findall(r"\w+", text)
        if not words:
            return 0.0

        avg_word_len = sum(len(w) for w in words) / len(words)
        avg_sent_len = len(words) / self._sentence_count(text)
        penalty = self._redundancy_penalty(text)

        score = (
            0.4 * avg_sent_len +
            0.4 * avg_word_len +
            0.2 * penalty
        )

        return round(score, 3)

    def _extract_keywords(self, text):
        """
        Extract keywords to represent the extracted text
        """
        kw_extractor = yake.KeywordExtractor(top=self.top_k)
        return [kw for kw, score in kw_extractor.extract_keywords(text)]

    def _extract_questions(self, text, max_q=5):
        """Return questions found in the body text"""
        qpattern = re.compile(r"^(what|why|how|when|where|who|which|can|does|do)\b", re.IGNORECASE)
        lines = text.split("\n")

        qs = []
        for line in lines:
            clean = line.strip()
            if clean.endswith("?") and qpattern.match(clean):
                qs.append(clean)

        return qs[:max_q]

    def _summary(self, parsed, max_chars=350):
        """return an initial substring of the description if available; fallback: truncate body"""
        desc = parsed.get("description")
        if desc:
            clean = " ".join(desc.split())
            return clean[:max_chars].rstrip() + ("..." if len(clean) > max_chars else "")

        body = parsed.get("body_text", "")
        clean = " ".join(body.split())
        return clean[:max_chars].rstrip() + ("..." if len(clean) > max_chars else "")
    
    def enrich(self, parsed):
        """
        Return AI-friendly enriched JSON object
        by combining parsed fields + metadata signals
        """
        text = parsed.get("body_text", "") or ""
        url = parsed.get("url", "")
        words = text.split()
        wcount = len(words)

        enriched = {
            "content_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "word_count": wcount,
            "char_count": len(text),
            "text_length": (
                "short" if wcount < 100 else
                "medium" if wcount < 500 else
                "long" if wcount < 2000 else
                "very_long"
            ),
            "readability_score": self._readability(text),
            "source_domain": self._extract_domain(url),
            "language": self._safe_lang(text),
            "keywords": self._extract_keywords(text),
            "content_type": self.content_type,
            "summary": self._summary(parsed),
            "questions": self._extract_questions(text),
            "fetched_at": int(time.time())
        }

        # merge parsed fields and enrichment fields
        return {**parsed, **enriched}