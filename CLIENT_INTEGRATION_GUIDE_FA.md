# 📱 راهنمای یکپارچه‌سازی کلاینت

## نگاه کلی

این راهنما برای توسعه‌دهندگان Frontend است که می‌خواهند از API های پروژه استفاده کنند.

---

## 🎯 پشتیبانی از Client Applications

### ✅ پلتفرم‌های پشتیبانی شده:

```
✅ Web (JavaScript/TypeScript)
✅ React / Next.js
✅ Vue.js
✅ Angular
✅ Mobile (React Native)
✅ iOS (Swift)
✅ Android (Kotlin/Java)
✅ Desktop (Electron)
✅ Python Scripts
✅ Any HTTP/WebSocket Client
```

---

## 🔌 روش‌های اتصال

### 1. REST API (HTTP/HTTPS)

**Base URL:**
```
Development:  http://localhost:7860
Production:   https://your-domain.com
```

**Headers مورد نیاز:**
```http
Content-Type: application/json
Accept: application/json
Origin: https://your-domain.com  (برای CORS)
```

**Headers اختیاری:**
```http
Authorization: Bearer YOUR_TOKEN  (برای endpoints محافظت شده)
X-Client-Version: 1.0.0
User-Agent: YourApp/1.0
```

---

### 2. WebSocket (Real-time)

**URLs:**
```
ws://localhost:7860/ws/master
ws://localhost:7860/ws/market_data
ws://localhost:7860/ws/news
wss://your-domain.com/ws/...  (برای HTTPS)
```

**Protocol:**
- JSON-based messaging
- Subscribe/Unsubscribe patterns
- Auto-reconnect recommended

---

## 📚 نمونه کدها

### JavaScript/TypeScript

#### Basic HTTP Request:
```typescript
// استفاده از fetch API
async function getBTCPrice(): Promise<number> {
  try {
    const response = await fetch('http://localhost:7860/api/resources/market/price/BTC');
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.price;
  } catch (error) {
    console.error('Error fetching BTC price:', error);
    throw error;
  }
}

// استفاده
const price = await getBTCPrice();
console.log(`BTC Price: $${price}`);
```

#### با Axios:
```typescript
import axios from 'axios';

const API_BASE = 'http://localhost:7860';

// تنظیم instance
const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// قیمت BTC
export async function getBTCPrice() {
  const { data } = await apiClient.get('/api/resources/market/price/BTC');
  return data.price;
}

// قیمت چندتا ارز
export async function getMultiplePrices(symbols: string[]) {
  const { data } = await apiClient.get('/api/resources/market/prices', {
    params: { symbols: symbols.join(',') }
  });
  return data.data;
}

// اخبار
export async function getLatestNews(limit = 20) {
  const { data } = await apiClient.get('/api/resources/news/latest', {
    params: { limit }
  });
  return data.news;
}
```

---

### React Hook

```typescript
import { useState, useEffect } from 'react';
import axios from 'axios';

interface PriceData {
  symbol: string;
  price: number;
  source: string;
  timestamp: string;
}

export function useCryptoPrice(symbol: string, refreshInterval = 5000) {
  const [price, setPrice] = useState<PriceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPrice = async () => {
      try {
        setLoading(true);
        const { data } = await axios.get(
          `http://localhost:7860/api/resources/market/price/${symbol}`
        );
        setPrice(data);
        setError(null);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    // اولین بار
    fetchPrice();

    // Polling برای بروزرسانی
    const interval = setInterval(fetchPrice, refreshInterval);

    return () => clearInterval(interval);
  }, [symbol, refreshInterval]);

  return { price, loading, error };
}

// استفاده در کامپوننت
function BTCPriceDisplay() {
  const { price, loading, error } = useCryptoPrice('BTC');

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Bitcoin Price</h2>
      <p>${price?.price.toLocaleString()}</p>
      <small>Source: {price?.source}</small>
    </div>
  );
}
```

---

### WebSocket در React

```typescript
import { useEffect, useState } from 'react';

