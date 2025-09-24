"""
YouTube extractor for Andalus Downloader Backend API
"""
import re
import yt_dlp
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse, parse_qs

from .base import PlatformExtractor
from ..core.models import VideoMetadata, FormatInfo, Platform
from ..utils.logger import get_logger

logger = get_logger()


class YouTubeExtractor(PlatformExtractor):
    """YouTube platform extractor using yt-dlp"""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "youtube"
        self.supported_domains = [
            "youtube.com", "www.youtube.com", "m.youtube.com",
            "youtu.be", "www.youtu.be"
        ]
        self.url_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]+)',
            r'(?:https?://)?youtu\.be/([a-zA-Z0-9_-]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)'
        ]
        
        # yt-dlp configuration
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extractaudio': False,
            'format': 'best',
            'noplaylist': False,  # We'll handle playlists
        }
    
    def detect_platform(self, url: str) -> bool:
        """Check if URL is from YouTube"""
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
        """Extract metadata from YouTube URL"""
        try:
            clean_url = self._clean_url(url)
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=False)
                
                # Handle playlist
                if 'entries' in info:
                    # This is a playlist, return first video metadata
                    if info['entries']:
                        first_entry = info['entries'][0]
                        return self._convert_to_metadata(first_entry, is_playlist=True, 
                                                       playlist_count=len(info['entries']))
                    else:
                        raise Exception("Empty playlist")
                else:
                    # Single video
                    return self._convert_to_metadata(info)
        
        except Exception as e:
            logger.error(f"Failed to extract YouTube metadata from {url}: {e}")
            raise Exception(f"Failed to extract metadata: {str(e)}")
    
    async def get_download_urls(self, url: str, quality: Optional[str] = None) -> List[FormatInfo]:
        """Get available download formats from YouTube"""
        try:
            clean_url = self._clean_url(url)
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=False)
                
                # Handle playlist - get first video formats
                if 'entries' in info and info['entries']:
                    info = info['entries'][0]
                
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
            logger.error(f"Failed to get YouTube formats from {url}: {e}")
            raise Exception(f"Failed to get formats: {str(e)}")
    
    async def supports_playlists(self) -> bool:
        """YouTube supports playlists"""
        return True
    
    async def is_playlist_url(self, url: str) -> bool:
        """Check if URL is a YouTube playlist"""
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            return 'list' in query_params
        except:
            return False
    
    async def extract_playlist(self, url: str) -> List[Dict[str, Any]]:
        """Extract playlist information from YouTube"""
        try:
            clean_url = self._clean_url(url)
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=False)
                
                if 'entries' not in info:
                    return []
                
                playlist_items = []
                for entry in info['entries']:
                    if entry:  # Some entries might be None
                        item = {
                            'id': entry.get('id'),
                            'title': entry.get('title'),
                            'url': entry.get('webpage_url'),
                            'duration': entry.get('duration'),
                            'thumbnail': entry.get('thumbnail'),
                            'uploader': entry.get('uploader'),
                            'view_count': entry.get('view_count')
                        }
                        playlist_items.append(item)
                
                return playlist_items
        
        except Exception as e:
            logger.error(f"Failed to extract YouTube playlist from {url}: {e}")
            return []
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _convert_to_metadata(self, info: Dict[str, Any], is_playlist: bool = False, 
                           playlist_count: Optional[int] = None) -> VideoMetadata:
        """Convert yt-dlp info to VideoMetadata"""
        # Ensure upload_date is a string, not datetime
        upload_date = info.get('upload_date')
        if upload_date and not isinstance(upload_date, str):
            upload_date = str(upload_date)
            
        return VideoMetadata(
            title=info.get('title'),
            description=info.get('description'),
            duration=info.get('duration'),
            thumbnail_url=info.get('thumbnail'),
            uploader=info.get('uploader') or info.get('channel'),
            upload_date=upload_date,
            view_count=info.get('view_count'),
            like_count=info.get('like_count'),
            platform=Platform.YOUTUBE,
            is_live=info.get('is_live', False),
            is_playlist=is_playlist,
            playlist_count=playlist_count
        )
