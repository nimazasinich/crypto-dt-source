# Cryptocurrency Data Collectors

Comprehensive data collection modules for cryptocurrency APIs, blockchain explorers, news sources, sentiment indicators, and on-chain analytics.

## Overview

This package provides production-ready collectors for gathering cryptocurrency data from various sources. Each collector is designed with robust error handling, logging, staleness tracking, and standardized output formats.

## Modules

### 1. Market Data (`market_data.py`)

Collects cryptocurrency market data from multiple providers.

**Providers:**
- **CoinGecko** - Free API for BTC, ETH, BNB prices with market cap and volume
- **CoinMarketCap** - Professional market data with API key
- **Binance** - Real-time ticker data from Binance exchange

**Functions:**
```python
from collectors.market_data import (
    get_coingecko_simple_price,
    get_coinmarketcap_quotes,
    get_binance_ticker,
    collect_market_data  # Collects from all sources
)

# Collect from all market data sources
results = await collect_market_data()
```

**Features:**
- Concurrent data collection
- Price tracking with volume and market cap
- 24-hour change percentages
- Timestamp extraction for staleness calculation

### 2. Blockchain Explorers (`explorers.py`)

Collects data from blockchain explorers and network statistics.

**Providers:**
- **Etherscan** - Ethereum gas prices and network stats
- **BscScan** - BNB prices and BSC network data
- **TronScan** - TRON network statistics

**Functions:**
```python
from collectors.explorers import (
    get_etherscan_gas_price,
    get_bscscan_bnb_price,
    get_tronscan_stats,
    collect_explorer_data  # Collects from all sources
)

# Collect from all explorers
results = await collect_explorer_data()
```

**Features:**
- Real-time gas price tracking
- Network health monitoring
- API key management
- Rate limit handling

### 3. News Aggregation (`news.py`)

Collects cryptocurrency news from multiple sources.

**Providers:**
- **CryptoPanic** - Cryptocurrency news aggregator with sentiment
- **NewsAPI** - General news with crypto filtering

**Functions:**
```python
from collectors.news import (
    get_cryptopanic_posts,
    get_newsapi_headlines,
    collect_news_data  # Collects from all sources
)

# Collect from all news sources
results = await collect_news_data()
```

**Features:**
- News post aggregation
- Article timestamps for freshness tracking
- Article count reporting
- Content filtering

### 4. Sentiment Analysis (`sentiment.py`)

Collects cryptocurrency market sentiment data.

**Providers:**
- **Alternative.me** - Fear & Greed Index (0-100 scale)

**Functions:**
```python
from collectors.sentiment import (
    get_fear_greed_index,
    collect_sentiment_data  # Collects from all sources
)

# Collect sentiment data
results = await collect_sentiment_data()
```

**Features:**
- Market sentiment indicator (Fear/Greed)
- Historical sentiment tracking
- Classification (Extreme Fear, Fear, Neutral, Greed, Extreme Greed)

### 5. On-Chain Analytics (`onchain.py`)

Placeholder implementations for on-chain data sources.

**Providers (Placeholder):**
- **The Graph** - GraphQL-based blockchain data
- **Blockchair** - Blockchain explorer and statistics
- **Glassnode** - Advanced on-chain metrics

**Functions:**
```python
from collectors.onchain import (
    get_the_graph_data,
    get_blockchair_data,
    get_glassnode_metrics,
    collect_onchain_data  # Collects from all sources
)

# Collect on-chain data (placeholder)
results = await collect_onchain_data()
```

**Planned Features:**
- DEX volume and liquidity tracking
- Token holder analytics
- NUPL, SOPR, and other on-chain metrics
- Exchange flow monitoring
- Whale transaction tracking

## Standard Output Format

All collectors return a standardized dictionary format:

