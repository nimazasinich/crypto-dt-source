---
title: Crypto API Monitor
emoji: 📊
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.14.0
app_file: app_gradio.py
pinned: false
license: mit
---

# 📊 Cryptocurrency API Monitor

> **Production-ready real-time health monitoring for 162+ cryptocurrency API endpoints**

A comprehensive monitoring dashboard that tracks the health, uptime, and performance of cryptocurrency APIs including block explorers, market data providers, RPC nodes, news sources, and more.

## 🌟 Features

### Core Capabilities
- **Real-Time Monitoring**: Async health checks for 162+ API endpoints
- **Multi-Tier Classification**: Critical (Tier 1), Important (Tier 2), and Others (Tier 3)
- **Persistent Storage**: SQLite database for historical metrics and incident tracking
- **Auto-Refresh**: Configurable background scheduler (1-60 minute intervals)
- **Category Organization**: Block Explorers, Market Data, RPC Nodes, News, Sentiment, etc.
- **Export Functionality**: Download status reports as CSV

### 5-Tab Interface

#### 📊 Tab 1: Real-Time Dashboard
- Live status grid with color-coded health badges (🟢🟡🔴)
- Summary cards: Total APIs, Online %, Critical Issues, Avg Response Time
- Advanced filtering: By category, status, or tier
- One-click CSV export
- Response time tracking per provider

#### 📁 Tab 2: Category View
- Accordion-style category breakdown
- Availability percentage per category
- Visual progress bars
- Average response time per category
- Interactive Plotly charts with dual-axis (availability + response time)

#### 📈 Tab 3: Health History
- Uptime percentage trends (last 1-168 hours)
- Response time evolution charts
- Incident log with timestamps and severity
- Per-provider detailed history
- Automatic data retention (24-hour rolling window)

#### 🔧 Tab 4: Test Endpoint
- Interactive endpoint testing
- Custom endpoint override support
- CORS proxy toggle
- Example queries for each provider
- Formatted JSON responses
- Troubleshooting hints for common errors (403, 429, timeout)

#### ⚙️ Tab 5: Configuration
- Refresh interval slider (1-60 minutes)
- Cache management controls
- Configuration statistics overview
- API key management instructions
- Scheduler status display

### Advanced Features
- **Async Architecture**: Concurrent health checks with semaphore-based rate limiting
- **Exponential Backoff**: Automatic retry logic for failed checks
- **Staggered Requests**: 0.1s delay between checks to respect rate limits
- **Caching**: 1-minute response cache to reduce API load
- **Incident Detection**: Automatic incident creation for Tier 1 outages
- **Alert System**: Database-backed alerting for critical issues
- **Data Aggregation**: Hourly response time rollups
- **Auto-Cleanup**: 7-day data retention policy

## 🚀 Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/nimazasinich/crypto-dt-source.git
cd crypto-dt-source

# Install dependencies
pip install -r requirements.txt

# Run the application
python app_gradio.py
```

Visit `http://localhost:7860` to access the dashboard.

### Hugging Face Spaces Deployment

1. **Create a new Space** on Hugging Face
2. **Link this GitHub repository** (Settings > Linked repositories)
3. **Set SDK to Gradio** in Space settings
4. **Configure app_file**: `app_gradio.py`
5. **Add API keys** as Space secrets (Settings > Repository secrets):
   - `ETHERSCAN_KEY`
   - `BSCSCAN_KEY`
   - `TRONSCAN_KEY`
   - `CMC_KEY` (CoinMarketCap)
   - `CRYPTOCOMPARE_KEY`
   - `NEWSAPI_KEY`

6. **Push to main branch** - Auto-deploy triggers!

## 📦 Project Structure

```
crypto-dt-source/
├── app_gradio.py                    # Main Gradio application
├── config.py                        # Configuration & JSON loader
├── monitor.py                       # Async health check engine
├── database.py                      # SQLite persistence layer
├── scheduler.py                     # Background job scheduler
├── requirements.txt                 # Python dependencies
├── ultimate_crypto_pipeline_2025_NZasinich.json  # API registry
├── all_apis_merged_2025.json       # Merged API resources
├── data/                            # SQLite database & exports
│   └── health_metrics.db
└── README_HF_SPACES.md             # This file
```

## 🔧 Configuration

### Environment Variables

All API keys are loaded from environment variables:

```bash
ETHERSCAN_KEY=your_key_here
BSCSCAN_KEY=your_key_here
TRONSCAN_KEY=your_key_here
CMC_KEY=your_coinmarketcap_key
CRYPTOCOMPARE_KEY=your_key_here
NEWSAPI_KEY=your_key_here
```

