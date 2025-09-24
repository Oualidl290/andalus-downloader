#!/bin/bash

# Andalus Downloader - Railway Deployment Script
# This script helps deploy the backend to Railway.app

set -e

echo "🚀 Andalus Downloader - Railway Deployment Script"
echo "=================================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI is not installed."
    echo "📥 Please install it from: https://docs.railway.app/develop/cli"
    echo "💡 Run: npm install -g @railway/cli"
    exit 1
fi

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway first:"
    echo "💡 Run: railway login"
    exit 1
fi

echo "✅ Railway CLI is ready!"

# Check if this is a new project or existing
if [ ! -f ".railway/project.json" ]; then
    echo "🆕 Creating new Railway project..."
    
    # Create new project
    railway init
    
    echo "📝 Setting up environment variables..."
    
    # Set production environment variables
    railway variables set ENVIRONMENT=production
    railway variables set PYTHONUNBUFFERED=1
    railway variables set PYTHONDONTWRITEBYTECODE=1
    railway variables set LOG_LEVEL=INFO
    railway variables set MAX_CONCURRENT_DOWNLOADS=3
    railway variables set ENABLE_CORS=true
    railway variables set DATABASE_PATH=/app/data/andalus_downloader.db
    railway variables set DOWNLOADS_PATH=/app/downloads
    
    echo "✅ Environment variables configured!"
else
    echo "🔄 Using existing Railway project..."
fi

echo "🔨 Building and deploying to Railway..."

# Deploy to Railway
railway up --detach

echo "⏳ Waiting for deployment to complete..."
sleep 10

# Get the deployment URL
RAILWAY_URL=$(railway status --json | grep -o '"url":"[^"]*' | cut -d'"' -f4)

if [ ! -z "$RAILWAY_URL" ]; then
    echo "🎉 Deployment successful!"
    echo "🌐 Your API is available at: $RAILWAY_URL"
    echo "📋 API Documentation: $RAILWAY_URL/docs"
    echo "🔍 Health Check: $RAILWAY_URL/health"
    echo "📊 System Status: $RAILWAY_URL/api/v1/status"
else
    echo "⚠️  Deployment completed but URL not found."
    echo "💡 Check Railway dashboard for deployment status."
fi

echo ""
echo "🔧 Useful Railway Commands:"
echo "  railway logs        - View application logs"
echo "  railway status      - Check deployment status"
echo "  railway open        - Open project in browser"
echo "  railway variables   - Manage environment variables"
echo ""
echo "📚 Documentation: https://docs.railway.app/"
echo "🎯 Happy downloading with Andalus Downloader!"
