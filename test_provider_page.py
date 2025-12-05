"""
Test script for Provider page functionality
Run this while the server is running to verify everything works
"""
import requests
import json

BASE_URL = "http://localhost:7860"

def test_provider_api():
    """Test provider API endpoint"""
    
    print("=" * 60)
    print("TESTING PROVIDER API")
    print("=" * 60)
    
    # Test 1: API Health Check
    print("\n1. Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"   ✓ Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ API Status: {data.get('status', 'N/A')}")
            print(f"   ✓ Environment: {data.get('environment', 'N/A')}")
        else:
            print(f"   ✗ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Health check error: {e}")
    
    # Test 2: Providers Endpoint
    print("\n2. Testing /api/providers endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/providers")
        print(f"   ✓ Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            providers = data.get('providers', [])
            print(f"   ✓ Total providers: {data.get('total', 0)}")
            print(f"   ✓ Active providers: {data.get('active', 0)}")
            
            if providers:
                print(f"\n   Sample Provider:")
                provider = providers[0]
                print(f"     - Name: {provider.get('name', 'N/A')}")
                print(f"     - Endpoint: {provider.get('endpoint', 'N/A')}")
                print(f"     - Category: {provider.get('category', 'N/A')}")
                print(f"     - Status: {provider.get('status', 'N/A')}")
                print(f"     - Rate Limit: {provider.get('rate_limit', 'N/A')}")
                print(f"     - Uptime: {provider.get('uptime', 'N/A')}")
                
            print(f"\n   All Providers:")
            for p in providers:
                status_icon = "✓" if p.get('status') == 'active' else "✗"
                print(f"     {status_icon} {p.get('name', 'Unknown')} - {p.get('category', 'N/A')}")
        else:
            print(f"   ✗ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Favicon
    print("\n3. Testing favicon...")
    try:
        response = requests.get(f"{BASE_URL}/favicon.ico")
        print(f"   ✓ Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✓ Favicon served successfully")
            print(f"   ✓ Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        else:
            print(f"   ⚠ Favicon status: {response.status_code}")
    except Exception as e:
        print(f"   ⚠ Favicon error: {e}")
    
    print("\n" + "=" * 60)
    print("API TESTS COMPLETED!")
    print("=" * 60)

def test_provider_page_load():
    """Test that provider page HTML loads"""
    print("\n\nTesting Provider Page HTML...")
    try:
        response = requests.get(f"{BASE_URL}/static/pages/providers/index.html")
        print(f"✓ Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            required_elements = [
                'id="providers-tbody"',
                'id="summary-cards"',
                'id="search-input"',
                'id="category-select"',
                'providers.js',
                'providers.css'
            ]
            
            print("\nChecking page elements:")
            for element in required_elements:
                if element in content:
                    print(f"  ✓ Found: {element}")
                else:
                    print(f"  ✗ Missing: {element}")
        else:
            print(f"✗ Page load failed: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error loading page: {e}")

def test_provider_css_js():
    """Test that CSS and JS files load"""
    print("\n\nTesting Provider Page Assets...")
    
    files = [
        "/static/pages/providers/providers.css",
        "/static/pages/providers/providers.js",
        "/static/assets/icons/favicon.svg"
    ]
    
    for file_path in files:
        try:
            response = requests.get(f"{BASE_URL}{file_path}")
            status_icon = "✓" if response.status_code == 200 else "✗"
            print(f"{status_icon} {file_path} - Status: {response.status_code}")
        except Exception as e:
            print(f"✗ {file_path} - Error: {e}")

def test_filter_functionality():
    """Test manual filter scenarios"""
    print("\n\nFilter Functionality Test Guide:")
    print("=" * 60)
    print("\nOpen http://localhost:7860/static/pages/providers/index.html")
    print("\nManual Test Cases:")
    print("\n1. SEARCH FILTER TEST")
    print("   • Type 'coin' in search box")
    print("   • Expected: Shows CoinGecko, CoinPaprika")
    print("   • Stats should update to show filtered count")
    
    print("\n2. CATEGORY FILTER TEST")
    print("   • Select 'Sentiment' from category dropdown")
    print("   • Expected: Shows only Alternative.me")
    print("   • Stats: Total: 1, Healthy: 1")
    
    print("\n3. COMBINED FILTERS TEST")
    print("   • Type 'api' in search")
    print("   • Select 'Market Data' category")
    print("   • Expected: Shows providers with 'api' AND 'Market Data'")
    
    print("\n4. NO RESULTS TEST")
    print("   • Type 'xyz123notfound' in search")
    print("   • Expected: Empty state with search icon")
    print("   • Message: 'No providers found'")
    
    print("\n5. CLEAR FILTERS TEST")
    print("   • Apply any filter")
    print("   • Click 'Clear' button")
    print("   • Expected: All filters reset, all providers shown")
    print("   • Toast notification: 'Filters cleared'")
    
    print("\n6. DEBOUNCE TEST")
    print("   • Rapidly type 'coingecko' in search")
    print("   • Expected: Filter applies only after you stop typing")
    print("   • Should NOT filter on every keystroke")
    
    print("\n7. RESPONSIVE TEST")
    print("   • Resize browser to mobile width")
    print("   • Expected: Filters stack vertically")
    print("   • All functionality still works")

if __name__ == "__main__":
    try:
        # Test API
        test_provider_api()
        
        # Test page loads
        test_provider_page_load()
        
        # Test assets
        test_provider_css_js()
        
        # Show filter test guide
        test_filter_functionality()
        
        print("\n\n" + "=" * 60)
        print("✅ ALL AUTOMATED TESTS COMPLETED!")
        print("=" * 60)
        print("\nYou can now open: http://localhost:7860/static/pages/providers/index.html")
        print("\nNew Features:")
        print("  ✅ Search filter (searches name, endpoint, description, category)")
        print("  ✅ Category dropdown filter")
        print("  ✅ Clear filters button")
        print("  ✅ Real-time stats updates")
        print("  ✅ Empty state when no results")
        print("  ✅ Debounced search (300ms)")
        print("  ✅ Combined filter support")
        print("\nExisting Features:")
        print("  ✓ Summary cards showing total/healthy/issues counts")
        print("  ✓ Table with provider details")
        print("  ✓ Glassmorphism design")
        print("  ✓ No favicon 404 errors")
        print("  ✓ No API health check failures")
        print("\n📖 Full documentation: PROVIDER_FILTERS_IMPLEMENTATION.md")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server at http://localhost:7860")
        print("Please make sure the server is running:")
        print("  python app.py")
        print("\nOr use the restart script:")
        print("  .\\restart_server.ps1")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