```python
{
    "provider": str,              # Provider name (e.g., "CoinGecko")
    "category": str,              # Category (e.g., "market_data")
    "data": dict/list/None,       # Raw API response data
    "timestamp": str,             # Collection timestamp (ISO format)
    "data_timestamp": str/None,   # Data timestamp from API (ISO format)
    "staleness_minutes": float/None,  # Age of data in minutes
    "success": bool,              # Whether collection succeeded
    "error": str/None,            # Error message if failed
    "error_type": str/None,       # Error classification
    "response_time_ms": float     # API response time
}
```

## Common Features

All collectors implement:

1. **Error Handling**
   - Graceful failure with detailed error messages
   - Exception catching and logging
   - API-specific error parsing

2. **Logging**
   - Structured JSON logging
   - Request/response logging
   - Error logging with context

3. **Staleness Tracking**
   - Extracts timestamps from API responses
   - Calculates data age in minutes
   - Handles missing timestamps

4. **Rate Limiting**
   - Respects provider rate limits
   - Exponential backoff on failures
   - Rate limit error detection

5. **Retry Logic**
   - Automatic retries on failure
   - Configurable retry attempts
   - Timeout handling

6. **API Key Management**
   - Loads keys from config
   - Handles missing keys gracefully
   - API key masking in logs

## Usage Examples

### Basic Usage

```python
import asyncio
from collectors import collect_market_data

async def main():
    results = await collect_market_data()

    for result in results:
        if result['success']:
            print(f"{result['provider']}: Success")
            print(f"  Staleness: {result['staleness_minutes']:.2f}m")
        else:
            print(f"{result['provider']}: Failed - {result['error']}")

asyncio.run(main())
```

### Collecting All Data

```python
import asyncio
from collectors import (
    collect_market_data,
    collect_explorer_data,
    collect_news_data,
    collect_sentiment_data,
    collect_onchain_data
)

async def collect_all():
    results = await asyncio.gather(
        collect_market_data(),
        collect_explorer_data(),
        collect_news_data(),
        collect_sentiment_data(),
        collect_onchain_data()
    )

    market, explorers, news, sentiment, onchain = results

    return {
        "market_data": market,
        "explorers": explorers,
        "news": news,
        "sentiment": sentiment,
        "onchain": onchain
    }

all_data = asyncio.run(collect_all())
```

### Individual Collector Usage

```python
import asyncio
from collectors.market_data import get_coingecko_simple_price

async def get_prices():
    result = await get_coingecko_simple_price()

    if result['success']:
        data = result['data']
        print(f"Bitcoin: ${data['bitcoin']['usd']}")
        print(f"Ethereum: ${data['ethereum']['usd']}")
        print(f"BNB: ${data['binancecoin']['usd']}")

asyncio.run(get_prices())
```

## Demo Script

Run the comprehensive demo to test all collectors:

```bash
python collectors/demo_collectors.py
```

This will:
- Execute all collectors concurrently
- Display detailed results for each category
- Show overall statistics
- Save results to a JSON file

## Configuration

Collectors use the central configuration system from `config.py`:

```python
from config import config

# Get provider configuration
provider = config.get_provider('CoinGecko')

# Get API key
api_key = config.get_api_key('coinmarketcap')

# Get providers by category
market_providers = config.get_providers_by_category('market_data')
```

## API Keys

API keys are loaded from environment variables:

```bash
# Market Data
export COINMARKETCAP_KEY_1="your_key_here"
export COINMARKETCAP_KEY_2="backup_key"

# Blockchain Explorers
export ETHERSCAN_KEY_1="your_key_here"
export ETHERSCAN_KEY_2="backup_key"
export BSCSCAN_KEY="your_key_here"
export TRONSCAN_KEY="your_key_here"

# News
export NEWSAPI_KEY="your_key_here"

# Analytics
export CRYPTOCOMPARE_KEY="your_key_here"
```

Or use `.env` file with `python-dotenv`:

