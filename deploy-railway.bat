@echo off
REM Andalus Downloader - Railway Deployment Script for Windows
REM This script helps deploy the backend to Railway.app

echo 🚀 Andalus Downloader - Railway Deployment Script
echo ==================================================

REM Check if Railway CLI is installed
railway --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Railway CLI is not installed.
    echo 📥 Please install it from: https://docs.railway.app/develop/cli
    echo 💡 Run: npm install -g @railway/cli
    pause
    exit /b 1
)

REM Check if user is logged in
railway whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔐 Please login to Railway first:
    echo 💡 Run: railway login
    pause
    exit /b 1
)

echo ✅ Railway CLI is ready!

REM Check if this is a new project or existing
if not exist ".railway\project.json" (
    echo 🆕 Creating new Railway project...
    
    REM Create new project
    railway init
    
    echo 📝 Setting up environment variables...
    
    REM Set production environment variables
    railway variables set ENVIRONMENT=production
    railway variables set PYTHONUNBUFFERED=1
    railway variables set PYTHONDONTWRITEBYTECODE=1
    railway variables set LOG_LEVEL=INFO
    railway variables set MAX_CONCURRENT_DOWNLOADS=3
    railway variables set ENABLE_CORS=true
    railway variables set DATABASE_PATH=/app/data/andalus_downloader.db
    railway variables set DOWNLOADS_PATH=/app/downloads
    
    echo ✅ Environment variables configured!
) else (
    echo 🔄 Using existing Railway project...
)

echo 🔨 Building and deploying to Railway...

REM Deploy to Railway
railway up --detach

echo ⏳ Waiting for deployment to complete...
timeout /t 10 /nobreak >nul

echo 🎉 Deployment initiated!
echo 💡 Check Railway dashboard for deployment status and URL.

echo.
echo 🔧 Useful Railway Commands:
echo   railway logs        - View application logs
echo   railway status      - Check deployment status
echo   railway open        - Open project in browser
echo   railway variables   - Manage environment variables
echo.
echo 📚 Documentation: https://docs.railway.app/
echo 🎯 Happy downloading with Andalus Downloader!

pause
