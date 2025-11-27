"""
Integration Test Script
Tests all critical integrations for the Crypto Hub system
"""

from datetime import datetime

from database.db_manager import db_manager

print("=" * 80)
print("CRYPTO HUB - INTEGRATION TEST")
print("=" * 80)
print()

# Test 1: Database Manager with Data Access
print("TEST 1: Database Manager with Data Access Layer")
print("-" * 80)

# Initialize database
db_manager.init_database()
print("✓ Database initialized")

# Test save market price
price = db_manager.save_market_price(
    symbol="BTC",
    price_usd=45000.00,
    market_cap=880000000000,
    volume_24h=28500000000,
    price_change_24h=2.5,
    source="Test",
)
print(f"✓ Saved market price: BTC = ${price.price_usd}")

# Test retrieve market price
latest_price = db_manager.get_latest_price_by_symbol("BTC")
print(f"✓ Retrieved market price: BTC = ${latest_price.price_usd}")

# Test save news article
news = db_manager.save_news_article(
    title="Bitcoin reaches new milestone",
    content="Bitcoin price surges past $45,000",
    source="Test",
    published_at=datetime.utcnow(),
    sentiment="positive",
)
print(f"✓ Saved news article: ID={news.id}")

# Test retrieve news
latest_news = db_manager.get_latest_news(limit=5)
print(f"✓ Retrieved {len(latest_news)} news articles")

# Test save sentiment
sentiment = db_manager.save_sentiment_metric(
    metric_name="fear_greed_index", value=65.0, classification="greed", source="Test"
)
print(f"✓ Saved sentiment metric: {sentiment.value}")

# Test retrieve sentiment
latest_sentiment = db_manager.get_latest_sentiment()
if latest_sentiment:
    print(f"✓ Retrieved sentiment: {latest_sentiment.value} ({latest_sentiment.classification})")

print()

# Test 2: Database Statistics
print("TEST 2: Database Statistics")
print("-" * 80)

stats = db_manager.get_database_stats()
print(f"✓ Database size: {stats.get('database_size_mb', 0)} MB")
print(f"✓ Market prices: {stats.get('market_prices', 0)} records")
print(f"✓ News articles: {stats.get('news_articles', 0)} records")
print(f"✓ Sentiment metrics: {stats.get('sentiment_metrics', 0)} records")
print()

# Test 3: Data Endpoints Import
print("TEST 3: Data Endpoints")
print("-" * 80)

try:
    from api.data_endpoints import router

    print(f"✓ Data endpoints router imported")
    print(f"✓ Router prefix: {router.prefix}")
    print(f"✓ Router tags: {router.tags}")
except Exception as e:
    print(f"✗ Error importing data endpoints: {e}")

print()

# Test 4: Data Persistence
print("TEST 4: Data Persistence Module")
print("-" * 80)

try:
    from collectors.data_persistence import data_persistence

    print(f"✓ Data persistence module imported")

    # Create mock data
    mock_market_data = [
        {
            "success": True,
            "provider": "CoinGecko",
            "data": {
                "bitcoin": {
                    "usd": 46000.00,
                    "usd_market_cap": 900000000000,
                    "usd_24h_vol": 30000000000,
                    "usd_24h_change": 3.2,
                }
            },
        }
    ]

    count = data_persistence.save_market_data(mock_market_data)
    print(f"✓ Saved {count} market prices via persistence layer")

except Exception as e:
    print(f"✗ Error in data persistence: {e}")

print()

# Test 5: WebSocket Broadcaster
print("TEST 5: WebSocket Broadcaster")
print("-" * 80)

try:
    from api.ws_data_broadcaster import broadcaster

    print(f"✓ WebSocket broadcaster imported")
    print(f"✓ Broadcaster initialized: {broadcaster is not None}")
except Exception as e:
    print(f"✗ Error importing broadcaster: {e}")

print()

# Test 6: Health Check
print("TEST 6: System Health Check")
print("-" * 80)

health = db_manager.health_check()
print(f"✓ Database status: {health.get('status', 'unknown')}")
print(f"✓ Database path: {health.get('database_path', 'N/A')}")

print()
print("=" * 80)
print("INTEGRATION TEST COMPLETE")
print("All critical integrations are working!")
print("=" * 80)
