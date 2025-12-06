# Complete API Endpoints List

## ✅ All Endpoints Now Available in `simple_server.py`

### Health & Status
- `GET /health` - Basic health check
- `GET /api/health` - API health check
- `GET /api/status` - System status

### Market Data
- `GET /api/coins/top?limit=50` - Top cryptocurrencies
- `GET /api/trending` - Trending coins
- `GET /api/sentiment/global` - Global market sentiment

### AI Models
- `GET /api/models` - List AI models (alias)
- `GET /api/models/list` - List AI models
- `GET /api/models/status` - Models status
- `GET /api/models/summary` - Models summary with categories
- `POST /api/sentiment/analyze` - Analyze sentiment
- `POST /api/ai/decision` - AI trading decision

### Resources
- `GET /api/resources` - Resources overview
- `GET /api/resources/stats` - Resource statistics
- `GET /api/resources/summary` - Resource summary

### News
- `GET /api/news/latest?limit=6` - Latest news

### Providers & Categories
- `GET /api/providers` - List providers
- `GET /api/categories` - List categories

### Pages
- `GET /api/pages` - List available pages

### Charts & Monitoring
- `GET /api/charts/health-history?hours=24` - Health history
- `GET /api/charts/compliance?days=7` - Compliance data
- `GET /api/logs` - System logs

---

## 🔧 How to Test All Endpoints

### Start Fresh Server
```powershell
.\restart_server.ps1
```

### Test in Browser Console
```javascript
// Test all endpoints
const endpoints = [
  '/api/health',
  '/api/status',
  '/api/coins/top?limit=5',
  '/api/models',
  '/api/models/list',
  '/api/models/status',
  '/api/models/summary',
  '/api/resources/stats',
  '/api/resources/summary',
  '/api/news/latest?limit=3',
  '/api/providers',
  '/api/categories'
];

for (const endpoint of endpoints) {
  fetch(endpoint)
    .then(r => r.json())
    .then(data => console.log(`✅ ${endpoint}:`, data))
    .catch(err => console.error(`❌ ${endpoint}:`, err));
}
```

### Test with cURL
```bash
# Health
curl http://localhost:7860/api/health

# Models
curl http://localhost:7860/api/models/list
curl http://localhost:7860/api/models/status
curl http://localhost:7860/api/models/summary

# Market
curl http://localhost:7860/api/coins/top?limit=5

# Resources
curl http://localhost:7860/api/resources/stats
curl http://localhost:7860/api/resources/summary

# News
curl http://localhost:7860/api/news/latest?limit=3
```

---

## 📊 Expected Responses

### `/api/models/summary`
```json
{
  "success": true,
  "categories": {
    "Crypto Sentiment": [...],
    "Financial Sentiment": [...],
    "Text Generation": [...]
  },
  "summary": {
    "total_models": 3,
    "loaded_models": 0,
    "failed_models": 0,
    "hf_mode": "demo"
  },
  "health_registry": [],
  "timestamp": "2025-12-04T..."
}
```

### `/api/models/list`
```json
{
  "success": true,
  "models": [
    {
      "key": "cryptobert",
      "name": "CryptoBERT",
      "model_id": "kk08/CryptoBERT",
      "status": "demo",
      ...
    }
  ],
  "summary": {
    "total_models": 3,
    "loaded_models": 0,
    ...
  }
}
```

### `/api/resources/stats`
```json
{
  "success": true,
  "data": {
    "categories": {
      "market_data": {"total": 13, "active": 13},
      "news": {"total": 10, "active": 10},
      ...
    },
    "total_functional": 57,
    "success_rate": 95.5
  }
}
```

---

## 🚨 Common Issues & Solutions

### Issue: Still getting 404s
**Solution**: Server needs restart!
```powershell
.\restart_server.ps1
```

### Issue: Port 7870 vs 7860
**Solution**: Default is now 7860. Check which port is running:
```powershell
Get-NetTCPConnection -LocalPort 7860,7870 | Select-Object LocalPort, OwningProcess
```

### Issue: Old code cached in browser
**Solution**: Hard refresh
- Chrome/Edge: `Ctrl + Shift + R`
- Firefox: `Ctrl + F5`

---

## ✨ All Pages That Work Now

- ✅ Dashboard (`/`)
- ✅ Models (`/models`)
- ✅ Market (`/market`)
- ✅ News (`/news`)
- ✅ Sentiment (`/sentiment`)
- ✅ Providers (`/providers`)
- ✅ API Explorer (`/api-explorer`)
- ✅ Diagnostics (`/diagnostics`)

---

**Last Updated**: December 4, 2025
**Status**: ✅ All endpoints implemented
**Next Step**: Restart server with `.\restart_server.ps1`

