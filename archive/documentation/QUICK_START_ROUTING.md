# 🚀 راهنمای سریع - Routing

## تست سریع اتصال

### 1. بررسی فایل config:
```bash
cd /workspace
python3 test_routing.py
```

**باید ببینید**:
```
✅ Total providers: 95
✅ HuggingFace Space providers: 2
✅ All routing connections are properly configured!
```

### 2. راه‌اندازی سرور:
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 7860
```

### 3. تست endpoint‌ها:
```bash
# تست health
curl http://localhost:7860/health

# تست info (باید 95 پرووایدر نمایش دهد)
curl http://localhost:7860/info

# تست providers (باید 95 پرووایدر بازگرداند)
curl http://localhost:7860/api/providers | jq '.total'
```

## مسیر Routing

```
main.py → hf_unified_server.py → providers_config_extended.json (95 providers)
```

## فایل‌های کلیدی

1. **main.py** - Entry point
2. **hf_unified_server.py** - API server با اتصال به config
3. **providers_config_extended.json** - 95 پرووایدر (شامل 2 پرووایدر HF Space)

## ✅ همه چیز آماده است!

مستندات کامل: [ROUTING_CONNECTION_SUMMARY_FA.md](./ROUTING_CONNECTION_SUMMARY_FA.md)
