# 📚 API Resources Guide

## فایل‌های منابع در این پوشه

این پوشه شامل منابع کاملی از **162+ API رایگان** است که می‌توانید از آنها استفاده کنید.

---

## 📁 فایل‌ها

### 1. `crypto_resources_unified_2025-11-11.json`
- **200+ منبع** کامل با تمام جزئیات
- شامل: RPC Nodes, Block Explorers, Market Data, News, Sentiment, DeFi
- ساختار یکپارچه برای همه منابع
- API Keys embedded برای برخی سرویس‌ها

### 2. `ultimate_crypto_pipeline_2025_NZasinich.json`
- **162 منبع** با نمونه کد TypeScript
- شامل: Block Explorers, Market Data, News, DeFi
- Rate Limits و توضیحات هر سرویس

### 3. `api-config-complete__1_.txt`
- تنظیمات و کانفیگ APIها
- Fallback strategies
- Authentication methods

---

## 🔑 APIهای استفاده شده در برنامه

برنامه فعلی از این APIها استفاده می‌کند:

### ✅ Market Data:
```json
{
  "CoinGecko": "https://api.coingecko.com/api/v3",
  "CoinCap": "https://api.coincap.io/v2",
  "CoinStats": "https://api.coinstats.app",
  "Cryptorank": "https://api.cryptorank.io/v1"
}
```

### ✅ Exchanges:
```json
{
  "Binance": "https://api.binance.com/api/v3",
  "Coinbase": "https://api.coinbase.com/v2",
  "Kraken": "https://api.kraken.com/0/public"
}
```

### ✅ Sentiment & Analytics:
```json
{
  "Alternative.me": "https://api.alternative.me/fng",
  "DeFi Llama": "https://api.llama.fi"
}
```

---

## 🚀 چگونه API جدید اضافه کنیم؟

### مثال: اضافه کردن CryptoCompare

#### 1. در `app.py` به `API_PROVIDERS` اضافه کنید:
```python
API_PROVIDERS = {
    "market_data": [
        # ... موارد قبلی
        {
            "name": "CryptoCompare",
            "base_url": "https://min-api.cryptocompare.com/data",
            "endpoints": {
                "price": "/price",
                "multiple": "/pricemulti"
            },
            "auth": None,
            "rate_limit": "100/hour",
            "status": "active"
        }
    ]
}
```

#### 2. تابع جدید برای fetch:
```python
async def get_cryptocompare_data():
    async with aiohttp.ClientSession() as session:
        url = "https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH&tsyms=USD"
        data = await fetch_with_retry(session, url)
        return data
```

#### 3. استفاده در endpoint:
```python
@app.get("/api/cryptocompare")
async def cryptocompare():
    data = await get_cryptocompare_data()
    return {"data": data}
```

---

## 📊 نمونه‌های بیشتر از منابع

### Block Explorer - Etherscan:
```python
# از crypto_resources_unified_2025-11-11.json
{
    "id": "etherscan_primary",
    "name": "Etherscan",
    "chain": "ethereum",
    "base_url": "https://api.etherscan.io/api",
    "auth": {
        "type": "apiKeyQuery",
        "key": "YOUR_KEY_HERE",
        "param_name": "apikey"
    },
    "endpoints": {
        "balance": "?module=account&action=balance&address={address}&apikey={key}"
    }
}
```

### استفاده:
```python
async def get_eth_balance(address):
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&apikey=YOUR_KEY"
    async with aiohttp.ClientSession() as session:
        data = await fetch_with_retry(session, url)
        return data
```

---

### News API - CryptoPanic:
```python
# از فایل منابع
{
    "id": "cryptopanic",
    "name": "CryptoPanic",
    "role": "crypto_news",
    "base_url": "https://cryptopanic.com/api/v1",
    "endpoints": {
        "posts": "/posts/?auth_token={key}"
    }
}
```

### استفاده:
```python
async def get_news():
    url = "https://cryptopanic.com/api/v1/posts/?auth_token=free"
    async with aiohttp.ClientSession() as session:
        data = await fetch_with_retry(session, url)
        return data["results"]
```

---

### DeFi - Uniswap:
```python
# از فایل منابع
{
    "name": "Uniswap",
    "url": "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3",
    "type": "GraphQL"
}
```

### استفاده:
```python
async def get_uniswap_data():
    query = """
    {
      pools(first: 10, orderBy: volumeUSD, orderDirection: desc) {
        id
        token0 { symbol }
        token1 { symbol }
        volumeUSD
      }
    }
    """
    url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"query": query}) as response:
            data = await response.json()
            return data
```

---

## 🔧 نکات مهم

### Rate Limits:
```python
# همیشه rate limit رو رعایت کنید
await asyncio.sleep(1)  # بین درخواست‌ها

# یا از cache استفاده کنید
cache = {"data": None, "timestamp": None, "ttl": 60}
```

### Error Handling:
```python
try:
    data = await fetch_api()
except aiohttp.ClientError:
    # Fallback به API دیگه
    data = await fetch_fallback_api()
```

### Authentication:
```python
# برخی APIها نیاز به auth دارند
headers = {"X-API-Key": "YOUR_KEY"}
async with session.get(url, headers=headers) as response:
    data = await response.json()
```

---

## 📝 چک‌لیست برای اضافه کردن API جدید

- [ ] API را در `API_PROVIDERS` اضافه کن
- [ ] تابع `fetch` بنویس
- [ ] Error handling اضافه کن
- [ ] Cache پیاده‌سازی کن
- [ ] Rate limit رعایت کن
- [ ] Fallback تعریف کن
- [ ] Endpoint در FastAPI بساز
- [ ] Frontend رو آپدیت کن
- [ ] تست کن

---

## 🌟 APIهای پیشنهادی برای توسعه

از فایل‌های منابع، این APIها خوب هستند:

### High Priority:
1. **Messari** - تحلیل عمیق
2. **Glassnode** - On-chain analytics
3. **LunarCrush** - Social sentiment
4. **Santiment** - Market intelligence

### Medium Priority:
1. **Dune Analytics** - Custom queries
2. **CoinMarketCap** - Alternative market data
3. **TradingView** - Charts data
4. **CryptoQuant** - Exchange flows

### Low Priority:
1. **Various RSS Feeds** - News aggregation
2. **Social APIs** - Twitter, Reddit
3. **NFT APIs** - OpenSea, Blur
4. **Blockchain RPCs** - Direct chain queries

---

## 🎓 منابع یادگیری

- [FastAPI Async](https://fastapi.tiangolo.com/async/)
- [aiohttp Documentation](https://docs.aiohttp.org/)
- [API Best Practices](https://restfulapi.net/)

---

## 💡 نکته نهایی

**همه APIهای موجود در فایل‌ها رایگان هستند!**

برای استفاده از آنها فقط کافیست:
1. API را از فایل منابع پیدا کنید
2. به `app.py` اضافه کنید
3. تابع fetch بنویسید
4. استفاده کنید!

---

**موفق باشید! 🚀**
