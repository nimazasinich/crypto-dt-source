#!/usr/bin/env python3
"""
Crypto Resources API - Hugging Face Space
سرور API با رابط کاربری وب و WebSocket
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from pathlib import Path
import json
import asyncio
from typing import List, Dict, Any, Set
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load resources
def load_resources():
    """بارگذاری منابع از فایل JSON"""
    resources_file = Path("api-resources/crypto_resources_unified_2025-11-11.json")
    
    if not resources_file.exists():
        logger.warning(f"Resources file not found: {resources_file}")
        return {}
    
    try:
        with open(resources_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"✅ Loaded resources from {resources_file}")
        return data.get('registry', {})
    except Exception as e:
        logger.error(f"Error loading resources: {e}")
        return {}

# Create FastAPI app
app = FastAPI(
    title="Crypto Resources API",
    description="API جامع برای دسترسی به منابع داده کریپتوکارنسی",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load resources
RESOURCES = load_resources()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """ارسال پیام به همه کلاینت‌ها"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected.add(connection)
        
        # حذف اتصالات قطع شده
        for conn in disconnected:
            self.active_connections.discard(conn)

manager = ConnectionManager()

# Background task for broadcasting stats
async def broadcast_stats():
    """ارسال دوره‌ای آمار به کلاینت‌ها"""
    while True:
        try:
            if manager.active_connections:
                stats = get_stats_data()
                await manager.broadcast({
                    "type": "stats_update",
                    "data": stats,
                    "timestamp": datetime.now().isoformat()
                })
            await asyncio.sleep(10)  # هر 10 ثانیه
        except Exception as e:
            logger.error(f"Error in broadcast_stats: {e}")
            await asyncio.sleep(5)

# Startup event
@app.on_event("startup")
async def startup_event():
    """راه‌اندازی سرویس‌های پس‌زمینه"""
    logger.info("🚀 Starting Crypto Resources API...")
    logger.info(f"📦 Loaded {len([k for k,v in RESOURCES.items() if isinstance(v, list)])} categories")
    
    # شروع broadcast task
    asyncio.create_task(broadcast_stats())
    logger.info("✅ Background tasks started")

# Helper functions
def get_stats_data():
    """دریافت آمار کلی"""
    categories_count = {}
    total_resources = 0
    
    for key, value in RESOURCES.items():
        if isinstance(value, list):
            count = len(value)
            categories_count[key] = count
            total_resources += count
    
    return {
        "total_resources": total_resources,
        "total_categories": len(categories_count),
        "categories": categories_count
    }

