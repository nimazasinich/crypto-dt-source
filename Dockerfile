# Hugging Face Spaces - Crypto Data Source Ultimate
# Docker-based deployment for complete API backend + Static Frontend

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create data directory for SQLite databases
RUN mkdir -p data

# Expose port 7860 (Hugging Face Spaces standard)
EXPOSE 7860

# Environment variables (can be overridden in HF Spaces settings)
ENV HOST=0.0.0.0
ENV PORT=7860
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:7860/api/health || exit 1

# Start the FastAPI server
CMD ["python", "-m", "uvicorn", "hf_unified_server:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
