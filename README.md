# Andalus Downloader - Backend API

A universal media downloader **backend API service** that supports downloading video and audio content from various platforms in multiple formats. This backend provides RESTful endpoints for integration with frontend applications.

## Features

- **Multi-Platform Support**: Download from YouTube, Vimeo, SoundCloud, Dailymotion, and more
- **Format Flexibility**: Support for video formats (MP4, AVI, MKV, WebM) and audio formats (MP3, WAV, FLAC, AAC, OGG)
- **Quality Selection**: Choose download quality (1080p, 720p, 480p, 360p, audio-only)
- **Batch Downloads**: Download multiple URLs simultaneously via API
- **Playlist Support**: Download entire playlists or channels
- **RESTful API**: Clean, well-documented API endpoints with OpenAPI/Swagger
- **Real-time Updates**: WebSocket support for live progress tracking
- **Format Conversion**: Built-in converter using FFmpeg
- **Cross-Platform**: Backend runs on Windows, macOS, and Linux
- **Frontend Ready**: Designed for Next.js frontend integration (coming soon)

## Installation

### Requirements
- Python 3.9 or higher
- FFmpeg (for format conversion)

### Quick Start
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/andalus-downloader.git
   cd andalus-downloader
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the production startup script:
   ```bash
   python start.py
   ```

### Manual Setup
If you prefer manual setup:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the backend API server:
   ```bash
   python main.py
   ```

### Development Mode
For development with auto-reload:
```bash
python start.py --dev --log-level DEBUG
```

### Production Deployment
For production deployment:
```bash
python start.py --host 0.0.0.0 --port 8000 --workers 4 --log-level INFO
```

### Docker Deployment (Recommended)

#### Quick Start with Docker
```bash
# Clone and navigate to the project
git clone https://github.com/your-username/andalus-downloader.git
cd andalus-downloader

# Start with Docker Compose
docker-compose up -d
```

#### Build Docker Image
```bash
# Linux/macOS
./scripts/docker-build.sh

# Windows
scripts\docker-build.bat
```

#### Production Deployment
```bash
# Deploy to production
./scripts/deploy.sh production

# Or manually with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

#### Docker Commands
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Update and restart
docker-compose pull && docker-compose up -d
```

### Environment Variables
You can configure the application using environment variables:
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `WORKERS`: Number of worker processes (default: 1)
- `LOG_LEVEL`: Logging level (default: INFO)
- `MAX_CONCURRENT_DOWNLOADS`: Max concurrent downloads (default: 3)
- `DEFAULT_OUTPUT_PATH`: Default download directory (default: downloads)
- `DATABASE_PATH`: Database file path (default: andalus_downloader.db)

## API Usage

The backend provides RESTful API endpoints for all functionality:

### Core Endpoints
- `POST /api/v1/downloads` - Create a new download
- `GET /api/v1/downloads` - List all downloads with pagination
- `GET /api/v1/downloads/{id}` - Get specific download status
- `PUT /api/v1/downloads/{id}/pause` - Pause a download
- `PUT /api/v1/downloads/{id}/resume` - Resume a download
- `DELETE /api/v1/downloads/{id}` - Cancel a download

### Metadata & Preview
- `POST /api/v1/validate` - Validate URL and detect platform
- `GET /api/v1/metadata/{url}` - Extract video/audio metadata
- `GET /api/v1/formats/{url}` - Get available formats and qualities
- `GET /api/v1/thumbnail/{url}` - Get thumbnail image

### Real-time Updates
- `WebSocket /ws/downloads` - Real-time download progress updates

### API Documentation
Once the server is running, visit `http://localhost:8000/docs` for interactive API documentation.

### Supported Platforms
- YouTube (videos, playlists, channels)
- Vimeo
- SoundCloud
- Dailymotion
- Direct media URLs

## Development

### Project Structure
```
andalus-downloader/
├── src/
│   ├── api/           # FastAPI application and endpoints
│   ├── core/          # Core download engine
│   ├── extractors/    # Platform-specific extractors
│   ├── network/       # Network layer
│   └── utils/         # Utility functions
├── tests/             # Unit and integration tests
├── docs/              # API documentation
└── requirements.txt   # Dependencies
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and personal use only. Please respect copyright laws and the terms of service of the platforms you download from. The developers are not responsible for any misuse of this software.
