# 🚀 Complete Deployment Steps for Andalus Downloader Backend

## 📋 Current Status
✅ Git repository initialized  
✅ All files committed  
✅ Railway CLI installed  
✅ Production configuration ready  
✅ Docker configuration optimized  

## 🔗 Step 1: Push to GitHub

### Option A: Using GitHub Web Interface (Recommended)

1. **Create a new repository on GitHub:**
   - Go to [github.com](https://github.com)
   - Click "New repository"
   - Name: `andalus-downloader` (or your preferred name)
   - Description: `Universal media downloader backend API`
   - Make it **Public** (for easier Railway integration)
   - Don't initialize with README (we already have files)

2. **Push your local repository:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/andalus-downloader.git
   git branch -M main
   git push -u origin main
   ```

### Option B: Using GitHub CLI (if you install it)

```bash
# Install GitHub CLI first
winget install GitHub.cli

# Then create and push
gh repo create andalus-downloader --public --source=. --remote=origin --push
```

## 🚀 Step 2: Deploy to Railway

### Option A: Using Railway Web Interface (Easiest)

1. **Go to Railway Dashboard:**
   - Visit [railway.app](https://railway.app)
   - Sign up/Login with GitHub

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `andalus-downloader` repository
   - Railway will auto-detect the Dockerfile

3. **Configure Environment Variables:**
   In Railway dashboard, add these variables:
   ```
   ENVIRONMENT=production
   PYTHONUNBUFFERED=1
   PYTHONDONTWRITEBYTECODE=1
   LOG_LEVEL=INFO
   MAX_CONCURRENT_DOWNLOADS=3
   ENABLE_CORS=true
   DATABASE_PATH=/app/data/andalus_downloader.db
   DOWNLOADS_PATH=/app/downloads
   ```

4. **Deploy:**
   - Railway will automatically build and deploy
   - You'll get a URL like `https://andalus-downloader-production.up.railway.app`

### Option B: Using Railway CLI

1. **Login to Railway:**
   ```bash
   railway login
   ```

2. **Initialize Project:**
   ```bash
   railway init
   ```

3. **Set Environment Variables:**
   ```bash
   railway variables set ENVIRONMENT=production
   railway variables set PYTHONUNBUFFERED=1
   railway variables set PYTHONDONTWRITEBYTECODE=1
   railway variables set LOG_LEVEL=INFO
   railway variables set MAX_CONCURRENT_DOWNLOADS=3
   railway variables set ENABLE_CORS=true
   railway variables set DATABASE_PATH=/app/data/andalus_downloader.db
   railway variables set DOWNLOADS_PATH=/app/downloads
   ```

4. **Deploy:**
   ```bash
   railway up
   ```

## 🔧 Step 3: Verify Deployment

After deployment, test these endpoints:

```bash
# Replace YOUR_APP_URL with your actual Railway URL

# Health check
curl https://YOUR_APP_URL/health

# System status
curl https://YOUR_APP_URL/api/v1/status

# API documentation (open in browser)
https://YOUR_APP_URL/docs

# Supported platforms
curl https://YOUR_APP_URL/api/v1/platforms
```

## 📊 Step 4: Test the API

Create a test download:

```bash
curl -X POST https://YOUR_APP_URL/api/v1/downloads \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "quality": "720p",
    "format": "mp4"
  }'
```

## 🎯 Quick Commands Reference

### Railway Management
```bash
# View logs
railway logs

# Check status
railway status

# Open in browser
railway open

# Manage variables
railway variables

# Connect to shell
railway shell
```

### Git Commands
```bash
# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Your message"

# Push to GitHub
git push origin main
```

## 🔒 Security Notes

1. **Environment Variables**: Never commit sensitive data to Git
2. **CORS**: Update CORS settings for production domains
3. **Rate Limiting**: Consider adding rate limiting
4. **Authentication**: Add API authentication for production

## 💰 Cost Estimation

**Railway Pricing:**
- $5/month free credit for new users
- ~$0.000463 per GB-hour for compute
- ~$0.25 per GB-month for storage

**Estimated monthly cost for light usage:** $2-5

## 🆘 Troubleshooting

### Common Issues:

1. **Build fails**: Check `railway logs --build`
2. **App crashes**: Check `railway logs`
3. **Port issues**: Ensure app uses `$PORT` environment variable
4. **Database issues**: Check file permissions and paths

### Support:
- Railway Discord: [discord.gg/railway](https://discord.gg/railway)
- Railway Docs: [docs.railway.app](https://docs.railway.app)

## 🎉 Next Steps

After successful deployment:

1. **Update your frontend** to use the new API URL
2. **Set up monitoring** and alerts
3. **Configure custom domain** (optional)
4. **Set up CI/CD** for automatic deployments
5. **Add authentication** for production security

---

**Your Andalus Downloader Backend is ready for production! 🚀**
