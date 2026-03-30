FROM python:3.12-slim

WORKDIR /app

# Install system deps for Playwright + PDF processing + OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libatk-bridge2.0-0 libdrm2 libxcomposite1 libxdamage1 \
    libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2 \
    ghostscript tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy everything needed for install
COPY pyproject.toml .
COPY ecfiler/ ecfiler/

# Install the package with all optional deps
RUN pip install --no-cache-dir ".[web,pdf-convert]"

# Install Playwright browser
RUN playwright install chromium --with-deps

# Create non-root user for runtime
RUN groupadd -r ecfiler && useradd -r -g ecfiler -d /data -s /sbin/nologin ecfiler

ENV PORT=8000
# Create persistent data directory (mount a Railway volume here)
RUN mkdir -p /data/.ecfiler && chown -R ecfiler:ecfiler /data
ENV ECFILER_DATA_DIR=/data/.ecfiler
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/api/health')" || exit 1

USER ecfiler

# Graceful shutdown: uvicorn handles SIGTERM natively
CMD ["sh", "-c", "uvicorn ecfiler.api.app:app --host 0.0.0.0 --port $PORT"]
