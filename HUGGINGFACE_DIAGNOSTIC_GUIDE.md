# 🔍 Complete Diagnostic & Fix Guide
## HuggingFace Space Integration Troubleshooting

**Version:** 2.0
**Last Updated:** 2025-11-15
**Target:** Node.js/React ↔ HuggingFace Space Integration
**Space URL:** https://really-amin-datasourceforcryptocurrency.hf.space

---

## 📋 Table of Contents

1. [Quick Start Diagnostic](#quick-start-diagnostic)
2. [Pre-Flight Checks](#pre-flight-checks)
3. [Automated Diagnostic Script](#automated-diagnostic-script)
4. [Common Issues & Fixes](#common-issues--fixes)
5. [Testing Protocol](#testing-protocol)
6. [Debugging Commands](#debugging-commands)
7. [Configuration Guide](#configuration-guide)
8. [Troubleshooting Decision Tree](#troubleshooting-decision-tree)
9. [FAQ](#faq)

---

## 🚀 Quick Start Diagnostic

### Step 1: Check HuggingFace Space Status

```bash
# Test if Space is alive
curl -v https://really-amin-datasourceforcryptocurrency.hf.space/api/health

# Expected Output:
# HTTP/2 200
# {"status": "healthy"}

# If you get:
# - Connection timeout → Space is sleeping or down
# - 404 Not Found → Endpoint doesn't exist
# - 503 Service Unavailable → Space is building
```

### Step 2: Discover Available Endpoints

```bash
# Try common endpoints
echo "Testing /api/health..."
curl -s https://really-amin-datasourceforcryptocurrency.hf.space/api/health | jq

echo "Testing /api/prices..."
curl -s "https://really-amin-datasourceforcryptocurrency.hf.space/api/prices?symbols=BTC,ETH" | jq

echo "Testing /api/ohlcv..."
curl -s "https://really-amin-datasourceforcryptocurrency.hf.space/api/ohlcv?symbol=BTCUSDT&interval=1h&limit=10" | jq

echo "Testing /api/market/overview..."
curl -s https://really-amin-datasourceforcryptocurrency.hf.space/api/market/overview | jq

echo "Testing /api/sentiment..."
curl -s https://really-amin-datasourceforcryptocurrency.hf.space/api/sentiment | jq

echo "Testing /docs (API documentation)..."
curl -s https://really-amin-datasourceforcryptocurrency.hf.space/docs | head -n 50
```

### Step 3: Quick Application Test

```bash
# Setup environment
cp .env.example .env

# Edit .env file - set:
# PRIMARY_DATA_SOURCE=huggingface
# HF_SPACE_BASE_URL=https://really-amin-datasourceforcryptocurrency.hf.space

# Install dependencies
npm install

# Start development server
npm run dev

# Open browser and check:
# 1. http://localhost:5173
# 2. Open DevTools (F12)
# 3. Go to Network tab
# 4. Check for any red requests
# 5. Go to Console tab
# 6. Look for error messages
```

---

## ✅ Pre-Flight Checks

Before troubleshooting, verify these requirements:

### System Requirements

```bash
# Check Node.js version (should be 18+)
node --version
# Expected: v18.0.0 or higher

# Check npm version
npm --version
# Expected: 9.0.0 or higher

# Check if git is installed
git --version

# Check if curl is available
curl --version

# Check if jq is installed (optional but helpful)
jq --version
# If not installed: sudo apt-get install jq (Ubuntu) or brew install jq (Mac)
```

### Project Structure Verification

```bash
# Verify critical files exist
ls -la hf-data-engine/main.py
ls -la hf-data-engine/requirements.txt
ls -la .env.example
ls -la package.json

# If any file is missing, run:
git status
git pull origin main
```

### Dependencies Installation

```bash
# Clean install
rm -rf node_modules package-lock.json
npm install

# Verify critical packages
npm list typescript
npm list vite
npm list react

# For Python dependencies (if working with backend)
cd hf-data-engine
pip install -r requirements.txt
cd ..
```

### Environment Configuration

```bash
# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating from .env.example..."
    cp .env.example .env
else
    echo "✅ .env file exists"
fi

# Verify required variables
grep -q "PRIMARY_DATA_SOURCE" .env && echo "✅ PRIMARY_DATA_SOURCE configured" || echo "❌ PRIMARY_DATA_SOURCE missing"
grep -q "HF_SPACE_BASE_URL" .env && echo "✅ HF_SPACE_BASE_URL configured" || echo "❌ HF_SPACE_BASE_URL missing"

# View current configuration (non-sensitive parts)
echo ""
echo "Current configuration:"
grep "PRIMARY_DATA_SOURCE\|HF_SPACE" .env | sed 's/=.*/=***/'
```

---

## 🤖 Automated Diagnostic Script

Save this as `diagnostic.sh` in your project root and run with `bash diagnostic.sh`:

```bash
#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "╔════════════════════════════════════════════════════════╗"
echo "║   HuggingFace Space Integration Diagnostic Tool       ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Configuration
HF_SPACE_URL="https://really-amin-datasourceforcryptocurrency.hf.space"
RESULTS_FILE="diagnostic_results_$(date +%Y%m%d_%H%M%S).log"

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
    fi
}

# Function to test endpoint
test_endpoint() {
    local endpoint=$1
    local description=$2

    echo -e "\n${BLUE}Testing:${NC} $description"
    echo "Endpoint: $endpoint"

    response=$(curl -s -w "\n%{http_code}" --connect-timeout 10 "$endpoint" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    echo "HTTP Status: $http_code"

    if [ "$http_code" = "200" ]; then
        print_status 0 "$description"
        echo "Response preview:"
        echo "$body" | head -n 5
        return 0
    else
        print_status 1 "$description (HTTP $http_code)"
        echo "Error details:"
        echo "$body" | head -n 3
        return 1
    fi
}

# Start logging
exec > >(tee -a "$RESULTS_FILE")
exec 2>&1

echo "Starting diagnostic at $(date)"
echo "Results will be saved to: $RESULTS_FILE"
echo ""

# Test 1: System Requirements
echo "════════════════════════════════════════════════════════"
echo "TEST 1: System Requirements"
echo "════════════════════════════════════════════════════════"

node --version > /dev/null 2>&1
print_status $? "Node.js installed"

npm --version > /dev/null 2>&1
print_status $? "npm installed"

curl --version > /dev/null 2>&1
print_status $? "curl installed"

# Test 2: Project Structure
echo ""
echo "════════════════════════════════════════════════════════"
echo "TEST 2: Project Structure"
echo "════════════════════════════════════════════════════════"

[ -f "package.json" ]
print_status $? "package.json exists"

[ -f ".env.example" ]
print_status $? ".env.example exists"

[ -d "hf-data-engine" ]
print_status $? "hf-data-engine directory exists"

[ -f "hf-data-engine/main.py" ]
print_status $? "HuggingFace engine implementation exists"

# Test 3: Environment Configuration
echo ""
echo "════════════════════════════════════════════════════════"
echo "TEST 3: Environment Configuration"
echo "════════════════════════════════════════════════════════"

if [ -f ".env" ]; then
    print_status 0 ".env file exists"

    grep -q "PRIMARY_DATA_SOURCE" .env
    print_status $? "PRIMARY_DATA_SOURCE configured"

    grep -q "HF_SPACE_BASE_URL" .env
    print_status $? "HF_SPACE_BASE_URL configured"

    echo ""
    echo "Current configuration:"
    grep "PRIMARY_DATA_SOURCE\|HF_SPACE" .env | sed 's/=.*/=***/' || true
else
    print_status 1 ".env file exists"
    echo "⚠️  Run: cp .env.example .env"
fi

# Test 4: HuggingFace Space Connectivity
echo ""
echo "════════════════════════════════════════════════════════"
echo "TEST 4: HuggingFace Space Connectivity"
echo "════════════════════════════════════════════════════════"

# Test DNS resolution
echo "Resolving DNS..."
host really-amin-datasourceforcryptocurrency.hf.space > /dev/null 2>&1
print_status $? "DNS resolution for HF Space"

# Test basic connectivity
echo ""
echo "Testing basic connectivity..."
ping -c 1 -W 5 hf.space > /dev/null 2>&1
print_status $? "Network connectivity to hf.space"

# Test 5: HuggingFace Space Endpoints
echo ""
echo "════════════════════════════════════════════════════════"
echo "TEST 5: HuggingFace Space Endpoints"
echo "════════════════════════════════════════════════════════"

test_endpoint "$HF_SPACE_URL/api/health" "Health check endpoint"
test_endpoint "$HF_SPACE_URL/api/prices?symbols=BTC,ETH" "Prices endpoint"
test_endpoint "$HF_SPACE_URL/api/ohlcv?symbol=BTCUSDT&interval=1h&limit=10" "OHLCV endpoint"
test_endpoint "$HF_SPACE_URL/api/market/overview" "Market overview endpoint"
test_endpoint "$HF_SPACE_URL/api/sentiment" "Sentiment endpoint"

# Test 6: CORS Headers
echo ""
echo "════════════════════════════════════════════════════════"
echo "TEST 6: CORS Configuration"
echo "════════════════════════════════════════════════════════"

cors_headers=$(curl -s -I -H "Origin: http://localhost:5173" "$HF_SPACE_URL/api/prices" 2>&1 | grep -i "access-control")

if [ -z "$cors_headers" ]; then
    print_status 1 "CORS headers present"
    echo "⚠️  No CORS headers found. This may cause browser errors."
    echo "    Consider using Vite proxy (see Configuration Guide)."
else
    print_status 0 "CORS headers present"
    echo "CORS headers:"
    echo "$cors_headers"
fi

# Test 7: Response Format Validation
echo ""
echo "════════════════════════════════════════════════════════"
echo "TEST 7: Response Format Validation"
echo "════════════════════════════════════════════════════════"

echo "Fetching sample data..."
sample_response=$(curl -s "$HF_SPACE_URL/api/prices?symbols=BTC" 2>&1)

if command -v jq > /dev/null 2>&1; then
    echo "$sample_response" | jq . > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        print_status 0 "Valid JSON response"
        echo ""
        echo "Response structure:"
        echo "$sample_response" | jq 'keys' 2>/dev/null || echo "Unable to parse keys"
    else
        print_status 1 "Valid JSON response"
        echo "Response is not valid JSON:"
        echo "$sample_response" | head -n 3
    fi
else
    echo "⚠️  jq not installed, skipping JSON validation"
    echo "Install with: sudo apt-get install jq (Ubuntu) or brew install jq (Mac)"
fi

# Test 8: Dependencies
echo ""
echo "════════════════════════════════════════════════════════"
echo "TEST 8: Node Dependencies"
echo "════════════════════════════════════════════════════════"

if [ -d "node_modules" ]; then
    print_status 0 "node_modules exists"

    [ -d "node_modules/typescript" ]
    print_status $? "TypeScript installed"

    [ -d "node_modules/vite" ]
    print_status $? "Vite installed"

    [ -d "node_modules/react" ]
    print_status $? "React installed"
else
    print_status 1 "node_modules exists"
    echo "⚠️  Run: npm install"
fi

# Test 9: Python Dependencies (if backend is present)
echo ""
echo "════════════════════════════════════════════════════════"
echo "TEST 9: Python Dependencies"
echo "════════════════════════════════════════════════════════"

if [ -f "hf-data-engine/requirements.txt" ]; then
    print_status 0 "requirements.txt exists"

    python3 -c "import fastapi" 2>/dev/null
    print_status $? "FastAPI installed"

    python3 -c "import aiohttp" 2>/dev/null
    print_status $? "aiohttp installed"
else
    print_status 1 "requirements.txt exists"
fi

# Summary
echo ""
echo "════════════════════════════════════════════════════════"
echo "DIAGNOSTIC SUMMARY"
echo "════════════════════════════════════════════════════════"

echo ""
echo "Results saved to: $RESULTS_FILE"
echo ""
echo "Next steps:"
echo "1. Review any failed tests above"
echo "2. Check the 'Common Issues & Fixes' section in HUGGINGFACE_DIAGNOSTIC_GUIDE.md"
echo "3. Run 'npm run dev' and test in browser"
echo ""
echo "Diagnostic completed at $(date)"
```

Make it executable and run:

```bash
chmod +x diagnostic.sh
./diagnostic.sh
```

---

## 🔧 Common Issues & Fixes

### Issue 1: HuggingFace Space is Sleeping/Down

**Symptoms:**
- `curl: (28) Connection timed out`
- `503 Service Unavailable`
- `Connection refused`
- Space shows "Building" or "Sleeping" on HuggingFace.co

**Root Cause:**
HuggingFace Spaces with free resources go to sleep after 48 hours of inactivity. They need to be "woken up" with a request.

**Diagnosis:**

```bash
# Check Space status via HuggingFace website
# Visit: https://huggingface.co/spaces/Really-amin/Datasourceforcryptocurrency

# Or test via API
curl -v https://really-amin-datasourceforcryptocurrency.hf.space/api/health

# Expected responses:
# 200 = Space is awake ✅
# 503 = Space is starting (wait 60 seconds)
# Timeout = Space is sleeping
```

**Fix Option 1: Wake Up the Space**

```bash
# Send a request to wake it up
curl https://really-amin-datasourceforcryptocurrency.hf.space/api/health

# Wait 30-60 seconds for Space to start
echo "Waiting for Space to start..."
sleep 60

# Try again
curl -s https://really-amin-datasourceforcryptocurrency.hf.space/api/health | jq

# You should see: {"status": "healthy"}
```

**Fix Option 2: Use Fallback Source**

```bash
# Edit .env
nano .env

# Add these settings:
PRIMARY_DATA_SOURCE=coingecko
FALLBACK_ENABLED=true
FALLBACK_SOURCES=coincap,binance

# Restart application
npm run dev
```

**Fix Option 3: Keep Space Awake (Linux/Mac)**

Create a persistent ping job:

```bash
# Edit crontab
crontab -e

# Add this line (runs every 10 minutes):
*/10 * * * * curl -s https://really-amin-datasourceforcryptocurrency.hf.space/api/health > /dev/null

# Verify cron was added
crontab -l
```

**Fix Option 4: Upgrade HuggingFace Space (Recommended)**

```
Contact HuggingFace to upgrade to paid resources for 24/7 uptime.
Visit: https://huggingface.co/spaces/Really-amin/Datasourceforcryptocurrency/settings
```

---

### Issue 2: Wrong API Endpoints (404 Errors)

**Symptoms:**
- `404 Not Found`
- `Cannot GET /api/crypto/prices/top`
- Empty response or HTML error page
- Console shows: `404: Not Found`

**Root Cause:**
The actual API endpoints don't match what's configured in your application.

**Diagnosis:**

```bash
# Discover actual endpoints by checking API docs
curl -s https://really-amin-datasourceforcryptocurrency.hf.space/docs | grep -oP 'href="[^"]*"' | head -20

# Or try different endpoint patterns manually
echo "Pattern 1: /api/prices"
curl -s https://really-amin-datasourceforcryptocurrency.hf.space/api/prices?symbols=BTC

echo ""
echo "Pattern 2: /prices"
curl -s https://really-amin-datasourceforcryptocurrency.hf.space/prices?symbols=BTC

echo ""
echo "Pattern 3: /v1/prices"
curl -s https://really-amin-datasourceforcryptocurrency.hf.space/v1/prices?symbols=BTC

echo ""
echo "Pattern 4: Root endpoint"
curl -s https://really-amin-datasourceforcryptocurrency.hf.space/ | head -n 20

# Check actual response format
curl -s https://really-amin-datasourceforcryptocurrency.hf.space/api/health | jq
```

**Fix: Update Adapter Configuration**

First, locate your adapter file:

```bash
find . -name "*huggingface*adapter*" -o -name "*hf*adapter*"
```

Then update the endpoint configuration:

**Option A: If using configuration object**

```typescript
// src/config/huggingface.ts or similar
export const huggingfaceConfig = {
  baseUrl: 'https://really-amin-datasourceforcryptocurrency.hf.space',
  endpoints: {
    prices: '/api/prices',           // Verify this path exists
    ohlcv: '/api/ohlcv',
    sentiment: '/api/sentiment',
    market: '/api/market/overview',
    health: '/api/health'
  },
  timeout: 30000,
};
```

**Option B: If endpoints need transformation**

```typescript
// src/services/adapters/huggingface.adapter.ts

private getEndpointPath(endpoint: string): string {
  // Map application endpoints to actual Space endpoints
  const endpointMap: Record<string, string> = {
    '/prices': '/api/prices',
    '/ohlcv': '/api/ohlcv',
    '/sentiment': '/api/sentiment',
    '/market-overview': '/api/market/overview',
  };

  return endpointMap[endpoint] || endpoint;
}

async fetchData(endpoint: string): Promise<any> {
  const actualEndpoint = this.getEndpointPath(endpoint);
  const url = `${this.baseUrl}${actualEndpoint}`;

  console.log(`Fetching from: ${url}`);

  const response = await fetch(url, {
    method: 'GET',
    headers: this.getHeaders(),
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}
```

**Option C: Add debugging**

```typescript
// Temporary debugging to find correct endpoints
async discoverEndpoints(): Promise<void> {
  const patterns = [
    '/api/prices',
    '/api/price',
    '/prices',
    '/v1/prices',
    '/price',
  ];

  for (const pattern of patterns) {
    try {
      const response = await fetch(`${this.baseUrl}${pattern}?symbols=BTC`, {
        timeout: 5000
      });
      console.log(`${pattern}: HTTP ${response.status}`);
    } catch (error) {
      console.log(`${pattern}: Error -`, error);
    }
  }
}

// Call this during development
// await adapter.discoverEndpoints();
```

---

### Issue 3: Response Format Mismatch

**Symptoms:**
- Data shows as `undefined` in UI
- Console errors: `Cannot read property 'symbol' of undefined`
- TypeScript type errors
- Numbers showing as strings

**Root Cause:**
The Space returns data in a different format than expected.

**Diagnosis:**

```bash
# Get actual response and examine structure
curl -s "https://really-amin-datasourceforcryptocurrency.hf.space/api/prices?symbols=BTC,ETH" | jq '.' -C

# Note the field names, types, and structure

# Compare with expected format
# Expected example:
# [
#   {
#     "symbol": "BTC",
#     "price": 50000,
#     "change24h": 2.5
#   }
# ]

# Actual format (if different):
# {
#   "data": [
#     {
#       "coin": "bitcoin",
#       "current_price": "50000.00",
#       "percent_change": "2.5"
#     }
#   ]
# }
```

**Fix: Update Data Mapping**

```typescript
// src/services/adapters/huggingface.adapter.ts

interface HFPriceResponse {
  // Define actual Space response structure
  data?: Array<{
    coin?: string;
    symbol?: string;
    current_price?: number | string;
    price?: number | string;
    percent_change?: number | string;
    change_24h?: number | string;
  }>;
  prices?: any[];
}

async getPrices(symbols: string[]): Promise<CryptoPrice[]> {
  const data = await this.fetchData<HFPriceResponse>('/api/prices?symbols=' + symbols.join(','));

  // Handle different response structures
  const prices = data.data || data.prices || [];

  return prices.map(item => {
    // Safely extract values with fallbacks
    const symbol = item.symbol || item.coin?.toUpperCase() || 'UNKNOWN';
    const price = Number(item.current_price || item.price || 0);
    const change24h = Number(item.percent_change || item.change_24h || 0);

    // Validate required fields
    if (isNaN(price)) {
      console.warn(`Invalid price for ${symbol}:`, item);
      return null;
    }

    return {
      symbol,
      price,
      change24h,
      timestamp: Date.now(),
    };
  }).filter(Boolean) as CryptoPrice[];
}
```

**Add Comprehensive Validation:**

```typescript
// src/services/validators/huggingface.validator.ts

export function validatePriceResponse(data: any): boolean {
  if (!Array.isArray(data) && !data?.data && !data?.prices) {
    console.error('Invalid response structure:', typeof data);
    return false;
  }

  const items = Array.isArray(data) ? data : (data.data || data.prices || []);

  if (items.length === 0) {
    console.warn('Response contains no items');
    return false;
  }

  // Validate first item has required fields
  const firstItem = items[0];
  if (!firstItem.symbol && !firstItem.coin) {
    console.error('Missing symbol/coin field:', firstItem);
    return false;
  }

  if (!firstItem.price && !firstItem.current_price) {
    console.error('Missing price field:', firstItem);
    return false;
  }

  return true;
}

export function normalizePriceData(data: any): CryptoPrice[] {
  if (!validatePriceResponse(data)) {
    throw new Error('Invalid price response format');
  }

  const items = Array.isArray(data) ? data : (data.data || data.prices);

  return items.map((item: any) => ({
    symbol: (item.symbol || item.coin || 'UNKNOWN').toUpperCase(),
    price: Number(item.current_price || item.price || 0),
    change24h: Number(item.percent_change || item.change_24h || 0),
    timestamp: Date.now(),
  }));
}
```

---

### Issue 4: CORS Errors in Browser

**Symptoms:**
- Browser console error: `Access to fetch at '...' from origin 'http://localhost:5173' has been blocked by CORS policy`
- Network tab shows request with red X
- `No 'Access-Control-Allow-Origin' header is present`

**Root Cause:**
Browser blocks cross-origin requests unless the server includes proper CORS headers.

**Diagnosis:**

```bash
# Check if Space returns CORS headers
curl -I -H "Origin: http://localhost:5173" \
  https://really-amin-datasourceforcryptocurrency.hf.space/api/prices

# Look for these headers in the response:
# Access-Control-Allow-Origin: *
# Access-Control-Allow-Methods: GET, POST, OPTIONS
# Access-Control-Allow-Headers: Content-Type

# If headers are missing, you'll see CORS errors in browser

# Test with preflight OPTIONS request
curl -X OPTIONS -I \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: GET" \
  https://really-amin-datasourceforcryptocurrency.hf.space/api/prices
```

**Fix Option 1: Add Vite Proxy (Recommended for Development)**

```typescript
// vite.config.ts

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api/hf': {
        target: 'https://really-amin-datasourceforcryptocurrency.hf.space',
        changeOrigin: true,
        rewrite: (path) => {
          // Remove /api/hf prefix and keep the rest
          return path.replace(/^\/api\/hf/, '');
        },
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.error('Proxy error:', err);
          });
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('Proxying:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('Proxy response:', proxyRes.statusCode);
          });
        }
      }
    }
  }
})
```

Then update your adapter:

```typescript
// src/services/adapters/huggingface.adapter.ts

async fetchData<T>(endpoint: string): Promise<T> {
  // In development, use Vite proxy
  // In production, use direct URL (if CORS enabled on Space)

  const baseUrl = import.meta.env.DEV
    ? '/api/hf'  // Proxied through Vite
    : this.config.baseUrl;  // Direct to Space

  const url = `${baseUrl}${endpoint}`;

  console.log(`[${import.meta.env.DEV ? 'DEV' : 'PROD'}] Fetching: ${url}`);

  const response = await fetch(url, {
    method: 'GET',
    headers: this.getHeaders(),
    signal: AbortSignal.timeout(this.config.timeout),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`HTTP ${response.status}: ${errorText}`);
  }

  return response.json();
}
```

**Fix Option 2: Update Space with CORS Headers (If you control the Space)**

If you control the HuggingFace Space, add CORS support:

**For FastAPI-based Space:**

```python
# hf-data-engine/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Crypto Data Engine")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify: ["http://localhost:5173", "https://yourdomain.com"]
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*", "Content-Type", "Authorization"],
    max_age=3600,  # Cache preflight for 1 hour
)

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

# ... rest of API endpoints
```

**For Gradio-based Space:**

```python
# app.py

import gradio as gr

# Create your interface
demo = gr.Blocks()

with demo:
    # Your components here
    pass

if __name__ == "__main__":
    demo.launch(
        share=True,
        server_name="0.0.0.0",
        server_port=7860,
        # Note: Gradio automatically handles CORS for public access
    )
```

**Fix Option 3: Use CORS Proxy Service (Development Only)**

⚠️ **Not recommended for production**

```typescript
// src/services/adapters/huggingface.adapter.ts

async fetchData<T>(endpoint: string): Promise<T> {
  let url = `${this.config.baseUrl}${endpoint}`;

  // Only use CORS proxy as last resort for testing
  if (import.meta.env.DEV && !import.meta.env.VITE_USE_PROXY) {
    const corsProxy = 'https://corsproxy.io/?';
    url = corsProxy + encodeURIComponent(url);
  }

  const response = await fetch(url);
  return response.json();
}
```

Available CORS proxy services (for testing only):
- https://corsproxy.io/
- https://cors-anywhere.herokuapp.com/
- https://api.allorigins.win/

---

### Issue 5: Timeout Errors

**Symptoms:**
- `AbortError: The operation was aborted due to timeout`
- Requests take > 30 seconds
- UI shows loading spinner that never completes
- Network tab shows request taking a long time

**Root Cause:**
Space is slow to respond or having performance issues, or timeout is too short.

**Diagnosis:**

```bash
# Measure actual response time
time curl -s https://really-amin-datasourceforcryptocurrency.hf.space/api/prices?symbols=BTC | jq > /dev/null

# Expected: < 5 seconds
# 5-15 seconds: Space is cold (starting up)
# > 30 seconds: Space might be sleeping or overloaded

# Check Space status
curl -I https://really-amin-datasourceforcryptocurrency.hf.space/api/health

# Test endpoint directly multiple times
for i in {1..3}; do
  echo "Request $i:"
  time curl -s https://really-amin-datasourceforcryptocurrency.hf.space/api/prices?symbols=BTC > /dev/null
  echo ""
done
```

**Fix Option 1: Increase Timeout**

```typescript
// .env
HF_REQUEST_TIMEOUT=60000  # 60 seconds

// src/config/huggingface.ts
export const huggingfaceConfig = {
  baseUrl: 'https://really-amin-datasourceforcryptocurrency.hf.space',
  timeout: parseInt(import.meta.env.VITE_HF_REQUEST_TIMEOUT || '60000'),
};

// src/services/adapters/huggingface.adapter.ts
async fetchData<T>(endpoint: string): Promise<T> {
  const url = `${this.config.baseUrl}${endpoint}`;

  console.log(`[HF] Requesting ${endpoint} (timeout: ${this.config.timeout}ms)`);

  const startTime = Date.now();

  try {
    const response = await fetch(url, {
      signal: AbortSignal.timeout(this.config.timeout),
    });

    const duration = Date.now() - startTime;
    console.log(`[HF] Completed in ${duration}ms`);

    return response.json();
  } catch (error) {
    const duration = Date.now() - startTime;
    console.error(`[HF] Failed after ${duration}ms:`, error);
    throw error;
  }
}
```

**Fix Option 2: Implement Proper Loading States**

```typescript
// src/hooks/useHuggingFaceData.ts

import { useState, useEffect } from 'react';

export function useHuggingFaceData<T>(
  fetchFn: () => Promise<T>,
  options?: { timeout?: number; retries?: number }
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let mounted = true;
    let retryCount = 0;
    const maxRetries = options?.retries ?? 1;

    async function fetchData() {
      try {
        setLoading(true);
        setError(null);

        const result = await fetchFn();

        if (mounted) {
          setData(result);
        }
      } catch (err) {
        if (mounted) {
          if (retryCount < maxRetries) {
            retryCount++;
            console.log(`Retrying... (${retryCount}/${maxRetries})`);
            setTimeout(fetchData, 2000 * retryCount); // Exponential backoff
          } else {
            setError(err instanceof Error ? err : new Error('Unknown error'));
          }
        }
      } finally {
        if (mounted) {
          setLoading(retryCount === 0 || retryCount === maxRetries);
        }
      }
    }

    fetchData();

    return () => { mounted = false; };
  }, [fetchFn, options?.retries]);

  return { data, loading, error };
}
```

**Fix Option 3: Implement Caching**

```typescript
// src/services/cache/huggingface.cache.ts

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

export class HuggingFaceCache {
  private cache = new Map<string, CacheEntry<any>>();
  private defaultTTL = 5 * 60 * 1000; // 5 minutes

  set<T>(key: string, data: T, ttl?: number): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.defaultTTL,
    });
  }

  get<T>(key: string): T | null {
    const entry = this.cache.get(key) as CacheEntry<T> | undefined;

    if (!entry) return null;

    const age = Date.now() - entry.timestamp;
    if (age > entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  isStale(key: string): boolean {
    const entry = this.cache.get(key);
    if (!entry) return true;

    const age = Date.now() - entry.timestamp;
    return age > entry.ttl;
  }

  clear(): void {
    this.cache.clear();
  }
}

// Usage in adapter
export class HuggingFaceAdapter {
  private cache = new HuggingFaceCache();

  async fetchData<T>(endpoint: string, cacheTTL?: number): Promise<T> {
    // Try cache first
    const cached = this.cache.get<T>(endpoint);
    if (cached) {
      console.log(`[Cache] Hit for ${endpoint}`);
      return cached;
    }

    // Fetch from Space
    console.log(`[HF] Fetching ${endpoint}...`);
    const data = await this.doFetch<T>(endpoint);

    // Cache result
    this.cache.set(endpoint, data, cacheTTL);

    return data;
  }

  private async doFetch<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.config.baseUrl}${endpoint}`);
    return response.json();
  }
}
```

**Fix Option 4: Use Request Pooling**

```typescript
// src/services/adapters/huggingface.adapter.ts

export class HuggingFaceAdapter {
  private requestPool = new Map<string, Promise<any>>();

  async fetchData<T>(endpoint: string): Promise<T> {
    // If same request is in-flight, return that promise instead of creating new request
    if (this.requestPool.has(endpoint)) {
      console.log(`[Pool] Reusing in-flight request for ${endpoint}`);
      return this.requestPool.get(endpoint)!;
    }

    // Create new request
    const promise = this.doFetch<T>(endpoint)
      .finally(() => {
        this.requestPool.delete(endpoint);
      });

    this.requestPool.set(endpoint, promise);
    return promise;
  }

  private async doFetch<T>(endpoint: string): Promise<T> {
    const url = `${this.config.baseUrl}${endpoint}`;
    const response = await fetch(url);
    return response.json();
  }
}
```

---

### Issue 6: Authentication Required (401/403)

**Symptoms:**
- `401 Unauthorized`
- `403 Forbidden`
- Response: `{"error": "Authentication required"}`
- Error: `Invalid token` or `Expired credentials`

**Root Cause:**
Space requires authentication (API token or credentials) that isn't provided.

**Diagnosis:**

```bash
# Test without authentication
curl -s https://really-amin-datasourceforcryptocurrency.hf.space/api/prices | jq

# Test with different auth methods

# Method 1: Bearer token
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  https://really-amin-datasourceforcryptocurrency.hf.space/api/prices

# Method 2: API key in header
curl -H "X-API-Key: YOUR_KEY_HERE" \
  https://really-amin-datasourceforcryptocurrency.hf.space/api/prices

# Method 3: API key in query
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/prices?api_key=YOUR_KEY_HERE"

# Check response status and error details
curl -i https://really-amin-datasourceforcryptocurrency.hf.space/api/prices
```

**Fix Option 1: Add Authentication to Configuration**

```bash
# .env
VITE_HF_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
VITE_HF_API_KEY=your-api-key-here
```

```typescript
// src/config/huggingface.ts
export const huggingfaceConfig = {
  baseUrl: 'https://really-amin-datasourceforcryptocurrency.hf.space',
  apiToken: import.meta.env.VITE_HF_API_TOKEN,
  apiKey: import.meta.env.VITE_HF_API_KEY,
};

// src/types/config.ts
export interface HuggingFaceConfig {
  baseUrl: string;
  timeout: number;
  apiToken?: string;  // For Bearer token auth
  apiKey?: string;    // For X-API-Key header
}
```

**Fix Option 2: Update Adapter to Include Auth Headers**

```typescript
// src/services/adapters/huggingface.adapter.ts

private getHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  // Add authentication if configured
  if (this.config.apiToken) {
    headers['Authorization'] = `Bearer ${this.config.apiToken}`;
  }

  if (this.config.apiKey) {
    headers['X-API-Key'] = this.config.apiKey;
  }

  return headers;
}

async fetchData<T>(endpoint: string): Promise<T> {
  const url = `${this.config.baseUrl}${endpoint}`;

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: this.getHeaders(),
      signal: AbortSignal.timeout(this.config.timeout),
    });

    if (response.status === 401 || response.status === 403) {
      throw new Error('Authentication failed. Check your API token/key.');
    }

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`HTTP ${response.status}: ${error}`);
    }

    return response.json();
  } catch (error) {
    console.error('[HF Auth Error]', error);
    throw error;
  }
}
```

**Fix Option 3: Get HuggingFace Token**

If Space requires HuggingFace credentials:

1. Visit: https://huggingface.co/settings/tokens
2. Click "New token"
3. Create token with "Read" access
4. Copy token to `.env`:
   ```env
   VITE_HF_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

