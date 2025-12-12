FROM python:3.12-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# HF Spaces: keep startup lightweight
ENV HF_MINIMAL=true

# Spaces sets PORT; default to 7860
ENV PORT=7860

EXPOSE 7860

CMD ["bash", "-lc", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
