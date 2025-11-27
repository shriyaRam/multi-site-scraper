Overview:

multi-site-scraper as I call it, is a configurable web scraping pipeline that crawls a public website, extracts clean text content, enriches it with AI-ready metadata, and outputs JSONL documents suitable for downstream AI workflows such as RAG, search indexing, and analytics. The project is general-purpose and driven entirely by site-specific configuration files.

1.  Site chosen
    This project uses MedlinePlus as the example site because it is a public, health-focused resource that explicitly allows scraping and provides clean, structured medical content. These pages form reliable ground-truth documents for building retrieval datasets that support AI Q&A systems. Unlike asking an LLM to browse the open internet, which can introduce hallucinations, stale data, and inconsistent sourcing, a curated scraper ensures that answers come from verified, reproducible, and trusted documents. As a future direction, providing an AI-agent interface on top of this curated retrieved dataset could make the health information far more accessible to laymen by enabling natural, guided interactions grounded in legitimate content.

2.  How to Run
    Before running the scraper, you must configure a site-specific JSON configuration file.
    For example, the configs/medlineplus.json file for this scraper controls:
    • allowed_domains: which domains the crawler is permitted to fetch
    • start_urls: where the crawl begins
    • crawl settings: min_depth, max_depth, max_pages, and regex patterns to include/exclude
    • CSS selectors: how to extract titles, descriptions, and main content blocks
    • enrichment flags: which metadata signals the Enricher should compute
    • content_type and keyword extraction count

    There are 3 ways you can run the scraper:

    i. Local Python
    Install dependencies:
    pip install -r requirements.txt
    Run the scraper:
    python main.py --config configs/medlineplus.json --output output/medlineplus.jsonl

    ii. Docker
    Build the image:
    docker build -t multi-site-scraper .
    Run the scraper:
    docker run -v $(pwd)/output:/app/output multi-site-scraper –config configs/medlineplus.json –output output/medlineplus.jsonl

    iii. Makefile
    Build the image:
    make build
    Run the scraper:
    make scrape
    OR
    make scrape CONFIG=configs/medlineplus.json OUTPUT=output/medlineplus.jsonl

3.  Data Schema

    Each record in the JSONL output follows this schema:

    {
    "url": string, // The page URL that was crawled
    "title": string or null, // Extracted page title, or null if missing
    "description": string or null, // Meta description or configured selector output
    "body_text": string, // Cleaned main text extracted from the page

    "content_hash": string, // SHA-256 hash of body_text for deduplication
    "word_count": number, // Total number of words in body_text
    "char_count": number, // Number of characters in body_text
    "text_length": string, // Length bucket: short | medium | long | very_long
    "readability_score": number, // Heuristic complexity score (higher = harder to read)

    "source_domain": string, // Domain extracted from the URL
    "language": string, // Detected language code (ISO)
    "keywords": [string], // Top keywords extracted from body_text
    "content_type": string, // Content category from config (e.g., health_topic_page)

    "summary": string, // Short summary (from meta description or truncated text)
    "questions": [string], // Extracted interrogative lines from the page

    "fetched_at": unix_timestamp // When the page was processed
    }

4.  Design Decisions

    Page Retention Policy:
    -restricts URLs to approved domains from the configuration file
    -filters out excluded paths such as feeds, login pages, and non-content directories
    -limits crawl depth and maximum pages for efficiency
    -retries failed fetches to handle network errors

        These decisions ensure only high-value, content-bearing pages are collected.

    Main Content Extraction:

    - site-specific CSS selectors for containers from config file
    - allowed inner tags such as p, h2, h3, li
    - a fallback that collects all paragraph tags if selectors fail

    The extracted text is cleaned through Unicode normalization, HTML artifact removal, whitespace normalization, and boilerplate removal. This ensures the resulting text is suitable for embeddings and downstream AI models.

    AI-Oriented Metadata

    The enricher.py script computes a set of metadata fields chosen to support typical AI collection workflows. These signals include:
    content_hash: enables fast deduplication and change detection so you don’t waste storage or training/inference on near-identical documents.
    word_count: to filter and bucket documents by size, which is crucial for chunking, windowing, and dataset balancing
    char_count: gives a low-level length signal that helps catch edge cases (like extremely short or weirdly dense documents)
    text_length: turns raw length into easy-to-use buckets for sampling, evaluation splits, and UI filtering
    readability_score: helps prioritize documents that are understandable to users and filter out content that’s too noisy or too complex
    source_domain: preserves provenance so you can enforce trust filters, or restrict retrieval to certain sites
    language: allows language-specific indexing, routing to the right model, and avoiding mixing languages in training or search
    keywords: provides lightweight semantic tags that improve search, faceting, clustering, and quick content inspection
    content_type: gives a coarse-grained label that’s great for routing queries, building topic-specific indexes, and evaluation by segment
    summary: enables fast preview in UIs and can be used as a condensed representation for retrieval or reranking.
    questions: surfaces likely user intents and can be used to generate synthetic QA pairs for fine-tuning or RAG evaluation
    fetched_at: captures freshness so you can reason about staleness, schedule recrawls, and time-slice analyses or experiments

5.  Bonus Tasks (All completed)

    - Tests: total of 28 test cases can be run using the 'make test' command.
    - Configurable filters:
      can configure any filters in the config file under config/
      For this scraper I have included filters limiting scraping certain pages
    - Simple Analytics:
      Have visualised the AI specific metadata collected in analytics/analytics.ipynb
    - Dockerfile:
      Scraper is configured to run in a container and the commands can be seen under the 'How to Run' section of this file.

6.  Future Work

    - A more sophisticated readability score metric
    - A more sophisticated to get keywords for the text in the Enricher module
    - Improve content-type inference using a lightweight classifier
    - Add an automated monitoring loop that periodically crawls for updates, detects stale pages, logs fetch failures, and schedules recrawls to maintain dataset freshness

7.  Other details
    - Author: Shriya Ramakrishnan
    - Email: shriyar@seas.upenn.edu
