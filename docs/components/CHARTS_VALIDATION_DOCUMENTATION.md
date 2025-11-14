# Charts Validation & Hardening Documentation

## Overview

This document provides comprehensive documentation for the newly implemented chart endpoints with validation and security hardening.

## New Endpoints

### 1. `/api/charts/rate-limit-history`

**Purpose:** Retrieve hourly rate limit usage history for visualization in charts.

**Method:** `GET`

**Parameters:**

| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `hours` | integer | No | 24 | 1-168 | Hours of history to retrieve (clamped server-side) |
| `providers` | string | No | top 5 | max 5, comma-separated | Provider names to include |

**Response Schema:**

```json
[
  {
    "provider": "coingecko",
    "hours": 24,
    "series": [
      {
        "t": "2025-11-10T13:00:00Z",
        "pct": 42.5
      },
      {
        "t": "2025-11-10T14:00:00Z",
        "pct": 38.2
      }
    ],
    "meta": {
      "limit_type": "per_minute",
      "limit_value": 30
    }
  }
]
```

**Response Fields:**

- `provider` (string): Provider name
- `hours` (integer): Number of hours covered
- `series` (array): Time series data points
  - `t` (string): ISO 8601 timestamp with 'Z' suffix
  - `pct` (number): Rate limit usage percentage [0-100]
- `meta` (object): Rate limit metadata
  - `limit_type` (string): Type of limit (per_second, per_minute, per_hour, per_day)
  - `limit_value` (integer|null): Limit value, null if no limit configured

**Behavior:**

- Returns one series object per provider
- Each series contains exactly `hours` data points (one per hour)
- Hours without data are filled with `pct: 0.0`
- If provider has no rate limit configured, returns `meta.limit_value: null` and `pct: 0`
- Default: Returns up to 5 providers with configured rate limits
- Series ordered chronologically (oldest to newest)

**Examples:**

```bash
# Default: Last 24 hours, top 5 providers
curl "http://localhost:7860/api/charts/rate-limit-history"

# Custom: 48 hours, specific providers
curl "http://localhost:7860/api/charts/rate-limit-history?hours=48&providers=coingecko,cmc,etherscan"

# Single provider, 1 week
curl "http://localhost:7860/api/charts/rate-limit-history?hours=168&providers=binance"
```

**Error Responses:**

- `400 Bad Request`: Invalid provider name
  ```json
  {
    "detail": "Invalid provider name: invalid_xyz. Must be one of: ..."
  }
  ```
- `422 Unprocessable Entity`: Invalid parameter type
- `500 Internal Server Error`: Database or processing error

---

### 2. `/api/charts/freshness-history`

**Purpose:** Retrieve hourly data freshness/staleness history for visualization.

**Method:** `GET`

**Parameters:**

| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `hours` | integer | No | 24 | 1-168 | Hours of history to retrieve (clamped server-side) |
| `providers` | string | No | top 5 | max 5, comma-separated | Provider names to include |

**Response Schema:**

```json
[
  {
    "provider": "coingecko",
    "hours": 24,
    "series": [
      {
        "t": "2025-11-10T13:00:00Z",
        "staleness_min": 7.2,
        "ttl_min": 15,
        "status": "fresh"
      },
      {
        "t": "2025-11-10T14:00:00Z",
        "staleness_min": 999.0,
        "ttl_min": 15,
        "status": "stale"
      }
    ],
    "meta": {
      "category": "market_data",
      "default_ttl": 1
    }
  }
]
```

**Response Fields:**

- `provider` (string): Provider name
- `hours` (integer): Number of hours covered
- `series` (array): Time series data points
  - `t` (string): ISO 8601 timestamp with 'Z' suffix
  - `staleness_min` (number): Data staleness in minutes (999.0 indicates no data)
  - `ttl_min` (integer): TTL threshold for this provider's category
  - `status` (string): Derived status: "fresh", "aging", or "stale"
- `meta` (object): Provider metadata
  - `category` (string): Provider category
  - `default_ttl` (integer): Default TTL for category (minutes)

**Status Derivation:**

