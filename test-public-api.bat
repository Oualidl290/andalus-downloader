@echo off
echo Testing Public API Endpoints
echo ============================

echo.
echo Please replace YOUR_NGROK_URL with your actual ngrok URL
echo Example: https://andalus-downloader.ngrok.io
echo.

set /p NGROK_URL="Enter your ngrok URL: https://andalus-downloader.ngrok.io"

echo.
echo Testing Health Endpoint...
curl %NGROK_URL%/health

echo.
echo.
echo Testing System Status...
curl %NGROK_URL%/api/v1/status

echo.
echo.
echo Testing Supported Platforms...
curl %NGROK_URL%/api/v1/platforms

echo.
echo.
echo Your public API is ready!
echo Frontend should use: %NGROK_URL%
pause
