# 🚀 Deploy Andalus Downloader Backend for FREE

## 🌟 **Easiest Option: Railway.app** (Recommended)

### **Step 1: Prepare Your Code**
```bash
# Push to GitHub (if not already done)
git add .
git commit -m "Ready for deployment"
git push origin main
```

### **Step 2: Deploy to Railway**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `Andalus-Downloader` repository
5. Railway auto-detects Docker and deploys!
6. Your API will be live at: `https://your-app-name.railway.app`

### **Step 3: Test Your Deployment**
```bash
# Test health endpoint
curl https://your-app-name.railway.app/health

# Test API
curl https://your-app-name.railway.app/api/v1/platforms
```

## 🆓 **Alternative: Render.com** (100% Free)

### **Step 1: Deploy to Render**
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New" → "Web Service"
4. Connect your GitHub repo
5. Select "Docker" as environment
6. Click "Create Web Service"
7. Your API will be live at: `https://your-app-name.onrender.com`

**Note**: Render free tier sleeps after 15 minutes of inactivity, but wakes up automatically when accessed.

## 🔧 **Environment Variables** (Set in Platform Dashboard)

For production deployment, set these environment variables:

```bash
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
MAX_CONCURRENT_DOWNLOADS=3
DEFAULT_OUTPUT_PATH=/tmp/downloads
DATABASE_PATH=/tmp/andalus_downloader.db
```

## 🎯 **Quick Commands**

### **Railway CLI Deployment** (Alternative)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up
```

### **Fly.io Deployment** (Alternative)
```bash
# Install Fly CLI
# Windows: iwr https://fly.io/install.ps1 -useb | iex
# macOS: brew install flyctl

# Deploy
flyctl auth login
flyctl launch --no-deploy
flyctl deploy
```

## 🌐 **Your API Endpoints Will Be:**

Once deployed, your API will be accessible at:

- **Health**: `https://your-domain.com/health`
- **Platforms**: `https://your-domain.com/api/v1/platforms`
- **Validate URL**: `https://your-domain.com/api/v1/validate`
- **Create Download**: `https://your-domain.com/api/v1/downloads`
- **API Docs**: `https://your-domain.com/docs`

## 💡 **Pro Tips**

1. **Use Railway** for production (no sleep, reliable)
2. **Use Render** for development (completely free)
3. **Set up GitHub Actions** for auto-deployment
4. **Monitor usage** to stay within free limits
5. **Use environment variables** for configuration

## 🎉 **Result**

Your Andalus Downloader backend will be:
- ✅ **Live and accessible** worldwide
- ✅ **Completely FREE** to run
- ✅ **Auto-scaling** based on usage
- ✅ **HTTPS enabled** by default
- ✅ **Ready for your frontend** integration

**Total deployment time: 2-5 minutes!** 🚀
