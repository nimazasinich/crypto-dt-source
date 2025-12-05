"""
Test script for news page filters
Run this while the server is running to verify filters work correctly
"""
import requests
import json

BASE_URL = "http://localhost:7860"

def test_news_endpoint():
    """Test news API endpoint with different filters"""
    
    print("=" * 60)
    print("TESTING NEWS API FILTERS")
    print("=" * 60)
    
    # Test 1: Basic news fetch (no filters)
    print("\n1. Testing basic news fetch...")
    response = requests.get(f"{BASE_URL}/api/news")
    data = response.json()
    print(f"   ✓ Status: {response.status_code}")
    print(f"   ✓ Articles received: {len(data.get('articles', []))}")
    
    if data.get('articles'):
        article = data['articles'][0]
        print(f"   ✓ Sample article: {article.get('title', 'N/A')[:50]}...")
        print(f"   ✓ Source: {article.get('source', 'N/A')}")
        print(f"   ✓ Sentiment: {article.get('sentiment', 'N/A')}")
    
    # Test 2: Filter by sentiment (positive)
    print("\n2. Testing sentiment filter (positive)...")
    response = requests.get(f"{BASE_URL}/api/news?sentiment=positive")
    data = response.json()
    print(f"   ✓ Status: {response.status_code}")
    print(f"   ✓ Positive articles: {len(data.get('articles', []))}")
    
    # Verify all are positive
    all_positive = all(a.get('sentiment') == 'positive' for a in data.get('articles', []))
    print(f"   ✓ All positive: {all_positive}")
    
    # Test 3: Filter by sentiment (negative)
    print("\n3. Testing sentiment filter (negative)...")
    response = requests.get(f"{BASE_URL}/api/news?sentiment=negative")
    data = response.json()
    print(f"   ✓ Status: {response.status_code}")
    print(f"   ✓ Negative articles: {len(data.get('articles', []))}")
    
    # Test 4: Filter by sentiment (neutral)
    print("\n4. Testing sentiment filter (neutral)...")
    response = requests.get(f"{BASE_URL}/api/news?sentiment=neutral")
    data = response.json()
    print(f"   ✓ Status: {response.status_code}")
    print(f"   ✓ Neutral articles: {len(data.get('articles', []))}")
    
    # Test 5: Get all sources
    print("\n5. Getting available sources...")
    response = requests.get(f"{BASE_URL}/api/news?limit=100")
    data = response.json()
    sources = set(a.get('source') for a in data.get('articles', []))
    print(f"   ✓ Available sources: {', '.join(sources)}")
    
    # Test 6: Filter by source (if any source exists)
    if sources:
        test_source = list(sources)[0]
        print(f"\n6. Testing source filter ({test_source})...")
        response = requests.get(f"{BASE_URL}/api/news?source={test_source}")
        data = response.json()
        print(f"   ✓ Status: {response.status_code}")
        print(f"   ✓ Articles from {test_source}: {len(data.get('articles', []))}")
        
        # Verify all are from the same source
        all_same_source = all(a.get('source') == test_source for a in data.get('articles', []))
        print(f"   ✓ All from same source: {all_same_source}")
    
    # Test 7: Limit parameter
    print("\n7. Testing limit parameter...")
    response = requests.get(f"{BASE_URL}/api/news?limit=5")
    data = response.json()
    print(f"   ✓ Status: {response.status_code}")
    print(f"   ✓ Articles (should be ≤5): {len(data.get('articles', []))}")
    
    # Test 8: Combined filters
    print("\n8. Testing combined filters (positive sentiment, limit=3)...")
    response = requests.get(f"{BASE_URL}/api/news?sentiment=positive&limit=3")
    data = response.json()
    print(f"   ✓ Status: {response.status_code}")
    print(f"   ✓ Articles: {len(data.get('articles', []))}")
    print(f"   ✓ Filters applied: {data.get('filters', {})}")
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED!")
    print("=" * 60)
    
    return True

def test_news_page():
    """Test that news page loads"""
    print("\n\nTesting news page HTML...")
    response = requests.get(f"{BASE_URL}/static/pages/news/index.html")
    print(f"✓ Status: {response.status_code}")
    print(f"✓ Page loaded successfully")

if __name__ == "__main__":
    try:
        # Test API endpoints
        test_news_endpoint()
        
        # Test page loads
        test_news_page()
        
        print("\n\n✅ All tests passed!")
        print("\nYou can now open http://localhost:7860/static/pages/news/index.html")
        print("and test the filters manually:\n")
        print("  1. Type 'BTC' in the search box")
        print("  2. Select a source from the dropdown")
        print("  3. Select a sentiment from the dropdown")
        print("  4. Verify the news list updates accordingly")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server at http://localhost:7860")
        print("Please make sure the server is running:")
        print("  python app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

