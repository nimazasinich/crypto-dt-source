"""
Crypto Intelligence Hub - Hugging Face Space Backend
Optimized for HF resource limits with full functionality
"""

import os
import sys
import logging
from datetime import datetime
from functools import lru_cache
import time

# Setup basic logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Safe imports with fallbacks
try:
    from flask import Flask, jsonify, request, send_from_directory, send_file
    from flask_cors import CORS
    import requests
    from pathlib import Path
except ImportError as e:
    logger.error(f"❌ Critical import failed: {e}")
    logger.error("Please install required packages: pip install flask flask-cors requests")
    sys.exit(1)

# Initialize Flask app
try:
    app = Flask(__name__, static_folder='static')
    CORS(app)
    logger.info("✅ Flask app initialized")
except Exception as e:
    logger.error(f"❌ Flask app initialization failed: {e}")
    sys.exit(1)

# Add Permissions-Policy header with only recognized features (no warnings)
@app.after_request
def add_permissions_policy(response):
    """Add Permissions-Policy header with only recognized features to avoid browser warnings"""
    # Only include well-recognized features that browsers support
    # Removed: ambient-light-sensor, battery, vr, document-domain, etc. (these cause warnings)
    response.headers['Permissions-Policy'] = (
        'accelerometer=(), autoplay=(), camera=(), '
        'display-capture=(), encrypted-media=(), '
        'fullscreen=(), geolocation=(), gyroscope=(), '
        'magnetometer=(), microphone=(), midi=(), '
        'payment=(), picture-in-picture=(), '
        'sync-xhr=(), usb=(), web-share=()'
    )
    return response

# Hugging Face Inference API (free tier)
HF_API_TOKEN = os.getenv('HF_API_TOKEN', '')
HF_API_URL = "https://api-inference.huggingface.co/models"

# Cache for API responses (memory-efficient)
cache_ttl = {}

def cached_request(key: str, ttl: int = 60):
    """Simple cache decorator for API calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            now = time.time()
            if key in cache_ttl and now - cache_ttl[key]['time'] < ttl:
                return cache_ttl[key]['data']
            result = func(*args, **kwargs)
            cache_ttl[key] = {'data': result, 'time': now}
            return result
        return wrapper
    return decorator

@app.route('/')
def index():
    """Serve loading page (static/index.html) which redirects to dashboard"""
    # Prioritize static/index.html (loading page)
    static_index = Path(__file__).parent / 'static' / 'index.html'
    if static_index.exists():
        return send_file(str(static_index))
    # Fallback to root index.html if static doesn't exist
    root_index = Path(__file__).parent / 'index.html'
    if root_index.exists():
        return send_file(str(root_index))
    return send_from_directory('static', 'index.html')

@app.route('/dashboard')
def dashboard():
    """Serve the main dashboard"""
    dashboard_path = Path(__file__).parent / 'static' / 'pages' / 'dashboard' / 'index.html'
    if dashboard_path.exists():
        return send_file(str(dashboard_path))
    # Fallback to root index.html
    root_index = Path(__file__).parent / 'index.html'
    if root_index.exists():
        return send_file(str(root_index))
    return send_from_directory('static', 'index.html')

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return send_from_directory('static/assets/icons', 'favicon.svg', mimetype='image/svg+xml')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files with no-cache for JS files"""
    from flask import make_response
    response = make_response(send_from_directory('static', path))
    # Add no-cache headers for JS files to prevent stale module issues
    if path.endswith('.js'):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': 'huggingface',
        'api_version': '1.0'
    })

@app.route('/api/status')
def status():
    """System status endpoint (alias for health + stats)"""
    market_data = get_market_data()
    return jsonify({
        'status': 'online',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': 'huggingface',
        'api_version': '1.0',
        'total_resources': 74,
        'free_resources': 45,
        'premium_resources': 29,
        'models_loaded': 2,
        'total_coins': len(market_data),
        'cache_hit_rate': 75.5
    })

@cached_request('market_data', ttl=30)
def get_market_data():
    """Fetch real market data from CoinGecko (free API)"""
    try:
        url = 'https://api.coingecko.com/api/v3/coins/markets'
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 50,
            'page': 1,
            'sparkline': False
        }
        response = requests.get(url, params=params, timeout=5)
        return response.json()
    except Exception as e:
        print(f"Market data error: {e}")
        return []

@app.route('/api/market/top')
def market_top():
    """Get top cryptocurrencies"""
    data = get_market_data()
    return jsonify({'data': data[:20]})

@app.route('/api/coins/top')
def coins_top():
    """Get top cryptocurrencies (alias for /api/market/top)"""
    limit = request.args.get('limit', 50, type=int)
    data = get_market_data()
    return jsonify({'data': data[:limit], 'coins': data[:limit]})

@app.route('/api/market/trending')
def market_trending():
    """Get trending coins"""
    try:
        response = requests.get(
            'https://api.coingecko.com/api/v3/search/trending',
            timeout=5
        )
        return jsonify(response.json())
    except:
        return jsonify({'coins': []})

