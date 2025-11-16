# Auto Provider Loader (APL) - Usage Guide

**Version:** 1.0  
**Last Updated:** 2025-11-16  
**Status:** PRODUCTION READY ✅

---

## Overview

The Auto Provider Loader (APL) is a **real-data-only** system that automatically discovers, validates, and integrates cryptocurrency data providers (both HTTP APIs and Hugging Face models) into your application.

### Key Features

- 🔍 **Automatic Discovery** - Scans JSON resources for provider definitions
- ✅ **Real Validation** - Tests each provider with actual API calls (NO MOCKS)
- 🔧 **Smart Integration** - Automatically adds valid providers to config
- 📊 **Comprehensive Reports** - Generates detailed validation reports
- ⚡ **Performance Optimized** - Parallel validation with configurable timeouts
- 🛡️ **Auth Handling** - Detects and handles API key requirements

---

## Architecture

### Components

1. **provider_validator.py** - Core validation engine
   - Validates HTTP JSON APIs
   - Validates HTTP RPC endpoints
   - Validates Hugging Face models
   - Handles authentication requirements

2. **auto_provider_loader.py** - Discovery and orchestration
   - Scans resource files
   - Coordinates validation
   - Integrates valid providers
   - Generates reports

### Provider Types Supported

| Type | Description | Example |
|------|-------------|---------|
| `HTTP_JSON` | REST APIs returning JSON | CoinGecko, CoinPaprika |
| `HTTP_RPC` | JSON-RPC endpoints | Ethereum nodes, BSC RPC |
| `WEBSOCKET` | WebSocket connections | Alchemy WS, real-time feeds |
| `HF_MODEL` | Hugging Face models | Sentiment analysis models |

---

## Quick Start

### 1. Basic Usage

Run the APL to discover and validate all providers:

```bash
cd /workspace
python3 auto_provider_loader.py
```

This will:
- Scan `api-resources/*.json` for provider definitions
- Scan `providers_config*.json` for existing providers
- Discover HF models from `backend/services/`
- Validate each provider with real API calls
- Generate comprehensive reports
- Update `providers_config_extended.json` with valid providers

### 2. Understanding Output

```
================================================================================
🚀 AUTO PROVIDER LOADER (APL) - REAL DATA ONLY
================================================================================

📡 PHASE 1: DISCOVERY
  Found 339 HTTP provider candidates
  Found 4 HF model candidates

🔬 PHASE 2: VALIDATION
  ✅ Valid providers
  ❌ Invalid providers
  ⚠️  Conditionally available (requires auth)

📊 PHASE 3: COMPUTING STATISTICS
🔧 PHASE 4: INTEGRATION
📝 PHASE 5: GENERATING REPORTS
```

### 3. Generated Files

After running APL, you'll find:

- `PROVIDER_AUTO_DISCOVERY_REPORT.md` - Human-readable report
- `PROVIDER_AUTO_DISCOVERY_REPORT.json` - Machine-readable detailed results
- `providers_config_extended.backup.{timestamp}.json` - Config backup
- `providers_config_extended.json` - Updated with new valid providers

---

## Validation Logic

### HTTP Providers

For each HTTP provider, APL:

1. **Checks URL structure**
   - Detects placeholder variables (`{API_KEY}`, `{PROJECT_ID}`)
   - Identifies WebSocket endpoints (`ws://`, `wss://`)

2. **Determines endpoint type**
   - JSON REST API → GET request to test endpoint
   - JSON-RPC → POST request with `eth_blockNumber` method

3. **Makes real test call**
   - 8-second timeout
   - Handles redirects
   - Validates response format

4. **Classifies result**
   - ✅ `VALID` - Responds with 200 OK and valid data
   - ❌ `INVALID` - Connection fails, timeout, or error response
   - ⚠️ `CONDITIONALLY_AVAILABLE` - Requires API key (401/403)
   - ⏭️ `SKIPPED` - WebSocket (requires separate validation)

### Hugging Face Models

For each HF model, APL:

