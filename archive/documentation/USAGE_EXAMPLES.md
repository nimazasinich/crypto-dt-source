# 🎯 Usage Examples - Crypto Intelligence Hub

This guide provides practical examples of how to use the integrated Hugging Face models and APIs.

---

## 🚀 Quick Start

### 1. Start the Server

```bash
# Set environment to load models
export HF_MODE=public
export PORT=7860

# Start server
uvicorn hf_unified_server:app --reload --port 7860
```

Visit: `http://localhost:7860`

---

## 📊 Example Use Cases

### Use Case 1: Crypto News Sentiment Analysis

**Scenario:** You want to analyze sentiment of crypto news articles.

**Via Web UI:**
1. Go to **Sentiment** tab
2. Click "News & Financial Sentiment Analysis" section
3. Enter title: "Bitcoin ETF Approval Expected"
4. Enter content: "Analysts predict Bitcoin spot ETF approval will drive massive institutional adoption"
5. Click "📰 Analyze News"
6. See result: 📈 Bullish with confidence score

**Via API:**
```bash
curl -X POST http://localhost:7860/api/news/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bitcoin ETF Approval Expected",
    "content": "Analysts predict Bitcoin spot ETF approval will drive massive institutional adoption"
  }'
```

**Response:**
```json
{
  "success": true,
  "available": true,
  "news": {
    "title": "Bitcoin ETF Approval Expected",
    "sentiment": "bullish",
    "confidence": 0.87
  }
}
```

---

### Use Case 2: Social Media Sentiment

**Scenario:** Analyze tweets about Ethereum.

**Via Web UI:**
1. Go to **Sentiment** tab → "Text Analysis"
2. Select mode: **Social**
3. Select model: **ElKulako/cryptobert** (or leave Auto)
4. Enter text: "ETH showing strong bullish momentum today! Breaking key resistance levels 🚀"
5. Click "🔍 Analyze"
6. Result shows: 📈 Bullish with confidence

**Via API:**
```bash
curl -X POST http://localhost:7860/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "ETH showing strong bullish momentum today! Breaking key resistance levels",
    "mode": "social"
  }'
```

---

### Use Case 3: Trading Signal Generation

**Scenario:** Get BTC trading signal using CryptoTrader-LM.

**Via Web UI:**
1. Go to **Sentiment** tab → "Text Analysis"
2. Select model: **agarkovv/CryptoTrader-LM**
3. Enter text: "BTC/USDT daily analysis"
4. Click "🔍 Analyze"
5. See trading decision: BUY/SELL/HOLD with rationale

**Via API:**
```bash
curl -X POST http://localhost:7860/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "BTC/USDT daily analysis",
    "model_key": "crypto_trade_0"
  }'
```

**Response:**
```json
{
  "ok": true,
  "sentiment": "buy",
  "confidence": 0.7,
  "model": "crypto_trade_0",
  "extra": {
    "decision": "BUY",
    "rationale": "Strong bullish momentum with breakout above resistance..."
  }
}
```

---

### Use Case 4: Financial Tweet Analysis

**Scenario:** Analyze financial tweets using FinTwitBERT.

**Via Web UI:**
1. Go to **Sentiment** tab
2. Select mode: **Financial**
3. Select model: **StephanAkkerman/FinTwitBERT-sentiment**
4. Enter: "NASDAQ hits new highs as tech stocks surge"
5. Analyze

**Via API:**
```bash
curl -X POST http://localhost:7860/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "NASDAQ hits new highs as tech stocks surge",
    "model_key": "financial_sent_0"
  }'
```

---

### Use Case 5: Crypto Market Overview

**Scenario:** Get overall market sentiment.

**Via Web UI:**
1. Go to **Sentiment** tab
2. Click "📊 Analyze Market Sentiment" under Global Market Sentiment
3. See aggregated sentiment across multiple models

**Via API:**
```bash
curl -X POST http://localhost:7860/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Cryptocurrency market showing mixed signals with BTC consolidation",
    "mode": "crypto"
  }'
```

---

### Use Case 6: Per-Asset Analysis

**Scenario:** Analyze sentiment for specific crypto asset.

