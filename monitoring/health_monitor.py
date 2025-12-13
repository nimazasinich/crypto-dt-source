#!/usr/bin/env python3
"""
Health Monitoring System
Continuous health monitoring for all API endpoints
"""

import schedule
import time
import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthMonitor:
    """Continuous health monitoring for all endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:7860"):
        self.base_url = base_url
        self.endpoints = self.load_endpoints()
        self.health_history = []
        self.alert_threshold = 3  # Number of consecutive failures before alert
        self.failure_counts = {}  # Track consecutive failures per endpoint
    
    def load_endpoints(self) -> List[Dict]:
        """Load endpoints from service registry"""
        registry_file = Path("config/service_registry.json")
        
        if not registry_file.exists():
            logger.warning("⚠ Service registry not found, using default endpoints")
            return self._get_default_endpoints()
        
        try:
            with open(registry_file, 'r') as f:
                registry = json.load(f)
            
            endpoints = []
            for service in registry.get("services", []):
                for endpoint in service.get("endpoints", []):
                    endpoints.append({
                        "path": endpoint.get("path", ""),
                        "method": endpoint.get("method", "GET"),
                        "category": service.get("category", "unknown"),
                        "service_id": service.get("id", "unknown"),
                        "base_url": self.base_url
                    })
            
            return endpoints
        
        except Exception as e:
            logger.error(f"❌ Failed to load endpoints: {e}")
            return self._get_default_endpoints()
    
    def _get_default_endpoints(self) -> List[Dict]:
        """Get default endpoints for monitoring"""
        return [
            {"path": "/api/health", "method": "GET", "category": "system", "base_url": self.base_url},
            {"path": "/api/ohlcv/BTC", "method": "GET", "category": "market_data", "base_url": self.base_url},
            {"path": "/api/v1/ohlcv/BTC", "method": "GET", "category": "market_data", "base_url": self.base_url},
            {"path": "/api/market/ohlcv", "method": "GET", "category": "market_data", "base_url": self.base_url, "params": {"symbol": "BTC", "interval": "1d", "limit": 30}},
        ]
    
    def check_endpoint_health(self, endpoint: Dict) -> Dict:
        """Check health of single endpoint"""
        path = endpoint["path"]
        method = endpoint.get("method", "GET").upper()
        params = endpoint.get("params", {})
        
        try:
            start_time = time.time()
            url = f"{endpoint['base_url']}{path}"
            
            if method == "GET":
                response = requests.get(url, params=params, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=params, timeout=10)
            else:
                response = requests.request(method, url, json=params, timeout=10)
            
            response_time = (time.time() - start_time) * 1000
            
            is_healthy = response.status_code in [200, 201]
            
            result = {
                "endpoint": path,
                "status": "healthy" if is_healthy else "degraded",
                "status_code": response.status_code,
                "response_time_ms": round(response_time, 2),
                "timestamp": datetime.now().isoformat(),
                "method": method
            }
            
            # Update failure count
            if is_healthy:
                self.failure_counts[path] = 0
            else:
                self.failure_counts[path] = self.failure_counts.get(path, 0) + 1
                result["consecutive_failures"] = self.failure_counts[path]
            
            return result
        
        except requests.exceptions.Timeout:
            self.failure_counts[path] = self.failure_counts.get(path, 0) + 1
            return {
                "endpoint": path,
                "status": "down",
                "error": "timeout",
                "timestamp": datetime.now().isoformat(),
                "method": method,
                "consecutive_failures": self.failure_counts[path]
            }
        
        except Exception as e:
            self.failure_counts[path] = self.failure_counts.get(path, 0) + 1
            return {
                "endpoint": path,
                "status": "down",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "method": method,
                "consecutive_failures": self.failure_counts[path]
            }
    
    def check_all_endpoints(self):
        """Check health of all registered endpoints"""
        results = []
        
        logger.info(f"🔍 Checking {len(self.endpoints)} endpoints...")
        
        for endpoint in self.endpoints:
            health = self.check_endpoint_health(endpoint)
            results.append(health)
            
            # Check if alert needed
            if health['status'] != "healthy":
                self.handle_unhealthy_endpoint(health)
        
        # Store in history
        self.health_history.append({
            "check_time": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "total": len(results),
                "healthy": sum(1 for r in results if r['status'] == "healthy"),
                "degraded": sum(1 for r in results if r['status'] == "degraded"),
                "down": sum(1 for r in results if r['status'] == "down")
            }
        })
        
        # Keep only last 100 checks
        if len(self.health_history) > 100:
            self.health_history = self.health_history[-100:]
        
        # Save to file
        self.save_health_report(results)
        
        return results
    
    def handle_unhealthy_endpoint(self, health: Dict):
        """Handle unhealthy endpoint detection"""
        path = health["endpoint"]
        consecutive_failures = health.get("consecutive_failures", 0)
        
        if consecutive_failures >= self.alert_threshold:
            self.send_alert(health)
    
    def send_alert(self, health: Dict):
        """Send alert about failing endpoint"""
        alert_message = f"""