---

## 🧪 Testing Protocol

### Test Sequence

Follow these tests in order. **Stop at the first failure** and fix before continuing.

#### Test 1: Space Health Check

```bash
echo "🔍 Test 1: Space Health Check"
curl -v https://really-amin-datasourceforcryptocurrency.hf.space/api/health

# ✅ Expected:
# HTTP/2 200 (or HTTP/1.1 200)
# Content-Type: application/json
# {"status": "healthy"}

# ❌ If fails:
# - HTTP 503: Space is building (wait 60 seconds)
# - HTTP 000 / Timeout: Space is sleeping (send request to wake it)
# - HTTP 404: Wrong endpoint (check endpoint mapping)
```

#### Test 2: Prices Endpoint

```bash
echo "🔍 Test 2: Prices Endpoint"
curl -s "https://really-amin-datasourceforcryptocurrency.hf.space/api/prices?symbols=BTC,ETH" | jq '.'

# ✅ Expected: Returns array or object with price data

# ❌ If fails:
# - Empty response: Try adding limit parameter
# - null: Endpoint exists but no data
# - 404: Wrong endpoint path
```

#### Test 3: OHLCV Endpoint

```bash
echo "🔍 Test 3: OHLCV Endpoint"
curl -s "https://really-amin-datasourceforcryptocurrency.hf.space/api/ohlcv?symbol=BTCUSDT&interval=1h&limit=10" | jq '.[:1]'

# ✅ Expected: OHLCV data with candle information

# ❌ If fails:
# - 404: Try different endpoint patterns
# - Wrong symbol format: Check symbol requirements (BTCUSDT vs BTC)
```