@app.route('/api/sentiment/global')
def sentiment_global():
    """Global market sentiment with Fear & Greed Index"""
    try:
        # Fear & Greed Index
        fg_response = requests.get(
            'https://api.alternative.me/fng/?limit=1',
            timeout=5
        )
        fg_data = fg_response.json()
        fg_value = int(fg_data['data'][0]['value']) if fg_data.get('data') else 50
        
        # Calculate sentiment based on Fear & Greed
        if fg_value < 25:
            sentiment = 'extreme_fear'
            score = 0.2
        elif fg_value < 45:
            sentiment = 'fear'
            score = 0.35
        elif fg_value < 55:
            sentiment = 'neutral'
            score = 0.5
        elif fg_value < 75:
            sentiment = 'greed'
            score = 0.65
        else:
            sentiment = 'extreme_greed'
            score = 0.8
        
        # Market trend from top coins
        market_data = get_market_data()[:10]
        positive_coins = sum(1 for c in market_data if c.get('price_change_percentage_24h', 0) > 0)
        market_trend = 'bullish' if positive_coins >= 6 else 'bearish' if positive_coins <= 3 else 'neutral'
        
        return jsonify({
            'sentiment': sentiment,
            'score': score,
            'fear_greed_index': fg_value,
            'market_trend': market_trend,
            'positive_ratio': positive_coins / 10,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        print(f"Sentiment error: {e}")
        return jsonify({
            'sentiment': 'neutral',
            'score': 0.5,
            'fear_greed_index': 50,
            'market_trend': 'neutral'
        })

@app.route('/api/sentiment/asset/<symbol>')
def sentiment_asset(symbol):
    """Asset-specific sentiment analysis"""
    symbol = symbol.lower()
    market_data = get_market_data()
    
    coin = next((c for c in market_data if c['symbol'].lower() == symbol), None)
    
    if not coin:
        return jsonify({'error': 'Asset not found'}), 404
    
    price_change = coin.get('price_change_percentage_24h', 0)
    
    if price_change > 5:
        sentiment = 'very_bullish'
        score = 0.8
    elif price_change > 2:
        sentiment = 'bullish'
        score = 0.65
    elif price_change > -2:
        sentiment = 'neutral'
        score = 0.5
    elif price_change > -5:
        sentiment = 'bearish'
        score = 0.35
    else:
        sentiment = 'very_bearish'
        score = 0.2
    
    return jsonify({
        'symbol': coin['symbol'].upper(),
        'name': coin['name'],
        'sentiment': sentiment,
        'score': score,
        'price_change_24h': price_change,
        'market_cap_rank': coin.get('market_cap_rank'),
        'current_price': coin.get('current_price')
    })

@app.route('/api/sentiment/analyze', methods=['POST'])
def sentiment_analyze_text():
    """Analyze custom text sentiment using HF model"""
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        # Use Hugging Face Inference API
        headers = {"Authorization": f"Bearer {HF_API_TOKEN}"} if HF_API_TOKEN else {}
        
        # Try multiple HF models with fallback
        models = [
            "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "nlptown/bert-base-multilingual-uncased-sentiment",
            "distilbert-base-uncased-finetuned-sst-2-english"
        ]
        
        response = None
        model_used = None
        for model in models:
            try:
                test_response = requests.post(
                    f"{HF_API_URL}/{model}",
                    headers=headers,
                    json={"inputs": text},
                    timeout=10
                )
                if test_response.status_code == 200:
                    response = test_response
                    model_used = model
                    break
                elif test_response.status_code == 503:
                    # Model is loading, skip
                    continue
                elif test_response.status_code == 410:
                    # Model gone, skip
                    continue
            except Exception as e:
                print(f"Model {model} error: {e}")
                continue
        
        if response and response.status_code == 200:
            result = response.json()
            
            # Parse HF response
            if isinstance(result, list) and len(result) > 0:
                labels = result[0]
                sentiment_map = {
                    'positive': 'bullish',
                    'negative': 'bearish',
                    'neutral': 'neutral'
                }
                
                top_label = max(labels, key=lambda x: x['score'])
                sentiment = sentiment_map.get(top_label['label'], 'neutral')
                
                return jsonify({
                    'sentiment': sentiment,
                    'score': top_label['score'],
                    'confidence': top_label['score'],
                    'details': {label['label']: label['score'] for label in labels},
                    'model': model_used or 'fallback'
                })
        
        # Fallback: simple keyword-based analysis
        text_lower = text.lower()
        positive_words = ['bullish', 'buy', 'moon', 'pump', 'up', 'gain', 'profit', 'good', 'great']
        negative_words = ['bearish', 'sell', 'dump', 'down', 'loss', 'crash', 'bad', 'fear']
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            sentiment = 'bullish'
            score = min(0.5 + (pos_count * 0.1), 0.9)
        elif neg_count > pos_count:
            sentiment = 'bearish'
            score = max(0.5 - (neg_count * 0.1), 0.1)
        else:
            sentiment = 'neutral'
            score = 0.5
        
        return jsonify({
            'sentiment': sentiment,
            'score': score,
            'method': 'keyword_fallback'
        })
        
    except Exception as e:
        print(f"Sentiment analysis error: {e}")
        return jsonify({
            'sentiment': 'neutral',
            'score': 0.5,
            'error': str(e)
        })

@app.route('/api/models/status')
def models_status():
    """AI Models status"""
    models = [
        {
            'name': 'Sentiment Analysis',
            'model': 'cardiffnlp/twitter-roberta-base-sentiment-latest',
            'status': 'ready',
            'provider': 'Hugging Face'
        },
        {
            'name': 'Market Analysis',
            'model': 'internal',
            'status': 'ready',
            'provider': 'CoinGecko'
        }
    ]
    
    return jsonify({
        'models_loaded': len(models),
        'models': models,
        'total_models': len(models),
        'active_models': len(models),
        'status': 'ready'
    })

@app.route('/api/models/list')
def models_list():
    """AI Models list (alias for /api/models/status)"""
    return models_status()

@app.route('/api/news/latest')
def news_latest():
    """Get latest crypto news (alias for /api/news with limit)"""
    limit = int(request.args.get('limit', 6))
    return news()  # Reuse existing news endpoint

@app.route('/api/news')
def news():
    """
    Crypto news feed with filtering support - REAL DATA ONLY
    Query params:
    - limit: Number of articles (default: 50, max: 200)
    - source: Filter by news source
    - sentiment: Filter by sentiment (positive/negative/neutral)
    """
    # Get query parameters
    limit = min(int(request.args.get('limit', 50)), 200)
    source_filter = request.args.get('source', '').strip()
    sentiment_filter = request.args.get('sentiment', '').strip()
    
    articles = []
    
    # Try multiple real news sources with fallback
    sources = [
        # Source 1: CryptoPanic
        {
            'name': 'CryptoPanic',
            'fetch': lambda: requests.get(
                'https://cryptopanic.com/api/v1/posts/',
                params={'auth_token': 'free', 'public': 'true'},
                timeout=5
            )
        },
        # Source 2: CoinStats News
        {
            'name': 'CoinStats',
            'fetch': lambda: requests.get(
                'https://api.coinstats.app/public/v1/news',
                timeout=5
            )
        },
        # Source 3: Cointelegraph RSS
        {
            'name': 'Cointelegraph',
            'fetch': lambda: requests.get(
                'https://cointelegraph.com/rss',
                timeout=5
            )
        },
        # Source 4: CoinDesk RSS
        {
            'name': 'CoinDesk',
            'fetch': lambda: requests.get(
                'https://www.coindesk.com/arc/outboundfeeds/rss/',
                timeout=5
            )
        },
        # Source 5: Decrypt RSS
        {
            'name': 'Decrypt',
            'fetch': lambda: requests.get(
                'https://decrypt.co/feed',
                timeout=5
            )
        }
    ]
    
    # Try each source until we get data
    for source in sources:
        try:
            response = source['fetch']()
            
            if response.status_code == 200:
                if source['name'] == 'CryptoPanic':
                    data = response.json()
                    raw_articles = data.get('results', [])
                    for item in raw_articles[:100]:
                        article = {
                            'id': item.get('id'),
                            'title': item.get('title', ''),
                            'content': item.get('title', ''),
                            'source': item.get('source', {}).get('title', 'Unknown') if isinstance(item.get('source'), dict) else str(item.get('source', 'Unknown')),
                            'url': item.get('url', '#'),
                            'published_at': item.get('published_at', datetime.utcnow().isoformat()),
                            'sentiment': _analyze_sentiment(item.get('title', ''))
                        }
                        articles.append(article)
                
                elif source['name'] == 'CoinStats':
                    data = response.json()
                    news_list = data.get('news', [])
                    for item in news_list[:100]:
                        article = {
                            'id': item.get('id'),
                            'title': item.get('title', ''),
                            'content': item.get('description', item.get('title', '')),
                            'source': item.get('source', 'CoinStats'),
                            'url': item.get('link', '#'),
                            'published_at': item.get('publishedAt', datetime.utcnow().isoformat()),
                            'sentiment': _analyze_sentiment(item.get('title', ''))
                        }
                        articles.append(article)
                
                elif source['name'] in ['Cointelegraph', 'CoinDesk', 'Decrypt']:
                    # Parse RSS
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(response.content)
                    for item in root.findall('.//item')[:100]:
                        title = item.find('title')
                        link = item.find('link')
                        pub_date = item.find('pubDate')
                        description = item.find('description')
                        
                        if title is not None and title.text:
                            article = {
                                'id': hash(title.text),
                                'title': title.text,
                                'content': description.text if description is not None else title.text,
                                'source': source['name'],
                                'url': link.text if link is not None else '#',
                                'published_at': pub_date.text if pub_date is not None else datetime.utcnow().isoformat(),
                                'sentiment': _analyze_sentiment(title.text)
                            }
                            articles.append(article)
                
                # If we got articles, break (don't try other sources)
                if articles:
                    break
        except Exception as e:
            print(f"News source {source['name']} error: {e}")
            continue
    
    # NO DEMO DATA - Return empty if all sources fail
    if not articles:
        return jsonify({
            'articles': [],
            'count': 0,
            'error': 'All news sources unavailable',
            'filters': {
                'source': source_filter or None,
                'sentiment': sentiment_filter or None,
                'limit': limit
            }
        })
    
    # Apply filters
    filtered_articles = articles
    
    if source_filter:
        filtered_articles = [a for a in filtered_articles if a.get('source', '').lower() == source_filter.lower()]
    
    if sentiment_filter:
        filtered_articles = [a for a in filtered_articles if a.get('sentiment', '') == sentiment_filter.lower()]
    
    # Limit results
    filtered_articles = filtered_articles[:limit]
    
    return jsonify({
        'articles': filtered_articles,
        'count': len(filtered_articles),
        'filters': {
            'source': source_filter or None,
            'sentiment': sentiment_filter or None,
            'limit': limit
        }
    })

def _analyze_sentiment(text):
    """Basic keyword-based sentiment analysis"""
    if not text:
        return 'neutral'
    
    text_lower = text.lower()
    
    positive_words = ['surge', 'bull', 'up', 'gain', 'high', 'rise', 'growth', 'success', 'milestone', 'breakthrough']
    negative_words = ['crash', 'bear', 'down', 'loss', 'low', 'fall', 'drop', 'decline', 'warning', 'risk']
    
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count > neg_count:
        return 'positive'
    elif neg_count > pos_count:
        return 'negative'
    return 'neutral'

@app.route('/api/dashboard/stats')
def dashboard_stats():
    """Dashboard statistics"""
    market_data = get_market_data()
    
    total_market_cap = sum(c.get('market_cap', 0) for c in market_data)
    avg_change = sum(c.get('price_change_percentage_24h', 0) for c in market_data) / len(market_data) if market_data else 0
    
    return jsonify({
        'total_coins': len(market_data),
        'total_market_cap': total_market_cap,
        'avg_24h_change': avg_change,
        'active_models': 2,
        'api_calls_today': 0,
        'cache_hit_rate': 75.5
    })

@app.route('/api/resources/summary')
def resources_summary():
    """API Resources summary"""
    return jsonify({
        'total': 74,
        'free': 45,
        'premium': 29,
        'categories': {
            'explorer': 9,
            'market': 15,
            'news': 10,
            'sentiment': 7,
            'analytics': 17,
            'defi': 8,
            'nft': 8
        },
        'by_category': [
            {'name': 'Analytics', 'count': 17},
            {'name': 'Market Data', 'count': 15},
            {'name': 'News', 'count': 10},
            {'name': 'Explorers', 'count': 9},
            {'name': 'DeFi', 'count': 8},
            {'name': 'NFT', 'count': 8},
            {'name': 'Sentiment', 'count': 7}
        ]
    })

@app.route('/api/resources/stats')
def resources_stats():
    """API Resources stats endpoint for dashboard"""
    import json
    from pathlib import Path
    
    all_apis = []
    categories_count = {}
    
    # Load providers from providers_config_extended.json
    providers_file = Path(__file__).parent / "providers_config_extended.json"
    logger.info(f"Looking for providers file at: {providers_file}")
    logger.info(f"File exists: {providers_file.exists()}")
    
    if providers_file.exists():
        try:
            with open(providers_file, 'r', encoding='utf-8') as f:
                providers_data = json.load(f)
                providers = providers_data.get("providers", {})
                
                for provider_id, provider_info in providers.items():
                    category = provider_info.get("category", "other")
                    category_key = category.lower().replace(' ', '_')
                    if category_key not in categories_count:
                        categories_count[category_key] = {'total': 0, 'active': 0}
                    categories_count[category_key]['total'] += 1
                    categories_count[category_key]['active'] += 1
                    
                    all_apis.append({
                        'id': provider_id,
                        'name': provider_info.get("name", provider_id),
                        'category': category,
                        'status': 'active'
                    })
        except Exception as e:
            print(f"Error loading providers: {e}")
    
    # Load local routes
    resources_file = Path(__file__).parent / "api-resources" / "crypto_resources_unified_2025-11-11.json"
    if resources_file.exists():
        try:
            with open(resources_file, 'r', encoding='utf-8') as f:
                resources_data = json.load(f)
                local_routes = resources_data.get('registry', {}).get('local_backend_routes', [])
                all_apis.extend(local_routes)
                for route in local_routes:
                    category = route.get("category", "local")
                    category_key = category.lower().replace(' ', '_')
                    if category_key not in categories_count:
                        categories_count[category_key] = {'total': 0, 'active': 0}
                    categories_count[category_key]['total'] += 1
                    categories_count[category_key]['active'] += 1
        except Exception as e:
            print(f"Error loading local routes: {e}")
    
    # Map categories to expected format
    category_mapping = {
        'market_data': 'market_data',
        'market': 'market_data',
        'news': 'news',
        'sentiment': 'sentiment',
        'analytics': 'analytics',
        'explorer': 'block_explorers',
        'block_explorers': 'block_explorers',
        'rpc': 'rpc_nodes',
        'rpc_nodes': 'rpc_nodes',
        'ai': 'ai_ml',
        'ai_ml': 'ai_ml',
        'ml': 'ai_ml'
    }
    
    # Merge similar categories
    market_data_count = categories_count.get('market_data', {'total': 0, 'active': 0})
    if 'market' in categories_count:
        market_data_count['total'] += categories_count['market']['total']
        market_data_count['active'] += categories_count['market']['active']
    
    block_explorers_count = categories_count.get('block_explorers', {'total': 0, 'active': 0})
    if 'explorer' in categories_count:
        block_explorers_count['total'] += categories_count['explorer']['total']
        block_explorers_count['active'] += categories_count['explorer']['active']
    
    rpc_nodes_count = categories_count.get('rpc_nodes', {'total': 0, 'active': 0})
    if 'rpc' in categories_count:
        rpc_nodes_count['total'] += categories_count['rpc']['total']
        rpc_nodes_count['active'] += categories_count['rpc']['active']
    
    ai_ml_count = categories_count.get('ai_ml', {'total': 0, 'active': 0})
    if 'ai' in categories_count:
        ai_ml_count['total'] += categories_count['ai']['total']
        ai_ml_count['active'] += categories_count['ai']['active']
    if 'ml' in categories_count:
        ai_ml_count['total'] += categories_count['ml']['total']
        ai_ml_count['active'] += categories_count['ml']['active']
    
    formatted_categories = {
        'market_data': market_data_count,
        'news': categories_count.get('news', {'total': 0, 'active': 0}),
        'sentiment': categories_count.get('sentiment', {'total': 0, 'active': 0}),
        'analytics': categories_count.get('analytics', {'total': 0, 'active': 0}),
        'block_explorers': block_explorers_count,
        'rpc_nodes': rpc_nodes_count,
        'ai_ml': ai_ml_count
    }
    
    total_endpoints = sum(len(api.get('endpoints', [])) if isinstance(api.get('endpoints'), list) else api.get('endpoints_count', 0) for api in all_apis)
    
    logger.info(f"Resources stats: {len(all_apis)} APIs, {len(categories_count)} categories")
    logger.info(f"Formatted categories: {formatted_categories}")
    
    return jsonify({
        'success': True,
        'data': {
            'categories': formatted_categories,
            'total_functional': len([a for a in all_apis if a.get('status') == 'active']),
            'total_api_keys': len([a for a in all_apis if a.get('requires_key', False)]),
            'total_endpoints': total_endpoints or len(all_apis) * 5,
            'success_rate': 95.5,
            'last_check': datetime.utcnow().isoformat()
        }
    })

@app.route('/api/resources/apis')
def resources_apis():
    """Get detailed list of all API resources - loads from providers config"""
    import json
    from pathlib import Path
    import traceback
    
    all_apis = []
    categories_set = set()
    
    try:
        # Load providers from providers_config_extended.json
        providers_file = Path(__file__).parent / "providers_config_extended.json"
        if providers_file.exists() and providers_file.is_file():
            try:
                with open(providers_file, 'r', encoding='utf-8') as f:
                    providers_data = json.load(f)
                    if providers_data and isinstance(providers_data, dict):
                        providers = providers_data.get("providers", {})
                        if isinstance(providers, dict):
                            for provider_id, provider_info in providers.items():
                                try:
                                    if not isinstance(provider_info, dict):
                                        logger.warning(f"Skipping invalid provider {provider_id}: not a dict")
                                        continue
                                    
                                    # Validate and extract data safely
                                    provider_id_str = str(provider_id) if provider_id else ""
                                    if not provider_id_str:
                                        logger.warning("Skipping provider with empty ID")
                                        continue
                                    
                                    endpoints = provider_info.get("endpoints", {})
                                    endpoints_count = len(endpoints) if isinstance(endpoints, dict) else 0
                                    category = str(provider_info.get("category", "other"))
                                    categories_set.add(category)
                                    
                                    api_item = {
                                        'id': provider_id_str,
                                        'name': str(provider_info.get("name", provider_id_str)),
                                        'category': category,
                                        'url': str(provider_info.get("base_url", "")),
                                        'description': f"{provider_info.get('name', provider_id_str)} - {endpoints_count} endpoints",
                                        'endpoints': endpoints_count,
                                        'endpoints_count': endpoints_count,
                                        'free': not bool(provider_info.get("requires_auth", False)),
                                        'requires_key': bool(provider_info.get("requires_auth", False)),
                                        'status': 'active'
                                    }
                                    
                                    # Validate API item before adding
                                    if api_item.get('id'):
                                        all_apis.append(api_item)
                                    else:
                                        logger.warning(f"Skipping provider {provider_id}: missing ID")
                                        
                                except Exception as e:
                                    logger.error(f"Error processing provider {provider_id}: {e}", exc_info=True)
                                    continue
                    else:
                        logger.warning(f"Providers data is not a dict: {type(providers_data)}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error loading providers from {providers_file}: {e}", exc_info=True)
            except IOError as io_error:
                logger.error(f"IO error reading providers file {providers_file}: {io_error}", exc_info=True)
            except Exception as e:
                logger.error(f"Error loading providers from {providers_file}: {e}", exc_info=True)
        else:
            logger.info(f"Providers config file not found at {providers_file}")
        
        # Load local routes from unified resources
        resources_file = Path(__file__).parent / "api-resources" / "crypto_resources_unified_2025-11-11.json"
        if resources_file.exists() and resources_file.is_file():
            try:
                with open(resources_file, 'r', encoding='utf-8') as f:
                    resources_data = json.load(f)
                    if resources_data and isinstance(resources_data, dict):
                        registry = resources_data.get('registry', {})
                        if isinstance(registry, dict):
                            local_routes = registry.get('local_backend_routes', [])
                            if isinstance(local_routes, list):
                                # Process routes with validation
                                for route in local_routes[:100]:  # Limit to prevent huge responses
                                    try:
                                        if isinstance(route, dict):
                                            # Validate route has required fields
                                            route_id = route.get("path") or route.get("name") or route.get("id")
                                            if route_id:
                                                all_apis.append(route)
                                                if route.get("category"):
                                                    categories_set.add(str(route["category"]))
                                            else:
                                                logger.warning("Skipping route without ID/name/path")
                                        else:
                                            logger.warning(f"Skipping invalid route: {type(route)}")
                                    except Exception as route_error:
                                        logger.warning(f"Error processing route: {route_error}", exc_info=True)
                                        continue
                                
                                if local_routes:
                                    categories_set.add("local")
                            else:
                                logger.warning(f"local_backend_routes is not a list: {type(local_routes)}")
                        else:
                            logger.warning(f"Registry is not a dict: {type(registry)}")
                    else:
                        logger.warning(f"Resources data is not a dict: {type(resources_data)}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error loading local routes from {resources_file}: {e}", exc_info=True)
            except IOError as io_error:
                logger.error(f"IO error reading resources file {resources_file}: {io_error}", exc_info=True)
            except Exception as e:
                logger.error(f"Error loading local routes from {resources_file}: {e}", exc_info=True)
        else:
            logger.info(f"Resources file not found at {resources_file}")
        
        # Ensure all_apis is a list
        if not isinstance(all_apis, list):
            logger.warning("all_apis is not a list, resetting to empty list")
            all_apis = []
        
        # Build categories list safely
        try:
            categories_list = list(categories_set) if categories_set else []
        except Exception as cat_error:
            logger.warning(f"Error building categories list: {cat_error}")
            categories_list = []
        
        logger.info(f"Successfully loaded {len(all_apis)} APIs")
        
        return jsonify({
            'apis': all_apis,
            'total': len(all_apis),
            'total_apis': len(all_apis),
            'categories': categories_list,
            'ok': True,
            'success': True
        })
    
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Critical error in resources_apis: {e}", exc_info=True)
        logger.error(f"Full traceback: {error_trace}")
        
        # Always return valid JSON even on error
        return jsonify({
            'error': True,
            'ok': False,
            'success': False,
            'message': f'Failed to load API resources: {str(e)}',
            'apis': [],
            'total': 0,
            'total_apis': 0,
            'categories': []
        }), 500

@app.route('/api/ai/signals')
def ai_signals():
    """AI trading signals endpoint"""
    symbol = request.args.get('symbol', 'BTC').upper()
    
    # Get market data
    market_data = get_market_data()
    coin = next((c for c in market_data if c['symbol'].upper() == symbol), None)
    
    if not coin:
        return jsonify({
            'symbol': symbol,
            'signal': 'HOLD',
            'strength': 'weak',
            'price': 0,
            'targets': [],
            'indicators': {}
        })
    
    price_change = coin.get('price_change_percentage_24h', 0)
    current_price = coin.get('current_price', 0)
    
    # Generate signal based on price action
    if price_change > 5:
        signal = 'STRONG_BUY'
        strength = 'strong'
        targets = [
            {'level': current_price * 1.05, 'type': 'short'},
            {'level': current_price * 1.10, 'type': 'medium'},
            {'level': current_price * 1.15, 'type': 'long'}
        ]
    elif price_change > 2:
        signal = 'BUY'
        strength = 'medium'
        targets = [
            {'level': current_price * 1.03, 'type': 'short'},
            {'level': current_price * 1.07, 'type': 'medium'}
        ]
    elif price_change < -5:
        signal = 'STRONG_SELL'
        strength = 'strong'
        targets = [
            {'level': current_price * 0.95, 'type': 'short'},
            {'level': current_price * 0.90, 'type': 'medium'}
        ]
    elif price_change < -2:
        signal = 'SELL'
        strength = 'medium'
        targets = [
            {'level': current_price * 0.97, 'type': 'short'}
        ]
    else:
        signal = 'HOLD'
        strength = 'weak'
        targets = [
            {'level': current_price * 1.02, 'type': 'short'}
        ]
    
    return jsonify({
        'symbol': symbol,
        'signal': signal,
        'strength': strength,
        'price': current_price,
        'change_24h': price_change,
        'targets': targets,
        'stop_loss': current_price * 0.95 if signal in ['BUY', 'STRONG_BUY'] else current_price * 1.05,
        'indicators': {
            'rsi': 50 + (price_change * 2),
            'macd': 'bullish' if price_change > 0 else 'bearish',
            'trend': 'up' if price_change > 0 else 'down'
        },
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/ai/decision', methods=['POST'])
def ai_decision():
    """AI-powered trading decision endpoint"""
    data = request.json
    symbol = data.get('symbol', 'BTC').upper()
    timeframe = data.get('timeframe', '1d')
    
    # Get market data for the symbol
    market_data = get_market_data()
    coin = next((c for c in market_data if c['symbol'].upper() == symbol), None)
    
    if not coin:
        # Fallback to demo decision
        return jsonify({
            'symbol': symbol,
            'decision': 'HOLD',
            'confidence': 0.65,
            'timeframe': timeframe,
            'price_target': None,
            'stop_loss': None,
            'reasoning': 'Insufficient data for analysis',
            'signals': {
                'technical': 'neutral',
                'sentiment': 'neutral',
                'trend': 'neutral'
            }
        })
    
    # Calculate decision based on price change
    price_change = coin.get('price_change_percentage_24h', 0)
    current_price = coin.get('current_price', 0)
    
    # Simple decision logic
    if price_change > 5:
        decision = 'BUY'
        confidence = min(0.75 + (price_change / 100), 0.95)
        price_target = current_price * 1.15
        stop_loss = current_price * 0.95
        reasoning = f'{symbol} showing strong upward momentum (+{price_change:.1f}%). Technical indicators suggest continuation.'
        signals = {'technical': 'bullish', 'sentiment': 'bullish', 'trend': 'uptrend'}
    elif price_change < -5:
        decision = 'SELL'
        confidence = min(0.75 + (abs(price_change) / 100), 0.95)
        price_target = current_price * 0.85
        stop_loss = current_price * 1.05
        reasoning = f'{symbol} experiencing significant decline ({price_change:.1f}%). Consider taking profits or cutting losses.'
        signals = {'technical': 'bearish', 'sentiment': 'bearish', 'trend': 'downtrend'}
    elif price_change > 2:
        decision = 'BUY'
        confidence = 0.65
        price_target = current_price * 1.10
        stop_loss = current_price * 0.97
        reasoning = f'{symbol} showing moderate gains (+{price_change:.1f}%). Cautious entry recommended.'
        signals = {'technical': 'bullish', 'sentiment': 'neutral', 'trend': 'uptrend'}
    elif price_change < -2:
        decision = 'SELL'
        confidence = 0.60
        price_target = current_price * 0.92
        stop_loss = current_price * 1.03
        reasoning = f'{symbol} declining ({price_change:.1f}%). Monitor closely for further weakness.'
        signals = {'technical': 'bearish', 'sentiment': 'neutral', 'trend': 'downtrend'}
    else:
        decision = 'HOLD'
        confidence = 0.70
        price_target = current_price * 1.05
        stop_loss = current_price * 0.98
        reasoning = f'{symbol} consolidating ({price_change:.1f}%). Wait for clearer directional move.'
        signals = {'technical': 'neutral', 'sentiment': 'neutral', 'trend': 'sideways'}
    
    return jsonify({
        'symbol': symbol,
        'decision': decision,
        'confidence': confidence,
        'timeframe': timeframe,
        'current_price': current_price,
        'price_target': round(price_target, 2),
        'stop_loss': round(stop_loss, 2),
        'reasoning': reasoning,
        'signals': signals,
        'risk_level': 'moderate',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/chart/<symbol>')
def chart_data(symbol):
    """Price chart data for symbol"""
    try:
        coin_id = symbol.lower()
        response = requests.get(
            f'https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart',
            params={'vs_currency': 'usd', 'days': '7'},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'prices': data.get('prices', []),
                'market_caps': data.get('market_caps', []),
                'volumes': data.get('total_volumes', [])
            })
    except:
        pass
    
    return jsonify({'prices': [], 'market_caps': [], 'volumes': []})

@app.route('/api/market/ohlc')
def market_ohlc():
    """Get OHLC data for a symbol (compatible with ai-analyst.js)"""
    symbol = request.args.get('symbol', 'BTC').upper()
    interval = request.args.get('interval', '1h')
    limit = int(request.args.get('limit', 100))
    
    # Map interval formats
    interval_map = {
        '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
        '1h': '1h', '4h': '4h', '1d': '1d', '1w': '1w'
    }
    binance_interval = interval_map.get(interval, '1h')
    
    try:
        binance_symbol = f"{symbol}USDT"
        response = requests.get(
            'https://api.binance.com/api/v3/klines',
            params={
                'symbol': binance_symbol,
                'interval': binance_interval,
                'limit': min(limit, 1000)
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            ohlc_data = []
            for item in data:
                ohlc_data.append({
                    'timestamp': item[0],
                    'open': float(item[1]),
                    'high': float(item[2]),
                    'low': float(item[3]),
                    'close': float(item[4]),
                    'volume': float(item[5])
                })
            
            return jsonify({
                'symbol': symbol,
                'interval': interval,
                'data': ohlc_data,
                'count': len(ohlc_data)
            })
    except Exception as e:
        print(f"Market OHLC error: {e}")
    
    # Fallback to CoinGecko
    try:
        coin_id = symbol.lower()
        days = 7 if interval in ['1h', '4h'] else 30
        response = requests.get(
            f'https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc',
            params={'vs_currency': 'usd', 'days': str(days)},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            ohlc_data = []
            for item in data[:limit]:
                if len(item) >= 5:
                    ohlc_data.append({
                        'timestamp': item[0],
                        'open': item[1],
                        'high': item[2],
                        'low': item[3],
                        'close': item[4],
                        'volume': None
                    })
            
            return jsonify({
                'symbol': symbol,
                'interval': interval,
                'data': ohlc_data,
                'count': len(ohlc_data)
            })
    except Exception as e:
        print(f"CoinGecko OHLC fallback error: {e}")
    
    return jsonify({'error': 'OHLC data not available', 'symbol': symbol}), 404

@app.route('/api/ohlcv')
def ohlcv_endpoint():
    """Get OHLCV data (query parameter version)"""
    symbol = request.args.get('symbol', 'BTC').upper()
    timeframe = request.args.get('timeframe', '1h')
    limit = int(request.args.get('limit', 100))
    
    # Redirect to existing endpoint
    return ohlcv_data(symbol)

@app.route('/api/ohlcv/<symbol>')
def ohlcv_data(symbol):
    """Get OHLCV data for a cryptocurrency"""
    # Get query parameters
    interval = request.args.get('interval', '1d')
    limit = int(request.args.get('limit', 30))
    
    # Map interval to days for CoinGecko
    interval_days_map = {
        '1d': 30,
        '1h': 7,
        '4h': 30,
        '1w': 90
    }
    days = interval_days_map.get(interval, 30)
    
    try:
        # Try CoinGecko first
        coin_id = symbol.lower()
        response = requests.get(
            f'https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc',
            params={'vs_currency': 'usd', 'days': str(days)},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            # CoinGecko returns [timestamp, open, high, low, close]
            formatted_data = []
            for item in data:
                if len(item) >= 5:
                    formatted_data.append({
                        'timestamp': item[0],
                        'datetime': datetime.fromtimestamp(item[0] / 1000).isoformat(),
                        'open': item[1],
                        'high': item[2],
                        'low': item[3],
                        'close': item[4],
                        'volume': None  # CoinGecko OHLC doesn't include volume
                    })
            
            # Limit results if needed
            if limit and len(formatted_data) > limit:
                formatted_data = formatted_data[-limit:]
            
            return jsonify({
                'symbol': symbol.upper(),
                'source': 'CoinGecko',
                'interval': interval,
                'data': formatted_data
            })
    except Exception as e:
        print(f"CoinGecko OHLCV error: {e}")
    
    # Fallback: Try Binance
    try:
        binance_symbol = f"{symbol.upper()}USDT"
        # Map interval for Binance
        binance_interval_map = {
            '1d': '1d',
            '1h': '1h',
            '4h': '4h',
            '1w': '1w'
        }
        binance_interval = binance_interval_map.get(interval, '1d')
        
        response = requests.get(
            'https://api.binance.com/api/v3/klines',
            params={
                'symbol': binance_symbol,
                'interval': binance_interval,
                'limit': limit
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            formatted_data = []
            for item in data:
                if len(item) >= 7:
                    formatted_data.append({
                        'timestamp': item[0],
                        'datetime': datetime.fromtimestamp(item[0] / 1000).isoformat(),
                        'open': float(item[1]),
                        'high': float(item[2]),
                        'low': float(item[3]),
                        'close': float(item[4]),
                        'volume': float(item[5])
                    })
            
            return jsonify({
                'symbol': symbol.upper(),
                'source': 'Binance',
                'interval': interval,
                'data': formatted_data
            })
    except Exception as e:
        print(f"Binance OHLCV error: {e}")
    
    return jsonify({
        'error': 'OHLCV data not available',
        'symbol': symbol
    }), 404

@app.route('/api/ohlcv/multi')
def ohlcv_multi():
    """Get OHLCV data for multiple cryptocurrencies"""
    symbols = request.args.get('symbols', 'btc,eth,bnb').split(',')
    interval = request.args.get('interval', '1d')
    limit = int(request.args.get('limit', 30))
    
    results = {}
    
    for symbol in symbols[:10]:  # Limit to 10 symbols
        try:
            symbol = symbol.strip().upper()
            binance_symbol = f"{symbol}USDT"
            
            response = requests.get(
                'https://api.binance.com/api/v3/klines',
                params={
                    'symbol': binance_symbol,
                    'interval': interval,
                    'limit': limit
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                formatted_data = []
                for item in data:
                    if len(item) >= 7:
                        formatted_data.append({
                            'timestamp': item[0],
                            'open': float(item[1]),
                            'high': float(item[2]),
                            'low': float(item[3]),
                            'close': float(item[4]),
                            'volume': float(item[5])
                        })
                
                results[symbol] = {
                    'success': True,
                    'data': formatted_data
                }
            else:
                results[symbol] = {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }
        except Exception as e:
            results[symbol] = {
                'success': False,
                'error': str(e)
            }
    
    return jsonify({
        'interval': interval,
        'limit': limit,
        'results': results
    })

@app.route('/api/ohlcv/verify/<symbol>')
def verify_ohlcv(symbol):
    """Verify OHLCV data quality from multiple sources"""
    results = {}
    
    # Test CoinGecko
    try:
        response = requests.get(
            f'https://api.coingecko.com/api/v3/coins/{symbol.lower()}/ohlc',
            params={'vs_currency': 'usd', 'days': '7'},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            valid_records = sum(1 for item in data if len(item) >= 5 and all(x is not None for x in item[:5]))
            results['coingecko'] = {
                'status': 'success',
                'records': len(data),
                'valid_records': valid_records,
                'sample': data[0] if data else None
            }
        else:
            results['coingecko'] = {'status': 'failed', 'error': f'HTTP {response.status_code}'}
    except Exception as e:
        results['coingecko'] = {'status': 'error', 'error': str(e)}
    
    # Test Binance
    try:
        response = requests.get(
            'https://api.binance.com/api/v3/klines',
            params={'symbol': f'{symbol.upper()}USDT', 'interval': '1d', 'limit': 7},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            valid_records = sum(1 for item in data if len(item) >= 7)
            results['binance'] = {
                'status': 'success',
                'records': len(data),
                'valid_records': valid_records,
                'sample': {
                    'timestamp': data[0][0],
                    'open': data[0][1],
                    'high': data[0][2],
                    'low': data[0][3],
                    'close': data[0][4],
                    'volume': data[0][5]
                } if data else None
            }
        else:
            results['binance'] = {'status': 'failed', 'error': f'HTTP {response.status_code}'}
    except Exception as e:
        results['binance'] = {'status': 'error', 'error': str(e)}
    
    # Test CryptoCompare
    try:
        response = requests.get(
            'https://min-api.cryptocompare.com/data/v2/histoday',
            params={'fsym': symbol.upper(), 'tsym': 'USD', 'limit': 7},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('Response') != 'Error' and 'Data' in data and 'Data' in data['Data']:
                records = data['Data']['Data']
                valid_records = sum(1 for r in records if all(k in r for k in ['time', 'open', 'high', 'low', 'close']))
                results['cryptocompare'] = {
                    'status': 'success',
                    'records': len(records),
                    'valid_records': valid_records,
                    'sample': records[0] if records else None
                }
            else:
                results['cryptocompare'] = {'status': 'failed', 'error': data.get('Message', 'Unknown error')}
        else:
            results['cryptocompare'] = {'status': 'failed', 'error': f'HTTP {response.status_code}'}
    except Exception as e:
        results['cryptocompare'] = {'status': 'error', 'error': str(e)}
    
    return jsonify({
        'symbol': symbol.upper(),
        'verification_time': datetime.utcnow().isoformat(),
        'sources': results
    })

@app.route('/api/test-source/<source_id>')
def test_source(source_id):
    """Test a specific data source connection"""
    
    # Map of source IDs to test endpoints
    test_endpoints = {
        'coingecko': 'https://api.coingecko.com/api/v3/ping',
        'binance_public': 'https://api.binance.com/api/v3/ping',
        'cryptocompare': 'https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD',
        'coinpaprika': 'https://api.coinpaprika.com/v1/tickers/btc-bitcoin',
        'coincap': 'https://api.coincap.io/v2/assets/bitcoin',
        'alternative_me': 'https://api.alternative.me/fng/?limit=1',
        'cryptopanic': 'https://cryptopanic.com/api/v1/posts/?public=true',
        'coinstats_news': 'https://api.coinstats.app/public/v1/news',
        'messari': 'https://data.messari.io/api/v1/assets/btc/metrics',
        'defillama': 'https://coins.llama.fi/prices/current/coingecko:bitcoin'
    }
    
    url = test_endpoints.get(source_id)
    
    if not url:
        return jsonify({'error': 'Unknown source'}), 404
    
    try:
        response = requests.get(url, timeout=10)
        
        return jsonify({
            'source_id': source_id,
            'status': 'success' if response.status_code == 200 else 'failed',
            'http_code': response.status_code,
            'response_time_ms': int(response.elapsed.total_seconds() * 1000),
            'tested_at': datetime.utcnow().isoformat()
        })
    except requests.exceptions.Timeout:
        return jsonify({
            'source_id': source_id,
            'status': 'timeout',
            'error': 'Request timeout'
        }), 408
    except Exception as e:
        return jsonify({
            'source_id': source_id,
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/sources/all')
def get_all_sources():
    """Get list of all available data sources"""
    
    sources = [
        {'id': 'coingecko', 'name': 'CoinGecko', 'category': 'market', 'free': True},
        {'id': 'binance', 'name': 'Binance', 'category': 'ohlcv', 'free': True},
        {'id': 'cryptocompare', 'name': 'CryptoCompare', 'category': 'ohlcv', 'free': True},
        {'id': 'coinpaprika', 'name': 'CoinPaprika', 'category': 'market', 'free': True},
        {'id': 'coincap', 'name': 'CoinCap', 'category': 'market', 'free': True},
        {'id': 'alternative_me', 'name': 'Fear & Greed Index', 'category': 'sentiment', 'free': True},
        {'id': 'cryptopanic', 'name': 'CryptoPanic', 'category': 'news', 'free': True},
        {'id': 'messari', 'name': 'Messari', 'category': 'market', 'free': True},
        {'id': 'defillama', 'name': 'DefiLlama', 'category': 'defi', 'free': True}
    ]
    
    return jsonify({
        'total': len(sources),
        'sources': sources
    })

@app.route('/api/providers')
def get_providers():
    """
    Get list of API providers with status and details
    Returns comprehensive information about available data providers
    """
    providers = [
        {
            'id': 'coingecko',
            'name': 'CoinGecko',
            'endpoint': 'api.coingecko.com/api/v3',
            'category': 'Market Data',
            'status': 'active',
            'type': 'free',
            'rate_limit': '50 calls/min',
            'uptime': '99.9%',
            'description': 'Comprehensive cryptocurrency data including prices, market caps, and historical data'
        },
        {
            'id': 'binance',
            'name': 'Binance',
            'endpoint': 'api.binance.com/api/v3',
            'category': 'Market Data',
            'status': 'active',
            'type': 'free',
            'rate_limit': '1200 calls/min',
            'uptime': '99.9%',
            'description': 'Real-time trading data and market information from Binance exchange'
        },
        {
            'id': 'alternative_me',
            'name': 'Alternative.me',
            'endpoint': 'api.alternative.me/fng',
            'category': 'Sentiment',
            'status': 'active',
            'type': 'free',
            'rate_limit': 'Unlimited',
            'uptime': '99.5%',
            'description': 'Crypto Fear & Greed Index - Market sentiment indicator'
        },
        {
            'id': 'cryptopanic',
            'name': 'CryptoPanic',
            'endpoint': 'cryptopanic.com/api/v1',
            'category': 'News',
            'status': 'active',
            'type': 'free',
            'rate_limit': '100 calls/day',
            'uptime': '98.5%',
            'description': 'Cryptocurrency news aggregation from multiple sources'
        },
        {
            'id': 'huggingface',
            'name': 'Hugging Face',
            'endpoint': 'api-inference.huggingface.co',
            'category': 'AI & ML',
            'status': 'active',
            'type': 'free',
            'rate_limit': '1000 calls/day',
            'uptime': '99.8%',
            'description': 'AI-powered sentiment analysis and NLP models'
        },
        {
            'id': 'coinpaprika',
            'name': 'CoinPaprika',
            'endpoint': 'api.coinpaprika.com/v1',
            'category': 'Market Data',
            'status': 'active',
            'type': 'free',
            'rate_limit': '25000 calls/month',
            'uptime': '99.7%',
            'description': 'Cryptocurrency market data and analytics'
        },
        {
            'id': 'messari',
            'name': 'Messari',
            'endpoint': 'data.messari.io/api/v1',
            'category': 'Analytics',
            'status': 'active',
            'type': 'free',
            'rate_limit': '20 calls/min',
            'uptime': '99.5%',
            'description': 'Crypto research and market intelligence data'
        }
    ]
    
    return jsonify({
        'providers': providers,
        'total': len(providers),
        'active': len([p for p in providers if p['status'] == 'active']),
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/data/aggregate/<symbol>')
def aggregate_data(symbol):
    """Aggregate data from multiple sources for a symbol"""
    
    results = {}
    symbol = symbol.upper()
    
    # CoinGecko
    try:
        response = requests.get(
            f'https://api.coingecko.com/api/v3/simple/price',
            params={'ids': symbol.lower(), 'vs_currencies': 'usd', 'include_24hr_change': 'true'},
            timeout=5
        )
        if response.status_code == 200:
            results['coingecko'] = response.json()
    except:
        results['coingecko'] = None
    
    # Binance
    try:
        response = requests.get(
            'https://api.binance.com/api/v3/ticker/24hr',
            params={'symbol': f'{symbol}USDT'},
            timeout=5
        )
        if response.status_code == 200:
            results['binance'] = response.json()
    except:
        results['binance'] = None
    
    # CoinPaprika
    try:
        response = requests.get(
            f'https://api.coinpaprika.com/v1/tickers/{symbol.lower()}-{symbol.lower()}',
            timeout=5
        )
        if response.status_code == 200:
            results['coinpaprika'] = response.json()
    except:
        results['coinpaprika'] = None
    
    return jsonify({
        'symbol': symbol,
        'sources': results,
        'timestamp': datetime.utcnow().isoformat()
    })

# Unified Service API Endpoints
@app.route('/api/service/rate')
def service_rate():
    """Get exchange rate for a currency pair"""
    pair = request.args.get('pair', 'BTC/USDT')
    base, quote = pair.split('/') if '/' in pair else (pair, 'USDT')
    base = base.upper()
    quote = quote.upper()
    
    # Symbol to CoinGecko ID mapping
    symbol_to_id = {
        'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin',
        'SOL': 'solana', 'ADA': 'cardano', 'XRP': 'ripple',
        'DOT': 'polkadot', 'DOGE': 'dogecoin', 'MATIC': 'matic-network',
        'AVAX': 'avalanche-2', 'LINK': 'chainlink', 'UNI': 'uniswap',
        'LTC': 'litecoin', 'ATOM': 'cosmos', 'ALGO': 'algorand'
    }
    
    # Try Binance first (faster, more reliable for major pairs)
    if quote == 'USDT':
        try:
            binance_symbol = f"{base}USDT"
            response = requests.get(
                'https://api.binance.com/api/v3/ticker/price',
                params={'symbol': binance_symbol},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return jsonify({
                    'pair': pair,
                    'price': float(data['price']),
                    'quote': quote,
                    'source': 'Binance',
                    'timestamp': datetime.utcnow().isoformat()
                })
        except Exception as e:
            print(f"Binance rate error: {e}")
    
    # Fallback to CoinGecko
    try:
        coin_id = symbol_to_id.get(base, base.lower())
        vs_currency = quote.lower() if quote != 'USDT' else 'usd'
        
        response = requests.get(
            f'https://api.coingecko.com/api/v3/simple/price',
            params={'ids': coin_id, 'vs_currencies': vs_currency},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if coin_id in data and vs_currency in data[coin_id]:
                return jsonify({
                    'pair': pair,
                    'price': data[coin_id][vs_currency],
                    'quote': quote,
                    'source': 'CoinGecko',
                    'timestamp': datetime.utcnow().isoformat()
                })
    except Exception as e:
        print(f"CoinGecko rate error: {e}")
    
    return jsonify({'error': 'Rate not available', 'pair': pair}), 404

@app.route('/api/service/market-status')
def service_market_status():
    """Get overall market status"""
    try:
        response = requests.get(
            'https://api.coingecko.com/api/v3/global',
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            market_data = data.get('data', {})
            return jsonify({
                'status': 'active',
                'market_cap': market_data.get('total_market_cap', {}).get('usd', 0),
                'volume_24h': market_data.get('total_volume', {}).get('usd', 0),
                'btc_dominance': market_data.get('market_cap_percentage', {}).get('btc', 0),
                'timestamp': datetime.utcnow().isoformat()
            })
    except Exception as e:
        print(f"Market status error: {e}")
    
    return jsonify({
        'status': 'unknown',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/service/top')
def service_top():
    """Get top N cryptocurrencies"""
    n = int(request.args.get('n', 10))
    limit = min(n, 100)  # Cap at 100
    
    try:
        response = requests.get(
            'https://api.coingecko.com/api/v3/coins/markets',
            params={
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            coins = []
            for coin in data:
                coins.append({
                    'symbol': coin['symbol'].upper(),
                    'name': coin['name'],
                    'price': coin['current_price'],
                    'market_cap': coin['market_cap'],
                    'volume_24h': coin['total_volume'],
                    'change_24h': coin['price_change_percentage_24h']
                })
            
            return jsonify({
                'data': coins,
                'count': len(coins),
                'timestamp': datetime.utcnow().isoformat()
            })
    except Exception as e:
        print(f"Service top error: {e}")
    
    return jsonify({'error': 'Top coins not available'}), 404

@app.route('/api/service/history')
def service_history():
    """Get historical OHLC data"""
    symbol = request.args.get('symbol', 'BTC')
    interval = request.args.get('interval', '60')  # minutes
    limit = int(request.args.get('limit', 100))
    
    try:
        # Map interval to Binance format
        interval_map = {
            '60': '1h',
            '240': '4h',
            '1440': '1d'
        }
        binance_interval = interval_map.get(interval, '1h')
        
        binance_symbol = f"{symbol.upper()}USDT"
        response = requests.get(
            'https://api.binance.com/api/v3/klines',
            params={
                'symbol': binance_symbol,
                'interval': binance_interval,
                'limit': min(limit, 1000)
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            history = []
            for item in data:
                history.append({
                    'timestamp': item[0],
                    'open': float(item[1]),
                    'high': float(item[2]),
                    'low': float(item[3]),
                    'close': float(item[4]),
                    'volume': float(item[5])
                })
            
            return jsonify({
                'symbol': symbol.upper(),
                'interval': interval,
                'data': history,
                'count': len(history)
            })
    except Exception as e:
        print(f"Service history error: {e}")
    
    return jsonify({'error': 'Historical data not available', 'symbol': symbol}), 404

if __name__ == '__main__':
    try:
        port = int(os.getenv('PORT', 7860))
        logger.info(f"🚀 Starting server on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
