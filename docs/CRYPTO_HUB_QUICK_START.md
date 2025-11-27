# Crypto API Hub Self-Healing System - Quick Start Guide

This guide will help you get the self-healing Crypto API Hub up and running in minutes.

## Prerequisites

- Python 3.8+
- pip
- Basic understanding of FastAPI

## Installation

### 1. Install Dependencies

```bash
pip install fastapi uvicorn httpx pydantic
```

### 2. Verify File Structure

Ensure you have the following files:

```
/workspace/
├── static/
│   ├── crypto-api-hub-stunning.html
│   └── js/
│       └── crypto-api-hub-self-healing.js
├── backend/
│   ├── routers/
│   │   └── crypto_api_hub_self_healing.py
│   └── services/
│       └── crypto_hub_monitoring.py
└── hf_unified_server.py
```

## Quick Start

### Step 1: Start the Server

```bash
# From the workspace root directory
python hf_unified_server.py
```

You should see:

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Access the Self-Healing Crypto Hub

Open your browser and navigate to:

```
http://localhost:8000/api/crypto-hub/
```

You should see the beautiful Crypto API Hub dashboard with 74+ services.

### Step 3: Test Self-Healing Features

#### Test 1: Basic API Call

1. Click on any service card (e.g., "CoinGecko")
2. Click the "Test" button on an endpoint
3. Observe the automatic retry and recovery in action

#### Test 2: Health Monitoring

1. Look for the "Health" button in the header (added automatically)
2. Click it to see the current system health status
3. Health percentage shows overall system health

#### Test 3: API Tester

1. Click "API Tester" in the header
2. Enter an API URL: `https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd`
3. Click "Send Request"
4. Watch the self-healing system work:
   - Automatic retry on failure
   - Fallback to alternative endpoints
   - Backend proxy as last resort
   - Cache fallback if all else fails

### Step 4: Monitor Backend Health

Open a new terminal and check the health status:

```bash
curl http://localhost:8000/api/crypto-hub/health-status
```

You'll see:

```json
{
  "total": 0,
  "healthy": 0,
  "degraded": 0,
  "unhealthy": 0,
  "health_percentage": 0,
  "failed_endpoints": 0,
  "endpoints": {},
  "timestamp": "2025-11-27T10:00:00Z"
}
```

*Note: Endpoints will be registered as you use them.*

### Step 5: Test Backend Proxy

Test the proxy endpoint:

```bash
curl -X POST http://localhost:8000/api/crypto-hub/proxy \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
    "method": "GET"
  }'
```

### Step 6: View Diagnostics

```bash
curl http://localhost:8000/api/crypto-hub/diagnostics
```

## Understanding the Self-Healing Flow

When you make an API request, the system follows this flow:

```
1. Try Primary Endpoint
   ├─ Success → Return data
   └─ Failure → Step 2

2. Retry with Exponential Backoff (3 attempts)
   ├─ Success → Return data
   └─ Failure → Step 3

3. Try Fallback Endpoints
   ├─ Success → Return data (marked as 'fallback')
   └─ Failure → Step 4

4. Try Backend Proxy
   ├─ Success → Return data (marked as 'backend-proxy')
   └─ Failure → Step 5

5. Use Stale Cache (if available)
   ├─ Success → Return data (marked as 'stale-cache' with warning)
   └─ Failure → Return error with suggestions
```

## Configuration

### Frontend Configuration

Edit `/static/crypto-api-hub-stunning.html` and modify the configuration:

```javascript
const selfHealing = new SelfHealingAPIHub({
    backendUrl: '/api/crypto-hub',      // Backend API URL
    enableAutoRecovery: true,            // Enable auto recovery
    enableCaching: true,                 // Enable caching
    retryAttempts: 3,                    // Number of retries
    retryDelay: 1000,                    // Initial delay (ms)
    healthCheckInterval: 60000,          // Health check interval (ms)
    cacheExpiry: 300000                  // Cache expiry time (ms)
});
```

### Backend Configuration

Edit `/backend/routers/crypto_api_hub_self_healing.py`:

```python
# Monitoring configuration
monitor = CryptoHubMonitor(
    check_interval=60,        # Health check every 60 seconds
    timeout=10,               # Request timeout
    max_retries=3,            # Max retry attempts
    alert_threshold=5         # Alert after 5 failures
)
```

## Common Use Cases

### Use Case 1: Handling API Outages

**Scenario:** CoinGecko API is down

**What happens:**
1. Primary request to CoinGecko fails
2. System retries 3 times with exponential backoff
3. Falls back to CoinPaprika or CoinCap
4. If those fail, proxies through backend
5. If all fail, returns cached data (if available)

**Result:** Your application continues to work!

### Use Case 2: Slow API Responses

**Scenario:** External API is responding slowly

**What happens:**
1. Request times out after 10 seconds
2. System immediately retries with cached data if available
3. Logs slow response for monitoring
4. Adjusts health status to "degraded"