interface MarketUpdate {
  symbol: string;
  price: number;
  change: number;
  timestamp: string;
}

export function useWebSocket(url: string) {
  const [data, setData] = useState<MarketUpdate | null>(null);
  const [connected, setConnected] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    const websocket = new WebSocket(url);

    websocket.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);

      // Subscribe به market data
      websocket.send(JSON.stringify({
        action: 'subscribe',
        service: 'market_data'
      }));
    };

    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      if (message.type === 'market_update') {
        setData(message.data);
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    websocket.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
      
      // Auto-reconnect بعد از 5 ثانیه
      setTimeout(() => {
        console.log('Attempting to reconnect...');
        // Recreate WebSocket
      }, 5000);
    };

    setWs(websocket);

    return () => {
      websocket.close();
    };
  }, [url]);

  const sendMessage = (message: any) => {
    if (ws && connected) {
      ws.send(JSON.stringify(message));
    }
  };

  return { data, connected, sendMessage };
}

// استفاده
function LivePriceDisplay() {
  const { data, connected } = useWebSocket('ws://localhost:7860/ws/market_data');

  return (
    <div>
      <div>Status: {connected ? '🟢 Connected' : '🔴 Disconnected'}</div>
      {data && (
        <div>
          <h3>{data.symbol}</h3>
          <p>${data.price}</p>
          <p className={data.change >= 0 ? 'green' : 'red'}>
            {data.change >= 0 ? '+' : ''}{data.change}%
          </p>
        </div>
      )}
    </div>
  );
}
```

---

### Vue.js Composable

```typescript
// composables/useCryptoAPI.ts
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';

export function useCryptoPrice(symbol: string) {
  const price = ref(null);
  const loading = ref(true);
  const error = ref(null);

  let intervalId: number;

  const fetchPrice = async () => {
    try {
      loading.value = true;
      const { data } = await axios.get(
        `http://localhost:7860/api/resources/market/price/${symbol}`
      );
      price.value = data;
      error.value = null;
    } catch (err: any) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };

  onMounted(() => {
    fetchPrice();
    intervalId = setInterval(fetchPrice, 5000);
  });

  onUnmounted(() => {
    clearInterval(intervalId);
  });

  return { price, loading, error };
}

// استفاده در component
<script setup>
import { useCryptoPrice } from '@/composables/useCryptoAPI';

const { price, loading, error } = useCryptoPrice('BTC');
</script>

<template>
  <div>
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">Error: {{ error }}</div>
    <div v-else>
      <h2>{{ price.symbol }}</h2>
      <p>${{ price.price }}</p>
    </div>
  </div>
</template>
```

---

### Python Client

```python
import requests
import asyncio
import websockets
import json

class CryptoAPIClient:
    """Python client برای Crypto API"""
    
    def __init__(self, base_url='http://localhost:7860'):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'PythonClient/1.0'
        })
    
    def get_price(self, symbol):
        """دریافت قیمت یک ارز"""
        response = self.session.get(
            f'{self.base_url}/api/resources/market/price/{symbol}'
        )
        response.raise_for_status()
        return response.json()
    
    def get_multiple_prices(self, symbols):
        """دریافت قیمت چند ارز"""
        response = self.session.get(
            f'{self.base_url}/api/resources/market/prices',
            params={'symbols': ','.join(symbols)}
        )
        response.raise_for_status()
        return response.json()['data']
    
    def get_news(self, limit=20):
        """دریافت آخرین اخبار"""
        response = self.session.get(
            f'{self.base_url}/api/resources/news/latest',
            params={'limit': limit}
        )
        response.raise_for_status()
        return response.json()['news']
    
    def get_fear_greed_index(self):
        """دریافت شاخص ترس و طمع"""
        response = self.session.get(
            f'{self.base_url}/api/resources/sentiment/fear-greed'
        )
        response.raise_for_status()
        return response.json()
    
    async def connect_websocket(self, on_message_callback):
        """اتصال به WebSocket"""
        uri = self.base_url.replace('http', 'ws') + '/ws/master'
        
        async with websockets.connect(uri) as websocket:
            # Subscribe
            await websocket.send(json.dumps({
                'action': 'subscribe',
                'service': 'market_data'
            }))
            
            # دریافت پیام‌ها
            async for message in websocket:
                data = json.loads(message)
                await on_message_callback(data)

