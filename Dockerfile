# Dockerfile for Crypto API Monitoring System
# Optimized for HuggingFace Spaces deployment
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables for better Python behavior
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies with optimizations
# Split into two steps: core dependencies first, then ML libraries
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    pydantic==2.5.0 \
    python-multipart==0.0.6 \
    websockets==12.0 \
    SQLAlchemy==2.0.23 \
    APScheduler==3.10.4 \
    aiohttp==3.9.1 \
    requests==2.31.0 \
    httpx \
    python-dotenv==1.0.0 \
    feedparser==6.0.11 \
    gradio==4.14.0 \
    pandas==2.1.4 \
    plotly==5.18.0

# Install HuggingFace ML dependencies separately
RUN pip install --no-cache-dir \
    transformers>=4.44.0 \
    datasets>=3.0.0 \
    huggingface_hub>=0.24.0 \
    torch>=2.0.0 --index-url https://download.pytorch.org/whl/cpu \
    sentencepiece>=0.1.99 \
    protobuf>=3.20.0

# Copy all application code
COPY . .

# Create necessary directories
RUN mkdir -p data logs

# Set proper permissions for data directories
RUN chmod -R 755 data logs

# Expose port 7860 (HuggingFace Spaces standard port)
EXPOSE 7860

# Health check endpoint for HuggingFace Spaces
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Run the FastAPI application with uvicorn
# Using multiple workers for better performance (adjust based on available resources)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860", "--log-level", "info", "--workers", "1"]
