#!/usr/bin/env python3
"""
Restricted APIs Configuration
تنظیمات APIهایی که نیاز به Proxy/DNS دارن

فقط APIهایی که واقعاً فیلتر شدن یا محدودیت دارن
"""

from typing import Dict, List
from enum import Enum


class AccessLevel(Enum):
    """سطح دسترسی"""
    DIRECT = "direct"  # مستقیم (بدون proxy/DNS)
    SMART = "smart"    # هوشمند (با fallback)
    FORCE_PROXY = "force_proxy"  # حتماً با proxy
    FORCE_DNS = "force_dns"  # حتماً با DNS


# ✅ APIهایی که به Proxy/DNS نیاز دارن
RESTRICTED_APIS = {
    # ─────────────────────────────────────────────────────────
    # 🔴 CRITICAL: حتماً نیاز به Proxy/DNS دارن
    # ─────────────────────────────────────────────────────────
    "kucoin": {
        "domains": [
            "api.kucoin.com",
            "api-futures.kucoin.com",
            "openapi-v2.kucoin.com"
        ],
        "access_level": AccessLevel.SMART,
        "priority": 1,
        "reason": "Critical exchange - always use smart access with rotating DNS/Proxy",
        "fallback_order": ["direct", "dns_cloudflare", "dns_google", "proxy", "dns_proxy"],
        "rotate_dns": True,  # چرخش DNS برای امنیت بیشتر
        "rotate_proxy": True,  # چرخش Proxy
        "always_secure": True  # همیشه امن
    },
    
    "binance": {
        "domains": [
            "api.binance.com",
            "api1.binance.com",
            "api2.binance.com",
            "api3.binance.com",
            "fapi.binance.com"
        ],
        "access_level": AccessLevel.SMART,  # همیشه Smart Access
        "priority": 1,
        "reason": "Critical exchange - always use smart access with rotating DNS/Proxy",
        "fallback_order": ["direct", "dns_cloudflare", "dns_google", "proxy", "dns_proxy"],
        "rotate_dns": True,  # چرخش DNS برای امنیت بیشتر
        "rotate_proxy": True,  # چرخش Proxy
        "always_secure": True  # همیشه امن
    },
    
    "bybit": {
        "domains": [
            "api.bybit.com",
            "api-testnet.bybit.com"
        ],
        "access_level": AccessLevel.SMART,
        "priority": 2,
        "reason": "May have regional restrictions",
        "fallback_order": ["direct", "dns_cloudflare", "proxy"]
    },
    
    "okx": {
        "domains": [
            "www.okx.com",
            "aws.okx.com"
        ],
        "access_level": AccessLevel.SMART,
        "priority": 2,
        "reason": "Geo-restrictions in some regions",
        "fallback_order": ["direct", "dns_google", "proxy"]
    },
    
    # ─────────────────────────────────────────────────────────
    # 🟡 MEDIUM: ممکنه نیاز داشته باشن
    # ─────────────────────────────────────────────────────────
    "coinmarketcap_pro": {
        "domains": [
            "pro-api.coinmarketcap.com"
        ],
        "access_level": AccessLevel.DIRECT,  # فعلاً مستقیم کافیه
        "priority": 3,
        "reason": "Usually works directly with API key",
        "fallback_order": ["direct", "dns_cloudflare"]
    },
}


# ✅ APIهایی که مستقیم کار می‌کنن (نیازی به Proxy/DNS ندارن)
UNRESTRICTED_APIS = {
    "coingecko": {
        "domains": [
            "api.coingecko.com",
            "pro-api.coingecko.com"
        ],
        "access_level": AccessLevel.DIRECT,
        "reason": "Works globally without restrictions"
    },
    
    "coinpaprika": {
        "domains": [
            "api.coinpaprika.com"
        ],
        "access_level": AccessLevel.DIRECT,
        "reason": "Free API, no restrictions"
    },
    
    "coincap": {
        "domains": [
            "api.coincap.io"
        ],
        "access_level": AccessLevel.DIRECT,
        "reason": "Free API, globally accessible"
    },
    
    "coinlore": {
        "domains": [
            "api.coinlore.net"
        ],
        "access_level": AccessLevel.DIRECT,
        "reason": "Free API, no geo-restrictions"
    },
    
    "cryptopanic": {
        "domains": [
            "cryptopanic.com"
        ],
        "access_level": AccessLevel.DIRECT,
        "reason": "News API, works globally"
    },
    
    "alternative_me": {
        "domains": [
            "api.alternative.me"
        ],
        "access_level": AccessLevel.DIRECT,
        "reason": "Fear & Greed index, no restrictions"
    },
    
    "blockchain_info": {
        "domains": [
            "blockchain.info"
        ],
        "access_level": AccessLevel.DIRECT,
        "reason": "Public blockchain explorer"
    },
    
    "etherscan": {
        "domains": [
            "api.etherscan.io"
        ],
        "access_level": AccessLevel.DIRECT,
        "reason": "Public API with key"
    },
    
    "bscscan": {
        "domains": [
            "api.bscscan.com"
        ],
        "access_level": AccessLevel.DIRECT,
        "reason": "Public API with key"
    },
}


