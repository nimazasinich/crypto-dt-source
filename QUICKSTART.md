# ⚡ Quick Start Guide

Get your Crypto API Monitor running in **under 5 minutes**!

---

## 🚀 Option 1: Docker Compose (Easiest)

```bash
# 1. Clone the repository
git clone https://github.com/nimazasinich/crypto-dt-source.git
cd crypto-dt-source

# 2. Set up environment
cp .env.example .env
nano .env  # Add your API keys

# 3. Start the application
./scripts/start.sh

# 4. Open your browser
# http://localhost:7860
```

**That's it!** 🎉

---

## 🤗 Option 2: Hugging Face Spaces (No Setup Required)

```bash
# 1. Run deployment script
./scripts/deploy-hf.sh

# 2. Follow the prompts
# Enter your HF username and Space name

# 3. Add API keys in Space Settings
# Go to Settings → Repository Secrets
```

**Your Space will be live in ~2 minutes!** 🎉

---

## 🐋 Option 3: Docker Only

```bash
# 1. Build image
docker build -t crypto-monitor .

# 2. Run container
docker run -d \
  --name crypto-monitor \
  -p 7860:7860 \
  -e ETHERSCAN_KEY_1=your_etherscan_key \
  -e COINMARKETCAP_KEY_1=your_cmc_key \
  -e NEWSAPI_KEY=your_news_key \
  crypto-monitor

# 3. Access application
# http://localhost:7860
```

---

## 🔑 Required API Keys

Get these **3 free API keys** (takes ~5 minutes total):

1. **Etherscan** (1 min)
   - Visit: https://etherscan.io/myapikey
   - Click "Sign Up" → Verify email → Generate API key
   - Free: 5 calls/second

2. **CoinMarketCap** (2 min)
   - Visit: https://pro.coinmarketcap.com/signup
   - Sign up → Email verification → Copy API key
   - Free: 333 calls/day

3. **NewsAPI** (2 min)
   - Visit: https://newsapi.org/register
   - Register → Copy API key
   - Free: 100 requests/day

---

## 📊 What You'll See

After starting, you'll have:

- ✅ **Dashboard**: Real-time metrics and charts
- ✅ **21 Data Sources**: Market, blockchain, news, sentiment
- ✅ **WebSocket Stream**: Live updates every 30 seconds
- ✅ **Health Monitoring**: Automatic API health checks
- ✅ **Rate Limit Tracking**: Per-provider usage monitoring

---

## 🛠️ Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Check status
docker-compose ps
```

---

## 📝 Need Help?

- **Full Documentation**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Troubleshooting**: Check [DEPLOYMENT.md#troubleshooting](DEPLOYMENT.md#troubleshooting)
- **Issues**: https://github.com/nimazasinich/crypto-dt-source/issues

---

## 🎯 Next Steps

1. **Customize**: Edit `config.py` to add more API providers
2. **Monitor**: Set up Prometheus + Grafana (optional)
3. **Scale**: Deploy to cloud platforms (AWS, GCP, Azure)
4. **Secure**: Add SSL/TLS certificates for production

---

**Happy Monitoring!** 🚀📊