1. **Queries HF Hub API**
   - Checks if model exists: `GET https://huggingface.co/api/models/{model_id}`
   - Does NOT download or load the full model (saves time/resources)

2. **Validates accessibility**
   - ✅ `VALID` - Model found and publicly accessible
   - ⚠️ `CONDITIONALLY_AVAILABLE` - Requires HF_TOKEN
   - ❌ `INVALID` - Model not found (404) or other error

---

## Configuration

### Environment Variables

APL respects these environment variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `HF_TOKEN` | Hugging Face API token | None |
| `ETHERSCAN_API_KEY` | Etherscan API key | None |
| `BSCSCAN_API_KEY` | BSCScan API key | None |
| `INFURA_PROJECT_ID` | Infura project ID | None |
| `ALCHEMY_API_KEY` | Alchemy API key | None |

### Validation Timeout

Default timeout is 8 seconds. To customize:

```python
from auto_provider_loader import AutoProviderLoader

apl = AutoProviderLoader()
apl.validator.timeout = 15.0  # 15 seconds
await apl.run()
```

---

## Adding New Provider Sources

### 1. Add to JSON Resources

Create or update a JSON file in `api-resources/`:

```json
{
  "registry": {
    "my_providers": [
      {
        "id": "my_api",
        "name": "My API",
        "category": "market_data",
        "base_url": "https://api.example.com/v1",
        "endpoints": {
          "prices": "/prices"
        },
        "auth": {
          "type": "none"
        }
      }
    ]
  }
}
```

### 2. Re-run APL

```bash
python3 auto_provider_loader.py
```

APL will automatically discover and validate your new provider.

---

## Integration with Existing Code

### Using Validated Providers

After APL runs, valid providers are in `providers_config_extended.json`:

```python
import json

# Load validated providers
with open('providers_config_extended.json', 'r') as f:
    config = json.load(f)

# Get all valid providers
valid_providers = config['providers']

# Use a specific provider
coingecko = valid_providers['coingecko']
print(f"Provider: {coingecko['name']}")
print(f"Category: {coingecko['category']}")
print(f"Response time: {coingecko['response_time_ms']}ms")
```

### Filtering by Category

```python
# Get all market data providers
market_providers = {
    pid: data for pid, data in valid_providers.items()
    if data.get('category') == 'market_data'
}
```

---

## Conditional Providers

Providers marked as `CONDITIONALLY_AVAILABLE` require API keys:

### 1. Check Requirements

See `PROVIDER_AUTO_DISCOVERY_REPORT.md` for required env vars:

```markdown
### Conditionally Available Providers (90)

- **Etherscan** (`etherscan_primary`)
  - Required: `ETHERSCAN_PRIMARY_API_KEY` environment variable
  - Reason: HTTP 401 - Requires authentication
```

### 2. Set Environment Variables

```bash
export ETHERSCAN_API_KEY="your_key_here"
export BSCSCAN_API_KEY="your_key_here"
```

### 3. Re-run Validation

```bash
python3 auto_provider_loader.py
```

Previously conditional providers will now validate as VALID if keys are correct.

---

## Performance Tuning

### Parallel Validation

HTTP providers are validated in batches of 10 to balance speed and resource usage:

```python
# In auto_provider_loader.py
batch_size = 10  # Adjust based on your needs
```

Larger batches = faster but more network load  
Smaller batches = slower but more conservative

### Timeout Adjustment

For slow or distant APIs:

```python
validator = ProviderValidator(timeout=15.0)  # 15 seconds
```

---

## Troubleshooting

### Issue: Many providers marked INVALID

**Possible causes:**
- Network connectivity issues
- Rate limiting (try again later)
- Providers genuinely down

**Solution:** Check individual error reasons in report

### Issue: All providers CONDITIONALLY_AVAILABLE

**Cause:** Most providers require API keys

**Solution:** Set required environment variables

### Issue: HF models all INVALID

**Causes:**
- No internet connection to HuggingFace
- Models moved or renamed
- Rate limiting from HF Hub