#### Test 4: Local Development (Vite Proxy)

```bash
echo "🔍 Test 4: Local Development"

# Make sure .env is configured
if [ ! -f .env ]; then
    cp .env.example .env
fi

# Install dependencies
npm install

# Start dev server
npm run dev &
DEV_PID=$!

# Wait for server to start
sleep 5

# Test via proxy
echo "Testing via proxy (http://localhost:5173/api/hf/...)"
curl -s "http://localhost:5173/api/hf/api/health" | jq

# Stop dev server
kill $DEV_PID

# ✅ Expected: Same response as direct Space call

# ❌ If fails:
# - Connection refused: Dev server didn't start
# - 404: Proxy path incorrect
# - CORS error: Check vite.config.ts
```

#### Test 5: Browser Testing

```bash
echo "🔍 Test 5: Browser Testing"

# 1. Start dev server
npm run dev

# 2. Open browser: http://localhost:5173

# 3. Open DevTools (F12)

# 4. Go to Network tab

# 5. Trigger data fetch (click buttons, load page, etc.)

# 6. Look for requests to /api/hf/...

# 7. Check response status
#    ✅ 200 = Success
#    ❌ 404 = Wrong endpoint
#    ❌ 0 (blocked) = CORS issue

# 8. Go to Console tab

# 9. Look for errors:
#    ❌ "Access to fetch blocked by CORS" → Use Vite proxy
#    ❌ "Cannot read property 'symbol' of undefined" → Data mapping issue
#    ❌ "Timeout" → Increase timeout in config
```

