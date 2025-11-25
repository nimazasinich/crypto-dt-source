# 🚀 راهنمای سریع استفاده از Data Hub

راهنمای کوتاه و کاربردی برای دریافت داده از Data Hub شما

---

## 📋 فهرست سریع

1. [دریافت داده با curl](#1-دریافت-داده-با-curl)
2. [استفاده با Python](#2-استفاده-با-python)
3. [دسترسی مستقیم به HuggingFace](#3-دسترسی-مستقیم-به-huggingface)
4. [API Endpoints موجود](#4-api-endpoints-موجود)

---

## 1. دریافت داده با curl

### الف) بدون نیاز به Authentication

```bash
# وضعیت Data Hub
curl http://localhost:7860/api/hub/status

# اطلاعات dataset
curl http://localhost:7860/api/hub/dataset-info?dataset_type=market

# Health check
curl http://localhost:7860/api/hub/health
```

### ب) با Authentication (نیاز به HF_TOKEN)

```bash
# تنظیم token
export HF_TOKEN="hf_xxxxxxxxxxxxx"

# دریافت قیمت‌های بازار (از HuggingFace)
curl -H "Authorization: Bearer $HF_TOKEN" \
  "http://localhost:7860/api/hub/market?symbols=BTC,ETH&limit=10"

# دریافت OHLC (از HuggingFace)
curl -H "Authorization: Bearer $HF_TOKEN" \
  "http://localhost:7860/api/hub/ohlc?symbol=BTCUSDT&interval=1h&limit=100"

# دریافت قیمت از cache محلی (سریع‌تر)
curl -H "Authorization: Bearer $HF_TOKEN" \
  "http://localhost:7860/api/market?limit=20"
```

---

## 2. استفاده با Python

### الف) دریافت از API

```python
import requests

# تنظیم
BASE_URL = "http://localhost:7860"
HF_TOKEN = "hf_xxxxxxxxxxxxx"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# 1. دریافت قیمت‌های بازار
response = requests.get(
    f"{BASE_URL}/api/hub/market",
    headers=headers,
    params={"symbols": "BTC,ETH,BNB", "limit": 10}
)
market_data = response.json()

for item in market_data:
    print(f"{item['symbol']}: ${item['price']:,.2f}")

# 2. دریافت OHLC
response = requests.get(
    f"{BASE_URL}/api/hub/ohlc",
    headers=headers,
    params={
        "symbol": "BTCUSDT",
        "interval": "1h",
        "limit": 24  # آخرین 24 ساعت
    }
)
ohlc_data = response.json()

for candle in ohlc_data[:5]:
    print(f"Time: {candle['timestamp']}, Close: ${candle['close']:,.2f}")

# 3. دریافت وضعیت
response = requests.get(f"{BASE_URL}/api/hub/status")
status = response.json()
print(f"Status: {status['status']}")
print(f"Market records: {status['market_dataset']['records']}")
```

### ب) استفاده با pandas

```python
import requests
import pandas as pd

HF_TOKEN = "hf_xxxxxxxxxxxxx"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# دریافت داده
response = requests.get(
    "http://localhost:7860/api/hub/market",
    headers=headers,
    params={"limit": 100}
)

# تبدیل به DataFrame
df = pd.DataFrame(response.json())

# تحلیل
print(df[['symbol', 'price', 'change_24h']].head(10))
print(f"\nTop gainers:")
print(df.nlargest(5, 'change_24h')[['symbol', 'change_24h']])
```

---

## 3. دسترسی مستقیم به HuggingFace

### الف) خواندن Dataset با Python

```python
from datasets import load_dataset

HF_TOKEN = "hf_xxxxxxxxxxxxx"
USERNAME = "your-username"  # username خودتان

# 1. دریافت Market Data
dataset = load_dataset(
    f"{USERNAME}/crypto-market-data",
    split="train",
    token=HF_TOKEN
)

# تبدیل به pandas
import pandas as pd
df = dataset.to_pandas()

print(f"Total records: {len(df)}")
print(df.head())

# فیلتر کردن
btc_data = df[df['symbol'] == 'BTC']
print(f"BTC Price: ${btc_data['price'].iloc[0]:,.2f}")

# 2. دریافت OHLC Data
ohlc_dataset = load_dataset(
    f"{USERNAME}/crypto-ohlc-data",
    split="train",
    token=HF_TOKEN
)

ohlc_df = ohlc_dataset.to_pandas()
btc_1h = ohlc_df[(ohlc_df['symbol'] == 'BTCUSDT') & (ohlc_df['interval'] == '1h')]
print(btc_1h.tail(10))

# 3. دریافت News Data
news_dataset = load_dataset(
    f"{USERNAME}/crypto-news-data",
    split="train",
    token=HF_TOKEN
)

news_df = news_dataset.to_pandas()
print(f"Total news: {len(news_df)}")
print(news_df[['title', 'source', 'published_at']].head(5))
```

### ب) دانلود Dataset به CSV

```python
from datasets import load_dataset

dataset = load_dataset(
    "your-username/crypto-market-data",
    split="train",
    token="hf_xxxxx"
)

# ذخیره به CSV
df = dataset.to_pandas()
df.to_csv("crypto_market_data.csv", index=False)
print("✅ Downloaded to crypto_market_data.csv")
```

---

## 4. API Endpoints موجود

### 🌐 Data Hub Endpoints (از HuggingFace)

| Endpoint | Method | نیاز به Auth | توضیح |
|----------|--------|--------------|-------|
| `/api/hub/status` | GET | ❌ | وضعیت Data Hub |
| `/api/hub/market` | GET | ✅ | قیمت‌های بازار |
| `/api/hub/ohlc` | GET | ✅ | OHLC candlesticks |
| `/api/hub/dataset-info` | GET | ❌ | اطلاعات dataset |
| `/api/hub/health` | GET | ❌ | Health check |

### 📊 Local Cache Endpoints (سریع‌تر)

| Endpoint | Method | نیاز به Auth | توضیح |
|----------|--------|--------------|-------|
| `/api/market` | GET | ✅ | قیمت‌ها از cache |
| `/api/market/history` | GET | ✅ | OHLC از cache |
| `/api/sentiment/analyze` | POST | ✅ | تحلیل احساسات |
| `/api/health` | GET | ❌ | وضعیت سیستم |

---

## 5. مثال‌های کاربردی

### مثال 1: نمایش قیمت‌های Top 10

```python
import requests
import pandas as pd

response = requests.get(
    "http://localhost:7860/api/hub/market",
    headers={"Authorization": "Bearer hf_xxxxx"},
    params={"limit": 10}
)

df = pd.DataFrame(response.json())
print("\n🏆 Top 10 Cryptocurrencies:\n")
for i, row in df.iterrows():
    change = row['change_24h']
    emoji = "🟢" if change > 0 else "🔴"
    print(f"{i+1}. {row['symbol']:6s} ${row['price']:12,.2f}  {emoji} {change:+.2f}%")
```

### مثال 2: رسم نمودار قیمت

```python
import requests
import pandas as pd
import matplotlib.pyplot as plt

# دریافت OHLC
response = requests.get(
    "http://localhost:7860/api/hub/ohlc",
    headers={"Authorization": "Bearer hf_xxxxx"},
    params={"symbol": "BTCUSDT", "interval": "1h", "limit": 24}
)

df = pd.DataFrame(response.json())
df['timestamp'] = pd.to_datetime(df['timestamp'])

# رسم نمودار
plt.figure(figsize=(12, 6))
plt.plot(df['timestamp'], df['close'], marker='o')
plt.title('BTC Price - Last 24 Hours')
plt.xlabel('Time')
plt.ylabel('Price (USDT)')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.savefig('btc_24h.png')
print("✅ Chart saved to btc_24h.png")
```

### مثال 3: مقایسه قیمت‌ها

```python
import requests
import pandas as pd

response = requests.get(
    "http://localhost:7860/api/hub/market",
    headers={"Authorization": "Bearer hf_xxxxx"},
    params={"symbols": "BTC,ETH,BNB,XRP,ADA", "limit": 10}
)

df = pd.DataFrame(response.json())

print("\n📊 Price Comparison:\n")
print(df[['symbol', 'price', 'market_cap', 'change_24h']].to_string(index=False))

# بهترین عملکرد
best = df.loc[df['change_24h'].idxmax()]
print(f"\n🚀 Best performer: {best['symbol']} (+{best['change_24h']:.2f}%)")

# بدترین عملکرد
worst = df.loc[df['change_24h'].idxmin()]
print(f"📉 Worst performer: {worst['symbol']} ({worst['change_24h']:.2f}%)")
```

---

## 6. نکات مهم

### ✅ بهترین روش‌ها

```python
# 1. استفاده از session برای چند request
session = requests.Session()
session.headers.update({"Authorization": f"Bearer {HF_TOKEN}"})

# حالا می‌توانید چندین بار استفاده کنید
market_data = session.get(f"{BASE_URL}/api/hub/market").json()
ohlc_data = session.get(f"{BASE_URL}/api/hub/ohlc?symbol=BTCUSDT").json()

# 2. مدیریت خطا
try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")

# 3. Cache کردن نتایج
import time

cache = {}
CACHE_DURATION = 60  # ثانیه

def get_market_data(symbols):
    key = f"market_{symbols}"
    now = time.time()

    if key in cache and now - cache[key]['time'] < CACHE_DURATION:
        return cache[key]['data']

    response = requests.get(...)
    data = response.json()

    cache[key] = {'data': data, 'time': now}
    return data
```

### ⚠️ محدودیت‌ها

- Rate limit برای API های رایگان
- Token باید در هر request ارسال شود
- Datasets هر 5 دقیقه به‌روز می‌شوند
- برخی منابع نیاز به API key دارند

---

## 7. Troubleshooting

### مشکل: "401 Unauthorized"

```bash
# چک کنید token درست است
echo $HF_TOKEN

# یا در Python
import os
print(os.getenv("HF_TOKEN"))
```

### مشکل: "Dataset not found"

```python
# چک کنید dataset وجود دارد
from huggingface_hub import HfApi

api = HfApi()
datasets = api.list_datasets(author="your-username", token=HF_TOKEN)
for d in datasets:
    print(d.id)
```

### مشکل: "No data returned"

```bash
# چک کنید worker ها در حال اجرا هستند
curl http://localhost:7860/api/health

# بررسی لاگ‌ها
tail -f logs/hf_space_api.log
```

---

## 8. لینک‌های مفید

### 📚 مستندات

- **API Docs**: http://localhost:7860/docs
- **Data Hub Status**: http://localhost:7860/api/hub/status
- **Health Check**: http://localhost:7860/api/health

### 🤗 HuggingFace Datasets

بعد از اینکه داده‌ها آپلود شدند، می‌توانید اینجا ببینید:

```
https://huggingface.co/datasets/{your-username}/crypto-market-data
https://huggingface.co/datasets/{your-username}/crypto-ohlc-data
https://huggingface.co/datasets/{your-username}/crypto-news-data
https://huggingface.co/datasets/{your-username}/crypto-sentiment-data
https://huggingface.co/datasets/{your-username}/crypto-onchain-data
https://huggingface.co/datasets/{your-username}/crypto-whale-data
https://huggingface.co/datasets/{your-username}/crypto-explorer-data
```

---

## 9. مثال کامل - Dashboard ساده

```python
#!/usr/bin/env python3
"""Simple Crypto Dashboard"""

import requests
import pandas as pd
from datetime import datetime

BASE_URL = "http://localhost:7860"
HF_TOKEN = "hf_xxxxxxxxxxxxx"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def main():
    print("=" * 60)
    print("🚀 CRYPTO DASHBOARD")
    print("=" * 60)

    # 1. System Status
    status = requests.get(f"{BASE_URL}/api/hub/status").json()
    print(f"\n📊 System Status: {status['status']}")
    print(f"   Market records: {status['market_dataset']['records']}")
    print(f"   OHLC records: {status['ohlc_dataset']['records']}")

    # 2. Top 5 Prices
    print("\n💰 Top 5 Cryptocurrencies:")
    response = requests.get(
        f"{BASE_URL}/api/hub/market",
        headers=headers,
        params={"limit": 5}
    )
    df = pd.DataFrame(response.json())

    for i, row in df.iterrows():
        change = row['change_24h']
        emoji = "🟢" if change > 0 else "🔴"
        print(f"   {i+1}. {row['symbol']:6s} ${row['price']:12,.2f}  {emoji} {change:+6.2f}%")

    # 3. Latest News
    try:
        news_data = requests.get(
            f"{BASE_URL}/api/hub/dataset-info?dataset_type=news",
            headers=headers
        ).json()
        print(f"\n📰 News Articles: {news_data.get('records', 0)}")
    except:
        print("\n📰 News: Not available yet")

    print("\n" + "=" * 60)
    print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

ذخیره کنید به عنوان `dashboard.py` و اجرا کنید:

```bash
python dashboard.py
```

---

## ✅ خلاصه سریع

### 🎯 یک نگاه سریع:

```bash
# 1. چک وضعیت
curl http://localhost:7860/api/hub/status

# 2. دریافت قیمت
curl -H "Authorization: Bearer $HF_TOKEN" \
  "http://localhost:7860/api/hub/market?symbols=BTC,ETH&limit=5"

# 3. در Python
import requests
data = requests.get(
    "http://localhost:7860/api/hub/market",
    headers={"Authorization": "Bearer hf_xxxxx"}
).json()

# 4. مستقیم از HuggingFace
from datasets import load_dataset
dataset = load_dataset("username/crypto-market-data", token="hf_xxxxx")
```

---

**موفق باشید! 🚀**

برای سوالات بیشتر، مستندات کامل را ببینید:
- `DATA_HUB_ARCHITECTURE.md`
- `COMPREHENSIVE_DATA_SOURCES.md`
