# Stage 1: Build Frontend
FROM node:18-slim AS frontend-builder

WORKDIR /app

# Copy frontend package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy frontend source files
COPY *.html ./
COPY *.js ./
COPY config.js ./

# Note: This project uses static HTML/JS files, no build step needed
# If you add a build step later, uncomment the next line
# RUN npm run build

# Stage 2: Setup Backend and Serve
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy other Python files
COPY *.py ./

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/*.html ./
COPY --from=frontend-builder /app/*.js ./
COPY --from=frontend-builder /app/config.js ./

# Copy additional directories
COPY api/ ./api/
COPY collectors/ ./collectors/
COPY database/ ./database/
COPY monitoring/ ./monitoring/
COPY scripts/ ./scripts/
COPY tests/ ./tests/
COPY utils/ ./utils/

# Copy data files
COPY *.json ./

# Create necessary directories
RUN mkdir -p data logs

# Set proper permissions
RUN chmod -R 755 data logs

# Expose Hugging Face Space port
EXPOSE 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860", "--log-level", "info"]