# استفاده
client = CryptoAPIClient()

# REST API
btc_price = client.get_price('BTC')
print(f"BTC Price: ${btc_price['price']}")

prices = client.get_multiple_prices(['BTC', 'ETH', 'BNB'])
for price_data in prices:
    print(f"{price_data['symbol']}: ${price_data['price']}")

# WebSocket
async def handle_message(data):
    print(f"Received: {data}")

asyncio.run(client.connect_websocket(handle_message))
```

---

### React Native

```typescript
import { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator } from 'react-native';

export function PriceScreen() {
  const [price, setPrice] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPrice = async () => {
      try {
        const response = await fetch(
          'http://your-api.com/api/resources/market/price/BTC'
        );
        const data = await response.json();
        setPrice(data.price);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    fetchPrice();
    const interval = setInterval(fetchPrice, 5000);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <ActivityIndicator />;
  }

  return (
    <View>
      <Text>BTC Price</Text>
      <Text>${price}</Text>
    </View>
  );
}
```

---

## 🔒 Authentication (در صورت نیاز)

### JWT Token Based:

```typescript
// دریافت توکن (login)
async function login(username: string, password: string) {
  const response = await fetch('http://localhost:7860/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  
  const data = await response.json();
  
  // ذخیره توکن
  localStorage.setItem('token', data.token);
  
  return data.token;
}

// استفاده از توکن در درخواست‌ها
async function getProtectedData() {
  const token = localStorage.getItem('token');
  
  const response = await fetch('http://localhost:7860/api/protected/data', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  return response.json();
}
```

---

## ⚡ بهینه‌سازی Performance

### 1. Caching در Client:

```typescript
class CachedAPIClient {
  private cache = new Map<string, { data: any; timestamp: number }>();
  private cacheTTL = 5000; // 5 seconds

  async get(url: string) {
    const cached = this.cache.get(url);
    
    // بررسی cache
    if (cached && Date.now() - cached.timestamp < this.cacheTTL) {
      return cached.data;
    }

    // درخواست جدید
    const response = await fetch(url);
    const data = await response.json();

    // ذخیره در cache
    this.cache.set(url, {
      data,
      timestamp: Date.now()
    });

    return data;
  }
}
```

### 2. Request Batching:

```typescript
class BatchedAPIClient {
  private pendingRequests: Map<string, Promise<any>> = new Map();

  async get(url: string) {
    // اگر همین درخواست در حال انجام است، همان را برگردان
    if (this.pendingRequests.has(url)) {
      return this.pendingRequests.get(url);
    }

    // درخواست جدید
    const promise = fetch(url).then(r => r.json());
    this.pendingRequests.set(url, promise);

    try {
      const data = await promise;
      return data;
    } finally {
      this.pendingRequests.delete(url);
    }
  }
}
```

### 3. Debouncing:

```typescript
function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };

    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// استفاده
const debouncedSearch = debounce(async (query: string) => {
  const results = await fetch(`/api/search?q=${query}`);
  // ...
}, 300);

// در input
<input onChange={(e) => debouncedSearch(e.target.value)} />
```

---

## 🚨 Error Handling

### Retry Logic:

```typescript
async function fetchWithRetry(
  url: string,
  options: RequestInit = {},
  retries = 3,
  delay = 1000
): Promise<any> {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    if (retries > 0) {
      console.log(`Retrying... (${retries} attempts left)`);
      await new Promise(resolve => setTimeout(resolve, delay));
      return fetchWithRetry(url, options, retries - 1, delay * 2);
    }
    
    throw error;
  }
}
```

### Global Error Handler:

```typescript
class APIClient {
  async request(url: string, options?: RequestInit) {
    try {
      const response = await fetch(url, options);
      
      if (response.status === 401) {
        // Token منقضی شده
        await this.refreshToken();
        return this.request(url, options); // Retry
      }
      
      if (response.status === 429) {
        // Rate limit
        const retryAfter = response.headers.get('Retry-After');
        await new Promise(r => setTimeout(r, parseInt(retryAfter || '5') * 1000));
        return this.request(url, options); // Retry
      }
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Request failed');
      }
      
      return await response.json();
    } catch (error) {
      // Log to monitoring service
      this.logError(error);
      throw error;
    }
  }
}
```

---

## 📊 Rate Limiting

**سمت سرور:**
```
✅ 100 requests/minute per IP
✅ Headers شامل rate limit info
```

**Response Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1702027200
```

