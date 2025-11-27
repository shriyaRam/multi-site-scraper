# ===== Base Image =====
FROM python:3.11-slim

# ===== Environment =====
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# ===== Install system dependencies =====
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ===== Create app user =====
RUN useradd -m scraperuser

# ===== Working directory =====
WORKDIR /app

# ===== Copy requirements =====
COPY requirements.txt .

# ===== Install Python dependencies =====
RUN pip install --no-cache-dir -r requirements.txt

# ===== Copy project code =====
COPY . .

# ===== Create output & logs folders with correct permissions =====
RUN mkdir -p /app/output /app/logs \
    && chown -R scraperuser:scraperuser /app/output /app/logs

# ===== Switch to non-root user =====
USER scraperuser

# ===== Default entrypoint =====
ENTRYPOINT ["python", "main.py"]