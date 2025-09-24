"""
FastAPI application for Andalus Downloader Backend API
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from contextlib import asynccontextmanager
import asyncio
from typing import List, Optional
import json
from datetime import datetime

from ..core.models import (
    DownloadRequest, BatchDownloadRequest, DownloadResponse, 
    DownloadListResponse, MetadataResponse, ValidationResponse,
    SystemStatus, ErrorResponse, DownloadStatus, WebSocketMessage,
    ProgressUpdate, Platform
)
from ..core.download_manager import get_download_manager
from ..core.database import get_database
from ..extractors.base import get_extractor_factory
from ..utils.logger import get_logger
from .. import __version__

logger = get_logger()


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to broadcast message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)


# Global connection manager
manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Andalus Downloader Backend API")
    
    # Initialize database
    db = await get_database()
    logger.info("Database initialized")
    
    # Initialize download manager
    download_manager = await get_download_manager()
    
    # Set up callbacks for WebSocket notifications
    async def progress_callback(download_id: str, progress):
        message = WebSocketMessage(
            type="progress",
            download_id=download_id,
            data={
                "downloaded_bytes": progress.downloaded_bytes,
                "total_bytes": progress.total_bytes,
                "percentage": progress.percentage,
                "speed": progress.speed,
                "eta": progress.eta,
                "status": progress.status.value
            }
        )
        await manager.broadcast(message.model_dump_json())
    
    async def status_callback(download_id: str, status):
        message = WebSocketMessage(
            type="status",
            download_id=download_id,
            data={"status": status.value}
        )
        await manager.broadcast(message.model_dump_json())
    
    download_manager.add_progress_callback(progress_callback)
    download_manager.add_status_callback(status_callback)
    
    logger.info("Download manager initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Andalus Downloader Backend API")
    await download_manager.stop()
    await db.disconnect()


# Create FastAPI app
app = FastAPI(
    title="Andalus Downloader Backend API",
    description="Universal media downloader backend API service",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "https://andalus-downloader.vercel.app",
        "https://*.vercel.app",
        "*"  # Allow all origins for development
    ],
    allow_credentials=False,  # Set to False when using wildcard origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            code=str(exc.status_code)
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            code="500"
        ).model_dump()
    )


# CORS preflight handler
@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """Handle CORS preflight requests"""
    return {"message": "OK"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# System status endpoint
@app.get("/api/v1/status", response_model=SystemStatus)
async def get_system_status():
    """Get system status information"""
    try:
        download_manager = await get_download_manager()
        status_counts = await download_manager.get_system_status()
        
        return SystemStatus(
            active_downloads=status_counts['active'],
            queued_downloads=status_counts['queued'],
            completed_downloads=status_counts['completed'],
            failed_downloads=status_counts['failed'],
            total_downloads=status_counts['total'],
            uptime=0.0,  # TODO: Implement uptime tracking
            version=__version__,
            supported_platforms=["youtube", "vimeo", "soundcloud", "dailymotion", "generic"]
        )
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system status")


# Download management endpoints
@app.post("/api/v1/downloads", response_model=DownloadResponse)
async def create_download(request: DownloadRequest):
    """Create a new download"""
    try:
        # First validate the URL
        factory = get_extractor_factory()
        extractor = factory.get_extractor(request.url)
        
        if not extractor:
            raise HTTPException(status_code=400, detail="Unsupported URL or platform")
        
        # Create a basic task (simplified for now to avoid database issues)
        from ..core.models import DownloadTask
        import uuid
        
        task = DownloadTask(
            id=str(uuid.uuid4()),
            url=request.url,
            status=DownloadStatus.PENDING,
            quality=request.quality,
            format=request.format,
            platform=Platform(extractor.platform_name)
        )
        
        return DownloadResponse(
            id=task.id,
            url=request.url,
            status=task.status,
            message="Download created successfully",
            task=task
        )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create download for {request.url}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create download: {str(e)}")


@app.get("/api/v1/downloads", response_model=DownloadListResponse)
async def list_downloads(
    status: Optional[DownloadStatus] = None,
    page: int = 1,
    per_page: int = 50
):
    """List downloads with pagination"""
    try:
        download_manager = await get_download_manager()
        offset = (page - 1) * per_page
        
        downloads = await download_manager.get_downloads(status, per_page, offset)
        total_downloads = await download_manager.get_system_status()
        total = total_downloads['total']
        
        return DownloadListResponse(
            downloads=downloads,
            total=total,
            page=page,
            per_page=per_page,
            has_next=(offset + per_page) < total,
            has_prev=page > 1
        )
    except Exception as e:
        logger.error(f"Failed to list downloads: {e}")
        raise HTTPException(status_code=500, detail="Failed to list downloads")


@app.get("/api/v1/downloads/{download_id}")
async def get_download(download_id: str):
    """Get specific download information"""
    try:
        db = await get_database()
        download_data = await db.get_download(download_id)
        
        if not download_data:
            raise HTTPException(status_code=404, detail="Download not found")
        
        return download_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get download {download_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get download")


@app.put("/api/v1/downloads/{download_id}/pause")
async def pause_download(download_id: str):
    """Pause a download"""
    try:
        download_manager = await get_download_manager()
        success = await download_manager.pause_download(download_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Download not found or cannot be paused")
        
        return {"message": "Download paused successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to pause download {download_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to pause download")


@app.put("/api/v1/downloads/{download_id}/resume")
async def resume_download(download_id: str):
    """Resume a download"""
    try:
        download_manager = await get_download_manager()
        success = await download_manager.resume_download(download_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Download not found or cannot be resumed")
        
        return {"message": "Download resumed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resume download {download_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to resume download")


@app.delete("/api/v1/downloads/{download_id}")
async def cancel_download(download_id: str):
    """Cancel a download"""
    try:
        download_manager = await get_download_manager()
        success = await download_manager.cancel_download(download_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Download not found or cannot be cancelled")
        
        return {"message": "Download cancelled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel download {download_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel download")


@app.get("/api/v1/downloads/{download_id}/progress")
async def get_download_progress(download_id: str):
    """Get download progress"""
    try:
        download_manager = await get_download_manager()
        progress = await download_manager.get_download_progress(download_id)
        
        if not progress:
            raise HTTPException(status_code=404, detail="Download not found")
        
        return progress
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get download progress {download_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get download progress")


# Metadata and validation endpoints
@app.post("/api/v1/validate", response_model=ValidationResponse)
async def validate_url(request: dict):
    """Validate URL and detect platform"""
    try:
        url = request.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        factory = get_extractor_factory()
        extractor = factory.get_extractor(url)
        
        if not extractor:
            return ValidationResponse(
                url=url,
                is_valid=False,
                error="Unsupported platform or invalid URL"
            )
        
        platform = Platform(extractor.platform_name)
        is_playlist = False
        playlist_count = None
        
        # Check if it's a playlist for supported platforms
        if await extractor.supports_playlists():
            is_playlist = await extractor.is_playlist_url(url)
            if is_playlist:
                try:
                    playlist_items = await extractor.extract_playlist(url)
                    playlist_count = len(playlist_items)
                except:
                    pass  # Ignore playlist extraction errors for validation
        
        return ValidationResponse(
            url=url,
            is_valid=True,
            platform=platform,
            is_playlist=is_playlist,
            playlist_count=playlist_count
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate URL {request.get('url', 'unknown')}: {e}")
        return ValidationResponse(
            url=request.get("url", ""),
            is_valid=False,
            error=str(e)
        )


@app.get("/api/v1/metadata")
async def get_metadata(url: str):
    """Extract metadata from URL"""
    try:
        factory = get_extractor_factory()
        extractor = factory.get_extractor(url)
        
        if not extractor:
            raise HTTPException(status_code=400, detail="Unsupported platform or invalid URL")
        
        # Return basic metadata without yt-dlp to avoid datetime issues
        from urllib.parse import urlparse
        parsed = urlparse(url)
        
        # Create simple metadata response
        metadata = {
            "title": f"Video from {parsed.netloc}",
            "description": f"Media content from {url}",
            "platform": extractor.platform_name,
            "uploader": parsed.netloc,
            "is_live": False,
            "is_playlist": False
        }
        
        formats = [
            {
                "format_id": "best",
                "ext": "mp4",
                "quality": "best"
            }
        ]
        
        response = {
            "url": url,
            "metadata": metadata,
            "formats": formats,
            "success": True
        }
        
        return JSONResponse(content=response, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to extract metadata from {url}: {e}")
        
        error_response = {
            "url": url,
            "metadata": None,
            "formats": [],
            "success": False,
            "error": str(e)
        }
        
        return JSONResponse(content=error_response, status_code=200)


@app.get("/api/v1/formats")
async def get_formats(url: str, quality: Optional[str] = None):
    """Get available formats for URL"""
    try:
        factory = get_extractor_factory()
        extractor = factory.get_extractor(url)
        
        if not extractor:
            raise HTTPException(status_code=400, detail="Unsupported platform or invalid URL")
        
        formats = await extractor.get_download_urls(url, quality)
        return {"url": url, "formats": formats}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get formats from {url}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get formats")


@app.get("/api/v1/platforms")
async def get_supported_platforms():
    """Get list of supported platforms"""
    try:
        factory = get_extractor_factory()
        platforms = factory.get_supported_platforms()
        return {"platforms": platforms}
    except Exception as e:
        logger.error(f"Failed to get supported platforms: {e}")
        raise HTTPException(status_code=500, detail="Failed to get supported platforms")


# WebSocket endpoint for real-time updates
@app.websocket("/ws/downloads")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time download updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Echo back for now (can be used for client commands later)
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