**Handle در Client:**
```typescript
async function checkRateLimit(response: Response) {
  const limit = response.headers.get('X-RateLimit-Limit');
  const remaining = response.headers.get('X-RateLimit-Remaining');
  const reset = response.headers.get('X-RateLimit-Reset');

  if (response.status === 429) {
    const retryAfter = parseInt(reset!) - Date.now() / 1000;
    throw new Error(`Rate limit exceeded. Retry after ${retryAfter}s`);
  }

  return {
    limit: parseInt(limit!),
    remaining: parseInt(remaining!),
    reset: new Date(parseInt(reset!) * 1000)
  };
}
```

---

## ✅ Best Practices

### 1. همیشه Error Handling داشته باشید
```typescript
try {
  const data = await apiCall();
} catch (error) {
  // Handle error
  console.error(error);
  showErrorToUser(error.message);
}
```

### 2. Timeout تنظیم کنید
```typescript
const controller = new AbortController();
const timeout = setTimeout(() => controller.abort(), 10000);

fetch(url, { signal: controller.signal })
  .finally(() => clearTimeout(timeout));
```

### 3. Loading States نشان دهید
```typescript
const [loading, setLoading] = useState(false);

setLoading(true);
try {
  await apiCall();
} finally {
  setLoading(false);
}
```

### 4. Cache استفاده کنید
```typescript
// React Query
const { data } = useQuery('prices', fetchPrices, {
  staleTime: 5000,
  cacheTime: 10000
});
```

---

## 📱 پلتفرم‌های خاص

### iOS (Swift):
```swift
import Foundation

class CryptoAPIClient {
    let baseURL = "http://localhost:7860"
    
    func getPrice(symbol: String, completion: @escaping (Result<Double, Error>) -> Void) {
        guard let url = URL(string: "\(baseURL)/api/resources/market/price/\(symbol)") else {
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                return
            }
            
            do {
                let json = try JSONDecoder().decode(PriceResponse.self, from: data)
                completion(.success(json.price))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
}

struct PriceResponse: Codable {
    let price: Double
    let symbol: String
}
```

### Android (Kotlin):
```kotlin
import retrofit2.http.GET
import retrofit2.http.Path

interface CryptoAPI {
    @GET("api/resources/market/price/{symbol}")
    suspend fun getPrice(@Path("symbol") symbol: String): PriceResponse
}

data class PriceResponse(
    val price: Double,
    val symbol: String,
    val source: String
)

// استفاده
val api = Retrofit.Builder()
    .baseUrl("http://localhost:7860")
    .addConverterFactory(GsonConverterFactory.create())
    .build()
    .create(CryptoAPI::class.java)

lifecycleScope.launch {
    val response = api.getPrice("BTC")
    println("BTC Price: ${response.price}")
}
```

---

**تاریخ بروزرسانی**: ۸ دسامبر ۲۰۲۵  
**نسخه**: ۱.۰  
**وضعیت**: ✅ تکمیل شده