**Via Web UI:**
1. Go to **Sentiment** tab → "Per-Asset Sentiment Analysis"
2. Select trading pair: **BTCUSDT** (from dropdown)
3. Enter related text: "Breaking resistance at $50k"
4. Click "🔍 Analyze Asset Sentiment"

**Via API:**
```bash
curl -X POST http://localhost:7860/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Breaking resistance at 50k",
    "mode": "crypto",
    "symbol": "BTCUSDT"
  }'
```

---

## 🤖 Model-Specific Examples

### kk08/CryptoBERT (crypto_sent_0)

**Best for:** General crypto sentiment

```bash
curl -X POST http://localhost:7860/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Bitcoin adoption growing rapidly in emerging markets",
    "model_key": "crypto_sent_0"
  }'
```

### ElKulako/cryptobert (crypto_sent_1)

**Best for:** Social media, returns Bullish/Neutral/Bearish

```bash
curl -X POST http://localhost:7860/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "ETH 2.0 upgrade complete, network performance improved significantly",
    "model_key": "crypto_sent_1"
  }'
```

### StephanAkkerman/FinTwitBERT-sentiment (financial_sent_0)

**Best for:** Financial news and tweets

```bash
curl -X POST http://localhost:7860/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Fed signals pause in rate hikes, markets rally",
    "model_key": "financial_sent_0"
  }'
```

### OpenC/crypto-gpt-o3-mini (crypto_gen_0)

**Best for:** Text generation, insights

```bash
curl -X POST http://localhost:7860/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Generate crypto market analysis for DeFi sector",
    "model_key": "crypto_gen_0"
  }'
```

### agarkovv/CryptoTrader-LM (crypto_trade_0)

**Best for:** Trading signals

```bash
curl -X POST http://localhost:7860/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "BTC daily trading signal analysis",
    "model_key": "crypto_trade_0"
  }'
```

---

## 🔧 Advanced API Usage

### List All Available Models

```bash
curl http://localhost:7860/api/models/list | jq '.models[] | {key, name: .model_id, category, loaded}'
```

### Initialize Models (Force Reload)

```bash
curl -X POST http://localhost:7860/api/models/initialize | jq
```

### Check Model Status

```bash
curl http://localhost:7860/api/models/status | jq '.status_message'
```

### Get System Status

```bash
curl http://localhost:7860/api/status | jq
```

### Search Resources

```bash
curl 'http://localhost:7860/api/resources/search?q=bitcoin' | jq
```

### List Providers (including HF Models)

```bash
curl http://localhost:7860/api/providers | jq '.providers[] | select(.type == "hf_model")'
```

---

## 📱 Frontend Workflows

### Workflow 1: Model Exploration

1. Start server with `HF_MODE=public`
2. Open browser to `http://localhost:7860`
3. Go to **AI Models** tab
4. Click "🚀 Load Models" button
5. Wait for models to initialize
6. View status and loaded models
7. Check which models succeeded/failed

### Workflow 2: Batch Sentiment Analysis

1. Go to **Sentiment** tab
2. Open browser console (F12)
3. Run batch analysis:

```javascript
async function batchAnalyze(texts) {
    const results = [];
    for (const text of texts) {
        const response = await fetch('/api/sentiment/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text, mode: 'crypto'})
        });
        results.push(await response.json());
    }
    return results;
}

// Example usage
const texts = [
    "Bitcoin breaking out!",
    "ETH price declining",
    "Market showing consolidation"
];

batchAnalyze(texts).then(results => console.table(results));
```

### Workflow 3: Compare Models

1. Go to **API Explorer** tab
2. Select endpoint: `POST /api/sentiment/analyze`
3. Test text: "Bitcoin showing bullish momentum"
4. Try with different models:

```json
{"text": "Bitcoin showing bullish momentum", "model_key": "crypto_sent_0"}
{"text": "Bitcoin showing bullish momentum", "model_key": "crypto_sent_1"}
{"text": "Bitcoin showing bullish momentum", "model_key": "financial_sent_0"}
```

5. Compare confidence scores and labels

---

## 🧪 Testing Scenarios

### Scenario 1: Model Availability Check

```bash
# Check if models loaded
curl http://localhost:7860/api/models/status | jq '{
  status: .status,
  loaded: .models_loaded,
  failed: .models_failed,
  hf_mode: .hf_mode
}'
```

