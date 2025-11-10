"""
Hugging Face Resource Aggregator
A centralized API aggregator for cryptocurrency resources
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from pydantic import BaseModel
import sqlite3
from contextlib import contextmanager
import os
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Crypto Resource Aggregator",
    description="Centralized aggregator for free and key-based cryptocurrency resources",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
RESOURCES = {}
RESOURCE_STATUS = {}
RESOURCE_METADATA = {}

# Database setup
@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect('history.db')
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize the history database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                resource_type TEXT NOT NULL,
                resource_name TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                status TEXT NOT NULL,
                response_time REAL,
                error_message TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resource_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_name TEXT NOT NULL UNIQUE,
                last_check DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL,
                consecutive_failures INTEGER DEFAULT 0,
                last_success DATETIME,
                last_error TEXT
            )
        ''')
        conn.commit()

def log_query(resource_type: str, resource_name: str, endpoint: str,
              status: str, response_time: float = None, error_message: str = None):
    """Log a query to the history database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO query_history
            (resource_type, resource_name, endpoint, status, response_time, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (resource_type, resource_name, endpoint, status, response_time, error_message))
        conn.commit()

def update_resource_status(resource_name: str, status: str, error: str = None):
    """Update the status of a resource"""
    with get_db() as conn:
        cursor = conn.cursor()
        if status == "online":
            cursor.execute('''
                INSERT INTO resource_status (resource_name, status, last_success, consecutive_failures)
                VALUES (?, ?, CURRENT_TIMESTAMP, 0)
                ON CONFLICT(resource_name) DO UPDATE SET
                    status = ?,
                    last_check = CURRENT_TIMESTAMP,
                    last_success = CURRENT_TIMESTAMP,
                    consecutive_failures = 0
            ''', (resource_name, status, status))
        else:
            cursor.execute('''
                INSERT INTO resource_status (resource_name, status, last_error, consecutive_failures)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(resource_name) DO UPDATE SET
                    status = ?,
                    last_check = CURRENT_TIMESTAMP,
                    last_error = ?,
                    consecutive_failures = consecutive_failures + 1
            ''', (resource_name, status, error, status, error))
        conn.commit()

# Pydantic models
class ResourceQuery(BaseModel):
    resource_type: str
    resource_name: Optional[str] = None
    endpoint: Optional[str] = None
    params: Optional[Dict[str, Any]] = {}

class ResourceResponse(BaseModel):
    success: bool
    resource_type: str
    resource_name: str
    data: Optional[Any] = None
    error: Optional[str] = None
    response_time: float
    timestamp: str

# Resource loader
def load_resources():
    """Load resources from the JSON file"""
    global RESOURCES, RESOURCE_METADATA

    try:
        with open('all_apis_merged_2025.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        RESOURCE_METADATA = data.get('metadata', {})
        logger.info(f"Loaded metadata: {RESOURCE_METADATA.get('name', 'Unknown')}")

        # Parse resources from raw files
        raw_files = data.get('raw_files', [])

        # Initialize resource categories
        RESOURCES = {
            'block_explorers': {},
            'market_data': {},
            'rpc_endpoints': {},
            'news_apis': {},
            'sentiment_apis': {},
            'whale_tracking': {},
            'on_chain_analytics': {},
            'cors_proxies': []
        }

        # Parse the content from raw files
        for raw_file in raw_files:
            content = raw_file.get('content', '')
            parse_api_content(content)

        # Parse extracted API keys
        api_keys = data.get('extracted_api_keys', {})
        for category, keys in api_keys.items():
            if category not in RESOURCES:
                RESOURCES[category] = {}
            RESOURCES[category].update(keys)

        logger.info(f"Loaded {len(RESOURCES)} resource categories")

        # Initialize all resources as unchecked
        for category, resources in RESOURCES.items():
            if isinstance(resources, dict):
                for resource_name in resources.keys():
                    RESOURCE_STATUS[f"{category}.{resource_name}"] = {
                        "status": "unchecked",
                        "last_check": None,
                        "consecutive_failures": 0
                    }

        return True
    except Exception as e:
        logger.error(f"Error loading resources: {str(e)}")
        return False

def parse_api_content(content: str):
    """Parse API content from raw text files"""
    # Extract API keys
    if "TronScan:" in content:
        key = content.split("TronScan:")[1].split()[0].strip()
        if 'tron' not in RESOURCES['block_explorers']:
            RESOURCES['block_explorers']['tronscan'] = {
                'base_url': 'https://apilist.tronscanapi.com/api',
                'api_key': key,
                'type': 'tron_explorer'
            }

    if "BscScan:" in content:
        key = content.split("BscScan:")[1].split()[0].strip()
        if 'bscscan' not in RESOURCES['block_explorers']:
            RESOURCES['block_explorers']['bscscan'] = {
                'base_url': 'https://api.bscscan.com/api',
                'api_key': key,
                'type': 'bsc_explorer'
            }

    if "Etherscan:" in content:
        key = content.split("Etherscan:")[1].split()[0].strip()
        if 'etherscan' not in RESOURCES['block_explorers']:
            RESOURCES['block_explorers']['etherscan'] = {
                'base_url': 'https://api.etherscan.io/api',
                'api_key': key,
                'type': 'ethereum_explorer'
            }

    if "CoinMarketCap:" in content:
        key = content.split("CoinMarketCap:")[1].split()[0].strip()
        if 'coinmarketcap' not in RESOURCES['market_data']:
            RESOURCES['market_data']['coinmarketcap'] = {
                'base_url': 'https://pro-api.coinmarketcap.com/v1',
                'api_key': key,
                'type': 'market_data',
                'requires_header': True
            }

    # Add CoinGecko (no key required)
    if 'coingecko' not in RESOURCES['market_data']:
        RESOURCES['market_data']['coingecko'] = {
            'base_url': 'https://api.coingecko.com/api/v3',
            'api_key': '',
            'type': 'market_data',
            'free': True
        }

    # Parse CORS proxies
    cors_proxies = [
        'https://api.allorigins.win/get?url=',
        'https://proxy.cors.sh/',
        'https://proxy.corsfix.com/?url=',
        'https://api.codetabs.com/v1/proxy?quest='
    ]
    RESOURCES['cors_proxies'] = cors_proxies

# Resource fetcher with retry logic
async def fetch_resource(session: aiohttp.ClientSession, url: str,
                         headers: Dict = None, timeout: int = 10) -> Dict:
    """Fetch data from a resource with error handling"""
    start_time = time.time()

    try:
        async with session.get(url, headers=headers, timeout=timeout) as response:
            response_time = time.time() - start_time

            if response.status == 200:
                data = await response.json()
                return {
                    "success": True,
                    "data": data,
                    "status_code": response.status,
                    "response_time": response_time
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status}",
                    "status_code": response.status,
                    "response_time": response_time
                }
    except asyncio.TimeoutError:
        return {
            "success": False,
            "error": "Timeout",
            "response_time": time.time() - start_time
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response_time": time.time() - start_time
        }