### Scheduler Settings

Default: 5-minute intervals
Configurable: 1-60 minutes via UI slider

### Database

- **Storage**: SQLite (`data/health_metrics.db`)
- **Tables**: status_log, response_times, incidents, alerts, configuration
- **Retention**: 7 days (configurable)
- **Fallback**: In-memory if persistent storage unavailable

## 📊 API Resources Monitored

### Categories

1. **Block Explorer** (25+ APIs)
   - Etherscan, BscScan, TronScan, Blockscout, Blockchair, etc.

2. **Market Data** (15+ APIs)
   - CoinGecko, CoinMarketCap, CryptoCompare, Coinpaprika, etc.

3. **RPC Nodes** (10+ providers)
   - Infura, Alchemy, Ankr, PublicNode, QuickNode, etc.

4. **News** (5+ sources)
   - CryptoPanic, CryptoControl, NewsAPI, etc.

5. **Sentiment** (5+ APIs)
   - Alternative.me Fear & Greed, LunarCrush, Santiment, etc.

6. **Whale Tracking** (5+ services)
   - Whale Alert, ClankApp, BitQuery, Arkham, etc.

7. **On-Chain Analytics** (10+ APIs)
   - The Graph, Glassnode, Dune, Covalent, Moralis, etc.

8. **CORS Proxies** (5+ proxies)
   - AllOrigins, CORS.sh, Corsfix, ThingProxy, etc.

## 🎨 Visual Design

- **Theme**: Dark mode with crypto-inspired gradients
- **Color Scheme**: Purple/Blue primary, semantic status colors
- **Status Badges**:
  - 🟢 Green: Online (200-299 status)
  - 🟡 Yellow: Degraded (400-499 status)
  - 🔴 Red: Offline (timeout or 500+ status)
  - ⚪ Gray: Unknown (not yet checked)
- **Charts**: Interactive Plotly with zoom, pan, hover details
- **Responsive**: Mobile-friendly grid layout

## 🔌 API Access

### Gradio Client (Python)

```python
from gradio_client import Client

client = Client("YOUR_USERNAME/crypto-api-monitor")
result = client.predict(api_name="/status")
print(result)
```

### Direct Embedding

```html
<iframe
  src="https://YOUR_USERNAME-crypto-api-monitor.hf.space"
  width="100%"
  height="800px"
  frameborder="0"
></iframe>
```

### REST API (via Gradio)

```bash
# Get current status
curl https://YOUR_USERNAME-crypto-api-monitor.hf.space/api/status

# Get category data
curl https://YOUR_USERNAME-crypto-api-monitor.hf.space/api/category/Market%20Data
```

## 📈 Performance

- **Concurrent Checks**: Up to 10 simultaneous API calls
- **Timeout**: 10 seconds per endpoint
- **Cache TTL**: 60 seconds
- **Stagger Delay**: 0.1 seconds between requests
- **Database**: Sub-millisecond query performance
- **UI Rendering**: <1 second for 162 providers

## 🛡️ Error Handling

- **Graceful Degradation**: UI loads even if APIs fail
- **Connection Timeout**: 10s timeout per endpoint
- **Retry Logic**: 3 attempts with exponential backoff
- **User Notifications**: Toast messages for errors
- **Logging**: Comprehensive stdout logging for HF Spaces
- **Fallback Resources**: Minimal hardcoded set if JSON fails

## 🔐 Security

- **API Keys**: Stored as HF Spaces secrets, never in code
- **Input Validation**: Pydantic models for all inputs
- **SQL Injection**: Parameterized queries only
- **Rate Limiting**: Respects API provider limits
- **No Secrets in Logs**: Masked keys in error messages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License - See LICENSE file for details

## 👤 Author

**Nima Zasinich** (@NZasinich)
- GitHub: [@nimazasinich](https://github.com/nimazasinich)
- Country: Estonia (EE)
- Project: Ultimate Free Crypto Data Pipeline 2025

## 🙏 Acknowledgments

- Built with [Gradio](https://gradio.app/) by Hugging Face
- Monitoring 162+ free and public crypto APIs
- Inspired by the crypto developer community's need for reliable data sources

## 🔗 Links

- **Live Demo**: [Hugging Face Space](https://huggingface.co/spaces/YOUR_USERNAME/crypto-api-monitor)
- **GitHub Repo**: [crypto-dt-source](https://github.com/nimazasinich/crypto-dt-source)
- **Issues**: [Report bugs](https://github.com/nimazasinich/crypto-dt-source/issues)

---

**Built with ❤️ for the crypto dev community**
