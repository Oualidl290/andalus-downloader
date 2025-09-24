#!/usr/bin/env python3
"""
Simple endpoint testing script for Andalus Downloader Backend API
"""
import requests
import json
import time
import sys
from typing import Dict, Any

# API Base URL
BASE_URL = "http://localhost:8000"

def test_endpoint(method: str, endpoint: str, data: Dict[Any, Any] = None, expected_status: int = 200) -> bool:
    """Test a single API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        print(f"Testing {method} {endpoint}...")
        
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        if response.status_code == expected_status:
            print(f"✅ {method} {endpoint} - Status: {response.status_code}")
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
            except:
                print(f"   Response: {response.text[:100]}...")
            return True
        else:
            print(f"❌ {method} {endpoint} - Expected: {expected_status}, Got: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint} - Connection refused (server not running?)")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {method} {endpoint} - Request timeout")
        return False
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {e}")
        return False

def main():
    """Run all endpoint tests"""
    print("🧪 Testing Andalus Downloader Backend API Endpoints")
    print("=" * 50)
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    for i in range(30):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                break
        except:
            pass
        time.sleep(1)
        if i % 5 == 0:
            print(f"   Still waiting... ({i+1}/30)")
    
    # Test cases
    tests = [
        # Basic endpoints
        ("GET", "/health", None, 200),
        ("GET", "/api/v1/status", None, 200),
        ("GET", "/api/v1/platforms", None, 200),
        ("GET", "/api/v1/downloads", None, 200),
        
        # URL validation
        ("POST", "/api/v1/validate", {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}, 200),
        ("POST", "/api/v1/validate", {"url": "invalid-url"}, 200),
        
        # Metadata extraction (might take time)
        ("GET", "/api/v1/metadata?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ", None, 200),
        
        # Create download (might take time)
        ("POST", "/api/v1/downloads", {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "quality": "720p",
            "format": "mp4"
        }, 200),
    ]
    
    passed = 0
    total = len(tests)
    
    for method, endpoint, data, expected_status in tests:
        if test_endpoint(method, endpoint, data, expected_status):
            passed += 1
        print()
        time.sleep(0.5)  # Small delay between tests
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