```
fresh:  staleness_min <= ttl_min
aging:  ttl_min < staleness_min <= ttl_min * 2
stale:  staleness_min > ttl_min * 2  OR  no data (999.0)
```

**TTL by Category:**

| Category | TTL (minutes) |
|----------|---------------|
| market_data | 1 |
| blockchain_explorers | 5 |
| defi | 10 |
| news | 15 |
| default | 5 |

**Behavior:**

- Returns one series object per provider
- Each series contains exactly `hours` data points (one per hour)
- Hours without data are marked with `staleness_min: 999.0` and `status: "stale"`
- Default: Returns up to 5 most active providers
- Series ordered chronologically (oldest to newest)

**Examples:**

```bash
# Default: Last 24 hours, top 5 providers
curl "http://localhost:7860/api/charts/freshness-history"

# Custom: 72 hours, specific providers
curl "http://localhost:7860/api/charts/freshness-history?hours=72&providers=coingecko,binance"

# Single provider, 3 days
curl "http://localhost:7860/api/charts/freshness-history?hours=72&providers=etherscan"
```

**Error Responses:**

- `400 Bad Request`: Invalid provider name
- `422 Unprocessable Entity`: Invalid parameter type
- `500 Internal Server Error`: Database or processing error

---

## Security & Validation

### Input Validation

1. **Hours Parameter:**
   - Server-side clamping: `1 <= hours <= 168`
   - Invalid types rejected with `422 Unprocessable Entity`
   - Out-of-range values automatically clamped (no error)

2. **Providers Parameter:**
   - Allow-list enforcement: Only valid provider names accepted
   - Max 5 providers enforced (excess silently truncated)
   - Invalid names trigger `400 Bad Request` with detailed error
   - SQL injection prevention: No raw SQL, parameterized queries only
   - XSS prevention: Input sanitized (strip whitespace)

3. **Rate Limiting (Recommended):**
   - Implement: 60 requests/minute per IP for chart routes
   - Use middleware or reverse proxy (nginx/cloudflare)

### Security Measures Implemented

✓ Allow-list validation for provider names
✓ Parameter clamping (hours: 1-168)
✓ Max provider limit (5)
✓ SQL injection prevention (ORM with parameterized queries)
✓ XSS prevention (input sanitization)
✓ Comprehensive error handling with safe error messages
✓ Logging of all chart requests for monitoring
✓ No sensitive data exposure in responses

### Edge Cases Handled

- Empty provider list → Returns default providers
- Unknown provider → 400 with valid options listed
- Hours out of bounds → Clamped to [1, 168]
- No data available → Returns empty series or 999.0 staleness
- Provider with no rate limit → Returns null limit_value
- Whitespace in provider names → Trimmed automatically
- Mixed valid/invalid providers → Rejects entire request

---

## Testing

### Automated Tests

Run the comprehensive test suite:

```bash
# Run all chart tests
pytest tests/test_charts.py -v

# Run specific test class
pytest tests/test_charts.py::TestRateLimitHistory -v

# Run with coverage
pytest tests/test_charts.py --cov=api --cov-report=html
```

**Test Coverage:**

- ✓ Default parameter behavior
- ✓ Custom time ranges (48h, 72h)
- ✓ Provider selection and filtering
- ✓ Response schema validation
- ✓ Percentage range validation [0-100]
- ✓ Timestamp format validation
- ✓ Status derivation logic
- ✓ Edge cases (invalid providers, hours clamping)
- ✓ Security (SQL injection, XSS prevention)
- ✓ Performance (response time < 500ms)
- ✓ Concurrent request handling

### Manual Sanity Checks

Run the CLI sanity check script:

```bash
# Ensure backend is running
python app.py &

# Run sanity checks
./tests/sanity_checks.sh
```

**Checks performed:**

1. Rate limit history (default params)
2. Freshness history (default params)
3. Custom time ranges
4. Response schema validation
5. Invalid provider rejection
6. Hours parameter clamping
7. Performance measurement
8. Edge case handling

---

## Performance Targets

### Response Time (P95)

| Environment | Target | Conditions |
|-------------|--------|------------|
| Production | < 200ms | 24h / 5 providers |
| Development | < 500ms | 24h / 5 providers |