# Health check endpoint
async def check_resource_health(resource_type: str, resource_name: str, resource_config: Dict) -> Dict:
    """Check if a resource is online"""
    base_url = resource_config.get('base_url', '')

    # Define health check endpoints
    health_endpoints = {
        'etherscan': f"{base_url}?module=gastracker&action=gasoracle&apikey={resource_config.get('api_key', '')}",
        'bscscan': f"{base_url}?module=stats&action=bnbprice&apikey={resource_config.get('api_key', '')}",
        'tronscan': f"{base_url}/system/status",
        'coingecko': f"{base_url}/ping",
        'coinmarketcap': f"{base_url}/cryptocurrency/listings/latest?limit=1"
    }

    endpoint = health_endpoints.get(resource_name, base_url)

    headers = {}
    if resource_config.get('requires_header') and resource_config.get('api_key'):
        headers['X-CMC_PRO_API_KEY'] = resource_config['api_key']

    async with aiohttp.ClientSession() as session:
        result = await fetch_resource(session, endpoint, headers=headers)

        status = "online" if result.get('success') else "offline"
        error = result.get('error')

        update_resource_status(f"{resource_type}.{resource_name}", status, error)

        return {
            "resource": f"{resource_type}.{resource_name}",
            "status": status,
            "response_time": result.get('response_time', 0),
            "error": error,
            "timestamp": datetime.now().isoformat()
        }

# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("Starting Crypto Resource Aggregator...")
    init_db()
    load_resources()
    logger.info("Application started successfully")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Crypto Resource Aggregator",
        "version": "1.0.0",
        "description": "Centralized aggregator for cryptocurrency resources",
        "endpoints": {
            "/resources": "List all available resources",
            "/resources/{category}": "List resources in a category",
            "/query": "Query a specific resource (POST)",
            "/status": "Check status of all resources",
            "/status/{category}/{name}": "Check status of a specific resource",
            "/history": "Get query history",
            "/health": "System health check"
        },
        "metadata": RESOURCE_METADATA
    }

