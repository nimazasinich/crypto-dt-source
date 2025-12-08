#!/usr/bin/env python3
"""
AI Models Monitor API
API برای نظارت و مدیریت مدل‌های AI
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.services.ai_models_monitor import db, monitor, agent

router = APIRouter(prefix="/api/ai-models", tags=["AI Models Monitor"])


# ===== Pydantic Models =====

class ScanResponse(BaseModel):
    total: int
    available: int
    loading: int
    failed: int
    auth_required: int
    not_found: int = 0
    models: List[Dict[str, Any]]


class ModelInfo(BaseModel):
    model_id: str
    model_key: Optional[str]
    task: str
    category: str
    provider: str = "huggingface"
    total_checks: Optional[int]
    successful_checks: Optional[int]
    success_rate: Optional[float]
    avg_response_time_ms: Optional[float]


class AgentStatus(BaseModel):
    running: bool
    interval_minutes: int
    last_scan: Optional[str]


# ===== Endpoints =====

@router.get("/scan", response_model=ScanResponse)
async def trigger_scan(background_tasks: BackgroundTasks):
    """
    شروع اسکن فوری همه مدل‌ها
    
    این endpoint یک اسکن کامل از همه مدل‌ها انجام می‌دهد و نتایج را در دیتابیس ذخیره می‌کند.
    """
    try:
        result = await monitor.scan_all_models()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.get("/models", response_model=List[ModelInfo])
async def get_all_models(status: Optional[str] = None):
    """
    دریافت لیست همه مدل‌ها
    
    Args:
        status: فیلتر بر اساس وضعیت (available, loading, failed, etc.)
    """
    try:
        if status:
            models = monitor.get_models_by_status(status)
        else:
            models = db.get_all_models()
        
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")


@router.get("/models/{model_id}/history")
async def get_model_history(model_id: str, limit: int = 100):
    """
    دریافت تاریخچه یک مدل
    
    Args:
        model_id: شناسه مدل (مثلاً kk08/CryptoBERT)
        limit: تعداد رکوردها (پیش‌فرض: 100)
    """
    try:
        history = db.get_model_history(model_id, limit)
        return {
            "model_id": model_id,
            "total_records": len(history),
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.get("/models/{model_id}/stats")
async def get_model_stats(model_id: str):
    """
    دریافت آمار یک مدل خاص
    """
    try:
        models = db.get_all_models()
        model = next((m for m in models if m['model_id'] == model_id), None)
        
        if not model:
            raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
        
        history = db.get_model_history(model_id, limit=10)
        
        return {
            "model_info": model,
            "recent_checks": history
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.get("/stats/summary")
async def get_summary_stats():
    """
    دریافت آمار خلاصه از همه مدل‌ها
    """
    try:
        models = db.get_all_models()
        
        total = len(models)
        with_checks = sum(1 for m in models if m.get('total_checks', 0) > 0)
        avg_success_rate = sum(m.get('success_rate', 0) for m in models if m.get('success_rate')) / with_checks if with_checks > 0 else 0
        
        # دسته‌بندی بر اساس category
        by_category = {}
        for model in models:
            cat = model.get('category', 'unknown')
            if cat not in by_category:
                by_category[cat] = {
                    'total': 0,
                    'avg_success_rate': 0,
                    'models': []
                }
            by_category[cat]['total'] += 1
            by_category[cat]['models'].append(model['model_id'])
            if model.get('success_rate'):
                by_category[cat]['avg_success_rate'] += model['success_rate']
        
        # محاسبه میانگین
        for cat in by_category:
            if by_category[cat]['total'] > 0:
                by_category[cat]['avg_success_rate'] /= by_category[cat]['total']
        
        return {
            "total_models": total,
            "models_with_checks": with_checks,
            "overall_success_rate": avg_success_rate,
            "by_category": by_category,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")


@router.get("/agent/status", response_model=AgentStatus)
async def get_agent_status():
    """
    دریافت وضعیت Agent
    """
    return {
        "running": agent.running,
        "interval_minutes": agent.interval / 60,
        "last_scan": None  # TODO: track last scan time
    }


@router.post("/agent/start")
async def start_agent(background_tasks: BackgroundTasks):
    """
    شروع Agent خودکار
    
    Agent به صورت خودکار هر 5 دقیقه مدل‌ها را بررسی می‌کند
    """
    if agent.running:
        return {
            "status": "already_running",
            "message": "Agent is already running",
            "interval_minutes": agent.interval / 60
        }
    
    try:
        background_tasks.add_task(agent.start)
        return {
            "status": "started",
            "message": "Agent started successfully",
            "interval_minutes": agent.interval / 60
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start agent: {str(e)}")


@router.post("/agent/stop")
async def stop_agent():
    """
    توقف Agent
    """
    if not agent.running:
        return {
            "status": "not_running",
            "message": "Agent is not running"
        }
    
    try:
        await agent.stop()
        return {
            "status": "stopped",
            "message": "Agent stopped successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop agent: {str(e)}")


@router.get("/dashboard")
async def get_dashboard_data():
    """
    دریافت داده‌های کامل برای داشبورد
    """
    try:
        models = db.get_all_models()
        summary = await get_summary_stats()
        
        # مدل‌های برتر (بر اساس success rate)
        top_models = sorted(
            [m for m in models if m.get('success_rate', 0) > 0],
            key=lambda x: x.get('success_rate', 0),
            reverse=True
        )[:10]
        
        # مدل‌های problem
        failed_models = sorted(
            [m for m in models if m.get('success_rate', 0) < 50],
            key=lambda x: x.get('success_rate', 0)
        )[:10]
        
        return {
            "summary": summary,
            "top_models": top_models,
            "failed_models": failed_models,
            "agent_running": agent.running,
            "total_models": len(models),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")


@router.get("/models/available")
async def get_available_models():
    """
    فقط مدل‌هایی که در حال حاضر کار می‌کنند
    """
    try:
        models = monitor.get_models_by_status('available')
        return {
            "total": len(models),
            "models": models
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available models: {str(e)}")


@router.get("/health")
async def health_check():
    """
    بررسی سلامت سیستم
    """
    return {
        "status": "healthy",
        "database": "connected",
        "agent_running": agent.running,
        "timestamp": datetime.now().isoformat()
    }

