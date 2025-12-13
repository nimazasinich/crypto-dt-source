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

# Create data directory for SQLite databases (must be writable at runtime)
RUN mkdir -p /app/data && chmod -R a+rwx /app/data

# Create a non-root user for runtime (HF Spaces may run as non-root)
RUN useradd -m -u 1000 appuser \
    && chown -R appuser:appuser /app

# Expose port 7860 (Hugging Face Spaces standard)
EXPOSE 7860

# Environment variables (can be overridden in HF Spaces settings)
ENV HOST=0.0.0.0
ENV PORT=7860
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f "http://localhost:${PORT:-7860}/api/health" || exit 1

# Drop privileges for runtime
USER appuser

# Start the FastAPI server
CMD ["python", "-m", "uvicorn", "hf_unified_server:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
