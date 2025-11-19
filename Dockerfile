FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements_hf.txt ./requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p data/database logs api-resources

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=7860
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860
ENV DOCKER_CONTAINER=true
# Default to FastAPI+HTML in Docker (for index.html frontend)
ENV USE_FASTAPI_HTML=true
ENV USE_GRADIO=false

EXPOSE 7860

# Run the application (will choose Gradio or FastAPI based on env vars)
CMD ["python", "app.py"]