### Complete Test Checklist

- [ ] Health check returns 200
- [ ] Prices endpoint returns data
- [ ] OHLCV endpoint returns data
- [ ] Vite proxy works locally
- [ ] No CORS errors in browser console
- [ ] Data renders correctly in UI
- [ ] No undefined values in UI
- [ ] Network requests complete < 30 seconds
- [ ] Application handles errors gracefully

---

## 🐛 Debugging Commands

### Debugging HuggingFace Integration

```bash
# Enable verbose logging
export DEBUG=*:huggingface*,*:adapter*

# Watch logs in real-time
npm run dev 2>&1 | grep -i "huggingface\|hf\|adapter"

# Log all fetch requests
cat > src/services/debug.ts << 'EOF'
// Intercept all fetch calls
const originalFetch = window.fetch;
window.fetch = function(...args) {
  const [resource] = args;
  console.log(`📡 Fetch: ${resource}`);

  return originalFetch.apply(this, args as any)
    .then(response => {
      console.log(`📡 Response: ${resource} → ${response.status}`);
      return response.clone();
    })
    .catch(error => {
      console.error(`📡 Error: ${resource} →`, error);
      throw error;
    });
};
EOF

# In your main component or app.tsx:
// Add this early in your app initialization
import './services/debug';
```

### Network Debugging

