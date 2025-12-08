#!/usr/bin/env python3
"""
Model Catalog API Router
API برای دسترسی به کاتالوگ مدل‌های AI
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Dict, Any, Optional
import sys
import os

# اضافه کردن مسیر root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.services.advanced_model_manager import get_model_manager, ModelInfo

router = APIRouter(prefix="/api/models", tags=["Model Catalog"])


@router.get("/catalog", response_model=List[Dict[str, Any]])
async def get_model_catalog(
    category: Optional[str] = Query(None, description="Filter by category"),
    size: Optional[str] = Query(None, description="Filter by size"),
    max_size_mb: Optional[int] = Query(None, description="Max size in MB"),
    language: Optional[str] = Query(None, description="Filter by language"),
    free_only: bool = Query(True, description="Free models only"),
    no_auth: bool = Query(True, description="No authentication required"),
    min_performance: float = Query(0.0, description="Minimum performance score"),
    limit: int = Query(100, description="Max results")
):
    """
    دریافت لیست مدل‌ها با فیلترهای مختلف
    
    ### مثال:
    ```
    GET /api/models/catalog?category=sentiment&max_size_mb=500&limit=10
    ```
    """
    manager = get_model_manager()
    
    models = manager.filter_models(
        category=category,
        size=size,
        max_size_mb=max_size_mb,
        language=language,
        free_only=free_only,
        no_auth=no_auth,
        min_performance=min_performance
    )
    
    # Convert to dict و محدود کردن به limit
    return [model.to_dict() for model in models[:limit]]


@router.get("/model/{model_id}", response_model=Dict[str, Any])
async def get_model_details(model_id: str):
    """
    دریافت جزئیات کامل یک مدل
    
    ### مثال:
    ```
    GET /api/models/model/cryptobert
    ```
    """
    manager = get_model_manager()
    model = manager.get_model_by_id(model_id)
    
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    return model.to_dict()


@router.get("/search")
async def search_models(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Max results")
):
    """
    جستجو در مدل‌ها
    
    ### مثال:
    ```
    GET /api/models/search?q=crypto&limit=5
    ```
    """
    manager = get_model_manager()
    results = manager.search_models(q)
    
    return {
        "query": q,
        "total": len(results),
        "results": [model.to_dict() for model in results[:limit]]
    }


@router.get("/best/{category}")
async def get_best_models(
    category: str,
    top_n: int = Query(3, description="Number of top models"),
    max_size_mb: Optional[int] = Query(None, description="Max size in MB")
):
    """
    دریافت بهترین مدل‌ها در یک category
    
    ### مثال:
    ```
    GET /api/models/best/sentiment?top_n=5&max_size_mb=500
    ```
    """
    manager = get_model_manager()
    
    try:
        models = manager.get_best_models(
            category=category,
            top_n=top_n,
            max_size_mb=max_size_mb
        )
        
        return {
            "category": category,
            "count": len(models),
            "models": [model.to_dict() for model in models]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/recommend")
async def recommend_models(
    use_case: str = Query(..., description="Use case (e.g., twitter, news, trading)"),
    max_models: int = Query(5, description="Max recommendations"),
    max_size_mb: Optional[int] = Query(None, description="Max size in MB")
):
    """
    توصیه مدل‌ها بر اساس use case
    
    ### مثال:
    ```
    GET /api/models/recommend?use_case=twitter&max_models=3
    ```
    """
    manager = get_model_manager()
    
    models = manager.recommend_models(
        use_case=use_case,
        max_models=max_models,
        max_size_mb=max_size_mb
    )
    
    return {
        "use_case": use_case,
        "count": len(models),
        "recommendations": [model.to_dict() for model in models]
    }


@router.get("/stats")
async def get_catalog_stats():
    """
    آمار کامل کاتالوگ مدل‌ها
    
    ### مثال:
    ```
    GET /api/models/stats
    ```
    """
    manager = get_model_manager()
    return manager.get_model_stats()


@router.get("/categories")
async def get_categories():
    """
    لیست categories با آمار
    
    ### مثال:
    ```
    GET /api/models/categories
    ```
    """
    manager = get_model_manager()
    return {
        "categories": manager.get_categories()
    }


@router.get("/ui", response_class=HTMLResponse)
async def model_catalog_ui():
    """
    رابط کاربری HTML برای مرور مدل‌ها
    """
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI Models Catalog</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .stats-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 40px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-card .value {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .stat-card .label {
            font-size: 0.9rem;
            color: #6c757d;
        }
        
        .filters {
            padding: 30px 40px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }
        
        .filter-row {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-bottom: 15px;
        }
        
        .filter-group {
            flex: 1;
            min-width: 200px;
        }
        
        .filter-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
            color: #495057;
        }
        
        .filter-group select,
        .filter-group input {
            width: 100%;
            padding: 10px 15px;
            border: 1px solid #ced4da;
            border-radius: 8px;
            font-size: 1rem;
        }
        
        .search-box {
            position: relative;
            flex: 2;
            min-width: 300px;
        }
        
        .search-box input {
            width: 100%;
            padding: 12px 45px 12px 15px;
            border: 2px solid #667eea;
            border-radius: 10px;
            font-size: 1rem;
        }
        
        .search-box button {
            position: absolute;
            right: 5px;
            top: 50%;
            transform: translateY(-50%);
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
        }
        
        .search-box button:hover {
            background: #5568d3;
        }
        
        .content {
            padding: 40px;
        }
        
        .models-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
        }
        
        .model-card {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 15px;
            padding: 25px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .model-card:hover {
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            transform: translateY(-5px);
            border-color: #667eea;
        }
        
        .model-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }
        
        .model-header {
            margin-bottom: 15px;
        }
        
        .model-name {
            font-size: 1.3rem;
            font-weight: bold;
            color: #212529;
            margin-bottom: 5px;
        }
        
        .model-id {
            font-size: 0.85rem;
            color: #6c757d;
            font-family: 'Courier New', monospace;
        }
        
        .model-description {
            color: #495057;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        
        .model-meta {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        
        .meta-item {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 0.9rem;
            color: #6c757d;
        }
        
        .meta-item .icon {
            font-size: 1.1rem;
        }
        
        .tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 15px;
        }
        
        .tag {
            background: #e7f0ff;
            color: #0056b3;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
        }
        
        .category-badge {
            background: #667eea;
            color: white;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        .performance-bar {
            margin-top: 15px;
        }
        
        .performance-label {
            font-size: 0.85rem;
            color: #6c757d;
            margin-bottom: 5px;
        }
        
        .progress-bar {
            height: 6px;
            background: #e9ecef;
            border-radius: 3px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 3px;
            transition: width 0.3s ease;
        }
        
        .model-actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .btn {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5568d3;
        }
        
        .btn-secondary {
            background: #f8f9fa;
            color: #495057;
            border: 1px solid #dee2e6;
        }
        
        .btn-secondary:hover {
            background: #e9ecef;
        }
        
        .loading {
            text-align: center;
            padding: 60px;
            color: #6c757d;
            font-size: 1.2rem;
        }
        
        .no-results {
            text-align: center;
            padding: 60px;
            color: #6c757d;
        }
        
        .no-results-icon {
            font-size: 4rem;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Models Catalog</h1>
            <p>Comprehensive catalog of 25+ AI models for crypto & finance</p>
        </div>
        
        <div class="stats-bar" id="stats-bar">
            <div class="stat-card">
                <div class="value" id="stat-total">-</div>
                <div class="label">Total Models</div>
            </div>
            <div class="stat-card">
                <div class="value" id="stat-free">-</div>
                <div class="label">Free Models</div>
            </div>
            <div class="stat-card">
                <div class="value" id="stat-api">-</div>
                <div class="label">API Compatible</div>
            </div>
            <div class="stat-card">
                <div class="value" id="stat-performance">-</div>
                <div class="label">Avg Performance</div>
            </div>
        </div>
        
        <div class="filters">
            <div class="filter-row">
                <div class="search-box">
                    <input type="text" id="search-input" placeholder="Search models by name, description, or tags...">
                    <button onclick="searchModels()">🔍 Search</button>
                </div>
            </div>
            <div class="filter-row">
                <div class="filter-group">
                    <label>Category</label>
                    <select id="filter-category" onchange="applyFilters()">
                        <option value="">All Categories</option>
                        <option value="sentiment">Sentiment</option>
                        <option value="generation">Generation</option>
                        <option value="trading">Trading</option>
                        <option value="summarization">Summarization</option>
                        <option value="ner">NER</option>
                        <option value="question_answering">Q&A</option>
                        <option value="classification">Classification</option>
                        <option value="embedding">Embedding</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Size</label>
                    <select id="filter-size" onchange="applyFilters()">
                        <option value="">All Sizes</option>
                        <option value="tiny">Tiny (&lt;100 MB)</option>
                        <option value="small">Small (100-500 MB)</option>
                        <option value="medium">Medium (500MB-1GB)</option>
                        <option value="large">Large (1-3GB)</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Max Size (MB)</label>
                    <input type="number" id="filter-max-size" placeholder="e.g., 500" onchange="applyFilters()">
                </div>
                <div class="filter-group">
                    <label>Min Performance</label>
                    <input type="number" id="filter-min-perf" placeholder="0.0-1.0" step="0.1" min="0" max="1" onchange="applyFilters()">
                </div>
            </div>
        </div>
        
        <div class="content">
            <div id="loading" class="loading">Loading models...</div>
            <div id="models-container" class="models-grid" style="display: none;"></div>
            <div id="no-results" class="no-results" style="display: none;">
                <div class="no-results-icon">🔍</div>
                <h2>No models found</h2>
                <p>Try adjusting your filters or search query</p>
            </div>
        </div>
    </div>
    
    <script>
        let allModels = [];
        
        // Load stats
        async function loadStats() {
            try {
                const response = await fetch('/api/models/stats');
                const stats = await response.json();
                
                document.getElementById('stat-total').textContent = stats.total_models;
                document.getElementById('stat-free').textContent = stats.free_models;
                document.getElementById('stat-api').textContent = stats.api_compatible;
                document.getElementById('stat-performance').textContent = stats.avg_performance.toFixed(2);
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        // Load models
        async function loadModels() {
            try {
                const response = await fetch('/api/models/catalog?limit=100');
                allModels = await response.json();
                
                document.getElementById('loading').style.display = 'none';
                displayModels(allModels);
            } catch (error) {
                console.error('Error loading models:', error);
                document.getElementById('loading').innerHTML = '❌ Error loading models';
            }
        }
        
        // Display models
        function displayModels(models) {
            const container = document.getElementById('models-container');
            
            if (models.length === 0) {
                container.style.display = 'none';
                document.getElementById('no-results').style.display = 'block';
                return;
            }
            
            document.getElementById('no-results').style.display = 'none';
            container.style.display = 'grid';
            
            container.innerHTML = models.map(model => `
                <div class="model-card">
                    <div class="model-header">
                        <div class="model-name">${model.name}</div>
                        <div class="model-id">${model.hf_id}</div>
                    </div>
                    
                    <div class="category-badge">${model.category}</div>
                    
                    <p class="model-description">${model.description}</p>
                    
                    <div class="model-meta">
                        <div class="meta-item">
                            <span class="icon">💾</span>
                            <span>${model.size_mb} MB</span>
                        </div>
                        <div class="meta-item">
                            <span class="icon">🌍</span>
                            <span>${model.languages.join(', ')}</span>
                        </div>
                        ${model.free ? '<div class="meta-item"><span class="icon">✅</span><span>Free</span></div>' : ''}
                        ${model.api_compatible ? '<div class="meta-item"><span class="icon">🔌</span><span>API</span></div>' : ''}
                    </div>
                    
                    <div class="tags">
                        ${model.tags.slice(0, 3).map(tag => `<span class="tag">${tag}</span>`).join('')}
                    </div>
                    
                    <div class="performance-bar">
                        <div class="performance-label">Performance: ${(model.performance_score * 100).toFixed(0)}%</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${model.performance_score * 100}%"></div>
                        </div>
                    </div>
                    
                    <div class="model-actions">
                        <button class="btn btn-primary" onclick="tryModel('${model.id}')">
                            Try Model
                        </button>
                        <button class="btn btn-secondary" onclick="viewDetails('${model.id}')">
                            Details
                        </button>
                    </div>
                </div>
            `).join('');
        }
        
        // Apply filters
        function applyFilters() {
            const category = document.getElementById('filter-category').value;
            const size = document.getElementById('filter-size').value;
            const maxSize = document.getElementById('filter-max-size').value;
            const minPerf = document.getElementById('filter-min-perf').value;
            
            let filtered = allModels;
            
            if (category) {
                filtered = filtered.filter(m => m.category === category);
            }
            
            if (size) {
                filtered = filtered.filter(m => m.size === size);
            }
            
            if (maxSize) {
                filtered = filtered.filter(m => m.size_mb <= parseInt(maxSize));
            }
            
            if (minPerf) {
                filtered = filtered.filter(m => m.performance_score >= parseFloat(minPerf));
            }
            
            displayModels(filtered);
        }
        
        // Search models
        async function searchModels() {
            const query = document.getElementById('search-input').value;
            
            if (!query) {
                displayModels(allModels);
                return;
            }
            
            try {
                const response = await fetch(`/api/models/search?q=${encodeURIComponent(query)}&limit=50`);
                const data = await response.json();
                displayModels(data.results);
            } catch (error) {
                console.error('Error searching:', error);
            }
        }
        
        // Try model
        function tryModel(modelId) {
            // Redirect to sentiment analysis page with model pre-selected
            window.location.href = `/api/ai/sentiment/quick?model=${modelId}`;
        }
        
        // View details
        async function viewDetails(modelId) {
            try {
                const response = await fetch(`/api/models/model/${modelId}`);
                const model = await response.json();
                
                alert(`
Model: ${model.name}
HuggingFace ID: ${model.hf_id}
Category: ${model.category}
Size: ${model.size_mb} MB
Description: ${model.description}
Use Cases: ${model.use_cases.join(', ')}
Performance: ${(model.performance_score * 100).toFixed(0)}%
Popularity: ${(model.popularity_score * 100).toFixed(0)}%
                `.trim());
            } catch (error) {
                console.error('Error loading details:', error);
            }
        }
        
        // Initialize
        window.addEventListener('DOMContentLoaded', () => {
            loadStats();
            loadModels();
        });
        
        // Enter key for search
        document.addEventListener('DOMContentLoaded', () => {
            document.getElementById('search-input').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    searchModels();
                }
            });
        });
    </script>
</body>
</html>
    """


# ===== Integration with production_server.py =====
"""
# در production_server.py:

from backend.routers.model_catalog import router as catalog_router

app = FastAPI()
app.include_router(catalog_router)

# حالا در دسترس است:
# - GET /api/models/catalog
# - GET /api/models/model/{model_id}
# - GET /api/models/search?q=...
# - GET /api/models/best/{category}
# - GET /api/models/recommend?use_case=...
# - GET /api/models/stats
# - GET /api/models/categories
# - GET /api/models/ui (صفحه HTML)
"""
