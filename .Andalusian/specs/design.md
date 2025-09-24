# Andalus Downloader - System Design Document

## Architecture Overview
Andalus Downloader follows a modular backend API architecture with clear separation between the REST API layer, business logic, and platform-specific implementations. The system is designed for extensibility, maintainability, and cross-platform compatibility with frontend integration capabilities.

### High-Level Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   REST API      │    │  Core Engine    │    │   Platform      │
│                 │    │                 │    │   Extractors    │
│  - Endpoints    │◄──►│  - Download Mgr │◄──►│                 │
│  - WebSocket    │    │  - Queue Mgr    │    │  - YouTube      │
│  - Validation   │    │  - Format Mgr   │    │  - Vimeo        │
│  - Auth         │    │  - Error Handler│    │  - SoundCloud   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Configuration │    │   File System   │    │   Network       │
{{ ... }}

### Component Specifications

### 1. REST API Layer

#### RESTful API Endpoints (Primary)
- **Framework**: FastAPI or Flask with async support
- **Design**: OpenAPI/Swagger documentation, JSON responses
- **Key Endpoints**:
  - `/api/v1/downloads` - Download management
  - `/api/v1/queue` - Queue operations
  - `/api/v1/metadata` - Video/audio information
  - `/api/v1/platforms` - Supported platforms
  - `/api/v1/status` - System status

#### WebSocket Interface (Real-time)
- **Purpose**: Real-time progress updates and notifications
- **Features**: Live download progress, queue updates, error notifications

#### Frontend Integration (Coming Soon)
- **Next.js Frontend**: Modern React-based interface
- **API Integration**: Seamless backend-frontend communication

### 2. Core Engine
  - queue: DownloadQueue
  - active_downloads: Dict[str, DownloadTask]
  - max_concurrent: int
  
  + add_download(url, options)
  + pause_download(task_id)
  + resume_download(task_id)
  + cancel_download(task_id)
  + get_progress(task_id)
```

#### Queue Manager
- **Persistent Queue**: SQLite-based task storage
- **Priority System**: User-defined download priorities
- **State Management**: Track download states (pending, active, paused, completed, failed)
- **Recovery**: Resume interrupted downloads on restart

#### Format Manager
- **Conversion Engine**: FFmpeg integration for format conversion
- **Quality Selection**: Automatic best quality detection
- **Codec Support**: Hardware acceleration when available
- **Metadata Preservation**: Title, artist, thumbnail embedding

### 3. Platform Extractors

#### Abstract Extractor Interface
```
abstract class PlatformExtractor:
  + detect_platform(url: str) -> bool
  + extract_metadata(url: str) -> VideoInfo
  + get_download_urls(url: str, quality: str) -> List[DownloadURL]
  + supports_playlists() -> bool
  + extract_playlist(url: str) -> List[VideoInfo]
```

#### Supported Platforms
- **YouTube**: Primary platform, full feature support
- **Vimeo**: Video downloads, privacy-aware
- **SoundCloud**: Audio-focused extraction
- **Dailymotion**: European video platform
- **Generic Extractor**: Fallback for unknown platforms

### 4. Network Layer

#### HTTP Client
- **Connection Pooling**: Reuse connections for efficiency
- **User Agent Management**: Rotate user agents to avoid blocking
- **Cookie Support**: Session management for authenticated content
- **Proxy Support**: SOCKS/HTTP proxy configuration

#### Rate Limiting
- **Platform-Specific**: Respect individual platform limits
- **Adaptive Throttling**: Slow down on rate limit detection
- **Concurrent Limits**: Prevent overwhelming servers

## Data Flow Architecture

### Download Process Flow
```
1. URL Input → Platform Detection
2. Metadata Extraction → Quality Selection
3. Queue Addition → Download Initiation
4. Network Request → Progress Tracking
5. File Writing → Format Conversion (if needed)
6. Metadata Embedding → Completion Notification
```

### Error Recovery Flow
```
1. Error Detection → Error Classification
2. Retry Logic → Exponential Backoff
3. Platform Update Check → Fallback Options
4. User Notification → Manual Intervention Options
```

## Database Schema

### Downloads Table
```sql
CREATE TABLE downloads (
    id TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    title TEXT,
    platform TEXT,
    status TEXT, -- pending, downloading, completed, failed, paused
    progress REAL DEFAULT 0,
    file_path TEXT,
    format TEXT,
    quality TEXT,
    created_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);
```

### Configuration Table
```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    category TEXT -- ui, download, network, platform
);
```

## Security Considerations

### Input Validation
- **URL Sanitization**: Prevent injection attacks through malformed URLs
- **File Path Validation**: Ensure safe file system operations
- **Platform Verification**: Validate platform responses

### Network Security
- **TLS Verification**: Enforce secure connections
- **Certificate Pinning**: For critical platform connections
- **Content Validation**: Verify downloaded content integrity

## Performance Optimization

### Caching Strategy
- **Metadata Caching**: Cache video information for repeated requests
- **Platform Response Caching**: Reduce API calls
- **Thumbnail Caching**: Local storage for preview images

### Resource Management
- **Memory Usage**: Stream large downloads to disk
- **CPU Optimization**: Efficient format conversion
- **Disk I/O**: Minimize temporary file creation

## Monitoring & Logging

### Application Metrics
- Download success/failure rates
- Average download speeds
- Platform extraction success rates
- Error frequency and types

### User Analytics (Optional)
- Feature usage patterns (anonymized)
- Performance metrics
- Platform popularity statistics

## Deployment Architecture

### Desktop Distribution
- **Installers**: Platform-specific installers (MSI, DMG, DEB)
- **Portable Version**: Self-contained executable
- **Auto-Updates**: Silent update mechanism

### Configuration Management
- **User Settings**: Local configuration files
- **Platform Configs**: Updateable extraction rules
- **Theme Support**: Customizable UI themes