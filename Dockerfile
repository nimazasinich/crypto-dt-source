FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create required directories
RUN mkdir -p /app/logs /app/data /app/data/database /app/data/backups

# Copy requirements files
COPY requirements.txt requirements_gradio.txt ./

# Install core dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Gradio dashboard dependencies (optional, based on build arg)
ARG INSTALL_GRADIO=false
RUN if [ "$INSTALL_GRADIO" = "true" ]; then \
    echo "Installing Gradio dependencies..." && \
    pip install --no-cache-dir -r requirements_gradio.txt; \
    fi

# Copy application code
COPY . .

# Set environment variables
ENV USE_MOCK_DATA=false
ENV PORT=7860
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose ports (7860 for Gradio, 8000 for API)
EXPOSE 7860 8000

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "api_server_extended:app", "--host", "0.0.0.0", "--port", "7860"]
