# 🚀 Railway Deployment Guide for Andalus Downloader Backend

This guide will help you deploy the Andalus Downloader backend API to Railway.app for production use.

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Railway CLI**: Install the Railway CLI tool
3. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)

## 🛠️ Installation Steps

### 1. Install Railway CLI

**Using npm (recommended):**
```bash
npm install -g @railway/cli
```

**Using curl (Linux/macOS):**
```bash
curl -fsSL https://railway.app/install.sh | sh
```

**Using PowerShell (Windows):**
```powershell
iwr https://railway.app/install.ps1 | iex
```

### 2. Login to Railway

```bash
railway login
```

This will open your browser for authentication.

## 🚀 Deployment Methods

### Method 1: Automated Script (Recommended)

**For Windows:**
```cmd
deploy-railway.bat
```

**For Linux/macOS:**
```bash
chmod +x deploy-railway.sh
./deploy-railway.sh
```

### Method 2: Manual Deployment

1. **Initialize Railway Project:**
   ```bash
   railway init
   ```

2. **Set Environment Variables:**
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

3. **Deploy:**
   ```bash
   railway up
   ```

### Method 3: GitHub Integration

1. **Connect GitHub Repository:**
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your Andalus Downloader repository

2. **Configure Environment Variables:**
   - In Railway dashboard, go to your project
   - Click on "Variables" tab
   - Add the following variables:
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

3. **Deploy:**
   - Railway will automatically deploy when you push to your main branch

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Application environment | `development` | ✅ |
| `PORT` | Server port (auto-set by Railway) | `8000` | ❌ |
| `LOG_LEVEL` | Logging level | `INFO` | ❌ |
| `MAX_CONCURRENT_DOWNLOADS` | Max simultaneous downloads | `3` | ❌ |
| `ENABLE_CORS` | Enable CORS | `true` | ❌ |
| `DATABASE_PATH` | SQLite database path | `/app/data/andalus_downloader.db` | ❌ |
| `DOWNLOADS_PATH` | Downloads directory | `/app/downloads` | ❌ |

### Production Optimizations

The deployment includes several production optimizations:

- **Docker Multi-stage Build**: Optimized container size
- **Non-root User**: Enhanced security
- **Health Checks**: Automatic health monitoring
- **Proper Logging**: Structured logging for production
- **Environment-based Config**: Separate production configuration
- **Resource Limits**: Controlled resource usage

## 📊 Monitoring & Management

### Check Deployment Status
```bash
railway status
```

### View Logs
```bash
railway logs
```

### Open in Browser
```bash
railway open
```

### Manage Variables
```bash
railway variables
```

## 🔗 API Endpoints

Once deployed, your API will be available at `https://your-app-name.railway.app`

### Key Endpoints:
- **Health Check**: `GET /health`
- **API Documentation**: `GET /docs`
- **System Status**: `GET /api/v1/status`
- **Create Download**: `POST /api/v1/downloads`
- **List Downloads**: `GET /api/v1/downloads`
- **WebSocket**: `WS /ws/downloads`

### Example Usage:
```bash
# Health check
curl https://your-app-name.railway.app/health

# System status
curl https://your-app-name.railway.app/api/v1/status

# Create download
curl -X POST https://your-app-name.railway.app/api/v1/downloads \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "quality": "720p", "format": "mp4"}'
```

## 💾 Persistent Storage

Railway provides ephemeral storage by default. For persistent downloads and database:

1. **Add Railway Volume** (Recommended):
   ```bash
   railway volume create --name andalus-data --mount-path /app/data
   railway volume create --name andalus-downloads --mount-path /app/downloads
   ```

2. **Or use External Storage**:
   - AWS S3
   - Google Cloud Storage
   - Azure Blob Storage

## 🔒 Security Considerations

- **CORS Configuration**: Update `cors_origins` in production config
- **Rate Limiting**: Consider adding rate limiting middleware
- **Authentication**: Add API authentication for production use
- **HTTPS**: Railway provides HTTPS by default
- **Environment Variables**: Never commit secrets to Git

## 🐛 Troubleshooting

### Common Issues:

1. **Build Failures**:
   ```bash
   railway logs --build
   ```

2. **Runtime Errors**:
   ```bash
   railway logs
   ```

3. **Port Issues**:
   - Ensure your app listens on `0.0.0.0:$PORT`
   - Railway automatically sets the `PORT` environment variable

4. **Memory Issues**:
   - Monitor resource usage in Railway dashboard
   - Consider upgrading to a paid plan for more resources

### Debug Commands:
```bash
# Check project info
railway status

# View environment variables
railway variables

# Connect to project shell
railway shell

# View build logs
railway logs --build

# View runtime logs
railway logs --tail
```

## 💰 Pricing

Railway offers:
- **$5/month free credit** for new users
- **Pay-as-you-go** pricing after free credit
- **No sleep mode** (unlike some free tiers)

Monitor your usage in the Railway dashboard.

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Railway CLI Reference](https://docs.railway.app/develop/cli)
- [Railway Pricing](https://railway.app/pricing)
- [Andalus Downloader API Documentation](https://your-app-name.railway.app/docs)

## 🎯 Next Steps

After successful deployment:

1. **Test all endpoints** using the API documentation
2. **Set up monitoring** and alerts
3. **Configure your frontend** to use the new API URL
4. **Set up CI/CD** for automatic deployments
5. **Add authentication** for production security

---

**Happy downloading with Andalus Downloader! 🎉**
