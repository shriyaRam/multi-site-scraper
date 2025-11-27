import pytest
import hashlib
import time
from scraper.core.enricher import Enricher

@pytest.fixture
def config():
    return {
        "enrichment": {
            "content_type": "health_topic",
            "topic_labels": ["health", "medicine", "allergy"]
        }
    }

@pytest.fixture
def enricher(config):
    return Enricher(config)


@pytest.fixture
def parsed_doc():
    return {
        "url": "https://example.com/health/food-allergy",
        "title": "Food Allergy",
        "description": "A reaction of the immune system to certain foods.",
        "body_text": (
            "Food allergies occur when the body reacts to certain foods.\n"
            "What causes food allergies?\n"
            "Common allergens include nuts, milk, and eggs.\n\n"
            "How do you diagnose food allergies?\n"
            "Testing usually involves skin or blood tests."
        )
    }


def test_language_detection(enricher, parsed_doc):
    result = enricher.enrich(parsed_doc)
    assert result["language"] == "en"

def test_domain_extraction(enricher, parsed_doc):
    result = enricher.enrich(parsed_doc)
    assert result["source_domain"] == "example.com"

def test_readability_score(enricher, parsed_doc):
    result = enricher.enrich(parsed_doc)
    score = result["readability_score"]

    assert isinstance(score, float)
    assert score >= 0.0

def test_summary_uses_description(enricher, parsed_doc):
    result = enricher.enrich(parsed_doc)
    assert result["summary"].startswith("A reaction of the immune system")
    assert len(result["summary"]) <= 360


def test_summary_fallback_to_body(enricher):
    doc = {
        "url": "x",
        "title": "t",
        "description": None,
        "body_text": "This is fallback body text used for summary."
    }

    result = enricher.enrich(doc)
    assert result["summary"].startswith("This is fallback")

def test_keywords_extracted(enricher, parsed_doc):
    result = enricher.enrich(parsed_doc)
    kws = result["keywords"]

    assert isinstance(kws, list)
    assert len(kws) > 0
    for kw in kws:
        assert isinstance(kw, str)

def test_extract_questions(enricher, parsed_doc):
    result = enricher.enrich(parsed_doc)
    qs = result["questions"]

    assert any(q.startswith("What") for q in qs)
    assert any(q.startswith("How") for q in qs)
    assert all(q.endswith("?") for q in qs)

def test_text_length_bin(enricher, parsed_doc):
    result = enricher.enrich(parsed_doc)
    length = result["text_length"]

    assert length in {"short", "medium", "long", "very_long"}

def test_content_hash(enricher, parsed_doc):
    result = enricher.enrich(parsed_doc)
    expected = hashlib.sha256(parsed_doc["body_text"].encode("utf-8")).hexdigest()

    assert result["content_hash"] == expected

def test_fetched_at_timestamp(monkeypatch, enricher, parsed_doc):
    fake_time = 1700000000
    monkeypatch.setattr(time, "time", lambda: fake_time)

    result = enricher.enrich(parsed_doc)
    assert result["fetched_at"] == fake_time

def test_enriched_contains_parsed_fields(enricher, parsed_doc):
    result = enricher.enrich(parsed_doc)

    assert result["url"] == parsed_doc["url"]
    assert result["title"] == parsed_doc["title"]
    assert result["body_text"] == parsed_doc["body_text"]
    assert "word_count" in result
    assert "language" in result
    assert "content_type" in result