@echo off
REM Docker build script for Andalus Downloader Backend API (Windows)

setlocal enabledelayedexpansion

REM Configuration
set IMAGE_NAME=andalus-downloader
set TAG=%1
if "%TAG%"=="" set TAG=latest
set FULL_IMAGE_NAME=%IMAGE_NAME%:%TAG%

echo.
echo 🐳 Building Andalus Downloader Docker Image
echo Image: %FULL_IMAGE_NAME%
echo ==================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker and try again.
    exit /b 1
)

REM Build the Docker image
echo 📦 Building Docker image...
docker build -t "%FULL_IMAGE_NAME%" .

if errorlevel 1 (
    echo ❌ Docker build failed!
    exit /b 1
)

echo ✅ Docker image built successfully!

REM Show image details
echo.
echo 📊 Image Details:
docker images %IMAGE_NAME% --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

REM Optional: Run a quick test
echo.
echo 🧪 Running quick health check...
for /f %%i in ('docker run -d -p 8001:8000 "%FULL_IMAGE_NAME%"') do set CONTAINER_ID=%%i

REM Wait for container to start
timeout /t 10 /nobreak >nul

REM Test health endpoint
curl -f http://localhost:8001/health >nul 2>&1
if errorlevel 1 (
    echo ❌ Health check failed
) else (
    echo ✅ Health check passed!
)

REM Clean up test container
docker stop %CONTAINER_ID% >nul
docker rm %CONTAINER_ID% >nul

echo.
echo 🎉 Build completed successfully!
echo.
echo To run the container:
echo   docker run -p 8000:8000 %FULL_IMAGE_NAME%
echo.
echo Or use docker-compose:
echo   docker-compose up -d

endlocal
