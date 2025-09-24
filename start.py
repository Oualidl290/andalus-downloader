#!/usr/bin/env python3
"""
Production startup script for Andalus Downloader Backend API
"""
import sys
import os
import subprocess
import argparse
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'aiosqlite', 
        'yt-dlp', 'requests', 'aiofiles', 'websockets'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg: {version_line}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("⚠️  FFmpeg not found - format conversion will be limited")
    print("Install FFmpeg: https://ffmpeg.org/download.html")
    return False

def setup_directories():
    """Create necessary directories"""
    directories = ['logs', 'downloads', 'config', 'cache']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Directory: {directory}/")

def run_tests():
    """Run basic tests"""
    try:
        print("\n🧪 Running basic tests...")
        result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-v'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ All tests passed")
            return True
        else:
            print("⚠️  Some tests failed:")
            print(result.stdout)
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  Tests could not be run (pytest not available)")
        return False

def start_server(args):
    """Start the API server"""
    print(f"\n🚀 Starting Andalus Downloader Backend API...")
    print(f"   Mode: {'Development' if args.dev else 'Production'}")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    
    # Set environment variables
    env = os.environ.copy()
    env['HOST'] = args.host
    env['PORT'] = str(args.port)
    env['LOG_LEVEL'] = args.log_level.upper()
    
    if args.dev:
        env['RELOAD'] = 'true'
        env['WORKERS'] = '1'
    else:
        env['RELOAD'] = 'false'
        env['WORKERS'] = str(args.workers)
    
    # Start the server
    try:
        subprocess.run([sys.executable, 'main.py'], env=env)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Andalus Downloader Backend API')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--workers', type=int, default=1, help='Number of worker processes')
    parser.add_argument('--log-level', default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Log level')
    parser.add_argument('--dev', action='store_true', help='Development mode (auto-reload)')
    parser.add_argument('--skip-checks', action='store_true', help='Skip system checks')
    parser.add_argument('--skip-tests', action='store_true', help='Skip tests')
    
    args = parser.parse_args()
    
    print("🔧 Andalus Downloader Backend API - Production Setup")
    print("=" * 50)
    
    if not args.skip_checks:
        print("\n📋 System Checks:")
        check_python_version()
        
        if not check_dependencies():
            sys.exit(1)
        
        check_ffmpeg()
        setup_directories()
        
        if not args.skip_tests:
            if not run_tests():
                response = input("\n⚠️  Tests failed. Continue anyway? (y/N): ")
                if response.lower() != 'y':
                    sys.exit(1)
    
    print("\n✅ All checks passed!")
    print("\n📚 API Documentation will be available at:")
    print(f"   • Swagger UI: http://{args.host}:{args.port}/docs")
    print(f"   • ReDoc: http://{args.host}:{args.port}/redoc")
    print(f"   • OpenAPI JSON: http://{args.host}:{args.port}/openapi.json")
    
    print("\n🌐 API Endpoints:")
    print(f"   • Health Check: http://{args.host}:{args.port}/health")
    print(f"   • System Status: http://{args.host}:{args.port}/api/v1/status")
    print(f"   • WebSocket: ws://{args.host}:{args.port}/ws/downloads")
    
    start_server(args)

if __name__ == "__main__":
    main()
