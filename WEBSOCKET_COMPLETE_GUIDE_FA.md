# 🔌 راهنمای کامل WebSocket - سیستم Real-time

**نسخه:** 2.0.0  
**تاریخ:** 2025-12-08  
**وضعیت:** ✅ عملیاتی و تست شده

---

## 📋 فهرست

1. [نمای کلی](#نمای-کلی)
2. [Endpoints موجود](#endpoints-موجود)
3. [راه‌اندازی سرور](#راه‌اندازی-سرور)
4. [استفاده در Frontend](#استفاده-در-frontend)
5. [استفاده در Backend](#استفاده-در-backend)
6. [پیام‌های WebSocket](#پیام‌های-websocket)
7. [Error Handling](#error-handling)
8. [بهترین روش‌ها](#بهترین-روش‌ها)
9. [عیب‌یابی](#عیب‌یابی)

---

## 🎯 نمای کلی

سیستم WebSocket پروژه شامل **5 endpoint اصلی** است که به صورت real-time داده‌های زیر را ارائه می‌دهند:

```
✅ System Monitoring    → وضعیت کلی سیستم
✅ Market Data          → قیمت‌ها و تغییرات
✅ News Feed            → اخبار لحظه‌ای
✅ Sentiment Updates    → احساسات بازار
✅ AI Models Status     → وضعیت مدل‌های هوش مصنوعی
```

### ویژگی‌های کلیدی

- 🚀 **Zero Latency:** داده‌ها بلافاصله منتقل می‌شوند
- 🔄 **Auto-reconnect:** اتصال مجدد خودکار در صورت قطع
- 💪 **Scalable:** پشتیبانی از هزاران اتصال همزمان
- 🛡️ **Reliable:** مدیریت خطا و fallback
- 📊 **Monitored:** لاگینگ و آمارگیری کامل

---

## 🌐 Endpoints موجود

### 1️⃣ System Monitoring

```
ws://localhost:7860/api/monitoring/ws
```

**داده‌های ارسالی:**
- وضعیت AI Models (available, failed, loading)
- وضعیت Data Sources (active, inactive, by category)
- وضعیت Database (online, last check)
- درخواست‌های اخیر (recent requests)
- آمار سیستم (requests/minute, requests/hour)

**فرکانس:** هر 5 ثانیه

**نمونه پیام:**
```json
{
  "type": "system_status",
  "timestamp": "2025-12-08T10:30:00Z",
  "ai_models": {
    "total": 18,
    "available": 18,
    "failed": 0,
    "loading": 0,
    "models": [
      {
        "id": "cryptobert",
        "status": "available",
        "success_rate": 98.5
      }
    ]
  },
  "data_sources": {
    "total": 137,
    "active": 137,
    "inactive": 0,
    "categories": {
      "market_data": {"total": 20, "active": 20},
      "news": {"total": 15, "active": 15}
    },
    "pools": 10,
    "sources": [...]
  },
  "database": {
    "online": true,
    "last_check": "2025-12-08T10:30:00Z",
    "ai_models_db": true,
    "main_db": true
  },
  "stats": {
    "total_sources": 137,
    "active_sources": 137,
    "total_models": 18,
    "available_models": 18,
    "requests_last_minute": 50,
    "requests_last_hour": 2500
  },
  "agent_running": true
}
```

---

### 2️⃣ Market Data Stream

```
ws://localhost:7860/ws/market_data
```

**قابلیت‌ها:**
- اشتراک در قیمت ارزهای خاص
- دریافت قیمت real-time
- تغییرات 24 ساعته
- حجم معاملات

**فرکانس:** هر 1 ثانیه (برای ارزهای subscribe شده)

**پیام‌های ارسالی به سرور:**
```json
// Subscribe
{
  "action": "subscribe",
  "symbols": ["BTC", "ETH", "SOL"]
}

// Unsubscribe
{
  "action": "unsubscribe",
  "symbols": ["SOL"]
}

// Get All
{
  "action": "get_all"
}
```

**پیام‌های دریافتی:**
```json
{
  "type": "price_update",
  "data": {
    "symbol": "BTC",
    "price": 43250.50,
    "change_24h": 2.5,
    "change_7d": -1.2,
    "volume_24h": 25000000000,
    "market_cap": 850000000000,
    "timestamp": "2025-12-08T10:30:15Z"
  },
  "source": "binance"
}
```

---

### 3️⃣ News Feed

```
ws://localhost:7860/ws/news
```

**قابلیت‌ها:**
- اخبار جدید به محض انتشار
- فیلتر بر اساس کلیدواژه
- Sentiment analysis

**فرکانس:** Real-time (به محض انتشار خبر)

**پیام‌های ارسالی:**
```json
{
  "action": "filter",
  "keywords": ["bitcoin", "ethereum"]
}
```

**پیام‌های دریافتی:**
```json
{
  "type": "news",
  "data": {
    "title": "Bitcoin Reaches New All-Time High",
    "description": "Bitcoin price surges past $45,000...",
    "url": "https://...",
    "source": "CoinDesk",
    "published_at": "2025-12-08T10:25:00Z",
    "sentiment": "positive",
    "sentiment_score": 0.85,
    "image_url": "https://..."
  }
}
```

---

### 4️⃣ Sentiment Updates

```
ws://localhost:7860/ws/sentiment
```

**قابلیت‌ها:**
- Fear & Greed Index
- Social sentiment
- Market sentiment

**فرکانس:** هر 1 دقیقه

**پیام‌های دریافتی:**
```json
{
  "type": "sentiment_update",
  "data": {
    "fear_greed": {
      "value": 75,
      "classification": "Extreme Greed",
      "timestamp": "2025-12-08T10:30:00Z"
    },
    "social": {
      "twitter": {
        "sentiment": "bullish",
        "score": 0.68,
        "mentions": 15000
      },
      "reddit": {
        "sentiment": "neutral",
        "score": 0.52,
        "mentions": 8000
      }
    },
    "market": {
      "overall": "bullish",
      "confidence": 0.72
    }
  }
}
```

---

### 5️⃣ AI Models Status

```
ws://localhost:7860/ws/huggingface
```

**قابلیت‌ها:**
- وضعیت مدل‌ها (available, loading, failed)
- نرخ موفقیت
- زمان پاسخ‌دهی

**فرکانس:** هر 10 ثانیه

**پیام‌های دریافتی:**
```json
{
  "type": "models_status",
  "data": {
    "total": 18,
    "available": 18,
    "loading": 0,
    "failed": 0,
    "models": [
      {
        "id": "ElKulako/CryptoBERT",
        "type": "sentiment",
        "status": "available",
        "success_rate": 98.5,
        "avg_response_time": 150,
        "last_used": "2025-12-08T10:29:00Z"
      }
    ]
  }
}
```

---

## 🚀 راه‌اندازی سرور

### 1. بدون Docker

```bash
# نصب dependencies
pip install uvicorn websockets fastapi

# اجرا
python3 app.py

# یا با uvicorn
uvicorn app:app --host 0.0.0.0 --port 7860 --ws websockets
```

### 2. با Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860", "--ws", "websockets"]
```

```bash
# Build و Run
docker build -t crypto-api .
docker run -p 7860:7860 crypto-api
```

### 3. HuggingFace Space

```python
# در app.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=7860,
        ws="websockets",  # ✅ مهم!
        log_level="info"
    )
```

**`requirements.txt`:**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
```

---

## 💻 استفاده در Frontend

### JavaScript (Vanilla)

```javascript
class WebSocketClient {
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.reconnectInterval = 5000;
        this.maxReconnectAttempts = 10;
        this.reconnectAttempts = 0;
    }
    
    connect() {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
            console.log(`✅ Connected to ${this.url}`);
            this.reconnectAttempts = 0;
        };
        
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('❌ Parse error:', error);
            }
        };
        
        this.ws.onerror = (error) => {
            console.error('❌ WebSocket error:', error);
        };
        
        this.ws.onclose = () => {
            console.log('⚠️ Connection closed');
            this.reconnect();
        };
    }
    
    reconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            setTimeout(() => this.connect(), this.reconnectInterval);
        } else {
            console.error('❌ Max reconnect attempts reached');
        }
    }
    
    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.error('❌ WebSocket not connected');
        }
    }
    
    handleMessage(data) {
        // Override این متد
        console.log('📨 Message:', data);
    }
    
    close() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// استفاده
class SystemMonitor extends WebSocketClient {
    constructor() {
        super('ws://localhost:7860/api/monitoring/ws');
    }
    
    handleMessage(data) {
        // به‌روزرسانی UI
        if (data.type === 'system_status') {
            document.getElementById('total-sources').textContent = data.stats.total_sources;
            document.getElementById('active-sources').textContent = data.stats.active_sources;
            document.getElementById('total-models').textContent = data.stats.total_models;
        }
    }
}

// شروع
const monitor = new SystemMonitor();
monitor.connect();
```

### React

```jsx
import { useState, useEffect } from 'react';

function useWebSocket(url) {
  const [data, setData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => {
      console.log('Connected');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setData(data);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('Disconnected');
      setIsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [url]);

  return { data, isConnected };
}

// استفاده در Component
function Dashboard() {
  const { data, isConnected } = useWebSocket('ws://localhost:7860/api/monitoring/ws');

  return (
    <div>
      <div>Status: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}</div>
      {data && (
        <div>
          <p>Total Sources: {data.stats?.total_sources}</p>
          <p>Active Sources: {data.stats?.active_sources}</p>
          <p>Total Models: {data.stats?.total_models}</p>
        </div>
      )}
    </div>
  );
}
```

### Vue.js

```vue
<template>
  <div>
    <div>Status: {{ isConnected ? '🟢 Connected' : '🔴 Disconnected' }}</div>
    <div v-if="data">
      <p>Total Sources: {{ data.stats?.total_sources }}</p>
      <p>Active Sources: {{ data.stats?.active_sources }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      ws: null,
      data: null,
      isConnected: false
    };
  },
  mounted() {
    this.connect();
  },
  beforeUnmount() {
    if (this.ws) {
      this.ws.close();
    }
  },
  methods: {
    connect() {
      this.ws = new WebSocket('ws://localhost:7860/api/monitoring/ws');
      
      this.ws.onopen = () => {
        console.log('Connected');
        this.isConnected = true;
      };
      
      this.ws.onmessage = (event) => {
        this.data = JSON.parse(event.data);
      };
      
      this.ws.onclose = () => {
        this.isConnected = false;
        // Auto-reconnect
        setTimeout(() => this.connect(), 5000);
      };
    }
  }
};
</script>
```

---

## 🐍 استفاده در Backend

### Python Client

```python
import asyncio
import websockets
import json

async def monitor_system():
    uri = "ws://localhost:7860/api/monitoring/ws"
    
    async with websockets.connect(uri) as websocket:
        print("✅ Connected")
        
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                
                # Process data
                print(f"📊 Sources: {data['stats']['total_sources']}")
                print(f"📊 Models: {data['stats']['total_models']}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                break

# اجرا
asyncio.run(monitor_system())
```

### Python Client با Auto-reconnect

```python
import asyncio
import websockets
import json
from typing import Callable

class WebSocketClient:
    def __init__(self, uri: str, on_message: Callable):
        self.uri = uri
        self.on_message = on_message
        self.running = False
    
    async def connect(self):
        """اتصال با auto-reconnect"""
        self.running = True
        
        while self.running:
            try:
                async with websockets.connect(self.uri) as websocket:
                    print(f"✅ Connected to {self.uri}")
                    
                    while self.running:
                        message = await websocket.recv()
                        data = json.loads(message)
                        await self.on_message(data)
                        
            except Exception as e:
                print(f"❌ Connection error: {e}")
                print("🔄 Reconnecting in 5 seconds...")
                await asyncio.sleep(5)
    
    def stop(self):
        """قطع اتصال"""
        self.running = False

# استفاده
async def handle_message(data):
    print(f"📨 Received: {data['type']}")
    print(f"   Sources: {data.get('stats', {}).get('total_sources', 'N/A')}")

client = WebSocketClient(
    'ws://localhost:7860/api/monitoring/ws',
    handle_message
)

try:
    await client.connect()
except KeyboardInterrupt:
    client.stop()
```

---

## 📨 پیام‌های WebSocket

### فرمت عمومی

همه پیام‌ها شامل:
```json
{
  "type": "message_type",
  "timestamp": "2025-12-08T10:30:00Z",
  "data": { ... }
}
```

### انواع پیام‌ها

| Type | توضیح | Endpoint |
|------|-------|----------|
| `system_status` | وضعیت سیستم | `/api/monitoring/ws` |
| `price_update` | به‌روزرسانی قیمت | `/ws/market_data` |
| `news` | خبر جدید | `/ws/news` |
| `sentiment_update` | به‌روزرسانی احساسات | `/ws/sentiment` |
| `models_status` | وضعیت مدل‌ها | `/ws/huggingface` |
| `error` | خطا | همه |
| `ping` | Heartbeat | همه |

---

## 🛡️ Error Handling

### خطاهای رایج

```json
// خطای عمومی
{
  "type": "error",
  "timestamp": "2025-12-08T10:30:00Z",
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Failed to fetch data",
    "details": "..."
  }
}

// خطای اتصال
{
  "type": "error",
  "error": {
    "code": "CONNECTION_ERROR",
    "message": "Lost connection to data source"
  }
}

// خطای احراز هویت
{
  "type": "error",
  "error": {
    "code": "AUTH_ERROR",
    "message": "Invalid or missing authentication"
  }
}
```

### مدیریت خطا در Client

```javascript
ws.onerror = (error) => {
    console.error('❌ WebSocket error:', error);
    
    // نمایش به کاربر
    showNotification('Connection error', 'error');
    
    // تلاش مجدد
    reconnect();
};

ws.onclose = (event) => {
    if (event.code === 1000) {
        console.log('✅ Normal closure');
    } else {
        console.error(`❌ Abnormal closure: ${event.code}`);
        reconnect();
    }
};
```

---

## 💡 بهترین روش‌ها

### 1. Heartbeat/Ping

```javascript
// Client-side heartbeat
setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
    }
}, 30000); // هر 30 ثانیه
```

### 2. Buffer Management

```javascript
// محدود کردن تعداد پیام‌های نگهداری شده
const messageBuffer = [];
const MAX_BUFFER = 100;

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    messageBuffer.unshift(data);
    if (messageBuffer.length > MAX_BUFFER) {
        messageBuffer.pop();
    }
};
```

### 3. Throttling

```javascript
// محدود کردن نرخ پردازش پیام‌ها
let lastProcessTime = 0;
const MIN_INTERVAL = 100; // 100ms

ws.onmessage = (event) => {
    const now = Date.now();
    
    if (now - lastProcessTime >= MIN_INTERVAL) {
        processMessage(event.data);
        lastProcessTime = now;
    }
};
```

### 4. Connection Pooling

```javascript
// مدیریت چند اتصال
class ConnectionPool {
    constructor() {
        this.connections = new Map();
    }
    
    add(name, url) {
        const ws = new WebSocket(url);
        this.connections.set(name, ws);
        return ws;
    }
    
    get(name) {
        return this.connections.get(name);
    }
    
    closeAll() {
        this.connections.forEach(ws => ws.close());
        this.connections.clear();
    }
}

const pool = new ConnectionPool();
pool.add('monitor', 'ws://localhost:7860/api/monitoring/ws');
pool.add('market', 'ws://localhost:7860/ws/market_data');
```

---

## 🔧 عیب‌یابی

### مشکل 1: اتصال برقرار نمی‌شود

**علل احتمالی:**
- سرور در حال اجرا نیست
- Port اشتباه است
- Firewall مسدود کرده

**راه‌حل:**
```bash
# بررسی سرور
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: test" \
     http://localhost:7860/api/monitoring/ws

# بررسی port
netstat -an | grep 7860
lsof -i :7860

# بررسی لاگ سرور
tail -f logs/server.log
```

### مشکل 2: پیام‌ها دریافت نمی‌شوند

**راه‌حل:**
```javascript
// Log همه چیز
ws.onopen = () => console.log('🟢 OPEN');
ws.onmessage = (e) => console.log('📨 MESSAGE:', e.data);
ws.onerror = (e) => console.error('❌ ERROR:', e);
ws.onclose = (e) => console.log('🔴 CLOSE:', e.code, e.reason);
```

### مشکل 3: اتصال قطع می‌شود

**راه‌حل:**
```javascript
// Implement heartbeat
const heartbeat = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
    } else {
        clearInterval(heartbeat);
        reconnect();
    }
}, 30000);
```

### مشکل 4: Memory leak

**راه‌حل:**
```javascript
// پاکسازی صحیح
function cleanup() {
    if (ws) {
        ws.onopen = null;
        ws.onmessage = null;
        ws.onerror = null;
        ws.onclose = null;
        ws.close();
        ws = null;
    }
}

// فراخوانی cleanup در unmount
window.addEventListener('beforeunload', cleanup);
```

---

## 📊 مانیتورینگ

### لاگ سرور

```python
# در backend
import logging

logger = logging.getLogger('websocket')
logger.setLevel(logging.INFO)

@app.websocket("/api/monitoring/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info(f"Client connected: {websocket.client}")
    
    try:
        while True:
            data = get_system_status()
            await websocket.send_json(data)
            await asyncio.sleep(5)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info(f"Client disconnected: {websocket.client}")
```

### آمار Client

```javascript
class WebSocketStats {
    constructor() {
        this.messagesReceived = 0;
        this.messagesSent = 0;
        this.errors = 0;
        this.reconnects = 0;
        this.startTime = Date.now();
    }
    
    getStats() {
        const uptime = Date.now() - this.startTime;
        return {
            messagesReceived: this.messagesReceived,
            messagesSent: this.messagesSent,
            errors: this.errors,
            reconnects: this.reconnects,
            uptime: uptime,
            messagesPerSecond: this.messagesReceived / (uptime / 1000)
        };
    }
}

const stats = new WebSocketStats();

ws.onmessage = () => {
    stats.messagesReceived++;
};
```

---

## 🎯 نتیجه‌گیری

### ویژگی‌های تکمیل شده

```
✅ 5 WebSocket endpoint کامل
✅ Auto-reconnect
✅ Error handling
✅ Message buffering
✅ Heartbeat/Ping
✅ Logging کامل
✅ آماده برای Production
✅ مستندسازی جامع
```

### استفاده

```javascript
// به سادگی:
const ws = new WebSocket('ws://localhost:7860/api/monitoring/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Update:', data);
};
```

---

**✅ WebSocket کاملاً عملیاتی است!**

*آخرین به‌روزرسانی: 2025-12-08 | نسخه: 2.0.0*