### Scenario 2: Fallback Behavior

```bash
# With HF_MODE=off, should use lexical fallback
export HF_MODE=off
# Restart server, then:
curl -X POST http://localhost:7860/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Bitcoin bullish rally", "mode": "crypto"}' | jq '{
    engine: .engine,
    available: .available,
    sentiment: .sentiment
  }'
```

### Scenario 3: Error Handling

```bash
# Invalid model key
curl -X POST http://localhost:7860/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "test", "model_key": "invalid_model"}' | jq

# Empty text
curl -X POST http://localhost:7860/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "", "mode": "crypto"}' | jq
```

---

## 💡 Pro Tips

1. **Model Selection:**
   - Use `crypto_sent_0` for general crypto sentiment
   - Use `financial_sent_0` for financial news
   - Use `crypto_trade_0` for trading signals

2. **Mode vs Model:**
   - `mode` selects category (crypto/financial/social)
   - `model_key` selects specific model
   - Specify both for precise control

3. **Performance:**
   - First inference per model is slower (loading)
   - Subsequent inferences are fast (cached)
   - Use `mode` without `model_key` for ensemble

4. **Error Recovery:**
   - If model fails, system falls back to lexical analysis
   - Check `/api/models/status` for failure reasons
   - Use `/api/models/initialize` to retry loading

5. **History Tracking:**
   - Sentiment analyses save to localStorage
   - View history in Sentiment tab
   - Export via browser console: `localStorage.getItem('sentiment_history')`

---

## 📊 Integration Examples

### Python Script

```python
import requests

def analyze_crypto_sentiment(text, model='auto'):
    """Analyze crypto sentiment using HF models"""
    url = 'http://localhost:7860/api/sentiment/analyze'
    
    payload = {'text': text, 'mode': 'crypto'}
    if model != 'auto':
        payload['model_key'] = model
    
    response = requests.post(url, json=payload)
    return response.json()

# Example
result = analyze_crypto_sentiment("Bitcoin breaking resistance!")
print(f"Sentiment: {result['sentiment']} ({result['confidence']:.2%})")
```

### JavaScript/Node.js

```javascript
const fetch = require('node-fetch');

async function analyzeSentiment(text, modelKey = null) {
    const body = { text, mode: 'crypto' };
    if (modelKey) body.model_key = modelKey;
    
    const response = await fetch('http://localhost:7860/api/sentiment/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    
    return await response.json();
}

// Example
analyzeSentiment("ETH bullish momentum").then(result => {
    console.log(`Sentiment: ${result.sentiment} (${result.confidence})`);
});
```

---

## 🎯 Common Patterns

### Pattern 1: News Analysis Pipeline

```bash
# 1. Fetch news (external API)
# 2. Analyze sentiment
curl -X POST http://localhost:7860/api/news/analyze \
  -H "Content-Type: application/json" \
  -d '{"title": "...", "content": "..."}'
# 3. Store in database (automatic)
# 4. View in News tab
```

### Pattern 2: Real-time Social Monitoring

```javascript
// Monitor Twitter/Reddit feeds
setInterval(async () => {
    const posts = await fetchSocialPosts(); // Your function
    for (const post of posts) {
        const sentiment = await analyzeSentiment(post.text);
        if (sentiment.sentiment === 'bullish' && sentiment.confidence > 0.8) {
            alert(`Strong bullish signal: ${post.text}`);
        }
    }
}, 60000); // Every minute
```

### Pattern 3: Asset-Specific Alerts

```python
import requests
import time

def monitor_asset(symbol, interval=60):
    """Monitor sentiment for specific asset"""
    while True:
        result = requests.post('http://localhost:7860/api/sentiment/analyze', json={
            'text': f'{symbol} market analysis',
            'mode': 'crypto',
            'symbol': symbol
        }).json()
        
        if result['confidence'] > 0.85:
            print(f"High confidence {result['sentiment']} for {symbol}")
        
        time.sleep(interval)

# Monitor BTC
monitor_asset('BTCUSDT')
```

---

*For more information, see:*
- `docs/project_mapping_doc.html` - Complete API reference
- `INTEGRATION_COMPLETE.md` - Technical details
- `INTEGRATION_SUMMARY_FOR_USER.md` - Quick start guide
