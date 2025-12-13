#!/usr/bin/env python3
"""
سرور API ساده برای نمایش منابع
فقط شامل endpoints اصلی برای تست
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from pathlib import Path
import json

# بارگذاری منابع
def load_resources():
    """بارگذاری منابع از فایل JSON"""
    resources_file = Path("api-resources/crypto_resources_unified_2025-11-11.json")
    
    if not resources_file.exists():
        return {}
    
    try:
        with open(resources_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('registry', {})
    except Exception as e:
        print(f"Error loading resources: {e}")
        return {}


# ایجاد app
app = FastAPI(
    title="Crypto Resources API",
    description="API برای نمایش منابع کریپتو",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# بارگذاری منابع
RESOURCES = load_resources()


@app.get("/")
async def root():
    """صفحه اصلی"""
    return {
        "message": "Crypto Resources API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "resources_stats": "/api/resources/stats",
            "resources_list": "/api/resources/list",
            "resources_by_category": "/api/resources/category/{category}",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "resources_loaded": len(RESOURCES) > 0,
        "total_categories": len([k for k, v in RESOURCES.items() if isinstance(v, list)])
    }


@app.get("/api/resources/stats")
async def resources_stats():
    """آمار منابع"""
    categories_count = {}
    total_resources = 0
    
    for key, value in RESOURCES.items():
        if isinstance(value, list):
            count = len(value)
            categories_count[key] = count
            total_resources += count
    
    metadata = RESOURCES.get('metadata', {})
    
    return {
        "total_resources": total_resources,
        "total_categories": len(categories_count),
        "categories": categories_count,
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
        "resources": all_resources[:50],  # فقط 50 مورد اول
        "note": f"Showing first 50 of {len(all_resources)} resources",
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


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 80)
    print("🚀 راه‌اندازی Crypto Resources API Server")
    print("=" * 80)
    print(f"\nبارگذاری منابع...")
    print(f"✅ {len([k for k,v in RESOURCES.items() if isinstance(v, list)])} دسته بارگذاری شد")
    print(f"\n🌐 Server: http://0.0.0.0:7860")
    print(f"📚 Docs: http://0.0.0.0:7860/docs")
    print(f"\nبرای توقف سرور: Ctrl+C")
    print("=" * 80 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=7860, log_level="info")
