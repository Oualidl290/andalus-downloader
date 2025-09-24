@echo off
REM Quick test script for Andalus Downloader Backend API

echo 🚀 Quick Test - Andalus Downloader Backend API
echo ===============================================

REM Stop any existing containers
echo 🛑 Stopping existing containers...
docker-compose -f docker-compose.test.yml down >nul 2>&1

REM Build and start the development environment
echo 🔨 Building and starting development environment...
docker-compose -f docker-compose.test.yml up -d --build andalus-dev

if errorlevel 1 (
    echo ❌ Failed to start development environment
    exit /b 1
)

echo ✅ Development environment started

REM Wait for server to be ready
echo ⏳ Waiting for server to start (30 seconds)...
timeout /t 30 /nobreak >nul

REM Test basic endpoints
echo 🧪 Testing endpoints...
echo.

echo Testing health endpoint:
curl -s http://localhost:8000/health
echo.
echo.

echo Testing system status:
curl -s http://localhost:8000/api/v1/status
echo.
echo.

echo Testing supported platforms:
curl -s http://localhost:8000/api/v1/platforms
echo.
echo.

echo Testing URL validation:
curl -s -X POST http://localhost:8000/api/v1/validate -H "Content-Type: application/json" -d "{\"url\": \"https://www.youtube.com/watch?v=dQw4w9WgXcQ\"}"
echo.
echo.

echo 📋 Container status:
docker-compose -f docker-compose.test.yml ps

echo.
echo 🌐 Access points:
echo   • API Docs: http://localhost:8000/docs
echo   • Health: http://localhost:8000/health
echo   • Status: http://localhost:8000/api/v1/status

echo.
echo 🔧 To stop: docker-compose -f docker-compose.test.yml down
echo 🔧 To view logs: docker-compose -f docker-compose.test.yml logs -f andalus-dev
