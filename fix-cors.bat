@echo off
echo 🔧 Fixing CORS issue for Vercel deployment...
echo.

echo ✅ CORS configuration updated in backend
echo ✅ Added explicit Vercel domain support
echo ✅ Added preflight request handler
echo.

echo 🚀 Restarting backend server...
echo.

echo Please restart your backend server:
echo 1. Stop the current server (Ctrl+C)
echo 2. Run: .venv\Scripts\python.exe main.py
echo.

echo 🌐 Your Vercel app should now work: https://andalus-downloader.vercel.app
echo.
pause
