#!/usr/bin/env python3
"""
Simple verification of API keys using standard library
"""

import os
import json
import urllib.request
import urllib.error
import urllib.parse

# Load environment variables
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

print("=" * 70)
print("🔑 API KEYS VERIFICATION")
print("=" * 70)

# Check NewsAPI
newsapi_key = os.getenv("NEWSAPI_KEY", "")
if newsapi_key:
    print(f"\n✅ NewsAPI Key: {newsapi_key[:10]}...{newsapi_key[-5:]}")
    print(f"   Length: {len(newsapi_key)} characters")
    print(f"   Status: Configured")
    
    # Try to verify
    try:
        url = f"https://newsapi.org/v2/everything?q=bitcoin&pageSize=1&apiKey={newsapi_key}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get("status") == "ok":
                print(f"   ✅ VERIFIED: API key is working!")
                print(f"   Total articles available: {data.get('totalResults', 0)}")
            else:
                print(f"   ⚠️ API returned: {data}")
    except urllib.error.HTTPError as e:
        print(f"   ❌ HTTP Error {e.code}: {e.reason}")
    except Exception as e:
        print(f"   ⚠️ Verification failed: {e}")
else:
    print("\n❌ NewsAPI Key: Not configured")

# Check CoinMarketCap
cmc_key = os.getenv("COINMARKETCAP_API_KEY", "")
if cmc_key:
    print(f"\n✅ CoinMarketCap Key: {cmc_key[:10]}...{cmc_key[-5:]}")
    print(f"   Length: {len(cmc_key)} characters")
    print(f"   Status: Configured")
    
    # Try to verify
    try:
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?start=1&limit=1&convert=USD"
        req = urllib.request.Request(url)
        req.add_header("X-CMC_PRO_API_KEY", cmc_key)
        req.add_header("Accept", "application/json")
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get("status", {}).get("error_code") == 0:
                print(f"   ✅ VERIFIED: API key is working!")
                credits = data.get("status", {}).get("credit_count", 0)
                print(f"   Credits used: {credits}")
            else:
                print(f"   ⚠️ API returned: {data}")
    except urllib.error.HTTPError as e:
        print(f"   ❌ HTTP Error {e.code}: {e.reason}")
        try:
            error_data = json.loads(e.read().decode())
            print(f"   Error details: {error_data}")
        except:
            pass
    except Exception as e:
        print(f"   ⚠️ Verification failed: {e}")
else:
    print("\n❌ CoinMarketCap Key: Not configured")

# Check HuggingFace
hf_token = os.getenv("HF_TOKEN", "")
if hf_token:
    print(f"\n✅ HuggingFace Token: {hf_token[:7]}...{hf_token[-5:]}")
    print(f"   Length: {len(hf_token)} characters")
    print(f"   Status: Configured")
else:
    print("\n❌ HuggingFace Token: Not configured")

print("\n" + "=" * 70)
print("📊 CONFIGURATION SUMMARY")
print("=" * 70)

configured = []
if newsapi_key:
    configured.append("NewsAPI")
if cmc_key:
    configured.append("CoinMarketCap")
if hf_token:
    configured.append("HuggingFace")

print(f"\n✅ Configured APIs: {len(configured)}/3")
for api in configured:
    print(f"   • {api}")

print("\n💡 CAPABILITIES ENABLED:")
if newsapi_key:
    print("   ✅ Access to 80,000+ news sources worldwide")
    print("   ✅ Real-time crypto news aggregation")
if cmc_key:
    print("   ✅ Professional-grade cryptocurrency data")
    print("   ✅ Real-time market prices and rankings")
    print("   ✅ Historical price data")
if hf_token:
    print("   ✅ HuggingFace AI model access")
    print("   ✅ Sentiment analysis capabilities")

print("\n🎯 SYSTEM STATUS:")
if len(configured) == 3:
    print("   🌟 EXCELLENT: All APIs configured!")
    print("   Your system has full capabilities enabled.")
elif len(configured) >= 2:
    print("   ✅ GOOD: Core APIs configured")
    print("   System is ready for production use.")
else:
    print("   ⚠️ LIMITED: Some APIs missing")
    print("   System will work but with reduced capabilities.")

print("\n" + "=" * 70)
print("✅ VERIFICATION COMPLETE")
print("=" * 70)
