"""
Vimeo extractor for Andalus Downloader Backend API
"""
import re
import yt_dlp
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

from .base import PlatformExtractor
from ..core.models import VideoMetadata, FormatInfo, Platform
from ..utils.logger import get_logger

logger = get_logger()


class VimeoExtractor(PlatformExtractor):
    """Vimeo platform extractor using yt-dlp"""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "vimeo"
        self.supported_domains = [
            "vimeo.com", "www.vimeo.com", "player.vimeo.com"
        ]
        self.url_patterns = [
            r'(?:https?://)?(?:www\.)?vimeo\.com/(\d+)',
            r'(?:https?://)?player\.vimeo\.com/video/(\d+)',
        ]
        
        # yt-dlp configuration for Vimeo
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extractaudio': False,
            'format': 'best',
            'noplaylist': True,
            'no_check_certificate': True,
            'geo_bypass': True,
            'socket_timeout': 30,
            'retries': 3,
        }
    
    def detect_platform(self, url: str) -> bool:
        """Check if URL is from Vimeo"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain in self.supported_domains
        except:
            return False
    
    async def extract_metadata(self, url: str) -> VideoMetadata:
        """Extract metadata from Vimeo URL"""
        try:
            clean_url = self._clean_url(url)
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=False)
                return self._convert_to_metadata(info)
        
        except Exception as e:
            logger.error(f"Failed to extract Vimeo metadata from {url}: {e}")
            raise Exception(f"Failed to extract metadata: {str(e)}")
    
    async def get_download_urls(self, url: str, quality: Optional[str] = None) -> List[FormatInfo]:
        """Get available download formats from Vimeo"""
        try:
            clean_url = self._clean_url(url)
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=False)
                
                formats = []
                if 'formats' in info:
                    for fmt in info['formats']:
                        format_info = FormatInfo(
                            format_id=fmt.get('format_id', ''),
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
                
                return formats
        
        except Exception as e:
            logger.error(f"Failed to get Vimeo formats from {url}: {e}")
            raise Exception(f"Failed to get formats: {str(e)}")
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract Vimeo video ID from URL"""
        patterns = [
            r'vimeo\.com/(\d+)',
            r'player\.vimeo\.com/video/(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _convert_to_metadata(self, info: Dict[str, Any]) -> VideoMetadata:
        """Convert yt-dlp info to VideoMetadata"""
        return VideoMetadata(
            title=info.get('title'),
            description=info.get('description'),
            duration=info.get('duration'),
            thumbnail_url=info.get('thumbnail'),
            uploader=info.get('uploader') or info.get('channel'),
            upload_date=info.get('upload_date'),
            view_count=info.get('view_count'),
            like_count=info.get('like_count'),
            platform=Platform.VIMEO,
            is_live=info.get('is_live', False),
            is_playlist=False
        )