```bash
# Monitor network activity
curl -v https://really-amin-datasourceforcryptocurrency.hf.space/api/prices

# Show request headers only
curl -I https://really-amin-datasourceforcryptocurrency.hf.space/api/health

# Show response headers
curl -D - https://really-amin-datasourceforcryptocurrency.hf.space/api/health

# Test with custom headers
curl -H "Authorization: Bearer token" \
     -H "X-Custom-Header: value" \
     https://really-amin-datasourceforcryptocurrency.hf.space/api/prices

# Save full request/response to file
curl -v https://really-amin-datasourceforcryptocurrency.hf.space/api/health 2>&1 | tee debug.log
```

### Response Inspection

```bash
# Pretty print JSON response
curl -s https://really-amin-datasourceforcryptocurrency.hf.space/api/prices | jq '.'

# Show specific fields
curl -s https://really-amin-datasourceforcryptocurrency.hf.space/api/prices | jq '.[0] | keys'

# Count items
curl -s https://really-amin-datasourceforcryptocurrency.hf.space/api/prices | jq 'length'

# Filter by condition
curl -s https://really-amin-datasourceforcryptocurrency.hf.space/api/prices | jq '.[] | select(.symbol == "BTC")'

# Convert to CSV
curl -s https://really-amin-datasourceforcryptocurrency.hf.space/api/prices | jq -r '.[] | [.symbol, .price] | @csv'
```

