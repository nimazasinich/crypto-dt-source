#!/usr/bin/env python3
"""
Test script for new API integrations (Alpha Vantage and Massive.com)
"""

import asyncio
import sys
import os
from pathlib import Path

# Add workspace and hf-data-engine to path
workspace_path = str(Path(__file__).parent)
hf_engine_path = os.path.join(workspace_path, "hf-data-engine")
sys.path.insert(0, workspace_path)
sys.path.insert(0, hf_engine_path)

async def test_alphavantage():
    """Test Alpha Vantage provider"""
    print("\n" + "="*80)
    print("Testing Alpha Vantage Provider")
    print("="*80)
    
    try:
        from providers.alphavantage_provider import AlphaVantageProvider
        
        # Initialize provider
        provider = AlphaVantageProvider(api_key="40XS7GQ6AU9NB6Y4")
        print("✅ Provider initialized")
        
        # Test health check
        print("\n📊 Testing health check...")
        health = await provider.get_health()
        print(f"   Status: {health.status}")
        print(f"   Last check: {health.lastCheck}")
        
        # Test price fetch
        print("\n💰 Testing price fetch for BTC, ETH...")
        try:
            prices = await provider.fetch_prices(["BTC", "ETH"])
            print(f"   Fetched {len(prices)} prices")
            for price in prices:
                print(f"   - {price.symbol}: ${price.price:.2f}")
        except Exception as e:
            print(f"   ⚠️ Price fetch: {e}")
        
        # Test OHLCV fetch
        print("\n📈 Testing OHLCV fetch for BTC...")
        try:
            ohlcv = await provider.fetch_ohlcv("BTC", "1d", 5)
            print(f"   Fetched {len(ohlcv)} candles")
            if ohlcv:
                latest = ohlcv[0]
                print(f"   Latest: O={latest.open:.2f} H={latest.high:.2f} L={latest.low:.2f} C={latest.close:.2f}")
        except Exception as e:
            print(f"   ⚠️ OHLCV fetch: {e}")
        
        # Close provider
        await provider.close()
        print("\n✅ Alpha Vantage tests completed")
        
    except Exception as e:
        print(f"\n❌ Alpha Vantage test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_massive():
    """Test Massive.com provider"""
    print("\n" + "="*80)
    print("Testing Massive.com Provider")
    print("="*80)
    
    try:
        from providers.massive_provider import MassiveProvider
        
        # Initialize provider
        provider = MassiveProvider(api_key="PwI1oqICvx9hNMzkGTHnGzA7v2VCE7JE")
        print("✅ Provider initialized")
        
        # Test health check
        print("\n📊 Testing health check...")
        health = await provider.get_health()
        print(f"   Status: {health.status}")
        print(f"   Last check: {health.lastCheck}")
        
        # Test dividends fetch
        print("\n💵 Testing dividends fetch for AAPL...")
        try:
            dividends = await provider.fetch_dividends(ticker="AAPL", limit=5)
            print(f"   Fetched {len(dividends)} dividend records")
            for div in dividends[:3]:
                print(f"   - {div.get('ticker', 'N/A')}: ${div.get('cash_amount', 0)} on {div.get('pay_date', 'N/A')}")
        except Exception as e:
            print(f"   ⚠️ Dividends fetch: {e}")
        
        # Test quotes fetch
        print("\n📊 Testing quote fetch for AAPL...")
        try:
            prices = await provider.fetch_prices(["AAPL"])
            print(f"   Fetched {len(prices)} quotes")
            for price in prices:
                print(f"   - {price.symbol}: ${price.price:.2f}")
        except Exception as e:
            print(f"   ⚠️ Quote fetch: {e}")
        
        # Test splits fetch
        print("\n🔀 Testing splits fetch...")
        try:
            splits = await provider.fetch_splits(limit=5)
            print(f"   Fetched {len(splits)} split records")
            for split in splits[:3]:
                print(f"   - {split.get('ticker', 'N/A')}")
        except Exception as e:
            print(f"   ⚠️ Splits fetch: {e}")
        
        # Close provider
        await provider.close()
        print("\n✅ Massive.com tests completed")
        
    except Exception as e:
        print(f"\n❌ Massive.com test failed: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 Testing New API Integrations")
    print("="*80)
    
    # Test Alpha Vantage
    await test_alphavantage()
    
    # Test Massive.com
    await test_massive()
    
    print("\n" + "="*80)
    print("✅ All tests completed!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
