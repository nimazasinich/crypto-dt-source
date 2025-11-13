# 📡 راهنمای استفاده از WebSocket API

## 🎯 مقدمه

این سیستم از WebSocket برای ارتباط بلادرنگ (Real-time) بین سرور و کلاینت استفاده می‌کند که سرعت و کارایی بسیار بالاتری نسبت به HTTP polling دارد.

## 🚀 مزایای WebSocket نسبت به HTTP

| ویژگی | HTTP Polling | WebSocket |
|-------|--------------|-----------|
| سرعت | کند (1-5 ثانیه تاخیر) | فوری (< 100ms) |
| منابع سرور | بالا | پایین |
| پهنای باند | زیاد | کم |
| اتصال | Multiple | Single (دائمی) |
| Overhead | بالا (headers هر بار) | خیلی کم |

## 📦 فایل‌های اضافه شده

### Backend:
- `backend/services/connection_manager.py` - مدیریت اتصالات WebSocket
- تغییرات در `api_server_extended.py` - اضافه شدن endpoint‌های WebSocket

### Frontend:
- `static/js/websocket-client.js` - کلاینت JavaScript
- `static/css/connection-status.css` - استایل‌های بصری
- `test_websocket.html` - صفحه تست

## 🔌 اتصال به WebSocket

### از JavaScript:

```javascript
// استفاده از کلاینت آماده
const wsClient = new CryptoWebSocketClient();

// یا اتصال دستی
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
    console.log('متصل شد!');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('پیام دریافت شد:', data);
};
```

### از Python:

```python
import asyncio
import websockets
import json

async def connect():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # دریافت پیام welcome
        welcome = await websocket.recv()
        print(f"دریافت: {welcome}")
        
        # ارسال پیام
        await websocket.send(json.dumps({
            "type": "subscribe",
            "group": "market"
        }))
        
        # دریافت پیام‌ها
        async for message in websocket:
            data = json.loads(message)
            print(f"داده جدید: {data}")

asyncio.run(connect())
```

## 📨 انواع پیام‌ها

### 1. پیام‌های سیستمی (Server → Client)

#### Welcome Message
```json
{
    "type": "welcome",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "به سیستم مانیتورینگ کریپتو خوش آمدید",
    "timestamp": "2024-01-15T10:30:00"
}
```

#### Stats Update (هر 30 ثانیه)
```json
{
    "type": "stats_update",
    "data": {
        "active_connections": 15,
        "total_sessions": 23,
        "messages_sent": 1250,
        "messages_received": 450,
        "client_types": {
            "browser": 12,
            "api": 2,
            "mobile": 1
        },
        "subscriptions": {
            "market": 8,
            "prices": 10,
            "all": 15
        }
    },
    "timestamp": "2024-01-15T10:30:30"
}
```

#### Provider Stats
```json
{
    "type": "provider_stats",
    "data": {
        "summary": {
            "total_providers": 150,
            "online": 142,
            "offline": 8,
            "overall_success_rate": 95.5
        }
    },
    "timestamp": "2024-01-15T10:30:30"
}
```

#### Market Update
```json
{
    "type": "market_update",
    "data": {
        "btc": { "price": 43250, "change_24h": 2.5 },
        "eth": { "price": 2280, "change_24h": -1.2 }
    },
    "timestamp": "2024-01-15T10:30:45"
}
```

#### Price Update
```json
{
    "type": "price_update",
    "data": {
        "symbol": "BTC",
        "price": 43250.50,
        "change_24h": 2.35
    },
    "timestamp": "2024-01-15T10:30:50"
}
```

#### Alert
```json
{
    "type": "alert",
    "data": {
        "alert_type": "price_threshold",
        "message": "قیمت بیت‌کوین از ۴۵۰۰۰ دلار عبور کرد",
        "severity": "info"
    },
    "timestamp": "2024-01-15T10:31:00"
}
```

#### Heartbeat
```json
{
    "type": "heartbeat",
    "timestamp": "2024-01-15T10:31:10"
}
```

### 2. پیام‌های کلاینت (Client → Server)

#### Subscribe
```json
{
    "type": "subscribe",
    "group": "market"
}
```

گروه‌های موجود:
- `market` - به‌روزرسانی‌های بازار
- `prices` - تغییرات قیمت
- `news` - اخبار
- `alerts` - هشدارها
- `all` - همه

#### Unsubscribe
```json
{
    "type": "unsubscribe",
    "group": "market"
}
```

#### Request Stats
```json
{
    "type": "get_stats"
}
```

#### Ping
```json
{
    "type": "ping"
}
```

## 🎨 استفاده از کامپوننت‌های بصری

### 1. نوار وضعیت اتصال

```html
<!-- اضافه کردن به صفحه -->
<div class="connection-status-bar" id="ws-connection-status">
    <div class="ws-connection-info">
        <span class="status-dot status-dot-offline" id="ws-status-dot"></span>
        <span class="ws-status-text" id="ws-status-text">در حال اتصال...</span>
    </div>
    
    <div class="online-users-widget">
        <div class="online-users-count">
            <span class="users-icon">👥</span>
            <span class="count-number" id="active-users-count">0</span>
            <span class="count-label">کاربر آنلاین</span>
        </div>
    </div>
</div>
```

