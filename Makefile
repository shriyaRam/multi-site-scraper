IMAGE_NAME = multi-site-scraper
CONFIG ?= configs/medlineplus.json
OUTPUT ?= output/medlineplus.jsonl

# ==========================================================
# Build Docker Image
# ==========================================================
build:
	docker build -t $(IMAGE_NAME) .

# ==========================================================
# Run Scraper
# ==========================================================
scrape:
	docker run \
		-v $(PWD)/output:/app/output \
		-v $(PWD)/logs:/app/logs \
		$(IMAGE_NAME) \
		--config $(CONFIG) \
		--output $(OUTPUT)

# ==========================================================
# Open interactive shell in container
# ==========================================================
shell:
	docker run -it \
		-v $(PWD)/output:/app/output \
		$(IMAGE_NAME) \
		bash

# ==========================================================
# View local logs
# ==========================================================
logs:
	tail -f logs/scraper.log

# ==========================================================
# Clean local Docker resources
# ==========================================================
clean:
	-docker rm -f $$(docker ps -a -q --filter ancestor=$(IMAGE_NAME)) 2>/dev/null
	-docker rmi -f $(IMAGE_NAME) 2>/dev/null

# =============================================
# Run full test suite
# =============================================
test:
	python -m pytest tests -q --disable-warnings --maxfail=1