# HTML UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crypto Resources API</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .header h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        
        .header p {
            color: #666;
            font-size: 1.1em;
        }
        
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin-top: 10px;
        }
        
        .status-online {
            background: #4CAF50;
            color: white;
        }
        
        .status-offline {
            background: #f44336;
            color: white;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }
        
        .stat-label {
            color: #666;
            font-size: 1.1em;
        }
        
        .categories-section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }
        
        .categories-section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        .category-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
        }
        
        .category-item {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .category-item:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
        }
        
        .category-name {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .category-count {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .api-endpoints {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .api-endpoints h2 {
            color: #667eea;
            margin-bottom: 20px;
        }
        
        .endpoint-item {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
        }
        
        .endpoint-method {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 3px 10px;
            border-radius: 5px;
            font-size: 0.85em;
            font-weight: bold;
            margin-left: 10px;
        }
        
        .endpoint-path {
            font-family: monospace;
            color: #333;
            font-weight: bold;
        }
        
        .websocket-status {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .websocket-status h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .ws-messages {
            background: #f9f9f9;
            border-radius: 8px;
            padding: 15px;
            max-height: 200px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.9em;
        }
        
        .ws-message {
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }
        
        .footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .loading {
            animation: pulse 1.5s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Crypto Resources API</h1>
            <p>API جامع برای دسترسی به منابع داده کریپتوکارنسی</p>
            <span id="statusBadge" class="status-badge status-offline">در حال اتصال...</span>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">مجموع منابع</div>
                <div class="stat-number" id="totalResources">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">دسته‌بندی‌ها</div>
                <div class="stat-number" id="totalCategories">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">وضعیت سرور</div>
                <div class="stat-number" id="serverStatus">⏳</div>
            </div>
        </div>
        
        <div class="categories-section">
            <h2>📂 دسته‌بندی منابع</h2>
            <div class="category-list" id="categoryList">
                <div class="loading">در حال بارگذاری...</div>
            </div>
        </div>
        
        <div class="api-endpoints">
            <h2>📡 API Endpoints</h2>
            <div class="endpoint-item">
                <span class="endpoint-method">GET</span>
                <span class="endpoint-path">/health</span>
                <span> - Health check</span>
            </div>
            <div class="endpoint-item">
                <span class="endpoint-method">GET</span>
                <span class="endpoint-path">/api/resources/stats</span>
                <span> - آمار کلی منابع</span>
            </div>
            <div class="endpoint-item">
                <span class="endpoint-method">GET</span>
                <span class="endpoint-path">/api/resources/list</span>
                <span> - لیست تمام منابع</span>
            </div>
            <div class="endpoint-item">
                <span class="endpoint-method">GET</span>
                <span class="endpoint-path">/api/categories</span>
                <span> - لیست دسته‌بندی‌ها</span>
            </div>
            <div class="endpoint-item">
                <span class="endpoint-method">GET</span>
                <span class="endpoint-path">/api/resources/category/{category}</span>
                <span> - منابع یک دسته خاص</span>
            </div>
            <div class="endpoint-item">
                <span class="endpoint-method">WS</span>
                <span class="endpoint-path">/ws</span>
                <span> - WebSocket برای بروزرسانی لحظه‌ای</span>
            </div>
        </div>
        
        <div class="websocket-status">
            <h3>🔌 WebSocket Status: <span id="wsStatus">Disconnected</span></h3>
            <div class="ws-messages" id="wsMessages">
                <div class="ws-message">در انتظار اتصال...</div>
            </div>
        </div>
        
        <div class="footer">
            <p>💜 ساخته شده با عشق برای جامعه کریپتو</p>
            <p>📚 مستندات کامل: <a href="/docs" style="color: white; text-decoration: underline;">/docs</a></p>
        </div>
    </div>
    
    <script>
        // WebSocket connection
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        let ws = null;
        let reconnectInterval = null;
        
        function connectWebSocket() {
            try {
                ws = new WebSocket(wsUrl);
                
                ws.onopen = () => {
                    console.log('✅ WebSocket connected');
                    document.getElementById('wsStatus').textContent = 'Connected ✅';
                    document.getElementById('statusBadge').className = 'status-badge status-online';
                    document.getElementById('statusBadge').textContent = 'آنلاین ✅';
                    addWsMessage('اتصال WebSocket برقرار شد ✅');
                    
                    if (reconnectInterval) {
                        clearInterval(reconnectInterval);
                        reconnectInterval = null;
                    }
                };
                
                ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        console.log('📨 Received:', data);
                        
                        if (data.type === 'stats_update') {
                            updateStats(data.data);
                            addWsMessage(`بروزرسانی آمار: ${data.data.total_resources} منبع`);
                        }
                    } catch (e) {
                        console.error('Error parsing message:', e);
                    }
                };
                
                ws.onerror = (error) => {
                    console.error('❌ WebSocket error:', error);
                    document.getElementById('wsStatus').textContent = 'Error ❌';
                    addWsMessage('خطا در اتصال WebSocket ❌');
                };
                
                ws.onclose = () => {
                    console.log('🔌 WebSocket disconnected');
                    document.getElementById('wsStatus').textContent = 'Disconnected';
                    document.getElementById('statusBadge').className = 'status-badge status-offline';
                    document.getElementById('statusBadge').textContent = 'آفلاین';
                    addWsMessage('اتصال WebSocket قطع شد. در حال تلاش مجدد...');
                    
                    // تلاش مجدد برای اتصال
                    if (!reconnectInterval) {
                        reconnectInterval = setInterval(() => {
                            console.log('🔄 Reconnecting...');
                            connectWebSocket();
                        }, 5000);
                    }
                };
            } catch (e) {
                console.error('Error creating WebSocket:', e);
            }
        }
        
        function addWsMessage(message) {
            const container = document.getElementById('wsMessages');
            const msgDiv = document.createElement('div');
            msgDiv.className = 'ws-message';
            msgDiv.textContent = `[${new Date().toLocaleTimeString('fa-IR')}] ${message}`;
            container.appendChild(msgDiv);
            container.scrollTop = container.scrollHeight;
            
            // نگه داشتن فقط 10 پیام آخر
            while (container.children.length > 10) {
                container.removeChild(container.firstChild);
            }
        }
        
        function updateStats(stats) {
            document.getElementById('totalResources').textContent = stats.total_resources;
            document.getElementById('totalCategories').textContent = stats.total_categories;
            document.getElementById('serverStatus').textContent = '✅';
            
            // بروزرسانی لیست دسته‌ها
            const categoryList = document.getElementById('categoryList');
            categoryList.innerHTML = '';
            
            for (const [name, count] of Object.entries(stats.categories)) {
                const item = document.createElement('div');
                item.className = 'category-item';
                item.innerHTML = `
                    <div class="category-name">${name}</div>
                    <div class="category-count">${count} منبع</div>
                `;
                item.onclick = () => {
                    window.open(`/api/resources/category/${name}`, '_blank');
                };
                categoryList.appendChild(item);
            }
        }
        
        // بارگذاری اولیه آمار
        async function loadInitialStats() {
            try {
                const response = await fetch('/api/resources/stats');
                const stats = await response.json();
                updateStats(stats);
            } catch (e) {
                console.error('Error loading initial stats:', e);
            }
        }
        
        // شروع اتصال
        connectWebSocket();
        loadInitialStats();
    </script>
</body>
</html>
"""

# Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """صفحه اصلی با UI"""
    return HTMLResponse(content=HTML_TEMPLATE)

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "resources_loaded": len(RESOURCES) > 0,
        "total_categories": len([k for k, v in RESOURCES.items() if isinstance(v, list)]),
        "websocket_connections": len(manager.active_connections)
    }

@app.get("/api/resources/stats")
async def resources_stats():
    """آمار منابع"""
    stats = get_stats_data()
    metadata = RESOURCES.get('metadata', {})
    
    return {
        **stats,
        "metadata": metadata,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/resources/list")
async def resources_list():
    """لیست همه منابع"""
    all_resources = []
    
    for category, resources in RESOURCES.items():
        if isinstance(resources, list):
            for resource in resources:
                if isinstance(resource, dict):
                    all_resources.append({
                        "category": category,
                        "id": resource.get('id', 'unknown'),
                        "name": resource.get('name', 'Unknown'),
                        "base_url": resource.get('base_url', ''),
                        "auth_type": resource.get('auth', {}).get('type', 'none')
                    })
    
    return {
        "total": len(all_resources),
        "resources": all_resources[:100],  # اولین 100 مورد
        "note": f"Showing first 100 of {len(all_resources)} resources",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/resources/category/{category}")
async def resources_by_category(category: str):
    """منابع یک دسته خاص"""
    if category not in RESOURCES:
        return JSONResponse(
            status_code=404,
            content={"error": f"Category '{category}' not found"}
        )
    
    resources = RESOURCES.get(category, [])
    
    if not isinstance(resources, list):
        return JSONResponse(
            status_code=400,
            content={"error": f"Category '{category}' is not a resource list"}
        )
    
    return {
        "category": category,
        "total": len(resources),
        "resources": resources,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/categories")
async def list_categories():
    """لیست دسته‌بندی‌ها"""
    categories = []
    
    for key, value in RESOURCES.items():
        if isinstance(value, list):
            categories.append({
                "name": key,
                "count": len(value),
                "endpoint": f"/api/resources/category/{key}"
            })
    
    return {
        "total": len(categories),
        "categories": categories,
        "timestamp": datetime.now().isoformat()
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint برای بروزرسانی لحظه‌ای"""
    await manager.connect(websocket)
    
    try:
        # ارسال آمار اولیه
        stats = get_stats_data()
        await websocket.send_json({
            "type": "initial_stats",
            "data": stats,
            "timestamp": datetime.now().isoformat()
        })
        
        # نگه داشتن اتصال
        while True:
            try:
                # دریافت پیام از کلاینت (اگر بفرستد)
                data = await websocket.receive_text()
                logger.info(f"Received from client: {data}")
                
                # پاسخ به کلاینت
                await websocket.send_json({
                    "type": "pong",
                    "message": "Server is alive",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error in websocket loop: {e}")
                break
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    
    print("=" * 80)
    print("🚀 راه‌اندازی Crypto Resources API Server")
    print("=" * 80)
    print(f"\nبارگذاری منابع...")
    print(f"✅ {len([k for k,v in RESOURCES.items() if isinstance(v, list)])} دسته بارگذاری شد")
    print(f"\n🌐 Server: http://0.0.0.0:7860")
    print(f"📚 Docs: http://0.0.0.0:7860/docs")
    print(f"🔌 WebSocket: ws://0.0.0.0:7860/ws")
    print(f"\nبرای توقف سرور: Ctrl+C")
    print("=" * 80 + "\n")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=7860, 
        log_level="info",
        access_log=True
    )
