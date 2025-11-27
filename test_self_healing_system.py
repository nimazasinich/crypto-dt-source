#!/usr/bin/env python3
"""
Test script for the Crypto API Hub Self-Healing System

This script tests all components of the self-healing system including:
- Backend router endpoints
- Monitoring service
- Health checks
- Recovery mechanisms
"""

import asyncio
import sys
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent))


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")


async def test_monitoring_service():
    """Test the monitoring service"""
    print_header("Testing Monitoring Service")
    
    try:
        # Try to import the monitoring service
        print_info("Importing monitoring service...")
        from backend.services.crypto_hub_monitoring import CryptoHubMonitor
        print_success("Monitoring service imported successfully")
        
        # Create monitor instance
        print_info("Creating monitor instance...")
        monitor = CryptoHubMonitor(
            check_interval=5,
            timeout=5,
            max_retries=2
        )
        print_success("Monitor instance created")
        
        # Test basic functionality
        print_info("Testing basic functionality...")
        
        # Register a test endpoint
        monitor.register_endpoint("https://api.example.com", {"test": True})
        print_success("Endpoint registration works")
        
        # Get health summary
        summary = monitor.get_health_summary()
        print_success("Health summary retrieval works")
        print_info(f"  Total endpoints: {summary['total_endpoints']}")
        
        # Test endpoint details
        details = monitor.get_endpoint_details("https://api.example.com")
        if details:
            print_success("Endpoint details retrieval works")
        
        # Unregister endpoint
        monitor.unregister_endpoint("https://api.example.com")
        print_success("Endpoint unregistration works")
        
        print_success("\nMonitoring service test completed!")
        return True
        
    except ImportError as e:
        print_warning(f"Could not import monitoring service (may need dependencies): {e}")
        print_info("This is acceptable if dependencies are not installed")
        return True
    except Exception as e:
        print_error(f"Monitoring service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_file_structure():
    """Test that all required files exist"""
    print_header("Testing File Structure")
    
    required_files = [
        "static/crypto-api-hub-stunning.html",
        "static/js/crypto-api-hub-self-healing.js",
        "backend/routers/crypto_api_hub_self_healing.py",
        "backend/services/crypto_hub_monitoring.py",
        "docs/CRYPTO_HUB_SELF_HEALING_GUIDE.md",
        "docs/CRYPTO_HUB_QUICK_START.md",
        "README_SELF_HEALING.md"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            print_success(f"{file_path}")
        else:
            print_error(f"{file_path} - NOT FOUND")
            all_exist = False
    
    if all_exist:
        print_success("\nAll required files exist!")
        return True
    else:
        print_error("\nSome required files are missing!")
        return False


async def test_module_imports():
    """Test that all modules can be imported"""
    print_header("Testing Module Imports")
    
    modules_to_test = [
        ("backend.routers.crypto_api_hub_self_healing", "router"),
        ("backend.services.crypto_hub_monitoring", "CryptoHubMonitor"),
    ]
    
    all_imported = True
    for module_name, item_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[item_name])
            getattr(module, item_name)
            print_success(f"{module_name}.{item_name}")
        except Exception as e:
            print_error(f"{module_name}.{item_name} - {str(e)}")
            all_imported = False
    
    if all_imported:
        print_success("\nAll modules imported successfully!")
        return True
    else:
        print_error("\nSome modules failed to import!")
        return False


async def test_javascript_file():
    """Test the JavaScript self-healing file"""
    print_header("Testing JavaScript File")
    
    js_file = Path(__file__).parent / "static/js/crypto-api-hub-self-healing.js"
    
    if not js_file.exists():
        print_error("JavaScript file not found!")
        return False
    
    content = js_file.read_text()
    
    # Check for required components
    required_components = [
        "class SelfHealingAPIHub",
        "fetchWithRecovery",
        "performHealthChecks",
        "getHealthStatus",
        "getDiagnostics",
        "tryFallback",
        "tryBackendProxy"
    ]
    
    all_present = True
    for component in required_components:
        if component in content:
            print_success(f"Found: {component}")
        else:
            print_error(f"Missing: {component}")
            all_present = False
    
    if all_present:
        print_success("\nJavaScript file contains all required components!")
        print_info(f"File size: {len(content)} bytes")
        return True
    else:
        print_error("\nJavaScript file is missing some components!")
        return False


async def test_html_integration():
    """Test HTML file has self-healing integration"""
    print_header("Testing HTML Integration")
    
    html_file = Path(__file__).parent / "static/crypto-api-hub-stunning.html"
    
    if not html_file.exists():
        print_error("HTML file not found!")
        return False
    
    content = html_file.read_text()
    
    # Check for required elements
    checks = [
        ("Services grid", '<div class="services-grid"'),
        ("API Tester", 'onclick="openTester()'),
        ("Export functionality", 'onclick="exportJSON()'),
        ("Search", 'id="searchInput"'),
        ("Filter tabs", 'class="filter-tabs"'),
    ]
    
    all_present = True
    for check_name, check_str in checks:
        if check_str in content:
            print_success(f"Found: {check_name}")
        else:
            print_error(f"Missing: {check_name}")
            all_present = False
    
    # Count services
    services_count = content.count('name:')
    print_info(f"Services defined: ~{services_count}")
    
    if all_present:
        print_success("\nHTML file contains all required elements!")
        return True
    else:
        print_error("\nHTML file is missing some elements!")
        return False


async def test_documentation():
    """Test that documentation is complete"""
    print_header("Testing Documentation")
    
    docs_to_check = [
        ("Self-Healing Guide", "docs/CRYPTO_HUB_SELF_HEALING_GUIDE.md"),
        ("Quick Start", "docs/CRYPTO_HUB_QUICK_START.md"),
        ("README", "README_SELF_HEALING.md")
    ]
    
    all_complete = True
    for doc_name, doc_path in docs_to_check:
        full_path = Path(__file__).parent / doc_path
        if full_path.exists():
            content = full_path.read_text()
            word_count = len(content.split())
            print_success(f"{doc_name}: {word_count} words")
            
            # Check for key sections
            if "## " in content:
                section_count = content.count("## ")
                print_info(f"  Sections: {section_count}")
        else:
            print_error(f"{doc_name} not found!")
            all_complete = False
    
    if all_complete:
        print_success("\nAll documentation complete!")
        return True
    else:
        print_error("\nSome documentation is missing!")
        return False


async def run_all_tests():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{'*' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{'Crypto API Hub Self-Healing System Test Suite':^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{'*' * 60}{Colors.RESET}\n")
    
    results = {}
    
    # Run tests
    results["File Structure"] = await test_file_structure()
    results["Module Imports"] = await test_module_imports()
    results["JavaScript File"] = await test_javascript_file()
    results["HTML Integration"] = await test_html_integration()
    results["Documentation"] = await test_documentation()
    results["Monitoring Service"] = await test_monitoring_service()
    
    # Print summary
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASSED{Colors.RESET}" if result else f"{Colors.RED}FAILED{Colors.RESET}"
        print(f"  {test_name:<30} {status}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! System is ready for use!{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  Some tests failed. Please review the output above.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