⚠️ ALERT: Endpoint Health Issue

Endpoint: {health['endpoint']}
Status: {health['status']}
Error: {health.get('error', 'N/A')}
Time: {health['timestamp']}
Consecutive Failures: {health.get('consecutive_failures', 0)}
"""
        
        logger.error(alert_message)
        
        # Save alert to file
        alerts_file = Path("monitoring/alerts.json")
        alerts_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if alerts_file.exists():
                with open(alerts_file, 'r') as f:
                    alerts = json.load(f)
            else:
                alerts = []
            
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "endpoint": health["endpoint"],
                "status": health["status"],
                "error": health.get("error"),
                "consecutive_failures": health.get("consecutive_failures", 0)
            })
            
            # Keep only last 50 alerts
            alerts = alerts[-50:]
            
            with open(alerts_file, 'w') as f:
                json.dump(alerts, f, indent=2)
        
        except Exception as e:
            logger.error(f"Failed to save alert: {e}")
    
    def save_health_report(self, results: List[Dict]):
        """Save health check results to file"""
        reports_dir = Path("monitoring/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = reports_dir / f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_endpoints": len(results),
            "healthy": sum(1 for r in results if r['status'] == "healthy"),
            "degraded": sum(1 for r in results if r['status'] == "degraded"),
            "down": sum(1 for r in results if r['status'] == "down"),
            "results": results
        }
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Also update latest report
            latest_file = reports_dir / "health_report_latest.json"
            with open(latest_file, 'w') as f:
                json.dump(report, f, indent=2)
        
        except Exception as e:
            logger.error(f"Failed to save health report: {e}")
    
    def get_health_summary(self) -> Dict:
        """Get summary of health status"""
        if not self.health_history:
            return {
                "status": "unknown",
                "message": "No health checks performed yet"
            }
        
        latest = self.health_history[-1]
        summary = latest["summary"]
        
        total = summary["total"]
        healthy = summary["healthy"]
        health_percentage = (healthy / total * 100) if total > 0 else 0
        
        return {
            "status": "healthy" if health_percentage >= 95 else "degraded" if health_percentage >= 80 else "unhealthy",
            "health_percentage": round(health_percentage, 2),
            "total_endpoints": total,
            "healthy": healthy,
            "degraded": summary["degraded"],
            "down": summary["down"],
            "last_check": latest["check_time"]
        }
    
    def start_monitoring(self, interval_minutes: int = 5):
        """Start continuous monitoring"""
        logger.info(f"🔍 Health monitoring started (checking every {interval_minutes} minutes)")
        logger.info(f"📊 Monitoring {len(self.endpoints)} endpoints")
        
        # Run initial check
        self.check_all_endpoints()
        
        # Schedule periodic checks
        schedule.every(interval_minutes).minutes.do(self.check_all_endpoints)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Health monitoring stopped")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Health Monitoring System")
    parser.add_argument("--base-url", default="http://localhost:7860", help="Base URL for API")
    parser.add_argument("--interval", type=int, default=5, help="Check interval in minutes")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    
    args = parser.parse_args()
    
    monitor = HealthMonitor(base_url=args.base_url)
    
    if args.once:
        results = monitor.check_all_endpoints()
        summary = monitor.get_health_summary()
        print("\n" + "="*50)
        print("HEALTH SUMMARY")
        print("="*50)
        print(json.dumps(summary, indent=2))
        print("="*50)
    else:
        monitor.start_monitoring(interval_minutes=args.interval)