### Optimization Strategies

1. **Database Indexing:**
   - Indexed: `timestamp`, `provider_id` columns
   - Composite indexes on frequently queried combinations

2. **Query Optimization:**
   - Hourly bucketing done in-memory (fast)
   - Limited to 168 hours max (1 week)
   - Provider limit enforced early (max 5)

3. **Caching (Future Enhancement):**
   - Consider Redis cache for 1-minute TTL
   - Cache key: `chart:type:hours:providers`
   - Invalidate on new data ingestion

4. **Connection Pooling:**
   - SQLAlchemy pool size: 10
   - Max overflow: 20
   - Recycle connections every 3600s

---

## Observability & Monitoring

### Logging

All chart requests are logged with:

```json
{
  "timestamp": "2025-11-11T01:00:00Z",
  "level": "INFO",
  "logger": "api_endpoints",
  "message": "Rate limit history: 3 providers, 48h"
}
```

### Recommended Metrics (Prometheus/Grafana)

```python
# Counter: Total requests per endpoint
chart_requests_total{endpoint="rate_limit_history"} 1523

# Histogram: Response time distribution
chart_response_time_seconds{endpoint="rate_limit_history", le="0.1"} 1450
chart_response_time_seconds{endpoint="rate_limit_history", le="0.2"} 1510

# Gauge: Current rate limit usage per provider
ratelimit_usage_pct{provider="coingecko"} 87.5

# Gauge: Freshness staleness per provider
freshness_staleness_min{provider="binance"} 3.2

# Counter: Invalid request count
chart_invalid_requests_total{endpoint="rate_limit_history", reason="invalid_provider"} 23
```

### Recommended Alerts

```yaml
# Critical: Rate limit exhaustion
- alert: RateLimitExhaustion
  expr: ratelimit_usage_pct > 90
  for: 3h
  annotations:
    summary: "Provider {{ $labels.provider }} at {{ $value }}% rate limit"
    action: "Add API keys or reduce request frequency"

# Critical: Data staleness
- alert: DataStale
  expr: freshness_staleness_min > ttl_min
  for: 15m
  annotations:
    summary: "Provider {{ $labels.provider }} data is stale ({{ $value }}m old)"
    action: "Check scheduler, verify API connectivity"

# Warning: Chart endpoint slow
- alert: ChartEndpointSlow
  expr: histogram_quantile(0.95, chart_response_time_seconds) > 0.2
  for: 10m
  annotations:
    summary: "Chart endpoint P95 latency above 200ms"
    action: "Check database query performance"
```

---

## Database Schema

### Tables Used

**RateLimitUsage**
```sql
CREATE TABLE rate_limit_usage (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME NOT NULL,  -- INDEXED
    provider_id INTEGER NOT NULL,  -- FOREIGN KEY, INDEXED
    limit_type VARCHAR(20),
    limit_value INTEGER,
    current_usage INTEGER,
    percentage REAL,
    reset_time DATETIME
);
```

**DataCollection**
```sql
CREATE TABLE data_collection (
    id INTEGER PRIMARY KEY,
    provider_id INTEGER NOT NULL,  -- FOREIGN KEY, INDEXED
    actual_fetch_time DATETIME NOT NULL,
    data_timestamp DATETIME,
    staleness_minutes REAL,
    record_count INTEGER,
    on_schedule BOOLEAN
);
```

---

## Frontend Integration

### Chart.js Example (Rate Limit)

```javascript
// Fetch rate limit history
const response = await fetch('/api/charts/rate-limit-history?hours=48&providers=coingecko,cmc');
const data = await response.json();

// Build Chart.js dataset
const datasets = data.map(series => ({
    label: series.provider,
    data: series.series.map(p => ({
        x: new Date(p.t),
        y: p.pct
    })),
    borderColor: getColorForProvider(series.provider),
    tension: 0.3
}));

// Create chart
new Chart(ctx, {
    type: 'line',
    data: { datasets },
    options: {
        scales: {
            x: { type: 'time', time: { unit: 'hour' } },
            y: { min: 0, max: 100, title: { text: 'Usage %' } }
        },
        interaction: { mode: 'index', intersect: false },
        plugins: {
            legend: { display: true, position: 'bottom' },
            tooltip: {
                callbacks: {
                    label: ctx => `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(1)}%`
                }
            }
        }
    }
});
```

