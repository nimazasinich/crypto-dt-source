#!/usr/bin/env python3
"""
OHLCV Data Verification Script
Tests multiple cryptocurrency APIs to verify accurate and complete OHLCV data.
"""

import requests
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import sys


class OHLCVVerifier:
    """Verifies OHLCV data from various cryptocurrency APIs"""
    
    def __init__(self):
        self.results = []
        self.test_time = datetime.now(timezone.utc).isoformat()
        
    def log_result(self, api_name: str, result: Dict[str, Any]):
        """Log test result"""
        result['api_name'] = api_name
        result['test_time'] = self.test_time
        self.results.append(result)
        
    def print_result(self, api_name: str, result: Dict[str, Any]):
        """Print formatted result"""
        print("\n" + "="*80)
        print(f"{api_name} API")
        print("="*80)
        print(f"Test Time: {result.get('test_time', 'N/A')}")
        print(f"Status: {result.get('status', 'UNKNOWN')}")
        print(f"URL: {result.get('url', 'N/A')}")
        
        if result.get('success'):
            print(f"\nValid Data Records: {result.get('valid_records', 0)}")
            print(f"Expected Records: {result.get('expected_records', 'N/A')}")
            print(f"Fields Verified: {', '.join(result.get('fields_verified', []))}")
            print(f"Missing Data: {result.get('missing_data', 'None')}")
            print(f"Issues: {result.get('issues', 'None')}")
            
            if result.get('sample_data'):
                print(f"\nSample Data (first record):")
                sample = result['sample_data']
                for key, value in sample.items():
                    print(f"  {key}: {value}")
        else:
            print(f"\nError: {result.get('error', 'Unknown error')}")
            if result.get('error_details'):
                print(f"Error Details: {result.get('error_details')}")
        
        print("="*80)
    
    def verify_coingecko(self) -> Dict[str, Any]:
        """Test CoinGecko API OHLCV endpoint"""
        api_name = "CoinGecko"
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/ohlc"
        params = {
            "vs_currency": "usd",
            "days": 30
        }
        
        result = {
            "success": False,
            "url": f"{url}?vs_currency=usd&days=30",
            "status": "FAILURE",
            "valid_records": 0,
            "expected_records": 30,
            "fields_verified": [],
            "missing_data": "Unknown",
            "issues": []
        }
        
        try:
            print(f"\nTesting {api_name} API...")
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # CoinGecko returns array of [timestamp, open, high, low, close]
                if isinstance(data, list) and len(data) > 0:
                    required_fields = ['timestamp', 'open', 'high', 'low', 'close']
                    valid_count = 0
                    missing_days = []
                    issues = []
                    
                    for idx, record in enumerate(data):
                        if len(record) >= 5:
                            timestamp, open_price, high, low, close = record[0], record[1], record[2], record[3], record[4]
                            
                            # Check for null or invalid values
                            if None in [timestamp, open_price, high, low, close]:
                                issues.append(f"Record {idx} has null values")
                            elif any(not isinstance(x, (int, float)) for x in [open_price, high, low, close]):
                                issues.append(f"Record {idx} has invalid data types")
                            elif high < low or high < open_price or high < close or low > open_price or low > close:
                                issues.append(f"Record {idx} has inconsistent OHLC values")
                            else:
                                valid_count += 1
                        else:
                            issues.append(f"Record {idx} has insufficient fields (expected 5, got {len(record)})")
                    
                    # Check for missing days (should have ~30 days)
                    if valid_count < 25:
                        missing_days.append(f"Expected ~30 days, got {valid_count} valid records")
                    
                    result.update({
                        "success": True,
                        "status": "SUCCESS" if valid_count >= 25 and len(issues) == 0 else "PARTIAL",
                        "valid_records": valid_count,
                        "fields_verified": required_fields,
                        "missing_data": f"{len(missing_days)} issues" if missing_days else "None",
                        "issues": issues if issues else "None",
                        "sample_data": {
                            "timestamp": data[0][0] if len(data) > 0 else None,
                            "open": data[0][1] if len(data) > 0 else None,
                            "high": data[0][2] if len(data) > 0 else None,
                            "low": data[0][3] if len(data) > 0 else None,
                            "close": data[0][4] if len(data) > 0 else None
                        } if len(data) > 0 else None,
                        "raw_response_preview": data[:3] if len(data) >= 3 else data
                    })
                else:
                    result.update({
                        "error": "Empty or invalid response format",
                        "error_details": f"Response type: {type(data)}, Length: {len(data) if isinstance(data, list) else 'N/A'}"
                    })
            else:
                result.update({
                    "error": f"HTTP {response.status_code}",
                    "error_details": response.text[:500]
                })
                
        except requests.exceptions.Timeout:
            result.update({
                "error": "Request timeout",
                "error_details": "Request exceeded 30 second timeout"
            })
        except requests.exceptions.RequestException as e:
            result.update({
                "error": "Request failed",
                "error_details": str(e)
            })
        except Exception as e:
            result.update({
                "error": "Unexpected error",
                "error_details": str(e)
            })
        
        self.log_result(api_name, result)
        self.print_result(api_name, result)
        return result
    
    def verify_binance(self) -> Dict[str, Any]:
        """Test Binance API klines endpoint"""
        api_name = "Binance"
        url = "https://api.binance.com/api/v3/klines"
        params = {
            "symbol": "BTCUSDT",
            "interval": "1d",
            "limit": 365
        }
        
        result = {
            "success": False,
            "url": f"{url}?symbol=BTCUSDT&interval=1d&limit=365",
            "status": "FAILURE",
            "valid_records": 0,
            "expected_records": 365,
            "fields_verified": [],
            "missing_data": "Unknown",
            "issues": []
        }
        
        try:
            print(f"\nTesting {api_name} API...")
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Binance returns array of arrays: [openTime, open, high, low, close, volume, closeTime, ...]
                if isinstance(data, list) and len(data) > 0:
                    required_fields = ['openTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime']
                    valid_count = 0
                    issues = []
                    
                    for idx, record in enumerate(data):
                        if len(record) >= 7:
                            open_time = record[0]
                            open_price = float(record[1])
                            high = float(record[2])
                            low = float(record[3])
                            close = float(record[4])
                            volume = float(record[5])
                            close_time = record[6]
                            
                            # Check for null or invalid values
                            if None in [open_time, open_price, high, low, close, volume, close_time]:
                                issues.append(f"Record {idx} has null values")
                            elif high < low or high < open_price or high < close or low > open_price or low > close:
                                issues.append(f"Record {idx} has inconsistent OHLC values")
                            elif volume < 0:
                                issues.append(f"Record {idx} has negative volume")
                            else:
                                valid_count += 1
                        else:
                            issues.append(f"Record {idx} has insufficient fields (expected at least 7, got {len(record)})")
                    
                    result.update({
                        "success": True,
                        "status": "SUCCESS" if valid_count >= 360 and len(issues) == 0 else "PARTIAL",
                        "valid_records": valid_count,
                        "fields_verified": required_fields,
                        "missing_data": "None" if valid_count >= 360 else f"Missing {365 - valid_count} records",
                        "issues": issues[:10] if issues else "None",  # Limit issues to first 10
                        "sample_data": {
                            "openTime": data[0][0] if len(data) > 0 else None,
                            "open": data[0][1] if len(data) > 0 else None,
                            "high": data[0][2] if len(data) > 0 else None,
                            "low": data[0][3] if len(data) > 0 else None,
                            "close": data[0][4] if len(data) > 0 else None,
                            "volume": data[0][5] if len(data) > 0 else None,
                            "closeTime": data[0][6] if len(data) > 0 else None
                        } if len(data) > 0 else None,
                        "raw_response_preview": data[:2] if len(data) >= 2 else data
                    })
                else:
                    result.update({
                        "error": "Empty or invalid response format",
                        "error_details": f"Response type: {type(data)}, Length: {len(data) if isinstance(data, list) else 'N/A'}"
                    })
            else:
                result.update({
                    "error": f"HTTP {response.status_code}",
                    "error_details": response.text[:500]
                })
                
        except requests.exceptions.Timeout:
            result.update({
                "error": "Request timeout",
                "error_details": "Request exceeded 30 second timeout"
            })
        except requests.exceptions.RequestException as e:
            result.update({
                "error": "Request failed",
                "error_details": str(e)
            })
        except Exception as e:
            result.update({
                "error": "Unexpected error",
                "error_details": str(e)
            })
        
        self.log_result(api_name, result)
        self.print_result(api_name, result)
        return result
    
    def verify_alphavantage(self) -> Dict[str, Any]:
        """Test Alpha Vantage API DIGITAL_CURRENCY_DAILY endpoint"""
        api_name = "Alpha Vantage"
        url = "https://www.alphavantage.co/query"
        
        # Check for API key in environment
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
        
        params = {
            "function": "DIGITAL_CURRENCY_DAILY",
            "symbol": "BTC",
            "market": "USD",
            "apikey": api_key
        }
        
        result = {
            "success": False,
            "url": f"{url}?function=DIGITAL_CURRENCY_DAILY&symbol=BTC&market=USD&apikey={'***' if api_key != 'demo' else 'demo'}",
            "status": "FAILURE",
            "valid_records": 0,
            "expected_records": "~100 days",
            "fields_verified": [],
            "missing_data": "Unknown",
            "issues": []
        }
        
        try:
            print(f"\nTesting {api_name} API...")
            if api_key == "demo":
                print("  Note: Using demo API key. Results may be limited.")
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for API limit error
                if "Note" in data or "Thank you for using Alpha Vantage" in str(data):
                    result.update({
                        "error": "API rate limit or demo key limitation",
                        "error_details": data.get("Note", "API call frequency limit reached")
                    })
                elif "Error Message" in data:
                    result.update({
                        "error": "API error",
                        "error_details": data.get("Error Message", "Unknown error")
                    })
                elif "Time Series (Digital Currency Daily)" in data:
                    time_series = data["Time Series (Digital Currency Daily)"]
                    
                    if isinstance(time_series, dict) and len(time_series) > 0:
                        required_fields = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                        valid_count = 0
                        issues = []
                        
                        for timestamp, values in time_series.items():
                            if isinstance(values, dict):
                                open_price = values.get("1a. open (USD)", values.get("1. open (USD)"))
                                high = values.get("2a. high (USD)", values.get("2. high (USD)"))
                                low = values.get("3a. low (USD)", values.get("3. low (USD)"))
                                close = values.get("4a. close (USD)", values.get("4. close (USD)"))
                                volume = values.get("5. volume", values.get("5a. volume"))
                                
                                try:
                                    open_price = float(open_price) if open_price else None
                                    high = float(high) if high else None
                                    low = float(low) if low else None
                                    close = float(close) if close else None
                                    volume = float(volume) if volume else None
                                    
                                    if None in [open_price, high, low, close, volume]:
                                        issues.append(f"Record {timestamp} has null values")
                                    elif high < low or high < open_price or high < close or low > open_price or low > close:
                                        issues.append(f"Record {timestamp} has inconsistent OHLC values")
                                    elif volume < 0:
                                        issues.append(f"Record {timestamp} has negative volume")
                                    else:
                                        valid_count += 1
                                except (ValueError, TypeError):
                                    issues.append(f"Record {timestamp} has invalid data types")
                            else:
                                issues.append(f"Record {timestamp} has invalid format")
                        
                        # Get sample data
                        sample_timestamp = list(time_series.keys())[0]
                        sample_values = time_series[sample_timestamp]
                        
                        result.update({
                            "success": True,
                            "status": "SUCCESS" if valid_count >= 50 and len(issues) == 0 else "PARTIAL",
                            "valid_records": valid_count,
                            "fields_verified": required_fields,
                            "missing_data": "None" if valid_count >= 50 else f"Only {valid_count} valid records",
                            "issues": issues[:10] if issues else "None",
                            "sample_data": {
                                "timestamp": sample_timestamp,
                                "open": sample_values.get("1a. open (USD)", sample_values.get("1. open (USD)")),
                                "high": sample_values.get("2a. high (USD)", sample_values.get("2. high (USD)")),
                                "low": sample_values.get("3a. low (USD)", sample_values.get("3. low (USD)")),
                                "close": sample_values.get("4a. close (USD)", sample_values.get("4. close (USD)")),
                                "volume": sample_values.get("5. volume", sample_values.get("5a. volume"))
                            },
                            "raw_response_preview": {k: v for k, v in list(time_series.items())[:2]}
                        })
                    else:
                        result.update({
                            "error": "Empty time series data",
                            "error_details": "Time series dictionary is empty or invalid"
                        })
                else:
                    result.update({
                        "error": "Unexpected response format",
                        "error_details": f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}"
                    })
            else:
                result.update({
                    "error": f"HTTP {response.status_code}",
                    "error_details": response.text[:500]
                })
                
        except requests.exceptions.Timeout:
            result.update({
                "error": "Request timeout",
                "error_details": "Request exceeded 30 second timeout"
            })
        except requests.exceptions.RequestException as e:
            result.update({
                "error": "Request failed",
                "error_details": str(e)
            })
        except Exception as e:
            result.update({
                "error": "Unexpected error",
                "error_details": str(e)
            })
        
        self.log_result(api_name, result)
        self.print_result(api_name, result)
        return result
    
    def verify_twelvedata(self) -> Dict[str, Any]:
        """Test Twelve Data API time_series endpoint"""
        api_name = "Twelve Data"
        url = "https://api.twelvedata.com/time_series"
        
        # Check for API key in environment
        api_key = os.getenv("TWELVE_DATA_API_KEY", "")
        
        params = {
            "symbol": "BTC/USD",
            "interval": "1min",
            "apikey": api_key,
            "outputsize": 1440
        }
        
        result = {
            "success": False,
            "url": f"{url}?symbol=BTC/USD&interval=1min&outputsize=1440&apikey={'***' if api_key else 'MISSING'}",
            "status": "FAILURE",
            "valid_records": 0,
            "expected_records": 1440,
            "fields_verified": [],
            "missing_data": "Unknown",
            "issues": []
        }
        
        try:
            print(f"\nTesting {api_name} API...")
            if not api_key:
                result.update({
                    "error": "API key required",
                    "error_details": "Set TWELVE_DATA_API_KEY environment variable to test this API"
                })
                self.log_result(api_name, result)
                self.print_result(api_name, result)
                return result
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for API errors
                if "status" in data and data["status"] == "error":
                    result.update({
                        "error": "API error",
                        "error_details": data.get("message", "Unknown API error")
                    })
                elif "values" in data:
                    values = data["values"]
                    
                    if isinstance(values, list) and len(values) > 0:
                        required_fields = ['datetime', 'open', 'high', 'low', 'close', 'volume']
                        valid_count = 0
                        issues = []
                        
                        for idx, record in enumerate(values):
                            if isinstance(record, dict):
                                datetime_val = record.get("datetime")
                                open_price = record.get("open")
                                high = record.get("high")
                                low = record.get("low")
                                close = record.get("close")
                                volume = record.get("volume")
                                
                                try:
                                    open_price = float(open_price) if open_price else None
                                    high = float(high) if high else None
                                    low = float(low) if low else None
                                    close = float(close) if close else None
                                    volume = float(volume) if volume else None
                                    
                                    if None in [datetime_val, open_price, high, low, close, volume]:
                                        issues.append(f"Record {idx} has null values")
                                    elif high < low or high < open_price or high < close or low > open_price or low > close:
                                        issues.append(f"Record {idx} has inconsistent OHLC values")
                                    elif volume < 0:
                                        issues.append(f"Record {idx} has negative volume")
                                    else:
                                        valid_count += 1
                                except (ValueError, TypeError):
                                    issues.append(f"Record {idx} has invalid data types")
                            else:
                                issues.append(f"Record {idx} has invalid format")
                        
                        result.update({
                            "success": True,
                            "status": "SUCCESS" if valid_count >= 1400 and len(issues) == 0 else "PARTIAL",
                            "valid_records": valid_count,
                            "fields_verified": required_fields,
                            "missing_data": "None" if valid_count >= 1400 else f"Missing {1440 - valid_count} records",
                            "issues": issues[:10] if issues else "None",
                            "sample_data": values[0] if len(values) > 0 else None,
                            "raw_response_preview": values[:2] if len(values) >= 2 else values
                        })
                    else:
                        result.update({
                            "error": "Empty values array",
                            "error_details": "Values array is empty or invalid"
                        })
                else:
                    result.update({
                        "error": "Unexpected response format",
                        "error_details": f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}"
                    })
            else:
                result.update({
                    "error": f"HTTP {response.status_code}",
                    "error_details": response.text[:500]
                })
                
        except requests.exceptions.Timeout:
            result.update({
                "error": "Request timeout",
                "error_details": "Request exceeded 30 second timeout"
            })
        except requests.exceptions.RequestException as e:
            result.update({
                "error": "Request failed",
                "error_details": str(e)
            })
        except Exception as e:
            result.update({
                "error": "Unexpected error",
                "error_details": str(e)
            })
        
        self.log_result(api_name, result)
        self.print_result(api_name, result)
        return result
    
    def verify_cryptocompare(self) -> Dict[str, Any]:
        """Test CryptoCompare API histoday endpoint"""
        api_name = "CryptoCompare"
        url = "https://min-api.cryptocompare.com/data/v2/histoday"
        params = {
            "fsym": "BTC",
            "tsym": "USD",
            "limit": 200
        }
        
        result = {
            "success": False,
            "url": f"{url}?fsym=BTC&tsym=USD&limit=200",
            "status": "FAILURE",
            "valid_records": 0,
            "expected_records": 200,
            "fields_verified": [],
            "missing_data": "Unknown",
            "issues": []
        }
        
        try:
            print(f"\nTesting {api_name} API...")
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for API errors
                if data.get("Response") == "Error":
                    result.update({
                        "error": "API error",
                        "error_details": data.get("Message", "Unknown API error")
                    })
                elif "Data" in data and "Data" in data["Data"]:
                    records = data["Data"]["Data"]
                    
                    if isinstance(records, list) and len(records) > 0:
                        required_fields = ['time', 'open', 'high', 'low', 'close', 'volumefrom']
                        valid_count = 0
                        issues = []
                        
                        for idx, record in enumerate(records):
                            if isinstance(record, dict):
                                time_val = record.get("time")
                                open_price = record.get("open")
                                high = record.get("high")
                                low = record.get("low")
                                close = record.get("close")
                                volumefrom = record.get("volumefrom")
                                
                                try:
                                    open_price = float(open_price) if open_price else None
                                    high = float(high) if high else None
                                    low = float(low) if low else None
                                    close = float(close) if close else None
                                    volumefrom = float(volumefrom) if volumefrom else None
                                    
                                    if None in [time_val, open_price, high, low, close, volumefrom]:
                                        issues.append(f"Record {idx} has null values")
                                    elif high < low or high < open_price or high < close or low > open_price or low > close:
                                        issues.append(f"Record {idx} has inconsistent OHLC values")
                                    elif volumefrom < 0:
                                        issues.append(f"Record {idx} has negative volume")
                                    else:
                                        valid_count += 1
                                except (ValueError, TypeError):
                                    issues.append(f"Record {idx} has invalid data types")
                            else:
                                issues.append(f"Record {idx} has invalid format")
                        
                        result.update({
                            "success": True,
                            "status": "SUCCESS" if valid_count >= 190 and len(issues) == 0 else "PARTIAL",
                            "valid_records": valid_count,
                            "fields_verified": required_fields,
                            "missing_data": "None" if valid_count >= 190 else f"Missing {200 - valid_count} records",
                            "issues": issues[:10] if issues else "None",
                            "sample_data": records[0] if len(records) > 0 else None,
                            "raw_response_preview": records[:2] if len(records) >= 2 else records
                        })
                    else:
                        result.update({
                            "error": "Empty data array",
                            "error_details": "Data array is empty or invalid"
                        })
                else:
                    result.update({
                        "error": "Unexpected response format",
                        "error_details": f"Response structure: {list(data.keys()) if isinstance(data, dict) else 'N/A'}"
                    })
            else:
                result.update({
                    "error": f"HTTP {response.status_code}",
                    "error_details": response.text[:500]
                })
                
        except requests.exceptions.Timeout:
            result.update({
                "error": "Request timeout",
                "error_details": "Request exceeded 30 second timeout"
            })
        except requests.exceptions.RequestException as e:
            result.update({
                "error": "Request failed",
                "error_details": str(e)
            })
        except Exception as e:
            result.update({
                "error": "Unexpected error",
                "error_details": str(e)
            })
        
        self.log_result(api_name, result)
        self.print_result(api_name, result)
        return result
    
    def generate_summary_report(self):
        """Generate summary report of all tests"""
        print("\n\n" + "="*80)
        print("SUMMARY REPORT")
        print("="*80)
        print(f"Test Execution Time: {self.test_time}")
        print(f"Total APIs Tested: {len(self.results)}")
        
        successful = sum(1 for r in self.results if r.get('success') and r.get('status') == 'SUCCESS')
        partial = sum(1 for r in self.results if r.get('success') and r.get('status') == 'PARTIAL')
        failed = sum(1 for r in self.results if not r.get('success'))
        
        print(f"\nResults:")
        print(f"  ✓ Successful: {successful}")
        print(f"  ⚠ Partial: {partial}")
        print(f"  ✗ Failed: {failed}")
        
        print("\nDetailed Results:")
        for result in self.results:
            status_icon = "✓" if result.get('status') == 'SUCCESS' else "⚠" if result.get('success') else "✗"
            print(f"\n{status_icon} {result.get('api_name')}:")
            print(f"   Status: {result.get('status')}")
            if result.get('success'):
                print(f"   Valid Records: {result.get('valid_records')}/{result.get('expected_records')}")
                print(f"   Issues: {result.get('issues', 'None')}")
            else:
                print(f"   Error: {result.get('error', 'Unknown')}")
        
        print("\n" + "="*80)
        
        # Save results to JSON file
        output_file = f"ohlcv_verification_results_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump({
                "test_time": self.test_time,
                "summary": {
                    "total_apis": len(self.results),
                    "successful": successful,
                    "partial": partial,
                    "failed": failed
                },
                "results": self.results
            }, f, indent=2)
        
        print(f"\nDetailed results saved to: {output_file}")
        print("="*80 + "\n")


def main():
    """Main execution function"""
    print("="*80)
    print("OHLCV Data Verification Test Suite")
    print("="*80)
    print("Testing multiple cryptocurrency APIs for accurate and complete OHLCV data...")
    
    verifier = OHLCVVerifier()
    
    # Run all tests
    verifier.verify_coingecko()
    verifier.verify_binance()
    verifier.verify_alphavantage()
    verifier.verify_twelvedata()
    verifier.verify_cryptocompare()
    
    # Generate summary report
    verifier.generate_summary_report()


if __name__ == "__main__":
    main()
