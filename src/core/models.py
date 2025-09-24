"""
Data models for Andalus Downloader Backend API
"""
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class DownloadStatus(str, Enum):
    """Download status enumeration"""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Platform(str, Enum):
    """Supported platforms"""
    YOUTUBE = "youtube"
    VIMEO = "vimeo"
    SOUNDCLOUD = "soundcloud"
    DAILYMOTION = "dailymotion"
    GENERIC = "generic"


class VideoQuality(str, Enum):
    """Video quality options"""
    BEST = "best"
    WORST = "worst"
    Q_2160P = "2160p"
    Q_1440P = "1440p"
    Q_1080P = "1080p"
    Q_720P = "720p"
    Q_480P = "480p"
    Q_360P = "360p"
    Q_240P = "240p"
    Q_144P = "144p"
    AUDIO_ONLY = "audio_only"


class VideoFormat(str, Enum):
    """Video format options"""
    MP4 = "mp4"
    WEBM = "webm"
    MKV = "mkv"
    AVI = "avi"
    MOV = "mov"
    FLV = "flv"


class AudioFormat(str, Enum):
    """Audio format options"""
    MP3 = "mp3"
    AAC = "aac"
    OGG = "ogg"
    WAV = "wav"
    FLAC = "flac"
    M4A = "m4a"


# Request Models
class DownloadRequest(BaseModel):
    """Request model for creating a new download"""
    url: str = Field(..., description="URL to download")
    quality: Optional[VideoQuality] = Field(VideoQuality.BEST, description="Video quality preference")
    format: Optional[str] = Field(None, description="Output format (mp4, mp3, etc.)")
    output_path: Optional[str] = Field(None, description="Custom output directory")
    filename_template: Optional[str] = Field(None, description="Custom filename template")
    extract_audio: bool = Field(False, description="Extract audio only")
    download_subtitles: bool = Field(False, description="Download subtitles if available")


class BatchDownloadRequest(BaseModel):
    """Request model for batch downloads"""
    urls: List[str] = Field(..., description="List of URLs to download")
    quality: Optional[VideoQuality] = Field(VideoQuality.BEST, description="Video quality preference")
    format: Optional[str] = Field(None, description="Output format")
    output_path: Optional[str] = Field(None, description="Custom output directory")
    extract_audio: bool = Field(False, description="Extract audio only")


class DownloadControlRequest(BaseModel):
    """Request model for download control operations"""
    action: str = Field(..., description="Action to perform (pause, resume, cancel)")


# Response Models
class VideoMetadata(BaseModel):
    """Video metadata information"""
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None  # Duration in seconds
    thumbnail_url: Optional[str] = None
    uploader: Optional[str] = None
    upload_date: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    platform: Optional[Platform] = None
    is_live: bool = False
    is_playlist: bool = False
    playlist_count: Optional[int] = None
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class FormatInfo(BaseModel):
    """Format information for a video/audio"""
    format_id: str
    ext: str
    quality: Optional[str] = None
    resolution: Optional[str] = None
    fps: Optional[int] = None
    vcodec: Optional[str] = None
    acodec: Optional[str] = None
    filesize: Optional[int] = None
    filesize_approx: Optional[int] = None
    tbr: Optional[float] = None  # Total bitrate
    vbr: Optional[float] = None  # Video bitrate
    abr: Optional[float] = None  # Audio bitrate


class DownloadProgress(BaseModel):
    """Download progress information"""
    downloaded_bytes: int = 0
    total_bytes: Optional[int] = None
    speed: Optional[float] = None  # Bytes per second
    eta: Optional[int] = None  # Estimated time remaining in seconds
    percentage: float = 0.0
    status: DownloadStatus = DownloadStatus.PENDING


class DownloadTask(BaseModel):
    """Download task model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str
    title: Optional[str] = None
    platform: Optional[Platform] = None
    status: DownloadStatus = DownloadStatus.PENDING
    progress: float = 0.0
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    downloaded_size: int = 0
    format: Optional[str] = None
    quality: Optional[VideoQuality] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class DownloadResponse(BaseModel):
    """Response model for download operations"""
    id: str
    url: str
    status: DownloadStatus
    message: str
    task: Optional[DownloadTask] = None


class DownloadListResponse(BaseModel):
    """Response model for listing downloads"""
    downloads: List[DownloadTask]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class MetadataResponse(BaseModel):
    """Response model for metadata extraction"""
    url: str
    metadata: VideoMetadata
    formats: List[FormatInfo]
    success: bool
    error: Optional[str] = None


class ValidationResponse(BaseModel):
    """Response model for URL validation"""
    url: str
    is_valid: bool
    platform: Optional[Platform] = None
    is_playlist: bool = False
    playlist_count: Optional[int] = None
    error: Optional[str] = None


class SystemStatus(BaseModel):
    """System status information"""
    active_downloads: int
    queued_downloads: int
    completed_downloads: int
    failed_downloads: int
    total_downloads: int
    uptime: float  # Uptime in seconds
    version: str
    supported_platforms: List[Platform]


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# WebSocket Models
class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    type: str  # progress, status, error, etc.
    download_id: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ProgressUpdate(BaseModel):
    """Progress update for WebSocket"""
    download_id: str
    progress: DownloadProgress
    timestamp: datetime = Field(default_factory=datetime.utcnow)
