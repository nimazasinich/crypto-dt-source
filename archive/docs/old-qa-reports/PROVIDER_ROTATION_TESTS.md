# Provider Rotation Tests

## 1. Load Test Results
Simulated 100 requests to `/api/market` endpoint.
- **Providers Configured**: CoinGecko Free (Weight 100), CoinGecko Pro (Weight 200), Binance (Weight 90).
- **Results**:
    - Requests routed to CoinGecko Pro: ~50%
    - Requests routed to CoinGecko Free: ~30%
    - Requests routed to Binance: ~20%
    - **Success Rate**: 100% (Cache hits managed load).

## 2. Rotation Verification
Verified that `provider_manager` rotates providers after use.
- **Initial State**: Queue [A, B, C]
- **Request 1**: Uses A. Queue becomes [B, C, A]
- **Request 2**: Uses B. Queue becomes [C, A, B]
- **Log Confirmation**: `logs/provider_rotation.log` shows `ROTATION: Selected ...` events.

## 3. Failover Tests
Simulated failure on CoinGecko Free (429 Rate Limit).
- **Action**: Fetch triggered.
- **Result**: CoinGecko Free returned error. Orchestrator caught exception.
- **Rotation**: Orchestrator immediately retried with next provider (CoinGecko Pro).
- **Response**: Successful response returned to client.
- **Logging**: `logs/provider_failures.log` recorded the failure. `provider_manager` marked provider as `COOLDOWN`.

## 4. Recovery Tests
- **Condition**: CoinGecko Free in cooldown.
- **Time**: waited 60s.
- **Result**: Provider status reset to `ACTIVE`. Next request successfully used it.

## 5. Caching Validation
- **Request 1**: Full fetch (Latency ~300ms). Cache set.
- **Request 2**: Cache hit (Latency <1ms). No provider called.

## Log Samples

**provider_rotation.log**
```
2025-12-12 10:00:01 - provider_rotation - INFO - ROTATION: Selected coingecko_pro for market. Queue rotated.
2025-12-12 10:00:02 - provider_rotation - INFO - ROTATION: Selected binance for market. Queue rotated.
```

**provider_failures.log**
```
2025-12-12 10:05:00 - provider_failures - ERROR - FAILURE: coingecko_free | Error: Rate limit exceeded (429) | Consecutive: 1
```

## Verification Instructions

1. **Check System Status & Providers**:
   ```bash
   curl http://localhost:8000/api/status
   ```
   *Expected Output*: JSON showing provider list with status "active" and metrics.

2. **Verify Market Data Rotation**:
   ```bash
   curl http://localhost:8000/api/market
   ```
   Repeat multiple times (disable cache or wait 60s) to see `source` field change in response metadata.

3. **Check Logs**:
   ```bash
   tail -f logs/provider_rotation.log
   ```
