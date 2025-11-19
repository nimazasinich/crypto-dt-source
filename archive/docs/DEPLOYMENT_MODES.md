# حالت‌های استقرار - Deployment Modes

این پروژه از دو حالت استقرار پشتیبانی می‌کند:

## 🎨 حالت 1: Gradio UI (پیش‌فرض)

رابط کاربری Gradio با تب‌های مختلف برای:
- داشبورد
- منابع داده
- مدل‌های AI
- تحلیل احساسات
- یکپارچه‌سازی API

### فعال‌سازی:
```bash
# پیش‌فرض - نیازی به تنظیم نیست
# یا به صورت صریح:
export USE_GRADIO=true
export USE_FASTAPI_HTML=false
python app.py
```

## 🌐 حالت 2: FastAPI + HTML

رابط کاربری HTML با FastAPI backend برای:
- نمایش داشبورد HTML
- دسترسی به API endpoints
- مستندات Swagger UI

### فعال‌سازی:
```bash
export USE_FASTAPI_HTML=true
export USE_GRADIO=false
python app.py
```

## 🐳 در Docker / Hugging Face Spaces

### استفاده از Gradio (پیش‌فرض):
```dockerfile
# در Dockerfile یا Environment Variables
ENV USE_GRADIO=true
ENV USE_FASTAPI_HTML=false
```

### استفاده از FastAPI + HTML:
```dockerfile
# در Dockerfile یا Environment Variables
ENV USE_FASTAPI_HTML=true
ENV USE_GRADIO=false
```

یا در Hugging Face Spaces Settings:
- `USE_FASTAPI_HTML` = `true`
- `USE_GRADIO` = `false`

## 🔍 تشخیص خودکار محیط

برنامه به صورت خودکار محیط Docker را تشخیص می‌دهد:
- بررسی وجود `/.dockerenv`
- بررسی وجود `/app` directory
- بررسی متغیر محیطی `DOCKER_CONTAINER`

## 📊 مقایسه حالت‌ها

| ویژگی | Gradio UI | FastAPI + HTML |
|-------|-----------|----------------|
| رابط کاربری | تب‌های تعاملی | HTML ساده |
| نمودارها | Plotly تعاملی | Chart.js |
| تحلیل احساسات | رابط کامل | از طریق API |
| مستندات API | در تب جداگانه | `/docs` (Swagger) |
| مناسب برای | استفاده عمومی | توسعه و یکپارچه‌سازی |

## 🚀 پیشنهاد

- **برای Hugging Face Spaces**: استفاده از **Gradio UI** (پیش‌فرض)
- **برای یکپارچه‌سازی**: استفاده از **FastAPI + HTML**

