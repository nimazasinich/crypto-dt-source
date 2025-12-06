# Crypto API Hub Self-Healing System Guide

## Overview

The **Crypto API Hub Self-Healing System** is an advanced, intelligent monitoring and recovery framework designed to ensure maximum uptime and reliability for cryptocurrency data services. This system automatically detects failures, attempts recovery, and provides fallback mechanisms to maintain service continuity.

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Components](#components)
4. [Getting Started](#getting-started)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [API Reference](#api-reference)
8. [Monitoring & Diagnostics](#monitoring--diagnostics)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

## Features

### Core Features

- **🔄 Automatic Recovery**: Automatically detects and recovers from API failures
- **🔁 Retry Logic**: Exponential backoff retry mechanism for failed requests
- **📊 Health Monitoring**: Continuous health checks for all registered endpoints
- **💾 Intelligent Caching**: Smart caching system to provide data during outages
- **🎯 Fallback Endpoints**: Automatic fallback to alternative data sources
- **🔌 Backend Proxy**: Last-resort proxy through backend when direct calls fail
- **📈 Real-time Statistics**: Comprehensive monitoring and reporting
- **🚨 Alert System**: Automatic alerts for critical failures
- **🧹 Self-Cleanup**: Automatic cleanup of old failure records
- **📝 Detailed Logging**: Complete audit trail of all operations

### Advanced Features

- **Multi-Strategy Recovery**: Multiple recovery strategies (simple retry, modified headers, GET fallback)
- **Response Time Tracking**: Monitor and analyze API performance
- **Failure Pattern Detection**: Identify recurring issues
- **Stale Data Recovery**: Use cached data as last resort
- **Configurable Thresholds**: Customize behavior for your needs

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Application                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         crypto-api-hub-stunning.html                  │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │   SelfHealingAPIHub (JavaScript Module)         │ │  │
│  │  │   - Automatic retry logic                       │ │  │
│  │  │   - Client-side caching                         │ │  │
│  │  │   - Fallback management                         │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Backend Services                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  crypto_api_hub_self_healing.py (FastAPI Router)     │  │
│  │  - /api/crypto-hub/ (serve page)                     │  │
│  │  - /api/crypto-hub/proxy (proxy requests)            │  │
│  │  - /api/crypto-hub/health-check                      │  │
│  │  - /api/crypto-hub/diagnostics                       │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  crypto_hub_monitoring.py (Monitoring Service)       │  │
│  │  - Continuous health monitoring                      │  │
│  │  - Automatic recovery attempts                       │  │
│  │  - Statistics collection                             │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   External APIs                              │
│  • CoinGecko        • Etherscan       • Binance             │
│  • CoinMarketCap    • BscScan         • CryptoPanic         │
│  • And 70+ more crypto data sources                         │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Frontend Self-Healing Module

**File**: `/static/js/crypto-api-hub-self-healing.js`

The JavaScript module that handles client-side self-healing:

```javascript
const selfHealing = new SelfHealingAPIHub({
    backendUrl: '/api/crypto-hub',
    enableAutoRecovery: true,
    enableCaching: true,
    retryAttempts: 3,
    healthCheckInterval: 60000
});
```

#### Key Methods

- `fetchWithRecovery(url, options)`: Fetch with automatic retry and fallback
- `performHealthChecks()`: Run health checks on all endpoints
- `getHealthStatus()`: Get current system health
- `getDiagnostics()`: Get detailed diagnostics

### 2. Backend Router

**File**: `/backend/routers/crypto_api_hub_self_healing.py`

FastAPI router providing backend support:

#### Endpoints

- `GET /api/crypto-hub/`: Serve the self-healing crypto hub page
- `POST /api/crypto-hub/proxy`: Proxy API requests with retry logic
- `POST /api/crypto-hub/health-check`: Perform health checks
- `GET /api/crypto-hub/health-status`: Get health status
- `POST /api/crypto-hub/recover`: Manually trigger recovery
- `GET /api/crypto-hub/diagnostics`: Get diagnostics
- `DELETE /api/crypto-hub/clear-failures`: Clear failure records

### 3. Monitoring Service

**File**: `/backend/services/crypto_hub_monitoring.py`

Background service for continuous monitoring:

#### Features

- Continuous endpoint monitoring
- Multiple recovery strategies
- Response time tracking
- Failure pattern analysis
- Automatic cleanup

## Getting Started

### Quick Start

1. **Start the server**:

```bash
python hf_unified_server.py
```

2. **Access the self-healing crypto hub**:

```
http://localhost:8000/api/crypto-hub/
```

3. **Monitor health status**:

```
http://localhost:8000/api/crypto-hub/health-status
```

### Integration Example

#### Frontend Integration

```html
<!-- Include the self-healing module -->
<script src="/static/js/crypto-api-hub-self-healing.js"></script>

<script>
    // Initialize self-healing system
    const selfHealing = new SelfHealingAPIHub({
        backendUrl: '/api/crypto-hub',
        retryAttempts: 3,
        retryDelay: 1000,
        healthCheckInterval: 60000,
        cacheExpiry: 300000
    });

    // Use self-healing fetch
    async function fetchCryptoData() {
        const result = await selfHealing.fetchWithRecovery(
            'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
            { method: 'GET' }
        );

        if (result.success) {
            console.log('Data:', result.data);
            console.log('Source:', result.source); // 'primary', 'fallback', 'backend-proxy', or 'stale-cache'
        } else {
            console.error('All recovery attempts failed:', result.error);
        }
    }

    // Check health status
    async function checkHealth() {
        const health = selfHealing.getHealthStatus();
        console.log(`System Health: ${health.healthPercentage}%`);
        console.log(`Healthy Endpoints: ${health.healthy}/${health.total}`);
    }

    // Start health monitoring
    selfHealing.startHealthMonitoring();
</script>
```

#### Backend Integration

```python
from backend.services.crypto_hub_monitoring import get_monitor

# Get monitor instance
monitor = get_monitor()

# Register endpoints for monitoring
monitor.register_endpoint('https://api.coingecko.com/api/v3', {
    'name': 'CoinGecko',
    'category': 'market'
})

# Start monitoring
await monitor.start()

# Get health summary
summary = monitor.get_health_summary()
print(f"Health: {summary['health_percentage']}%")

# Get endpoint details
details = monitor.get_endpoint_details('https://api.coingecko.com/api/v3')
print(f"Status: {details['status']}")
```

## Configuration

### Frontend Configuration

```javascript
const config = {
    // Backend API base URL
    backendUrl: '/api/crypto-hub',
    
    // Enable automatic recovery
    enableAutoRecovery: true,
    
    // Enable response caching
    enableCaching: true,
    
    // Number of retry attempts
    retryAttempts: 3,
    
    // Initial retry delay (ms)
    retryDelay: 1000,
    
    // Health check interval (ms)
    healthCheckInterval: 60000,
    
    // Cache expiry time (ms)
    cacheExpiry: 300000
};
```

### Backend Configuration

```python
# In backend/routers/crypto_api_hub_self_healing.py
monitor = CryptoHubMonitor(
    check_interval=60,        # Health check interval in seconds
    timeout=10,               # Request timeout in seconds
    max_retries=3,            # Maximum retry attempts
    alert_threshold=5         # Failures before alerting
)
```

## Usage

### Basic Usage

#### 1. Making Self-Healing API Calls

```javascript
// Simple GET request with self-healing
const result = await selfHealing.fetchWithRecovery(
    'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
);

if (result.success) {
    console.log('Bitcoin Price:', result.data.bitcoin.usd);
    
    // Check data source
    switch (result.source) {
        case 'primary':
            console.log('✅ Data from primary endpoint');
            break;
        case 'fallback':
            console.log('⚠️ Using fallback endpoint:', result.fallbackUrl);
            break;
        case 'backend-proxy':
            console.log('🔄 Data via backend proxy');
            break;
        case 'stale-cache':
            console.log('💾 Using stale cached data');
            break;
    }
}
```

#### 2. POST Request with Self-Healing

```javascript
const result = await selfHealing.fetchWithRecovery(
    'https://api.example.com/v1/data',
    {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer YOUR_TOKEN'
        },
        body: JSON.stringify({ key: 'value' })
    }
);
```

#### 3. Manual Health Checks

```javascript
// Check specific endpoint
const isHealthy = await selfHealing.checkEndpointHealth(
    'https://api.coingecko.com/api/v3'
);

if (isHealthy) {
    console.log('✅ Endpoint is healthy');
} else {
    console.log('❌ Endpoint is unhealthy');
}
```

#### 4. Trigger Manual Recovery

```javascript
const result = await selfHealing.triggerRecovery(
    'https://api.coingecko.com/api/v3'
);

if (result.success) {
    console.log('✅ Recovery successful');
} else {
    console.log('❌ Recovery failed');
}
```

### Advanced Usage

#### 1. Custom Fallback Mapping

```javascript
// Override fallback endpoint mapping
selfHealing.transformToFallback = function(originalUrl, fallbackBase) {
    if (originalUrl.includes('coingecko') && fallbackBase === 'coinpaprika') {
        // Transform CoinGecko URL to CoinPaprika format
        return 'https://api.coinpaprika.com/v1/tickers';
    }
    return null;
};
```

#### 2. Custom Cache Strategy

```javascript
// Set custom cache for specific data
selfHealing.setCache('my-custom-key', { 
    data: myData,
    metadata: { source: 'custom' }
});

// Retrieve cached data
const cached = selfHealing.getFromCache('my-custom-key');
```

#### 3. Export Diagnostics Report

```javascript
// Get comprehensive diagnostics
const diagnostics = selfHealing.getDiagnostics();

// Export as JSON
const blob = new Blob([JSON.stringify(diagnostics, null, 2)], { 
    type: 'application/json' 
});
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = `diagnostics-${Date.now()}.json`;
a.click();
```

## API Reference

### Frontend API

#### Class: `SelfHealingAPIHub`

##### Constructor

```javascript
new SelfHealingAPIHub(config)
```

**Parameters:**
- `config` (Object): Configuration options

**Returns:** SelfHealingAPIHub instance

##### Methods

###### `fetchWithRecovery(url, options)`

Fetch data with automatic retry and fallback mechanisms.

**Parameters:**
- `url` (String): Request URL
- `options` (Object): Fetch options

**Returns:** Promise<Object>
- `success` (Boolean): Whether request succeeded
- `data` (Any): Response data if successful
- `source` (String): Data source ('primary', 'fallback', 'backend-proxy', 'stale-cache')
- `error` (String): Error message if failed

###### `performHealthChecks()`

Perform health checks on all registered endpoints.

**Returns:** Promise<void>

###### `getHealthStatus()`

Get current system health status.

**Returns:** Object
- `total` (Number): Total monitored endpoints
- `healthy` (Number): Number of healthy endpoints
- `degraded` (Number): Number of degraded endpoints
- `unhealthy` (Number): Number of unhealthy endpoints
- `healthPercentage` (Number): Overall health percentage
- `failedEndpoints` (Number): Number of failed endpoints
- `cacheSize` (Number): Number of cached items

###### `getDiagnostics()`

Get detailed diagnostics information.

**Returns:** Object with health, failedEndpoints, cache, and config details

### Backend API

#### Endpoints

##### `GET /api/crypto-hub/`

Serve the self-healing crypto API hub page.

**Response:** HTML page with integrated self-healing

##### `POST /api/crypto-hub/proxy`

Proxy API requests with retry logic.

**Request Body:**
```json
{
    "url": "https://api.example.com/endpoint",
    "method": "GET",
    "headers": {},
    "body": null,
    "timeout": 10
}
```

**Response:**
```json
{
    "success": true,
    "status_code": 200,
    "data": {},
    "source": "proxy",
    "attempt": 1
}
```

##### `GET /api/crypto-hub/health-status`

Get current health status of all monitored endpoints.

**Response:**
```json
{
    "total": 74,
    "healthy": 68,
    "degraded": 3,
    "unhealthy": 3,
    "health_percentage": 92,
    "failed_endpoints": 3,
    "endpoints": {},
    "timestamp": "2025-11-27T10:00:00Z"
}
```

##### `POST /api/crypto-hub/recover`

Manually trigger recovery for a specific endpoint.

**Request Body:**
```json
{
    "endpoint": "https://api.example.com"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Endpoint recovered successfully",
    "endpoint": "https://api.example.com"
}
```

##### `GET /api/crypto-hub/diagnostics`

Get comprehensive diagnostics information.

**Response:**
```json
{
    "health": {},
    "failed_endpoints": [],
    "recovery_log": [],
    "timestamp": "2025-11-27T10:00:00Z"
}
```

## Monitoring & Diagnostics

### Real-Time Monitoring

The system provides real-time monitoring through multiple channels:

1. **Frontend Health Indicator**: Shows health percentage in the UI
2. **Console Logging**: Detailed logs for all operations
3. **Backend Metrics**: Comprehensive statistics collection

### Viewing Health Status

#### Frontend

```javascript
// Get current health
const health = selfHealing.getHealthStatus();
console.log(`Health: ${health.healthPercentage}%`);
console.log(`Healthy: ${health.healthy}/${health.total}`);
console.log(`Failed: ${health.failedEndpoints}`);
console.log(`Cache: ${health.cacheSize} items`);
```

#### Backend API

```bash
curl http://localhost:8000/api/crypto-hub/health-status
```

### Viewing Diagnostics

#### Frontend

```javascript
const diagnostics = selfHealing.getDiagnostics();
console.log('Diagnostics:', diagnostics);
```

#### Backend API

```bash
curl http://localhost:8000/api/crypto-hub/diagnostics
```

### Exporting Reports

```bash
# Export monitoring report
curl http://localhost:8000/api/crypto-hub/diagnostics > report.json
```

## Best Practices

### 1. Configuration

- **Set appropriate retry attempts**: Too many retries can cause delays, too few may not recover
- **Configure cache expiry**: Balance between freshness and availability
- **Set reasonable timeouts**: Prevent long-hanging requests

### 2. Monitoring

- **Check health status regularly**: Monitor the health indicator
- **Review diagnostics**: Periodically check diagnostics for patterns
- **Monitor cache usage**: Ensure cache isn't growing unbounded

### 3. Recovery

- **Use fallback endpoints**: Define fallback URLs for critical services
- **Implement custom transformations**: Map URLs between different providers
- **Log all failures**: Keep detailed logs for troubleshooting

### 4. Performance

- **Enable caching**: Reduce load on external APIs
- **Use health checks wisely**: Don't check too frequently
- **Clean up old data**: Regularly clean up expired cache and old failures

### 5. Security

- **Validate endpoints**: Only proxy to whitelisted domains
- **Secure API keys**: Don't expose keys in frontend code
- **Rate limiting**: Implement rate limiting to prevent abuse

## Troubleshooting

### Issue: All recovery attempts fail

**Symptoms:** No data source works, not even stale cache

**Solutions:**
1. Check internet connectivity
2. Verify API keys are valid
3. Check if external services are operational
4. Review CORS settings
5. Check backend proxy is running

### Issue: Slow response times

**Symptoms:** Requests take too long to complete

**Solutions:**
1. Reduce retry attempts
2. Decrease timeout values
3. Enable caching
4. Use fallback endpoints
5. Check external API performance

### Issue: High failure rate

**Symptoms:** Many endpoints showing as unhealthy

**Solutions:**
1. Check if external services are down
2. Verify API keys and authentication
3. Review rate limiting settings
4. Check network connectivity
5. Examine failure logs for patterns

### Issue: Cache not working

**Symptoms:** Every request hits the network

**Solutions:**
1. Verify `enableCaching` is true
2. Check cache expiry settings
3. Ensure method is 'GET'
4. Review cache key generation
5. Check browser storage limits

### Issue: Backend proxy not working

**Symptoms:** Fallback to proxy fails

**Solutions:**
1. Verify backend server is running
2. Check backend URL configuration
3. Review CORS settings
4. Check backend logs for errors
5. Verify proxy endpoint is accessible

## Support

For additional support:

- Check the GitHub repository issues
- Review the code documentation
- Contact the development team

## License

This self-healing system is part of the Crypto API Hub project.

---

**Last Updated:** November 27, 2025
**Version:** 1.0.0