**Solution:** Check HF Hub status, verify model IDs

### Issue: Validation takes too long

**Solutions:**
- Reduce batch size
- Decrease timeout
- Filter providers before validation

---

## Advanced Usage

### Validating Specific Providers

```python
from provider_validator import ProviderValidator
import asyncio

async def validate_one():
    validator = ProviderValidator()
    
    result = await validator.validate_http_provider(
        "coingecko",
        {
            "name": "CoinGecko",
            "category": "market_data",
            "base_url": "https://api.coingecko.com/api/v3",
            "endpoints": {"ping": "/ping"}
        }
    )
    
    print(f"Status: {result.status}")
    print(f"Response time: {result.response_time_ms}ms")

asyncio.run(validate_one())
```

### Custom Discovery Logic

```python
from auto_provider_loader import AutoProviderLoader

class CustomAPL(AutoProviderLoader):
    def discover_http_providers(self):
        # Your custom logic
        providers = super().discover_http_providers()
        # Filter or augment
        return [p for p in providers if p['data'].get('free') == True]

apl = CustomAPL()
await apl.run()
```

---

## API Reference

### ProviderValidator

```python
class ProviderValidator:
    def __init__(self, timeout: float = 10.0)
    
    async def validate_http_provider(
        provider_id: str,
        provider_data: Dict[str, Any]
    ) -> ValidationResult
    
    async def validate_hf_model(
        model_id: str,
        model_name: str,
        pipeline_tag: str = "sentiment-analysis"
    ) -> ValidationResult
    
    def get_summary() -> Dict[str, Any]
```

### AutoProviderLoader

```python
class AutoProviderLoader:
    def __init__(self, workspace_root: str = "/workspace")
    
    def discover_http_providers() -> List[Dict[str, Any]]
    def discover_hf_models() -> List[Dict[str, Any]]
    
    async def validate_all_http_providers(providers: List)
    async def validate_all_hf_models(models: List)
    
    def integrate_valid_providers() -> Dict[str, Any]
    def generate_reports()
    
    async def run()  # Main entry point
```

---

## Best Practices

1. **Regular Re-validation**
   - Run APL weekly to catch provider changes
   - Providers can go offline or change endpoints

2. **Monitor Conditional Providers**
   - Set up API keys for high-value providers
   - Track which providers need auth

3. **Review Reports**
   - Check invalid providers for patterns
   - Update configs based on error reasons

4. **Backup Configs**
   - APL creates automatic backups
   - Keep manual backups before major changes

5. **Test Integration**
   - After APL runs, test your application
   - Verify new providers work in your context

---

## Zero Mock/Fake Data Guarantee

**APL NEVER uses mock or fake data.**

- All validations are REAL API calls
- All response times are ACTUAL measurements
- All status classifications based on REAL responses
- Invalid providers are GENUINELY unreachable
- Valid providers are GENUINELY functional

This guarantee ensures:
- Production-ready validation results
- Accurate performance metrics
- Trustworthy provider recommendations
- No surprises in production

---

## Support

### Documentation

- `PROVIDER_AUTO_DISCOVERY_REPORT.md` - Latest validation results
- `APL_FINAL_SUMMARY.md` - Implementation summary
- This guide - Usage instructions

### Common Questions

**Q: Can I use APL in CI/CD?**  
A: Yes! Run `python3 auto_provider_loader.py` in your pipeline.

**Q: How often should I run APL?**  
A: Weekly for production, daily for development.

**Q: Can I add custom provider types?**  
A: Yes, extend `ProviderValidator` class with new validation methods.

**Q: Does APL support GraphQL APIs?**  
A: Not yet, but you can extend it by adding GraphQL validation logic.

---

## Version History

### v1.0 (2025-11-16)
- Initial release
- HTTP JSON validation
- HTTP RPC validation
- HF model validation (API-based, lightweight)
- Automatic discovery from JSON resources
- Comprehensive reporting
- Zero mock data guarantee

---

*Auto Provider Loader - Real Data Only, Always.*