### TypeScript/React Debugging

```typescript
// Add detailed logging to adapter
class HuggingFaceAdapter {
  async fetchData<T>(endpoint: string): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    console.group(`🔵 HF Fetch: ${endpoint}`);
    console.log('URL:', url);
    console.log('Headers:', this.getHeaders());
    console.log('Timeout:', this.config.timeout);
    console.timeStamp('start');

    try {
      const response = await fetch(url, {
        headers: this.getHeaders(),
      });

      const elapsed = performance.now() - performance.timing.navigationStart;
      console.log('Response status:', response.status);
      console.log('Time elapsed:', `${elapsed}ms`);

      const data = await response.json();
      console.log('Response data:', data);
      console.groupEnd();

      return data;
    } catch (error) {
      console.error('Error:', error);
      console.groupEnd();
      throw error;
    }
  }
}
```

### Performance Profiling

```bash
# Measure response time
time curl -s https://really-amin-datasourceforcryptocurrency.hf.space/api/prices > /dev/null

# Detailed timing breakdown
curl -w "
Time breakdown:
  DNS lookup: %{time_namelookup}s
  TCP connect: %{time_connect}s
  TLS handshake: %{time_appconnect}s
  Server processing: %{time_starttransfer}s
  Total: %{time_total}s
" -o /dev/null -s https://really-amin-datasourceforcryptocurrency.hf.space/api/prices

# Repeat tests and get average
for i in {1..5}; do
  echo "Request $i:"
  curl -w "Time: %{time_total}s\n" -o /dev/null -s https://really-amin-datasourceforcryptocurrency.hf.space/api/prices
done
```

