@echo off
echo 🚀 Starting ngrok tunnel for Andalus Downloader...
echo.

echo ✅ Authtoken configured
echo 🌐 Starting tunnel on domain: andalus-downloader.ngrok.io
echo 📡 Forwarding to: http://localhost:8000
echo.

ngrok http 8000 --domain=andalus-downloader.ngrok.io

pause
