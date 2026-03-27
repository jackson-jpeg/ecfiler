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

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn ecfiler.api.app:app --host 0.0.0.0 --port $PORT"]
