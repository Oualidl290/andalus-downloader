#!/usr/bin/env python3
"""
Test the API structure without running the server
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test if all modules can be imported"""
    print("🧪 Testing API Structure and Imports")
    print("=" * 40)
    
    tests = [
        ("Core Models", "from src.core.models import DownloadRequest, DownloadStatus"),
        ("Database", "from src.core.database import get_database"),
        ("Download Manager", "from src.core.download_manager import get_download_manager"),
        ("Download Task", "from src.core.download_task import DownloadTaskRunner"),
        ("Network Client", "from src.utils.network import get_http_client"),
        ("Logger", "from src.utils.logger import get_logger"),
        ("Config", "from src.utils.config import get_config"),
        ("Extractors", "from src.extractors.base import get_extractor_factory"),
        ("YouTube Extractor", "from src.extractors.youtube import YouTubeExtractor"),
        ("Generic Extractor", "from src.extractors.generic import GenericExtractor"),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, import_statement in tests:
        try:
            exec(import_statement)
            print(f"✅ {name}")
            passed += 1
        except ImportError as e:
            print(f"❌ {name} - ImportError: {e}")
        except Exception as e:
            print(f"❌ {name} - Error: {e}")
    
    print("=" * 40)
    print(f"📊 Import Results: {passed}/{total} modules imported successfully")
    
    return passed == total

def test_api_structure():
    """Test API structure"""
    print("\n🏗️  Testing API Structure")
    print("=" * 40)
    
    try:
        from src.api.app import app
        print("✅ FastAPI app created successfully")
        
        # Get routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                for method in route.methods:
                    if method != 'HEAD':  # Skip HEAD methods
                        routes.append(f"{method} {route.path}")
        
        print(f"📋 Available API Routes ({len(routes)}):")
        for route in sorted(routes):
            print(f"   • {route}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create FastAPI app: {e}")
        return False

def test_extractors():
    """Test extractor functionality"""
    print("\n🔌 Testing Extractors")
    print("=" * 40)
    
    try:
        from src.extractors.base import get_extractor_factory
        
        factory = get_extractor_factory()
        platforms = factory.get_supported_platforms()
        
        print(f"✅ Extractor factory initialized")
        print(f"📋 Supported Platforms ({len(platforms)}):")
        for platform in platforms:
            print(f"   • {platform}")
        
        # Test URL detection
        test_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://example.com/video.mp4",
            "invalid-url"
        ]
        
        print(f"\n🔍 URL Detection Tests:")
        for url in test_urls:
            extractor = factory.get_extractor(url)
            if extractor:
                print(f"   ✅ {url} → {extractor.platform_name}")
            else:
                print(f"   ❌ {url} → No extractor found")
        
        return True
        
    except Exception as e:
        print(f"❌ Extractor test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Andalus Downloader Backend - Structure Tests")
    print("=" * 50)
    
    results = []
    results.append(test_imports())
    results.append(test_api_structure())
    results.append(test_extractors())
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 All structure tests passed!")
        print("✅ The API backend is properly structured and ready to run.")
        print("\n💡 To start the server:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Run server: python main.py")
        print("   3. Or use Docker: docker-compose up -d")
        return 0
    else:
        print(f"⚠️  {passed}/{total} tests passed. Some issues found.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
