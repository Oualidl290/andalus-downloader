"""
SoundCloud extractor for Andalus Downloader Backend API
"""
import re
import yt_dlp
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

from .base import PlatformExtractor
from ..core.models import VideoMetadata, FormatInfo, Platform
from ..utils.logger import get_logger

logger = get_logger()


class SoundCloudExtractor(PlatformExtractor):
    """SoundCloud platform extractor using yt-dlp"""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "soundcloud"
        self.supported_domains = [
            "soundcloud.com", "www.soundcloud.com", "m.soundcloud.com"
        ]
        self.url_patterns = [
            r'(?:https?://)?(?:www\.)?soundcloud\.com/[\w-]+/[\w-]+',
            r'(?:https?://)?(?:www\.)?soundcloud\.com/[\w-]+/sets/[\w-]+',
        ]
        
        # yt-dlp configuration for SoundCloud
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extractaudio': False,
            'format': 'best',
            'noplaylist': False,  # SoundCloud supports playlists
            'no_check_certificate': True,
            'geo_bypass': True,
            'socket_timeout': 30,
            'retries': 3,
        }
    
    def detect_platform(self, url: str) -> bool:
        """Check if URL is from SoundCloud"""
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
        """Extract metadata from SoundCloud URL"""
        try:
            clean_url = self._clean_url(url)
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=False)
                
                # Handle playlist
                if 'entries' in info:
                    # This is a playlist, return first track metadata
                    if info['entries']:
                        first_entry = info['entries'][0]
                        return self._convert_to_metadata(first_entry, is_playlist=True, 
                                                       playlist_count=len(info['entries']))
                    else:
                        raise Exception("Empty playlist")
                else:
                    # Single track
                    return self._convert_to_metadata(info)
        
        except Exception as e:
            logger.error(f"Failed to extract SoundCloud metadata from {url}: {e}")
            raise Exception(f"Failed to extract metadata: {str(e)}")
    
    async def get_download_urls(self, url: str, quality: Optional[str] = None) -> List[FormatInfo]:
        """Get available download formats from SoundCloud"""
        try:
            clean_url = self._clean_url(url)
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=False)
                
                # Handle playlist - get first track formats
                if 'entries' in info and info['entries']:
                    info = info['entries'][0]
                
                formats = []
                if 'formats' in info:
                    for fmt in info['formats']:
                        format_info = FormatInfo(
                            format_id=fmt.get('format_id', ''),
                            ext=fmt.get('ext', 'mp3'),
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
                        format_id='soundcloud',
                        ext='mp3',
                        quality='best',
                        acodec='mp3',
                        tbr=info.get('tbr'),
                        abr=info.get('abr')
                    )
                    formats.append(format_info)
                
                return formats
        
        except Exception as e:
            logger.error(f"Failed to get SoundCloud formats from {url}: {e}")
            raise Exception(f"Failed to get formats: {str(e)}")
    
    async def supports_playlists(self) -> bool:
        """SoundCloud supports playlists"""
        return True
    
    async def is_playlist_url(self, url: str) -> bool:
        """Check if URL is a SoundCloud playlist"""
        try:
            return '/sets/' in url
        except:
            return False
    
    async def extract_playlist(self, url: str) -> List[Dict[str, Any]]:
        """Extract playlist information from SoundCloud"""
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
            logger.error(f"Failed to extract SoundCloud playlist from {url}: {e}")
            return []
    
    def _convert_to_metadata(self, info: Dict[str, Any], is_playlist: bool = False, 
                           playlist_count: Optional[int] = None) -> VideoMetadata:
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
            platform=Platform.SOUNDCLOUD,
            is_live=info.get('is_live', False),
            is_playlist=is_playlist,
            playlist_count=playlist_count
        )