---

## ⚙️ Configuration Guide

### Environment Variables

Create `.env` file based on `.env.example`:

```bash
# Copy template
cp .env.example .env
```

### Available Configuration Options

```env
# Data Source Configuration
PRIMARY_DATA_SOURCE=huggingface          # Main data source: huggingface, coingecko, binance
FALLBACK_ENABLED=true                   # Enable fallback sources
FALLBACK_SOURCES=coingecko,coincap       # Comma-separated fallback sources

# HuggingFace Space Configuration
HF_SPACE_BASE_URL=https://really-amin-datasourceforcryptocurrency.hf.space
HF_REQUEST_TIMEOUT=30000                # Request timeout in milliseconds
HF_CACHE_TTL=300000                     # Cache time-to-live in milliseconds (5 minutes)
HF_API_TOKEN=                           # HuggingFace API token (if required)

# Development Configuration
VITE_DEV_SERVER_HOST=localhost
VITE_DEV_SERVER_PORT=5173
VITE_LOG_LEVEL=info                     # debug, info, warn, error

# Proxy Configuration (for development)
VITE_USE_PROXY=true                     # Use Vite proxy for API calls
VITE_PROXY_PATH=/api/hf                 # Proxy mount path
```

### Vite Configuration

File: `vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],

  server: {
    host: 'localhost',
    port: 5173,

    proxy: {
      '/api/hf': {
        target: 'https://really-amin-datasourceforcryptocurrency.hf.space',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/hf/, ''),
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.error('Proxy error:', err);
          });
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('→ Proxying:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('← Response:', proxyRes.statusCode);
          });
        }
      }
    }
  },

  build: {
    outDir: 'dist',
    sourcemap: true,
  }
})
```