### Chart.js Example (Freshness)

```javascript
// Fetch freshness history
const response = await fetch('/api/charts/freshness-history?hours=72&providers=binance');
const data = await response.json();

// Build datasets with status-based colors
const datasets = data.map(series => ({
    label: series.provider,
    data: series.series.map(p => ({
        x: new Date(p.t),
        y: p.staleness_min,
        status: p.status
    })),
    borderColor: getColorForProvider(series.provider),
    segment: {
        borderColor: ctx => {
            const point = ctx.p1.$context.raw;
            return point.status === 'fresh' ? 'green'
                 : point.status === 'aging' ? 'orange'
                 : 'red';
        }
    }
}));

// Create chart with TTL reference line
new Chart(ctx, {
    type: 'line',
    data: { datasets },
    options: {
        scales: {
            x: { type: 'time' },
            y: { title: { text: 'Staleness (min)' } }
        },
        plugins: {
            annotation: {
                annotations: {
                    ttl: {
                        type: 'line',
                        yMin: data[0].meta.default_ttl,
                        yMax: data[0].meta.default_ttl,
                        borderColor: 'rgba(255, 99, 132, 0.5)',
                        borderWidth: 2,
                        label: { content: 'TTL Threshold', enabled: true }
                    }
                }
            }
        }
    }
});
```

---

## Troubleshooting

### Common Issues

**1. Empty series returned**

- Check if providers have data in the time range
- Verify provider names are correct (case-sensitive)
- Ensure database has historical data

**2. Response time > 500ms**

- Check database indexes exist
- Reduce `hours` parameter
- Limit number of providers
- Consider adding caching layer

**3. 400 Bad Request on valid provider**

- Verify provider is in database: `SELECT name FROM providers`
- Check for typos or case mismatch
- Ensure provider has not been renamed

**4. Missing data points (gaps in series)**

- Normal behavior: gaps filled with zeros/999.0
- Check data collection scheduler is running
- Review logs for collection failures

---

## Changelog

### v1.0.0 - 2025-11-11

**Added:**
- `/api/charts/rate-limit-history` endpoint
- `/api/charts/freshness-history` endpoint
- Comprehensive input validation
- Security hardening (allow-list, clamping, sanitization)
- Automated test suite (pytest)
- CLI sanity check script
- Full API documentation

**Security:**
- SQL injection prevention
- XSS prevention
- Parameter validation and clamping
- Allow-list enforcement for providers
- Max provider limit (5)

**Testing:**
- 20+ automated tests
- Schema validation tests
- Security tests
- Performance tests
- Edge case coverage

---

## Future Enhancements

### Phase 2 (Optional)

1. **Provider Picker UI Component**
   - Dropdown with multi-select (max 5)
   - Persist selection in localStorage
   - Auto-refresh on selection change

2. **Advanced Filtering**
   - Filter by category
   - Filter by rate limit status (ok/warning/critical)
   - Filter by freshness status (fresh/aging/stale)

3. **Aggregation Options**
   - Category-level aggregation
   - System-wide average/percentile
   - Compare providers side-by-side

4. **Export Functionality**
   - CSV export
   - JSON export
   - PNG/SVG chart export

5. **Real-time Updates**
   - WebSocket streaming for live updates
   - Auto-refresh without flicker
   - Smooth transitions on new data

6. **Historical Analysis**
   - Trend detection (improving/degrading)
   - Anomaly detection
   - Predictive alerts

---

## Support & Maintenance

### Code Location

- Endpoints: `api/endpoints.py` (lines 947-1250)
- Tests: `tests/test_charts.py`
- Sanity checks: `tests/sanity_checks.sh`
- Documentation: `CHARTS_VALIDATION_DOCUMENTATION.md`

### Contact

For issues or questions:
- Create GitHub issue with `[charts]` prefix
- Tag: `enhancement`, `bug`, or `documentation`
- Provide: Request details, expected vs actual behavior, logs

---

## License

Same as parent project.
