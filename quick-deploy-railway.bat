@echo off
echo 🚀 Quick Railway Deploy Script
echo ===============================

echo Setting environment variables...
railway variables --set "ENVIRONMENT=production" --set "PYTHONUNBUFFERED=1" --set "PYTHONDONTWRITEBYTECODE=1" --set "LOG_LEVEL=INFO" --set "MAX_CONCURRENT_DOWNLOADS=3" --set "ENABLE_CORS=true" --set "DATABASE_PATH=/app/data/andalus_downloader.db" --set "DOWNLOADS_PATH=/app/downloads"

echo Deploying to Railway...
railway up

echo Getting deployment URL...
railway status

echo 🎉 Deployment complete!
pause
