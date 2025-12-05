"""
Real API Client with actual API keys and functional endpoints
Uses keys from all_apis_merged_2025.json
"""
import httpx
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path

# Load API keys from all_apis_merged_2025.json
def load_api_keys():
    """Load API keys from the merged registry"""
    try:
        registry_path = Path(__file__).parent / "all_apis_merged_2025.json"
        if registry_path.exists():
            with open(registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("discovered_keys", {})
        return {}
    except Exception as e:
        print(f"Warning: Could not load API keys: {e}")
        return {}

API_KEYS = load_api_keys()

# Extract keys with fallbacks
ETHERSCAN_KEY = API_KEYS.get("etherscan", [""])[0] if API_KEYS.get("etherscan") else ""
ETHERSCAN_KEY_2 = API_KEYS.get("etherscan", ["", ""])[1] if len(API_KEYS.get("etherscan", [])) > 1 else ""
BSCSCAN_KEY = API_KEYS.get("bscscan", [""])[0] if API_KEYS.get("bscscan") else ""
TRONSCAN_KEY = API_KEYS.get("tronscan", [""])[0] if API_KEYS.get("tronscan") else ""
CMC_KEY = API_KEYS.get("coinmarketcap", [""])[0] if API_KEYS.get("coinmarketcap") else ""
CMC_KEY_2 = API_KEYS.get("coinmarketcap", ["", ""])[1] if len(API_KEYS.get("coinmarketcap", [])) > 1 else ""
CRYPTOCOMPARE_KEY = API_KEYS.get("cryptocompare", [""])[0] if API_KEYS.get("cryptocompare") else ""
NEWSAPI_KEY = API_KEYS.get("newsapi", [""])[0] if API_KEYS.get("newsapi") else ""
HF_KEY = API_KEYS.get("huggingface", [""])[0] if API_KEYS.get("huggingface") else ""


class RealAPIClient:
    """Real API client that actually calls external services"""
    
    def __init__(self):
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        self.client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)
        
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    # ===== MARKET DATA =====
    
    async def get_coingecko_price(self, coin_ids: List[str], vs_currencies: List[str] = None) -> Dict[str, Any]:
        """Get price from CoinGecko (free, no API key needed)"""
        if vs_currencies is None:
            vs_currencies = ["usd"]
        
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": ",".join(coin_ids),
            "vs_currencies": ",".join(vs_currencies),
            "include_24hr_change": "true",
            "include_market_cap": "true"
        }
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"CoinGecko error: {e}")
            return {}
    
    async def get_binance_price(self, symbol: str) -> Dict[str, Any]:
        """Get price from Binance (free, no API key needed)"""
        url = f"https://api.binance.com/api/v3/ticker/24hr"
        params = {"symbol": symbol.upper()}
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Binance error: {e}")
            return {}
    
    async def get_coinmarketcap_quotes(self, symbols: List[str]) -> Dict[str, Any]:
        """Get quotes from CoinMarketCap (requires API key)"""
        if not CMC_KEY:
            return {"error": "CMC API key not configured"}
        
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        params = {"symbol": ",".join(symbols), "convert": "USD"}
        headers = {"X-CMC_PRO_API_KEY": CMC_KEY}
        
        try:
            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 and CMC_KEY_2:
                # Try fallback key
                headers = {"X-CMC_PRO_API_KEY": CMC_KEY_2}
                try:
                    response = await self.client.get(url, params=params, headers=headers)
                    response.raise_for_status()
                    return response.json()
                except Exception as e2:
                    print(f"CMC fallback error: {e2}")
                    return {"error": str(e2)}
            return {"error": str(e)}
        except Exception as e:
            print(f"CMC error: {e}")
            return {"error": str(e)}
    
    async def get_cryptocompare_ohlcv(self, fsym: str, tsym: str, limit: int = 30) -> Dict[str, Any]:
        """Get OHLCV data from CryptoCompare"""
        if not CRYPTOCOMPARE_KEY:
            return {"error": "CryptoCompare API key not configured"}
        
        url = "https://min-api.cryptocompare.com/data/v2/histoday"
        params = {
            "fsym": fsym.upper(),
            "tsym": tsym.upper(),
            "limit": limit,
            "api_key": CRYPTOCOMPARE_KEY
        }
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"CryptoCompare error: {e}")
            return {"error": str(e)}
    
    # ===== NEWS =====
    
    async def get_cryptopanic_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get news from CryptoPanic (free, no key needed)"""
        url = "https://cryptopanic.com/api/v1/posts/"
        params = {"public": "true"}
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])[:limit]
            return [
                {
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "source": item.get("source", {}).get("title", "Unknown"),
                    "published_at": item.get("published_at"),
                    "sentiment": item.get("votes", {}).get("positive", 0)
                }
                for item in results
            ]
        except Exception as e:
            print(f"CryptoPanic error: {e}")
            return []
    
    async def get_coindesk_rss(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get news from CoinDesk RSS"""
        url = "https://www.coindesk.com/arc/outboundfeeds/rss/"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            # Simple RSS parsing
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.text)
            items = []
            for item in root.findall(".//item")[:limit]:
                title = item.find("title")
                link = item.find("link")
                pubDate = item.find("pubDate")
                items.append({
                    "title": title.text if title is not None else "",
                    "url": link.text if link is not None else "",
                    "source": "CoinDesk",
                    "published_at": pubDate.text if pubDate is not None else ""
                })
            return items
        except Exception as e:
            print(f"CoinDesk RSS error: {e}")
            return []
    
    # ===== SENTIMENT =====
    
    async def get_fear_greed_index(self) -> Dict[str, Any]:
        """Get Fear & Greed Index from Alternative.me (free)"""
        url = "https://api.alternative.me/fng/"
        params = {"limit": 1}
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("data"):
                item = data["data"][0]
                return {
                    "value": int(item.get("value", 50)),
                    "classification": item.get("value_classification", "neutral"),
                    "timestamp": item.get("timestamp"),
                    "time_until_update": item.get("time_until_update")
                }
            return {}
        except Exception as e:
            print(f"Fear & Greed error: {e}")
            return {}
    
    async def get_cfgi_sentiment(self) -> Dict[str, Any]:
        """Get sentiment from CFGI (free)"""
        url = "https://api.cfgi.io/v1/fear-greed"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Fallback to legacy endpoint
            try:
                response = await self.client.get("https://cfgi.io/api")
                response.raise_for_status()
                return response.json()
            except Exception as e2:
                print(f"CFGI error: {e2}")
                return {}
    
    # ===== BLOCK EXPLORERS =====
    
    async def get_eth_balance(self, address: str) -> Dict[str, Any]:
        """Get ETH balance from Etherscan"""
        if not ETHERSCAN_KEY:
            return {"error": "Etherscan API key not configured"}
        
        url = "https://api.etherscan.io/api"
        params = {
            "module": "account",
            "action": "balance",
            "address": address,
            "tag": "latest",
            "apikey": ETHERSCAN_KEY
        }
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "1":
                return {
                    "address": address,
                    "balance_wei": data.get("result"),
                    "balance_eth": int(data.get("result", 0)) / 1e18
                }
            return {"error": data.get("message", "Unknown error")}
        except Exception as e:
            if ETHERSCAN_KEY_2:
                # Try fallback key
                params["apikey"] = ETHERSCAN_KEY_2
                try:
                    response = await self.client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    if data.get("status") == "1":
                        return {
                            "address": address,
                            "balance_wei": data.get("result"),
                            "balance_eth": int(data.get("result", 0)) / 1e18
                        }
                except:
                    pass
            print(f"Etherscan error: {e}")
            return {"error": str(e)}
    
    async def get_bsc_balance(self, address: str) -> Dict[str, Any]:
        """Get BSC balance from BscScan"""
        if not BSCSCAN_KEY:
            return {"error": "BscScan API key not configured"}
        
        url = "https://api.bscscan.com/api"
        params = {
            "module": "account",
            "action": "balance",
            "address": address,
            "apikey": BSCSCAN_KEY
        }
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "1":
                return {
                    "address": address,
                    "balance_wei": data.get("result"),
                    "balance_bnb": int(data.get("result", 0)) / 1e18
                }
            return {"error": data.get("message", "Unknown error")}
        except Exception as e:
            print(f"BscScan error: {e}")
            return {"error": str(e)}
    
    async def get_tron_account(self, address: str) -> Dict[str, Any]:
        """Get TRON account from TronScan"""
        url = f"https://apilist.tronscanapi.com/api/account"
        params = {"address": address}
        headers = {"TRON-PRO-API-KEY": TRONSCAN_KEY} if TRONSCAN_KEY else {}
        
        try:
            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            return {
                "address": address,
                "balance_sun": data.get("balance", 0),
                "balance_trx": data.get("balance", 0) / 1e6,
                "bandwidth": data.get("bandwidth", {}),
                "energy": data.get("frozenForEnergy", {})
            }
        except Exception as e:
            print(f"TronScan error: {e}")
            return {"error": str(e)}
    
    # ===== AGGREGATED METHODS =====
    
    async def get_multi_source_price(self, symbol: str) -> Dict[str, Any]:
        """Get price from multiple sources and aggregate"""
        symbol_lower = symbol.lower()
        
        # Run all sources in parallel
        tasks = [
            self.get_coingecko_price([symbol_lower]),
            self.get_binance_price(f"{symbol.upper()}USDT"),
        ]
        
        if CMC_KEY:
            tasks.append(self.get_coinmarketcap_quotes([symbol.upper()]))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        prices = []
        sources = []
        
        # Parse CoinGecko
        if results[0] and not isinstance(results[0], Exception):
            if symbol_lower in results[0]:
                cg_data = results[0][symbol_lower]
                if "usd" in cg_data:
                    prices.append(cg_data["usd"])
                    sources.append({
                        "name": "CoinGecko",
                        "price": cg_data["usd"],
                        "change_24h": cg_data.get("usd_24h_change")
                    })
        
        # Parse Binance
        if results[1] and not isinstance(results[1], Exception):
            if "lastPrice" in results[1]:
                price = float(results[1]["lastPrice"])
                prices.append(price)
                sources.append({
                    "name": "Binance",
                    "price": price,
                    "change_24h": float(results[1].get("priceChangePercent", 0))
                })
        
        # Parse CMC
        if len(results) > 2 and results[2] and not isinstance(results[2], Exception):
            if "data" in results[2] and symbol.upper() in results[2]["data"]:
                cmc_data = results[2]["data"][symbol.upper()]
                price = cmc_data.get("quote", {}).get("USD", {}).get("price")
                if price:
                    prices.append(price)
                    sources.append({
                        "name": "CoinMarketCap",
                        "price": price,
                        "change_24h": cmc_data.get("quote", {}).get("USD", {}).get("percent_change_24h")
                    })
        
        if not prices:
            return {"error": "No price data available from any source"}
        
        avg_price = sum(prices) / len(prices)
        
        return {
            "symbol": symbol,
            "sources": sources,
            "average_price": avg_price,
            "source_count": len(sources),
            "spread": max(prices) - min(prices) if len(prices) > 1 else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_aggregated_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get news from multiple sources"""
        tasks = [
            self.get_cryptopanic_news(limit),
            self.get_coindesk_rss(limit)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_news = []
        for result in results:
            if result and not isinstance(result, Exception):
                all_news.extend(result)
        
        # Sort by timestamp if available
        return all_news[:limit]


# Global client instance
_client = None

def get_api_client() -> RealAPIClient:
    """Get or create global API client"""
    global _client
    if _client is None:
        _client = RealAPIClient()
    return _client

async def close_api_client():
    """Close global API client"""
    global _client
    if _client:
        await _client.close()
        _client = None