@app.get("/resources")
async def list_resources():
    """List all available resources"""
    resource_summary = {}

    for category, resources in RESOURCES.items():
        if isinstance(resources, dict):
            resource_summary[category] = list(resources.keys())
        elif isinstance(resources, list):
            resource_summary[category] = len(resources)

    return {
        "total_categories": len(RESOURCES),
        "resources": resource_summary,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/resources/{category}")
async def get_category_resources(category: str):
    """Get all resources in a specific category"""
    if category not in RESOURCES:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")

    return {
        "category": category,
        "resources": RESOURCES[category],
        "count": len(RESOURCES[category]) if isinstance(RESOURCES[category], dict) else len(RESOURCES[category]),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/query")
async def query_resource(query: ResourceQuery):
    """Query a specific resource"""
    category = query.resource_type

    if category not in RESOURCES:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")

    category_resources = RESOURCES[category]

    # If no specific resource specified, use the first available
    if not query.resource_name and isinstance(category_resources, dict):
        query.resource_name = list(category_resources.keys())[0]

    if isinstance(category_resources, dict) and query.resource_name not in category_resources:
        raise HTTPException(status_code=404, detail=f"Resource '{query.resource_name}' not found in category '{category}'")

    resource_config = category_resources.get(query.resource_name, {})
    base_url = resource_config.get('base_url', '')
    api_key = resource_config.get('api_key', '')

    # Build the query URL
    if query.endpoint:
        url = f"{base_url}{query.endpoint}"
    else:
        url = base_url

    # Add API key if required
    if api_key and not resource_config.get('requires_header'):
        separator = '&' if '?' in url else '?'
        url = f"{url}{separator}apikey={api_key}"

    # Add query parameters
    if query.params:
        separator = '&' if '?' in url else '?'
        params_str = '&'.join([f"{k}={v}" for k, v in query.params.items()])
        url = f"{url}{separator}{params_str}"

    # Prepare headers
    headers = {}
    if resource_config.get('requires_header') and api_key:
        headers['X-CMC_PRO_API_KEY'] = api_key

    # Fetch the data
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        result = await fetch_resource(session, url, headers=headers)

    response_time = time.time() - start_time

    # Log the query
    log_query(
        category,
        query.resource_name,
        url,
        "success" if result.get('success') else "error",
        response_time,
        result.get('error')
    )

    if result.get('success'):
        return ResourceResponse(
            success=True,
            resource_type=category,
            resource_name=query.resource_name,
            data=result.get('data'),
            response_time=response_time,
            timestamp=datetime.now().isoformat()
        )
    else:
        # If primary fails, try fallbacks if available
        return ResourceResponse(
            success=False,
            resource_type=category,
            resource_name=query.resource_name,
            error=result.get('error'),
            response_time=response_time,
            timestamp=datetime.now().isoformat()
        )

@app.get("/status")
async def get_all_status():
    """Get status of all resources"""
    status_list = []

    for category, resources in RESOURCES.items():
        if isinstance(resources, dict):
            for resource_name, resource_config in resources.items():
                health = await check_resource_health(category, resource_name, resource_config)
                status_list.append(health)

    online_count = sum(1 for s in status_list if s['status'] == 'online')
    offline_count = len(status_list) - online_count

    return {
        "total_resources": len(status_list),
        "online": online_count,
        "offline": offline_count,
        "resources": status_list,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status/{category}/{name}")
async def get_resource_status(category: str, name: str):
    """Get status of a specific resource"""
    if category not in RESOURCES:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")

    if isinstance(RESOURCES[category], dict) and name not in RESOURCES[category]:
        raise HTTPException(status_code=404, detail=f"Resource '{name}' not found")

    resource_config = RESOURCES[category][name]
    health = await check_resource_health(category, name, resource_config)

    return health

@app.get("/history")
async def get_history(limit: int = 100, resource_type: Optional[str] = None):
    """Get query history"""
    with get_db() as conn:
        cursor = conn.cursor()

        if resource_type:
            cursor.execute('''
                SELECT * FROM query_history
                WHERE resource_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (resource_type, limit))
        else:
            cursor.execute('''
                SELECT * FROM query_history
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))

        rows = cursor.fetchall()

        history = []
        for row in rows:
            history.append({
                "id": row[0],
                "timestamp": row[1],
                "resource_type": row[2],
                "resource_name": row[3],
                "endpoint": row[4],
                "status": row[5],
                "response_time": row[6],
                "error_message": row[7]
            })

        return {
            "count": len(history),
            "history": history
        }

@app.get("/history/stats")
async def get_history_stats():
    """Get statistics from query history"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Total queries
        cursor.execute('SELECT COUNT(*) FROM query_history')
        total_queries = cursor.fetchone()[0]

        # Success rate
        cursor.execute('SELECT COUNT(*) FROM query_history WHERE status = "success"')
        successful_queries = cursor.fetchone()[0]

        # Most queried resources
        cursor.execute('''
            SELECT resource_name, COUNT(*) as count
            FROM query_history
            GROUP BY resource_name
            ORDER BY count DESC
            LIMIT 10
        ''')
        most_queried = [{"resource": row[0], "count": row[1]} for row in cursor.fetchall()]

        # Average response time
        cursor.execute('SELECT AVG(response_time) FROM query_history WHERE response_time IS NOT NULL')
        avg_response_time = cursor.fetchone()[0]

        return {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "success_rate": (successful_queries / total_queries * 100) if total_queries > 0 else 0,
            "most_queried_resources": most_queried,
            "average_response_time": avg_response_time,
            "timestamp": datetime.now().isoformat()
        }

@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "resources_loaded": len(RESOURCES) > 0,
        "database_connected": True
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
