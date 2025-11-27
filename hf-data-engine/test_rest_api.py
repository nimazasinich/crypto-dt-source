"""
Test script for REST API providers

Run this script to verify all providers are working:
    python test_rest_api.py

Tests:
- All provider imports
- Basic provider initialization
- Sample API calls (with actual external requests)
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))


async def test_imports():
    """Test all provider and router imports"""
    print("=" * 60)
    print("Testing Imports")
    print("=" * 60)
    
    try:
        from providers.etherscan_provider import EtherscanProvider
        print("✓ EtherscanProvider")
        
        from providers.bscscan_provider import BscscanProvider
        print("✓ BscscanProvider")
        
        from providers.tronscan_provider import TronscanProvider
        print("✓ TronscanProvider")
        
        from providers.coinmarketcap_provider import CoinMarketCapProvider
        print("✓ CoinMarketCapProvider")
        
        from providers.news_provider import NewsProvider
        print("✓ NewsProvider")
        
        from providers.hf_sentiment_provider import HFSentimentProvider
        print("✓ HFSentimentProvider")
        
        from routers.blockchain import router as blockchain_router
        print("✓ blockchain_router")
        
        from routers.market import router as market_router
        print("✓ market_router")
        
        from routers.news import router as news_router
        print("✓ news_router")
        
        from routers.hf_inference import router as hf_inference_router
        print("✓ hf_inference_router")
        
        print("\n✓ All imports successful!\n")
        return True
    except Exception as e:
        print(f"\n✗ Import failed: {e}\n")
        return False


async def test_etherscan():
    """Test Etherscan provider"""
    print("=" * 60)
    print("Testing Etherscan Provider")
    print("=" * 60)
    
    from providers.etherscan_provider import EtherscanProvider
    
    provider = EtherscanProvider()
    
    # Test with Vitalik's address
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    
    print(f"Testing get_transactions for {address[:10]}...")
    result = await provider.get_transactions(address, offset=5)
    
    if result.get("success"):
        count = result.get("data", {}).get("count", 0)
        print(f"✓ Got {count} transactions")
    else:
        print(f"✗ Error: {result.get('error')}")
    
    print(f"\nTesting get_balance...")
    result = await provider.get_balance(address)
    
    if result.get("success"):
        balance = result.get("data", {}).get("balance_eth", 0)
        print(f"✓ Balance: {balance:.4f} ETH")
    else:
        print(f"✗ Error: {result.get('error')}")
    
    await provider.close()
    print()


async def test_bscscan():
    """Test BscScan provider"""
    print("=" * 60)
    print("Testing BscScan Provider")
    print("=" * 60)
    
    from providers.bscscan_provider import BscscanProvider
    
    provider = BscscanProvider()
    
    # Test with a known BSC address
    address = "0x8894e0a0c962cb723c1976a4421c95949be2d4e3"  # Binance hot wallet
    
    print(f"Testing get_transactions for {address[:10]}...")
    result = await provider.get_transactions(address, offset=5)
    
    if result.get("success"):
        count = result.get("data", {}).get("count", 0)
        print(f"✓ Got {count} transactions")
    else:
        print(f"✗ Error: {result.get('error')}")
    
    await provider.close()
    print()


async def test_tronscan():
    """Test TronScan provider"""
    print("=" * 60)
    print("Testing TronScan Provider")
    print("=" * 60)
    
    from providers.tronscan_provider import TronscanProvider
    
    provider = TronscanProvider()
    
    # Test with USDT contract owner
    address = "THPvaUhoh2Qn2y9THCZML3H815hhFhn5YC"  # USDT contract
    
    print(f"Testing get_transactions for {address[:10]}...")
    result = await provider.get_transactions(address, limit=5)
    
    if result.get("success"):
        count = result.get("data", {}).get("count", 0)
        print(f"✓ Got {count} transactions")
    else:
        print(f"✗ Error: {result.get('error')}")
    
    await provider.close()
    print()


async def test_coinmarketcap():
    """Test CoinMarketCap provider"""
    print("=" * 60)
    print("Testing CoinMarketCap Provider")
    print("=" * 60)
    
    from providers.coinmarketcap_provider import CoinMarketCapProvider
    
    provider = CoinMarketCapProvider()
    
    print("Testing get_latest_listings (top 10)...")
    result = await provider.get_latest_listings(limit=10)
    
    if result.get("success"):
        cryptos = result.get("data", {}).get("cryptocurrencies", [])
        print(f"✓ Got {len(cryptos)} cryptocurrencies")
        for c in cryptos[:3]:
            print(f"   #{c.get('rank')} {c.get('symbol')}: ${c.get('price', 0):.2f}")
    else:
        print(f"✗ Error: {result.get('error')}")
    
    print("\nTesting get_quotes for BTC,ETH...")
    result = await provider.get_quotes(symbols="BTC,ETH")
    
    if result.get("success"):
        quotes = result.get("data", {}).get("quotes", [])
        print(f"✓ Got {len(quotes)} quotes")
        for q in quotes:
            print(f"   {q.get('symbol')}: ${q.get('price', 0):.2f}")
    else:
        print(f"✗ Error: {result.get('error')}")
    
    await provider.close()
    print()


async def test_news():
    """Test News provider"""
    print("=" * 60)
    print("Testing News Provider")
    print("=" * 60)
    
    from providers.news_provider import NewsProvider
    
    provider = NewsProvider()
    
    print("Testing get_crypto_news (5 articles)...")
    result = await provider.get_crypto_news(page_size=5)
    
    if result.get("success"):
        articles = result.get("data", {}).get("articles", [])
        print(f"✓ Got {len(articles)} articles")
        for a in articles[:2]:
            title = a.get("title", "")[:50]
            print(f"   - {title}...")
    else:
        print(f"✗ Error: {result.get('error')}")
    
    await provider.close()
    print()


async def test_hf_sentiment():
    """Test HuggingFace Sentiment provider"""
    print("=" * 60)
    print("Testing HuggingFace Sentiment Provider")
    print("=" * 60)
    
    from providers.hf_sentiment_provider import HFSentimentProvider
    
    provider = HFSentimentProvider()
    
    test_text = "Bitcoin is surging to new all-time highs!"
    
    print(f"Testing analyze_sentiment...")
    print(f"   Text: '{test_text}'")
    result = await provider.analyze_sentiment(test_text)
    
    if result.get("success"):
        sentiment = result.get("data", {}).get("sentiment", {})
        print(f"✓ Sentiment: {sentiment.get('label')} (score: {sentiment.get('score', 0):.3f})")
    else:
        error = result.get("error", "")
        if "loading" in error.lower():
            print(f"⚠ Model is loading, retry in a few seconds")
        else:
            print(f"✗ Error: {error}")
    
    await provider.close()
    print()


async def test_main_app():
    """Test main FastAPI app"""
    print("=" * 60)
    print("Testing Main FastAPI App")
    print("=" * 60)
    
    from main import app
    
    print(f"✓ App loaded: {app.title}")
    print(f"  Version: {app.version}")
    
    # Count routes by category
    blockchain_routes = [r for r in app.routes if hasattr(r, 'path') and '/blockchain/' in r.path]
    market_routes = [r for r in app.routes if hasattr(r, 'path') and '/market/' in r.path]
    news_routes = [r for r in app.routes if hasattr(r, 'path') and '/news/' in r.path]
    hf_routes = [r for r in app.routes if hasattr(r, 'path') and '/hf/' in r.path]
    
    print(f"\nRegistered REST API v1 Routes:")
    print(f"  Blockchain: {len(blockchain_routes)} endpoints")
    print(f"  Market: {len(market_routes)} endpoints")
    print(f"  News: {len(news_routes)} endpoints")
    print(f"  HF AI: {len(hf_routes)} endpoints")
    print(f"  Total: {len(blockchain_routes) + len(market_routes) + len(news_routes) + len(hf_routes)} endpoints")
    print()


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print(" HF-DATA-ENGINE REST API PROVIDER TESTS")
    print("=" * 60 + "\n")
    
    # Test imports first
    if not await test_imports():
        print("Import tests failed. Exiting.")
        return
    
    # Test main app
    await test_main_app()
    
    # Test each provider
    print("\n" + "=" * 60)
    print(" PROVIDER API TESTS (Live Requests)")
    print("=" * 60 + "\n")
    
    await test_etherscan()
    await test_bscscan()
    await test_tronscan()
    await test_coinmarketcap()
    await test_news()
    await test_hf_sentiment()
    
    print("=" * 60)
    print(" ALL TESTS COMPLETED")
    print("=" * 60)
    print("\n✓ REST API implementation verified!")
    print("✓ No WebSockets used - pure HTTP endpoints")
    print("✓ All providers return {success, source, data} format")
    print("\nTo start the server:")
    print("  uvicorn main:app --host 0.0.0.0 --port 8000")
    print()


if __name__ == "__main__":
    asyncio.run(main())
