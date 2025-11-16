# Use Python 3.11 Slim for smaller image size
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ENABLE_AUTO_DISCOVERY=false \
    USE_MOCK_DATA=false

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency files
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create required directories for runtime
RUN mkdir -p logs data exports backups data/database data/backups

# Expose port (Hugging Face uses PORT env var, default 7860)
EXPOSE 7860 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:' + __import__('os').getenv('PORT', '7860') + '/health').read()" || exit 1

# Run server with PORT environment variable support for Hugging Face Spaces
CMD uvicorn api_server_extended:app --host 0.0.0.0 --port ${PORT:-7860} --workers 1