```env
COINMARKETCAP_KEY_1=your_key_here
ETHERSCAN_KEY_1=your_key_here
BSCSCAN_KEY=your_key_here
NEWSAPI_KEY=your_key_here
```

## Dependencies

- `aiohttp` - Async HTTP client
- `asyncio` - Async programming
- `datetime` - Timestamp handling
- `utils.api_client` - Robust API client with retry logic
- `utils.logger` - Structured JSON logging
- `config` - Centralized configuration

## Error Handling

Collectors handle various error types:

- **config_error** - Provider not configured
- **missing_api_key** - API key required but not available
- **authentication** - API key invalid or expired
- **rate_limit** - Rate limit exceeded
- **timeout** - Request timeout
- **server_error** - API server error (5xx)
- **network_error** - Network connectivity issue
- **api_error** - API-specific error
- **exception** - Unexpected Python exception

## Extending Collectors

To add a new collector:

1. Create a new module or add to existing category
2. Implement collector function following the standard pattern
3. Use `get_client()` for API requests
4. Extract and calculate staleness from timestamps
5. Return standardized output format
6. Add to `__init__.py` exports
7. Update this README

Example:

```python
async def get_new_provider_data() -> Dict[str, Any]:
    """Fetch data from new provider"""
    provider = "NewProvider"
    category = "market_data"
    endpoint = "/api/v1/data"

    logger.info(f"Fetching data from {provider}")

    try:
        client = get_client()
        provider_config = config.get_provider(provider)

        # Make request
        url = f"{provider_config.endpoint_url}{endpoint}"
        response = await client.get(url)

        # Log request
        log_api_request(
            logger, provider, endpoint,
            response.get("response_time_ms", 0),
            "success" if response["success"] else "error",
            response.get("status_code")
        )

        if not response["success"]:
            # Handle error
            return {
                "provider": provider,
                "category": category,
                "success": False,
                "error": response.get("error_message")
            }

        # Parse data and timestamps
        data = response["data"]
        data_timestamp = # extract from response
        staleness = calculate_staleness_minutes(data_timestamp)

        return {
            "provider": provider,
            "category": category,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_timestamp": data_timestamp.isoformat(),
            "staleness_minutes": staleness,
            "success": True,
            "error": None,
            "response_time_ms": response.get("response_time_ms", 0)
        }

    except Exception as e:
        log_error(logger, provider, "exception", str(e), endpoint, exc_info=True)
        return {
            "provider": provider,
            "category": category,
            "success": False,
            "error": str(e),
            "error_type": "exception"
        }
```

## Testing

Test individual collectors:

```bash
# Test market data collector
python -m collectors.market_data

# Test explorers
python -m collectors.explorers

# Test news
python -m collectors.news

# Test sentiment
python -m collectors.sentiment

# Test on-chain (placeholder)
python -m collectors.onchain
```

## Performance

- Collectors run concurrently using `asyncio.gather()`
- Typical response times: 100-2000ms per collector
- Connection pooling for efficiency
- Configurable timeouts
- Automatic retry with exponential backoff

## Monitoring

All collectors provide metrics for monitoring:

- **Success Rate** - Percentage of successful collections
- **Response Time** - API response time in milliseconds
- **Staleness** - Data age in minutes
- **Error Types** - Classification of failures
- **Retry Count** - Number of retries needed

## Future Enhancements

1. **On-Chain Implementation**
   - Complete The Graph integration
   - Implement Blockchair endpoints
   - Add Glassnode metrics

2. **Additional Providers**
   - Messari
   - DeFiLlama
   - CoinAPI
   - Nomics

3. **Advanced Features**
   - Circuit breaker pattern
   - Data caching
   - Webhook notifications
   - Real-time streaming

4. **Performance**
   - Redis caching
   - Database persistence
   - Rate limit optimization
   - Parallel processing

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Verify API keys are configured correctly
3. Review provider rate limits
4. Check network connectivity
5. Consult provider documentation

## License

Part of the Crypto API Monitoring system.