### 2. اضافه کردن CSS و JS

```html
<head>
    <link rel="stylesheet" href="/static/css/connection-status.css">
</head>
<body>
    <!-- محتوا -->
    
    <script src="/static/js/websocket-client.js"></script>
</body>
```

### 3. استفاده از Client

```javascript
// کلاینت به صورت خودکار متصل می‌شود
// در دسترس از طریق window.wsClient

// ثبت handler سفارشی
window.wsClient.on('custom_event', (message) => {
    console.log('رویداد سفارشی:', message);
});

// اتصال به وضعیت اتصال
window.wsClient.onConnection((isConnected) => {
    if (isConnected) {
        console.log('✅ متصل شد');
    } else {
        console.log('❌ قطع شد');
    }
});

// ارسال پیام
window.wsClient.send({
    type: 'custom_action',
    data: { value: 123 }
});
```

## 🔧 API Endpoints

### GET `/api/sessions`
دریافت لیست session‌های فعال

**Response:**
```json
{
    "sessions": {
        "550e8400-...": {
            "session_id": "550e8400-...",
            "client_type": "browser",
            "connected_at": "2024-01-15T10:00:00",
            "last_activity": "2024-01-15T10:30:00"
        }
    },
    "stats": {
        "active_connections": 15,
        "total_sessions": 23
    }
}
```

### GET `/api/sessions/stats`
دریافت آمار اتصالات

**Response:**
```json
{
    "active_connections": 15,
    "total_sessions": 23,
    "messages_sent": 1250,
    "messages_received": 450,
    "client_types": {
        "browser": 12,
        "api": 2
    }
}
```

### POST `/api/broadcast`
ارسال پیام به همه کلاینت‌ها

**Request:**
```json
{
    "message": {
        "type": "notification",
        "text": "سیستم به‌روز شد"
    },
    "group": "all"
}
```

## 🧪 تست

### 1. باز کردن صفحه تست:
```
http://localhost:8000/test_websocket.html
```

### 2. چک کردن اتصال:
- نوار بالای صفحه باید سبز شود (متصل)
- تعداد کاربران آنلاین باید نمایش داده شود

### 3. تست دستورات:
- کلیک روی دکمه‌های مختلف
- مشاهده لاگ پیام‌ها در پنل پایین

### 4. تست چند تب:
- باز کردن چند تب مرورگر
- تعداد کاربران آنلاین باید افزایش یابد

## 📊 مانیتورینگ

### لاگ‌های سرور:
```bash
# مشاهده لاگ‌های WebSocket
tail -f logs/app.log | grep "WebSocket"
```

### متریک‌ها:
- تعداد اتصالات فعال
- تعداد کل session‌ها
- پیام‌های ارسالی/دریافتی
- توزیع انواع کلاینت

## 🔒 امنیت

### توصیه‌ها:
1. برای production از `wss://` (WebSocket Secure) استفاده کنید
2. محدودیت تعداد اتصال برای هر IP
3. Rate limiting برای پیام‌ها
4. اعتبارسنجی token برای authentication

### مثال با Token:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onopen = () => {
    ws.send(JSON.stringify({
        type: 'auth',
        token: 'YOUR_JWT_TOKEN'
    }));
};
```

## 🐛 عیب‌یابی

### مشکل: اتصال برقرار نمی‌شود
```bash
# چک کردن اجرای سرور
curl http://localhost:8000/health

# بررسی پورت
netstat -an | grep 8000
```

### مشکل: اتصال قطع می‌شود
- Heartbeat فعال است؟
- Proxy یا Firewall مشکل ندارد؟
- Log‌های سرور را بررسی کنید

### مشکل: پیام‌ها دریافت نمی‌شوند
- Subscribe کرده‌اید؟
- نوع پیام صحیح است؟
- کنسول مرورگر را بررسی کنید

## 📚 منابع بیشتر

- [WebSocket API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [websockets Python library](https://websockets.readthedocs.io/)

## 🎓 مثال کامل Integration

```html
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <link rel="stylesheet" href="/static/css/connection-status.css">
</head>
<body>
    <!-- UI Components -->
    <div class="connection-status-bar" id="ws-connection-status">
        <!-- ... -->
    </div>

    <div class="dashboard">
        <h1>تعداد کاربران: <span id="user-count">0</span></h1>
    </div>

    <script src="/static/js/websocket-client.js"></script>
    <script>
        // Custom logic
        if (window.wsClient) {
            window.wsClient.on('stats_update', (msg) => {
                document.getElementById('user-count').textContent = 
                    msg.data.active_connections;
            });
        }
    </script>
</body>
</html>
```

---

**نکته مهم:** این سیستم به صورت خودکار reconnect می‌کند و نیازی به مدیریت دستی ندارید!

