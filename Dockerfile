FROM python:3.10

WORKDIR /app

# Create required directories
RUN mkdir -p /app/logs /app/data /app/data/database /app/data/backups

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV USE_MOCK_DATA=false
ENV PORT=7860
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 7860

# Launch command
CMD ["uvicorn", "api_server_extended:app", "--host", "0.0.0.0", "--port", "7860"]
