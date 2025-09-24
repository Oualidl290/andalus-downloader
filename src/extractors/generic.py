"""
Generic extractor for direct media URLs and unknown platforms
"""
import re
import yt_dlp
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

from .base import PlatformExtractor
from ..core.models import VideoMetadata, FormatInfo, Platform
from ..utils.logger import get_logger

logger = get_logger()


class GenericExtractor(PlatformExtractor):
    """Generic extractor for direct media URLs and fallback"""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "generic"
        self.supported_domains = []  # Supports any domain as fallback
        
        # Common media file extensions
        self.media_extensions = {
            'video': ['mp4', 'avi', 'mkv', 'webm', 'mov', 'flv', 'm4v', '3gp'],
            'audio': ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'wma']
        }
        
        # yt-dlp configuration for universal extraction
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extractaudio': False,
            'format': 'best/bestvideo+bestaudio/best',
            'noplaylist': True,
            'extract_flat': False,
            'no_check_certificate': True,
            'ignoreerrors': False,
            'geo_bypass': True,
            'age_limit': None,
            'socket_timeout': 30,
            'retries': 3,
            'fragment_retries': 3,
        }
    
    def detect_platform(self, url: str) -> bool:
        """Generic extractor accepts any URL as fallback"""
        return self._validate_url(url)
    
    async def extract_metadata(self, url: str) -> VideoMetadata:
        """Extract metadata using yt-dlp generic extractor"""
        try:
            # Check if it's a direct media URL first
            if self._is_direct_media_url(url):
                return await self._extract_direct_media_metadata(url)
            
            # Try yt-dlp generic extraction
            clean_url = self._clean_url(url)
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(clean_url, download=False)
                    return self._convert_to_metadata(info)
                except Exception as e:
                    logger.warning(f"yt-dlp generic extraction failed for {url}: {e}")
                    # Fallback to basic metadata
                    return await self._extract_basic_metadata(url)
        
        except Exception as e:
            logger.error(f"Failed to extract generic metadata from {url}: {e}")
            raise Exception(f"Failed to extract metadata: {str(e)}")
    
    async def get_download_urls(self, url: str, quality: Optional[str] = None) -> List[FormatInfo]:
        """Get available download formats"""
        try:
            # For direct media URLs, return the URL itself
            if self._is_direct_media_url(url):
                return await self._get_direct_media_formats(url)
            
            # Try yt-dlp generic extraction
            clean_url = self._clean_url(url)
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=False)
                
                formats = []
                if 'formats' in info:
                    for fmt in info['formats']:
                        format_info = FormatInfo(
                            format_id=fmt.get('format_id', 'generic'),
                            ext=fmt.get('ext', 'mp4'),
                            quality=fmt.get('quality'),
                            resolution=fmt.get('resolution'),
                            fps=fmt.get('fps'),
                            vcodec=fmt.get('vcodec'),
                            acodec=fmt.get('acodec'),
                            filesize=fmt.get('filesize'),
                            filesize_approx=fmt.get('filesize_approx'),
                            tbr=fmt.get('tbr'),
                            vbr=fmt.get('vbr'),
                            abr=fmt.get('abr')
                        )
                        formats.append(format_info)
                elif 'url' in info:
                    # Single format
                    format_info = FormatInfo(
                        format_id='generic',
                        ext=info.get('ext', 'mp4'),
                        quality=info.get('quality'),
                        resolution=info.get('resolution'),
                        filesize=info.get('filesize'),
                        tbr=info.get('tbr')
                    )
                    formats.append(format_info)
                
                return formats
        
        except Exception as e:
            logger.error(f"Failed to get generic formats from {url}: {e}")
            # Return basic format info as fallback
            return [FormatInfo(format_id='generic', ext='mp4')]
    
    def _is_direct_media_url(self, url: str) -> bool:
        """Check if URL points directly to a media file"""
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            # Check file extension
            for ext_list in self.media_extensions.values():
                for ext in ext_list:
                    if path.endswith(f'.{ext}'):
                        return True
            
            return False
        except:
            return False
    
    async def _extract_direct_media_metadata(self, url: str) -> VideoMetadata:
        """Extract metadata for direct media URLs"""
        try:
            parsed = urlparse(url)
            filename = parsed.path.split('/')[-1] if parsed.path else 'media'
            
            # Determine if it's audio or video
            is_audio = any(filename.lower().endswith(f'.{ext}') 
                          for ext in self.media_extensions['audio'])
            
            return VideoMetadata(
                title=filename,
                description=f"Direct media file from {parsed.netloc}",
                platform=Platform.GENERIC,
                thumbnail_url=None,
                uploader=parsed.netloc,
                is_live=False,
                is_playlist=False
            )
        except Exception as e:
            logger.error(f"Failed to extract direct media metadata: {e}")
            return VideoMetadata(
                title="Unknown Media",
                platform=Platform.GENERIC
            )
    
    async def _extract_basic_metadata(self, url: str) -> VideoMetadata:
        """Extract basic metadata when other methods fail"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            
            return VideoMetadata(
                title=f"Media from {domain}",
                description=f"Content from {url}",
                platform=Platform.GENERIC,
                uploader=domain,
                is_live=False,
                is_playlist=False
            )
        except:
            return VideoMetadata(
                title="Unknown Media",
                platform=Platform.GENERIC
            )
    
    async def _get_direct_media_formats(self, url: str) -> List[FormatInfo]:
        """Get format info for direct media URLs"""
        try:
            parsed = urlparse(url)
            filename = parsed.path.split('/')[-1] if parsed.path else 'media'
            
            # Extract extension
            ext = 'mp4'  # default
            if '.' in filename:
                ext = filename.split('.')[-1].lower()
            
            return [FormatInfo(
                format_id='direct',
                ext=ext,
                quality='unknown'
            )]
        except:
            return [FormatInfo(format_id='direct', ext='mp4')]
    
    def _convert_to_metadata(self, info: Dict[str, Any]) -> VideoMetadata:
        """Convert yt-dlp info to VideoMetadata"""
        # Ensure upload_date is a string, not datetime
        upload_date = info.get('upload_date')
        if upload_date and not isinstance(upload_date, str):
            upload_date = str(upload_date)
            
        return VideoMetadata(
            title=info.get('title', 'Unknown Title'),
            description=info.get('description'),
            duration=info.get('duration'),
            thumbnail_url=info.get('thumbnail'),
            uploader=info.get('uploader') or info.get('channel'),
            upload_date=upload_date,
            view_count=info.get('view_count'),
            like_count=info.get('like_count'),
            platform=Platform.GENERIC,
            is_live=info.get('is_live', False),
            is_playlist=False
        )