**Result:** Fast failover to cached or alternative data

### Use Case 3: Rate Limiting

**Scenario:** You hit an API rate limit

**What happens:**
1. Primary endpoint returns 429 (Too Many Requests)
2. System immediately tries fallback endpoint
3. Different API provider doesn't have same rate limit
4. Request succeeds

**Result:** Transparent fallback to alternative provider

## Testing Self-Healing

### Test 1: Simulate API Failure

Modify the HTML to test with a failing endpoint:

```javascript
// In browser console
const result = await selfHealing.fetchWithRecovery(
    'https://nonexistent-api.example.com/data'
);
console.log(result);
// Will show multiple retry attempts and eventual failure handling
```

### Test 2: Test Cache

```javascript
// Make a request to populate cache
const result1 = await selfHealing.fetchWithRecovery(
    'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
);

// Make the same request again - should use cache
const result2 = await selfHealing.fetchWithRecovery(
    'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
);

console.log('First call source:', result1.source);   // 'primary'
console.log('Second call source:', result2.source);  // Uses cache (faster)
```

### Test 3: Manual Recovery

```bash
# Trigger manual recovery for an endpoint
curl -X POST http://localhost:8000/api/crypto-hub/recover \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "https://api.coingecko.com/api/v3"}'
```

## Monitoring Dashboard

### View Real-Time Health

Access the diagnostics endpoint:

```bash
# Get health summary
curl http://localhost:8000/api/crypto-hub/health-status | jq

# Get detailed diagnostics
curl http://localhost:8000/api/crypto-hub/diagnostics | jq
```

### Export Reports

```bash
# Export diagnostics report
curl http://localhost:8000/api/crypto-hub/diagnostics > report-$(date +%Y%m%d).json
```

## Troubleshooting

### Problem: Server won't start

**Solution:**
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Kill the process if needed
kill -9 <PID>

# Or use a different port
uvicorn hf_unified_server:app --port 8080
```

### Problem: Frontend not loading

**Solution:**
1. Check browser console for errors
2. Verify `/static/crypto-api-hub-stunning.html` exists
3. Verify `/static/js/crypto-api-hub-self-healing.js` exists
4. Check server logs for errors

### Problem: Self-healing not working

**Solution:**
1. Check browser console for JavaScript errors
2. Verify `SelfHealingAPIHub` class is loaded
3. Check backend is accessible
4. Review backend logs

### Problem: All requests fail

**Solution:**
1. Check internet connectivity
2. Verify API keys (if required)
3. Check CORS settings
4. Review backend proxy configuration

## Advanced Features

### Custom Fallback Mapping

```javascript
// Define custom fallback logic
selfHealing.getFallbackEndpoints = function(url) {
    if (url.includes('coingecko')) {
        return [
            'https://api.coinpaprika.com/v1/tickers',
            'https://api.coincap.io/v2/assets'
        ];
    }
    return [];
};
```

### Custom Health Checks

```javascript
// Add custom health check logic
selfHealing.checkEndpointHealth = async function(endpoint) {
    // Custom health check implementation
    const response = await fetch(endpoint, { method: 'HEAD' });
    return response.ok;
};
```

### Custom Cache Strategy

```javascript
// Implement custom cache strategy
selfHealing.setCache = function(key, data) {
    // Custom cache implementation
    localStorage.setItem(key, JSON.stringify({
        data,
        timestamp: Date.now()
    }));
};

selfHealing.getFromCache = function(key) {
    // Custom cache retrieval
    const cached = localStorage.getItem(key);
    if (cached) {
        const parsed = JSON.parse(cached);
        return parsed.data;
    }
    return null;
};
```

## Performance Tips

1. **Enable Caching**: Reduces API calls and improves response time
2. **Adjust Retry Delays**: Balance between recovery speed and server load
3. **Set Appropriate Timeouts**: Prevent long-hanging requests
4. **Monitor Health Regularly**: Catch issues early
5. **Use Fallbacks**: Define fallback endpoints for critical services

## Security Considerations

1. **API Keys**: Store securely, never expose in frontend
2. **CORS**: Configure properly for your domain
3. **Rate Limiting**: Implement to prevent abuse
4. **Validation**: Validate all inputs
5. **Logging**: Log security-relevant events

## Next Steps

1. **Read the Full Guide**: See `/docs/CRYPTO_HUB_SELF_HEALING_GUIDE.md`
2. **Customize Configuration**: Adjust settings for your needs
3. **Add More Endpoints**: Register more APIs for monitoring
4. **Set Up Alerts**: Configure alerts for critical failures
5. **Monitor Performance**: Use diagnostics to optimize

## Support

For help:
- Check the full documentation
- Review code comments
- Check server logs
- Contact support team

---

**Quick Start Version:** 1.0.0  
**Last Updated:** November 27, 2025