### TypeScript Configuration

File: `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "strict": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "allowJs": false,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@/services/*": ["src/services/*"],
      "@/components/*": ["src/components/*"],
      "@/types/*": ["src/types/*"]
    }
  }
}
```

---

## 🌳 Troubleshooting Decision Tree

Start here when you encounter issues:

```
┌─ START: Application not working
│
├─ Step 1: Can you reach the Space?
│  │
│  ├─ NO (timeout, connection refused)
│  │  └─ Issue 1: Space is sleeping → Wake it up
│  │
│  └─ YES (200 OK)
│     │
│     └─ Step 2: Are you getting the correct endpoints?
│        │
│        ├─ NO (404 Not Found)
│        │  └─ Issue 2: Wrong endpoints → Update adapter
│        │
│        └─ YES (200 OK)
│           │
│           └─ Step 3: Is the data in the correct format?
│              │
│              ├─ NO (undefined values, type errors)
│              │  └─ Issue 3: Response format mismatch → Update mapping
│              │
│              └─ YES (correct data types)
│                 │
│                 └─ Step 4: Does the browser show CORS errors?
│                    │
│                    ├─ YES (Access blocked by CORS)
│                    │  └─ Issue 4: CORS errors → Add Vite proxy
│                    │
│                    └─ NO (no CORS errors)
│                       │
│                       └─ Step 5: Are requests timing out?
│                          │
│                          ├─ YES (AbortError timeout)
│                          │  └─ Issue 5: Timeout → Increase timeout or use caching
│                          │
│                          └─ NO (requests complete)
│                             │
│                             └─ Step 6: Check authentication
│                                │
│                                ├─ 401/403 errors
│                                │  └─ Issue 6: Auth required → Add token/key
│                                │
│                                └─ ✅ WORKING!
```

**Quick Reference:**
- Space not responding → Check Space status, wait 60 seconds
- Getting 404 → Update endpoint paths in adapter
- Data undefined → Update field name mappings
- CORS errors → Enable Vite proxy
- Timeouts → Increase timeout or implement caching
- 401/403 → Add API token/key to config

---

## ❓ FAQ

### Q: How do I know which version of the Space is deployed?

```bash
# Check Space's version endpoint (if available)
curl -s https://really-amin-datasourceforcryptocurrency.hf.space/api/version

# Or check the Space's README on HuggingFace
# Visit: https://huggingface.co/spaces/Really-amin/Datasourceforcryptocurrency

# Or check git log if you have access
cd hf-data-engine
git log --oneline | head -5
```

### Q: Can I use this application without HuggingFace?

Yes! Configure fallback data sources:

```env
PRIMARY_DATA_SOURCE=coingecko
FALLBACK_ENABLED=true
FALLBACK_SOURCES=coincap,binance
```

### Q: What if HuggingFace Space goes down permanently?

1. Deploy your own instance of `hf-data-engine`
2. Update `HF_SPACE_BASE_URL` in `.env`
3. Or switch to fallback sources permanently

### Q: How do I cache data for offline use?

```typescript
// src/services/storage/localStorage.cache.ts

export class LocalStorageCache {
  static set<T>(key: string, data: T): void {
    localStorage.setItem(key, JSON.stringify({
      data,
      timestamp: Date.now(),
    }));
  }

  static get<T>(key: string, maxAge?: number): T | null {
    const stored = localStorage.getItem(key);
    if (!stored) return null;

    const { data, timestamp } = JSON.parse(stored);

    if (maxAge && Date.now() - timestamp > maxAge) {
      localStorage.removeItem(key);
      return null;
    }

    return data;
  }
}
```

### Q: How do I monitor HuggingFace Space uptime?

Use a monitoring service or cron job:

```bash
# Create uptime.sh
#!/bin/bash
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://really-amin-datasourceforcryptocurrency.hf.space/api/health)
echo "$TIMESTAMP,HuggingFace Space,$STATUS" >> uptime.log

# Add to crontab
*/5 * * * * /path/to/uptime.sh
```

### Q: Can I contribute improvements to the HuggingFace Space?

Yes! The space is open source:

1. Fork the repository
2. Make improvements
3. Submit a pull request
4. Visit: https://huggingface.co/spaces/Really-amin/Datasourceforcryptocurrency

### Q: What are the rate limits?

From the Space documentation:
- `/api/prices`: 120 requests/minute
- `/api/ohlcv`: 60 requests/minute
- `/api/sentiment`: 30 requests/minute
- `/api/health`: Unlimited

Implement rate limiting in your client:

```typescript
// src/services/rateLimit.ts

export class RateLimiter {
  private timestamps: number[] = [];

  constructor(private maxRequests: number, private windowMs: number) {}

  canRequest(): boolean {
    const now = Date.now();

    // Remove old timestamps outside window
    this.timestamps = this.timestamps.filter(ts => now - ts < this.windowMs);

    // Check if under limit
    if (this.timestamps.length < this.maxRequests) {
      this.timestamps.push(now);
      return true;
    }

    return false;
  }
}

// Usage
const limiter = new RateLimiter(100, 60000); // 100 req/min

if (limiter.canRequest()) {
  // Make request
} else {
  // Wait or queue request
}
```

### Q: How do I debug issues in production?

1. Check browser console for errors
2. Check Network tab for failed requests
3. Review server logs
4. Use error tracking service (Sentry, LogRocket, etc.)

```typescript
// Error tracking integration
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "your-sentry-dsn",
  environment: import.meta.env.MODE,
  tracesSampleRate: 0.1,
});

try {
  // Your code
} catch (error) {
  Sentry.captureException(error);
}
```

---

## 📞 Support

- **HuggingFace Space:** https://huggingface.co/spaces/Really-amin/Datasourceforcryptocurrency
- **GitHub Issues:** Report bugs and request features
- **Documentation:** See README.md and other docs

---

**Last Updated:** 2025-11-15
**Version:** 2.0
**Maintained by:** Crypto Data Aggregator Team
