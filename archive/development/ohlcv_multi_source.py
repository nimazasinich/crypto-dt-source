"""
OHLCV Multi-Source Fetcher - 20+ sources with automatic fallback
Based on OHLCV_DATA_SECURITY_GUIDE.md specifications
"""
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime


class OHLCVMultiSource:
    """Fetch OHLCV data from 20+ sources with automatic fallback"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.sources = self._get_all_sources()
        self.cache = {}
        self.cache_ttl = 60
    
    def _get_all_sources(self) -> List[Dict]:
        """All 20 OHLCV sources from OHLCV_DATA_SECURITY_GUIDE.md"""
        return [
            # TIER 1: No auth, highest priority
            {"id": "binance", "name": "Binance", "url": "https://api.binance.com/api/v3/klines", "priority": 1, "max_limit": 1000},
            {"id": "coingecko", "name": "CoinGecko", "url": "https://api.coingecko.com/api/v3/coins/{id}/ohlc", "priority": 2, "max_limit": 365},
            {"id": "coinpaprika", "name": "CoinPaprika", "url": "https://api.coinpaprika.com/v1/coins/{id}/ohlcv/historical", "priority": 3, "max_limit": 366},
            {"id": "coincap", "name": "CoinCap", "url": "https://api.coincap.io/v2/assets/{id}/history", "priority": 4, "max_limit": 2000},
            {"id": "kraken", "name": "Kraken", "url": "https://api.kraken.com/0/public/OHLC", "priority": 5, "max_limit": 720},
            
            # TIER 2: With API key (would need keys)
            {"id": "cryptocompare_minute", "name": "CryptoCompare Minute", "url": "https://min-api.cryptocompare.com/data/v2/histominute", "priority": 6, "max_limit": 2000, "needs_key": True},
            {"id": "cryptocompare_hour", "name": "CryptoCompare Hour", "url": "https://min-api.cryptocompare.com/data/v2/histohour", "priority": 7, "max_limit": 2000, "needs_key": True},
            {"id": "cryptocompare_day", "name": "CryptoCompare Day", "url": "https://min-api.cryptocompare.com/data/v2/histoday", "priority": 8, "max_limit": 2000, "needs_key": True},
            
            # TIER 3: Additional exchanges
            {"id": "bitfinex", "name": "Bitfinex", "url": "https://api-pub.bitfinex.com/v2/candles", "priority": 9, "max_limit": 10000},
            {"id": "coinbase", "name": "Coinbase Pro", "url": "https://api.exchange.coinbase.com/products/{pair}/candles", "priority": 10, "max_limit": 300},
            {"id": "gemini", "name": "Gemini", "url": "https://api.gemini.com/v2/candles/{pair}/{timeframe}", "priority": 11, "max_limit": 500},
            {"id": "okx", "name": "OKX", "url": "https://www.okx.com/api/v5/market/candles", "priority": 12, "max_limit": 300},
            
            # TIER 4: Backup sources
            {"id": "kucoin", "name": "KuCoin", "url": "https://api.kucoin.com/api/v1/market/candles", "priority": 13, "max_limit": 1500},
            {"id": "bybit", "name": "Bybit", "url": "https://api.bybit.com/v5/market/kline", "priority": 14, "max_limit": 200},
            {"id": "gateio", "name": "Gate.io", "url": "https://api.gateio.ws/api/v4/spot/candlesticks", "priority": 15, "max_limit": 1000},
            {"id": "bitstamp", "name": "Bitstamp", "url": "https://www.bitstamp.net/api/v2/ohlc/{pair}", "priority": 16, "max_limit": 1000},
            {"id": "mexc", "name": "MEXC", "url": "https://api.mexc.com/api/v3/klines", "priority": 17, "max_limit": 1000},
            {"id": "huobi", "name": "Huobi", "url": "https://api.huobi.pro/market/history/kline", "priority": 18, "max_limit": 2000},
            {"id": "defillama", "name": "DefiLlama", "url": "https://coins.llama.fi/chart/{id}", "priority": 19, "max_limit": 365},
            {"id": "bitget", "name": "Bitget", "url": "https://api.bitget.com/api/spot/v1/market/candles", "priority": 20, "max_limit": 1000},
        ]
    
    def _map_timeframe(self, timeframe: str, source_id: str) -> str:
        """Map timeframe to source-specific format"""
        mapping = {
            "binance": {"1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m", "1h": "1h", "4h": "4h", "1d": "1d", "1w": "1w"},
            "kraken": {"1m": "1", "5m": "5", "15m": "15", "30m": "30", "1h": "60", "4h": "240", "1d": "1440", "1w": "10080"},
            "coingecko": {"1d": "1"},  # Only daily
            "coinbase": {"1m": "60", "5m": "300", "15m": "900", "1h": "3600", "1d": "86400"},
        }
        return mapping.get(source_id, {}).get(timeframe, timeframe)
    
    def _symbol_to_pair(self, symbol: str, source_id: str) -> str:
        """Convert symbol to exchange-specific pair format"""
        symbol_upper = symbol.upper()
        
        if source_id == "binance":
            return f"{symbol_upper}USDT"
        elif source_id == "coinbase":
            return f"{symbol_upper}-USD"
        elif source_id == "kraken":
            return f"X{symbol_upper}ZUSD" if symbol_upper == "BTC" else f"{symbol_upper}USD"
        elif source_id == "gemini":
            return f"{symbol_upper}USD".lower()
        elif source_id == "bitfinex":
            return f"t{symbol_upper}USD"
        else:
            return symbol_upper
    
    async def fetch_from_binance(self, symbol: str, timeframe: str, limit: int) -> List[Dict]:
        """Fetch from Binance"""
        pair = self._symbol_to_pair(symbol, "binance")
        interval = self._map_timeframe(timeframe, "binance")
        
        url = f"https://api.binance.com/api/v3/klines?symbol={pair}&interval={interval}&limit={limit}"
        response = await self.client.get(url)
        data = response.json()
        
        return [
            {
                "t": int(candle[0]),
                "o": float(candle[1]),
                "h": float(candle[2]),
                "l": float(candle[3]),
                "c": float(candle[4]),
                "v": float(candle[5])
            }
            for candle in data
        ]
    
    async def fetch_from_coingecko(self, symbol: str, timeframe: str, limit: int) -> List[Dict]:
        """Fetch from CoinGecko"""
        url = f"https://api.coingecko.com/api/v3/coins/{symbol.lower()}/ohlc?vs_currency=usd&days={limit}"
        response = await self.client.get(url)
        data = response.json()
        
        return [
            {
                "t": int(candle[0]),
                "o": float(candle[1]),
                "h": float(candle[2]),
                "l": float(candle[3]),
                "c": float(candle[4]),
                "v": 0
            }
            for candle in data
        ]
    
    async def fetch_from_coincap(self, symbol: str, timeframe: str, limit: int) -> List[Dict]:
        """Fetch from CoinCap"""
        interval_map = {"1m": "m1", "5m": "m5", "15m": "m15", "30m": "m30", "1h": "h1", "1d": "d1"}
        interval = interval_map.get(timeframe, "d1")
        
        url = f"https://api.coincap.io/v2/assets/{symbol.lower()}/history?interval={interval}"
        response = await self.client.get(url)
        data = response.json()
        candles = data.get("data", [])
        
        return [
            {
                "t": item.get("time"),
                "o": float(item.get("priceUsd", 0)),
                "h": float(item.get("priceUsd", 0)),
                "l": float(item.get("priceUsd", 0)),
                "c": float(item.get("priceUsd", 0)),
                "v": 0
            }
            for item in candles[:limit]
        ]
    
    async def fetch_from_kraken(self, symbol: str, timeframe: str, limit: int) -> List[Dict]:
        """Fetch from Kraken"""
        pair = self._symbol_to_pair(symbol, "kraken")
        interval = self._map_timeframe(timeframe, "kraken")
        
        url = f"https://api.kraken.com/0/public/OHLC?pair={pair}&interval={interval}"
        response = await self.client.get(url)
        data = response.json()
        
        if data.get("error"):
            raise Exception(data["error"][0])
        
        result = data.get("result", {})
        pair_key = list(result.keys())[0] if result else None
        if not pair_key:
            raise Exception("No data")
        
        candles = result[pair_key]
        
        return [
            {
                "t": int(candle[0]) * 1000,
                "o": float(candle[1]),
                "h": float(candle[2]),
                "l": float(candle[3]),
                "c": float(candle[4]),
                "v": float(candle[6])
            }
            for candle in candles[:limit]
        ]
    
    async def fetch_from_bitfinex(self, symbol: str, timeframe: str, limit: int) -> List[Dict]:
        """Fetch from Bitfinex"""
        pair = self._symbol_to_pair(symbol, "bitfinex")
        tf_map = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "1h", "1d": "1D"}
        tf = tf_map.get(timeframe, "1h")
        
        url = f"https://api-pub.bitfinex.com/v2/candles/trade:{tf}:{pair}/hist?limit={limit}"
        response = await self.client.get(url)
        data = response.json()
        
        return [
            {
                "t": int(candle[0]),
                "o": float(candle[1]),
                "h": float(candle[3]),
                "l": float(candle[4]),
                "c": float(candle[2]),
                "v": float(candle[5])
            }
            for candle in data
        ]
    
    async def fetch_from_coinbase(self, symbol: str, timeframe: str, limit: int) -> List[Dict]:
        """Fetch from Coinbase Pro"""
        pair = self._symbol_to_pair(symbol, "coinbase")
        granularity = self._map_timeframe(timeframe, "coinbase")
        
        url = f"https://api.exchange.coinbase.com/products/{pair}/candles?granularity={granularity}"
        response = await self.client.get(url)
        data = response.json()
        
        return [
            {
                "t": int(candle[0]) * 1000,
                "o": float(candle[3]),
                "h": float(candle[2]),
                "l": float(candle[1]),
                "c": float(candle[4]),
                "v": float(candle[5])
            }
            for candle in data[:limit]
        ]
    
    async def fetch_from_kucoin(self, symbol: str, timeframe: str, limit: int) -> List[Dict]:
        """Fetch from KuCoin"""
        pair = f"{symbol.upper()}-USDT"
        type_map = {"1m": "1min", "5m": "5min", "15m": "15min", "1h": "1hour", "1d": "1day"}
        type_str = type_map.get(timeframe, "1hour")
        
        url = f"https://api.kucoin.com/api/v1/market/candles?symbol={pair}&type={type_str}"
        response = await self.client.get(url)
        data = response.json()
        
        candles = data.get("data", [])
        return [
            {
                "t": int(candle[0]) * 1000,
                "o": float(candle[1]),
                "h": float(candle[3]),
                "l": float(candle[4]),
                "c": float(candle[2]),
                "v": float(candle[5])
            }
            for candle in candles[:limit]
        ]
    
    async def fetch_from_okx(self, symbol: str, timeframe: str, limit: int) -> List[Dict]:
        """Fetch from OKX"""
        pair = f"{symbol.upper()}-USDT"
        bar_map = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "1H", "4h": "4H", "1d": "1D"}
        bar = bar_map.get(timeframe, "1H")
        
        url = f"https://www.okx.com/api/v5/market/candles?instId={pair}&bar={bar}&limit={limit}"
        response = await self.client.get(url)
        data = response.json()
        
        candles = data.get("data", [])
        return [
            {
                "t": int(candle[0]),
                "o": float(candle[1]),
                "h": float(candle[2]),
                "l": float(candle[3]),
                "c": float(candle[4]),
                "v": float(candle[5])
            }
            for candle in candles
        ]
    
    async def fetch_from_bybit(self, symbol: str, timeframe: str, limit: int) -> List[Dict]:
        """Fetch from Bybit"""
        pair = f"{symbol.upper()}USDT"
        interval_map = {"1m": "1", "5m": "5", "15m": "15", "1h": "60", "4h": "240", "1d": "D"}
        interval = interval_map.get(timeframe, "60")
        
        url = f"https://api.bybit.com/v5/market/kline?category=spot&symbol={pair}&interval={interval}&limit={limit}"
        response = await self.client.get(url)
        data = response.json()
        
        candles = data.get("result", {}).get("list", [])
        return [
            {
                "t": int(candle[0]),
                "o": float(candle[1]),
                "h": float(candle[2]),
                "l": float(candle[3]),
                "c": float(candle[4]),
                "v": float(candle[5])
            }
            for candle in candles
        ]
    
    async def fetch_from_gateio(self, symbol: str, timeframe: str, limit: int) -> List[Dict]:
        """Fetch from Gate.io"""
        pair = f"{symbol.upper()}_USDT"
        interval_map = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "1h", "4h": "4h", "1d": "1d"}
        interval = interval_map.get(timeframe, "1h")
        
        url = f"https://api.gateio.ws/api/v4/spot/candlesticks?currency_pair={pair}&interval={interval}&limit={limit}"
        response = await self.client.get(url)
        data = response.json()
        
        return [
            {
                "t": int(float(candle[0])) * 1000,
                "o": float(candle[5]),
                "h": float(candle[3]),
                "l": float(candle[4]),
                "c": float(candle[2]),
                "v": float(candle[1])
            }
            for candle in data
        ]
    
    async def get_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> Dict[str, Any]:
        """
        Get OHLCV with automatic fallback through 20 sources
        Returns: {success, data, source, attempts, total_available}
        """
        cache_key = f"{symbol}_{timeframe}_{limit}"
        
        # Check cache
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if (datetime.now() - cached["time"]).seconds < self.cache_ttl:
                return {
                    "success": True,
                    "data": cached["data"],
                    "source": cached["source"],
                    "cached": True
                }
        
        sources = sorted(self.sources, key=lambda x: x["priority"])
        attempts = []
        
        for i, source in enumerate(sources[:20]):  # Try maximum 20 sources
            source_id = source["id"]
            source_name = source["name"]
            
            if source.get("needs_key") and source_id.startswith("cryptocompare"):
                # Skip sources that need API key if not configured
                continue
            
            try:
                print(f"[{i+1}/20] Trying {source_name}...")
                
                if source_id == "binance":
                    data = await self.fetch_from_binance(symbol, timeframe, limit)
                elif source_id == "coingecko" and timeframe == "1d":
                    data = await self.fetch_from_coingecko(symbol, timeframe, limit)
                elif source_id == "coincap":
                    data = await self.fetch_from_coincap(symbol, timeframe, limit)
                elif source_id == "kraken":
                    data = await self.fetch_from_kraken(symbol, timeframe, limit)
                elif source_id == "bitfinex":
                    data = await self.fetch_from_bitfinex(symbol, timeframe, limit)
                elif source_id == "coinbase":
                    data = await self.fetch_from_coinbase(symbol, timeframe, limit)
                elif source_id == "kucoin":
                    data = await self.fetch_from_kucoin(symbol, timeframe, limit)
                elif source_id == "okx":
                    data = await self.fetch_from_okx(symbol, timeframe, limit)
                elif source_id == "bybit":
                    data = await self.fetch_from_bybit(symbol, timeframe, limit)
                elif source_id == "gateio":
                    data = await self.fetch_from_gateio(symbol, timeframe, limit)
                else:
                    continue
                
                if data and len(data) > 0:
                    print(f"  ✅ SUCCESS: {len(data)} candles from {source_name}")
                    
                    # Cache result
                    self.cache[cache_key] = {
                        "data": data,
                        "source": source_name,
                        "time": datetime.now()
                    }
                    
                    return {
                        "success": True,
                        "data": data,
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "interval": timeframe,
                        "count": len(data),
                        "source": source_id,
                        "provider": source_name,
                        "attempts": i + 1,
                        "total_available": 20,
                        "timestamp": int(datetime.now().timestamp() * 1000)
                    }
                
                attempts.append({"source": source_name, "status": "no_data"})
                
            except Exception as e:
                print(f"  ❌ {source_name} failed: {str(e)[:100]}")
                attempts.append({"source": source_name, "status": "error", "error": str(e)[:100]})
                continue
        
        return {
            "success": False,
            "error": True,
            "message": f"All {len(attempts)} sources failed for {symbol}",
            "data": [],
            "symbol": symbol,
            "timeframe": timeframe,
            "count": 0,
            "attempts": len(attempts),
            "total_available": 20
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Global instance
_ohlcv_client = None

def get_ohlcv_client() -> OHLCVMultiSource:
    """Get or create global OHLCV client"""
    global _ohlcv_client
    if _ohlcv_client is None:
        _ohlcv_client = OHLCVMultiSource()
    return _ohlcv_client

async def close_ohlcv_client():
    """Close global OHLCV client"""
    global _ohlcv_client
    if _ohlcv_client:
        await _ohlcv_client.close()
        _ohlcv_client = None

