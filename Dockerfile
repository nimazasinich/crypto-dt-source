# استفاده از Python 3.11 Slim
FROM python:3.11-slim

# تنظیم متغیرهای محیطی
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ENABLE_AUTO_DISCOVERY=false

# نصب وابستگی‌های سیستمی
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ساخت دایرکتوری کاری
WORKDIR /app

# کپی فایل‌های وابستگی
COPY requirements.txt .

# نصب وابستگی‌های Python
RUN pip install --no-cache-dir -r requirements.txt

# کپی کد برنامه
COPY . .

# ساخت دایرکتوری برای لاگ‌ها
RUN mkdir -p logs

# Expose کردن پورت (پیش‌فرض Hugging Face ۷۸۶۰ است)
EXPOSE 8000 7860

# Health Check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os, requests; requests.get('http://localhost:{}/health'.format(os.getenv('PORT', '8000')))" || exit 1

# اجرای سرور (پشتیبانی از PORT متغیر محیطی برای Hugging Face)
CMD ["sh", "-c", "python -m uvicorn api_server_extended:app --host 0.0.0.0 --port ${PORT:-8000}"]