def get_access_config(domain: str) -> Dict:
    """
    دریافت تنظیمات دسترسی برای یک domain
    
    Returns:
        {
            "access_level": AccessLevel,
            "use_smart_access": bool,
            "fallback_order": List[str]
        }
    """
    # جستجو در Restricted APIs
    for api_name, config in RESTRICTED_APIS.items():
        if domain in config["domains"]:
            return {
                "api_name": api_name,
                "access_level": config["access_level"],
                "use_smart_access": config["access_level"] != AccessLevel.DIRECT,
                "fallback_order": config.get("fallback_order", ["direct"]),
                "priority": config.get("priority", 99),
                "reason": config.get("reason", "")
            }
    
    # جستجو در Unrestricted APIs
    for api_name, config in UNRESTRICTED_APIS.items():
        if domain in config["domains"]:
            return {
                "api_name": api_name,
                "access_level": config["access_level"],
                "use_smart_access": False,
                "fallback_order": ["direct"],
                "priority": 99,
                "reason": config.get("reason", "")
            }
    
    # Default: استفاده از Smart Access
    return {
        "api_name": "unknown",
        "access_level": AccessLevel.SMART,
        "use_smart_access": True,
        "fallback_order": ["direct", "dns_cloudflare", "proxy"],
        "priority": 50,
        "reason": "Unknown API, using smart access"
    }


def should_use_smart_access(url: str) -> bool:
    """
    آیا این URL نیاز به Smart Access داره؟
    """
    # استخراج domain از URL
    if "://" in url:
        domain = url.split("://")[1].split("/")[0]
    else:
        domain = url.split("/")[0]
    
    config = get_access_config(domain)
    return config["use_smart_access"]


def get_restricted_apis_list() -> List[str]:
    """لیست APIهایی که نیاز به Proxy/DNS دارن"""
    return list(RESTRICTED_APIS.keys())


def get_unrestricted_apis_list() -> List[str]:
    """لیست APIهایی که مستقیم کار می‌کنن"""
    return list(UNRESTRICTED_APIS.keys())


def get_all_monitored_domains() -> List[str]:
    """همه domainهایی که تحت نظارت هستن"""
    domains = []
    
    for config in RESTRICTED_APIS.values():
        domains.extend(config["domains"])
    
    for config in UNRESTRICTED_APIS.values():
        domains.extend(config["domains"])
    
    return domains


def print_config_summary():
    """چاپ خلاصه تنظیمات"""
    print("=" * 60)
    print("📋 RESTRICTED APIS CONFIGURATION")
    print("=" * 60)
    
    print("\n🔴 APIs that need Proxy/DNS:")
    for api_name, config in RESTRICTED_APIS.items():
        print(f"\n  {api_name.upper()}:")
        print(f"    Domains: {', '.join(config['domains'])}")
        print(f"    Access: {config['access_level'].value}")
        print(f"    Priority: {config['priority']}")
        print(f"    Reason: {config['reason']}")
    
    print("\n\n✅ APIs that work DIRECT:")
    for api_name, config in UNRESTRICTED_APIS.items():
        print(f"  • {api_name}: {config['domains'][0]}")
    
    print("\n" + "=" * 60)
    print(f"Total Restricted: {len(RESTRICTED_APIS)}")
    print(f"Total Unrestricted: {len(UNRESTRICTED_APIS)}")
    print("=" * 60)


if __name__ == "__main__":
    print_config_summary()

