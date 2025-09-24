@echo off
REM Local testing script for Andalus Downloader Backend API (Windows)

setlocal enabledelayedexpansion

echo.
echo 🐳 Andalus Downloader - Local Development & Testing
echo ================================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker and try again.
    exit /b 1
)

echo ✅ Docker is running

REM Build and start development environment
echo.
echo 🔨 Building development environment...
docker-compose -f docker-compose.test.yml build andalus-dev

if errorlevel 1 (
    echo ❌ Failed to build development environment
    exit /b 1
)

echo ✅ Development environment built successfully

REM Start the development server
echo.
echo 🚀 Starting development server...
docker-compose -f docker-compose.test.yml up -d andalus-dev

if errorlevel 1 (
    echo ❌ Failed to start development server
    exit /b 1
)

echo ✅ Development server started

REM Wait for server to be ready
echo.
echo ⏳ Waiting for server to be ready...
timeout /t 15 /nobreak >nul

REM Test if server is responding
echo.
echo 🧪 Testing server health...
for /l %%i in (1,1,10) do (
    curl -f http://localhost:8000/health >nul 2>&1
    if not errorlevel 1 (
        echo ✅ Server is healthy and responding
        goto :server_ready
    )
    echo Attempt %%i/10 - Server not ready yet...
    timeout /t 3 /nobreak >nul
)

echo ❌ Server failed to start properly
echo 📋 Checking server logs:
docker-compose -f docker-compose.test.yml logs --tail=20 andalus-dev
exit /b 1

:server_ready

REM Run endpoint tests
echo.
echo 🧪 Running endpoint tests...
docker-compose -f docker-compose.test.yml run --rm andalus-test

REM Show server status
echo.
echo 📊 Server Status:
docker-compose -f docker-compose.test.yml ps

echo.
echo 🌐 Available endpoints:
echo   • API Documentation: http://localhost:8000/docs
echo   • Health Check: http://localhost:8000/health
echo   • System Status: http://localhost:8000/api/v1/status
echo   • WebSocket: ws://localhost:8000/ws/downloads

echo.
echo 🔧 Management commands:
echo   • View logs: docker-compose -f docker-compose.test.yml logs -f andalus-dev
echo   • Stop server: docker-compose -f docker-compose.test.yml down
echo   • Shell access: docker-compose -f docker-compose.test.yml exec andalus-dev bash
echo   • Run tests: docker-compose -f docker-compose.test.yml run --rm andalus-test

echo.
echo 🎉 Local testing environment is ready!

endlocal
