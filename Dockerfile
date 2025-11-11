# Stage 1: Prepare Frontend Assets
FROM node:18-slim AS frontend-builder

WORKDIR /frontend

# Copy package files
COPY package*.json ./

# Install Node dependencies (if needed for any frontend tools)
RUN npm install || true

# Copy all frontend static files
COPY *.html ./
COPY *.js ./

# Stage 2: Build Backend and Final Image
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (for better layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python application files
COPY *.py ./

# Copy application directories
COPY api/ ./api/
COPY backend/ ./backend/
COPY collectors/ ./collectors/
COPY database/ ./database/
COPY monitoring/ ./monitoring/
COPY scripts/ ./scripts/
COPY tests/ ./tests/
COPY utils/ ./utils/

# Copy data and config files
COPY *.json ./
COPY .env.example ./

# Copy frontend static files from builder stage
COPY --from=frontend-builder /frontend/*.html ./
COPY --from=frontend-builder /frontend/*.js ./

# Create necessary directories
RUN mkdir -p data logs static

# Set proper permissions
RUN chmod -R 755 data logs static

# Expose Hugging Face Space port
EXPOSE 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860", "--log-level", "info"]
