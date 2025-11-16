# Quick Start - Admin Dashboard

## 🚀 Start in 3 Commands

```bash
cd /workspace
pip install -r requirements.txt
python3 api_server_extended.py
```

Then open: **http://localhost:7860/**

---

## 📊 What You'll See

### Admin Dashboard with 7 Tabs:

1. **📊 Status** - System overview, live BTC/ETH/BNB prices
2. **🔌 Providers** - List of 94 providers from APL
3. **💰 Market Data** - Real prices, sentiment, trending
4. **🤖 APL Scanner** - Run provider discovery scans
5. **🧠 HF Models** - Hugging Face models management
6. **🔧 Diagnostics** - System health checks
7. **📝 Logs** - System logs and errors

---

## ✅ Key Features

### Real Data Only
- ✅ Live market data from CoinGecko
- ✅ Sentiment from Alternative.me
- ✅ Providers from APL validation
- ✅ NO mock/fake data anywhere

### Admin Actions
- 🔄 Refresh data in real-time
- 🤖 Run APL scans to discover providers
- 🔧 Run diagnostics with auto-fix
- 📊 View provider statistics
- 🧠 Monitor HF model health

---

## 🌐 Deploy to HuggingFace Spaces

### Already Configured!

1. Push to HF Space:
```bash
git push
```

2. Access at: `https://your-space.hf.space/`

3. Admin dashboard loads automatically!

**Everything is HF Spaces compatible:**
- ✅ Relative URLs
- ✅ Port 7860
- ✅ Dockerfile ready
- ✅ Static files mounted
- ✅ CORS configured

---

## 📖 First Steps

### 1. Check System Status
- Open Status tab (default)
- See provider counts
- View live market prices

### 2. Run APL Scan
- Go to APL Scanner tab
- Click "🤖 Run APL Scan"
- Wait 1-2 minutes
- See updated provider counts

### 3. View Providers
- Go to Providers tab
- See all 94 validated providers
- Filter by category

### 4. Monitor Market
- Go to Market Data tab
- Click "🔄 Refresh Prices"
- See live BTC/ETH/BNB data
- View Fear & Greed Index
- Check trending coins

### 5. Check Diagnostics
- Go to Diagnostics tab
- Click "🔧 Run with Auto-Fix"
- See system health status

---

## 🔧 Troubleshooting

### No providers showing?
→ Run APL scan (APL Scanner tab → Run APL Scan)

### Market data fails?
→ Check internet connection to CoinGecko
→ May hit rate limits (wait a few minutes)

### APL scan fails?
→ Check Python dependencies installed
→ Check auto_provider_loader.py exists

---

## 📚 Documentation

- `ADMIN_DASHBOARD_COMPLETE.md` - Full documentation
- `APL_USAGE_GUIDE.md` - APL usage guide
- `APL_FINAL_SUMMARY.md` - APL implementation summary

---

## ✨ That's It!

**You now have a fully functional admin dashboard with:**
- Real-time market data
- 94 validated providers
- APL integration
- HF models support
- Zero mock data
- HuggingFace Spaces ready

**Start managing your crypto data sources now!** 🚀
