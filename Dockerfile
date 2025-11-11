# Dockerfile for Crypto API Monitor Backend
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files and directories
COPY app.py .
COPY config.py .
COPY all_apis_merged_2025.json .

# Copy module directories
COPY database/ ./database/
COPY monitoring/ ./monitoring/
COPY collectors/ ./collectors/
COPY api/ ./api/
COPY utils/ ./utils/

# Expose port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860/health')"

# Run the application with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
