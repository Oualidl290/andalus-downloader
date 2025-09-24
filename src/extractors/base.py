"""
Base platform extractor interface for Andalus Downloader Backend API
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import re
from urllib.parse import urlparse

from ..core.models import VideoMetadata, FormatInfo, Platform
from ..utils.logger import get_logger

logger = get_logger()


class PlatformExtractor(ABC):
    """Abstract base class for platform-specific extractors"""
    
    def __init__(self):
        self.platform_name: str = "unknown"
        self.supported_domains: List[str] = []
        self.url_patterns: List[str] = []
    
    @abstractmethod
    async def extract_metadata(self, url: str) -> VideoMetadata:
        """Extract metadata from a URL"""
        pass
    
    @abstractmethod
    async def get_download_urls(self, url: str, quality: Optional[str] = None) -> List[FormatInfo]:
        """Get available download URLs and formats"""
        pass
    
    @abstractmethod
    def detect_platform(self, url: str) -> bool:
        """Check if this extractor can handle the given URL"""
        pass
    
    async def supports_playlists(self) -> bool:
        """Check if this platform supports playlist extraction"""
        return False
    
    async def extract_playlist(self, url: str) -> List[Dict[str, Any]]:
        """Extract playlist information (override if supported)"""
        return []
    
    async def is_playlist_url(self, url: str) -> bool:
        """Check if URL is a playlist"""
        return False
    
    def _clean_url(self, url: str) -> str:
        """Clean and normalize URL"""
        # Remove tracking parameters and fragments
        parsed = urlparse(url)
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # Keep essential query parameters only
        if parsed.query:
            essential_params = []
            for param in parsed.query.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    # Keep video ID and essential parameters
                    if key.lower() in ['v', 'id', 'video_id', 'list', 'playlist']:
                        essential_params.append(param)
            
            if essential_params:
                clean_url += '?' + '&'.join(essential_params)
        
        return clean_url
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from URL (platform-specific implementation)"""
        return None
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except:
            return False


class ExtractorFactory:
    """Factory for creating platform-specific extractors"""
    
    def __init__(self):
        self.extractors: List[PlatformExtractor] = []
        self.domain_map: Dict[str, PlatformExtractor] = {}
    
    def register_extractor(self, extractor: PlatformExtractor) -> None:
        """Register a platform extractor"""
        self.extractors.append(extractor)
        
        # Map domains to extractor
        for domain in extractor.supported_domains:
            self.domain_map[domain.lower()] = extractor
        
        logger.info(f"Registered extractor for {extractor.platform_name}")
    
    def get_extractor(self, url: str) -> Optional[PlatformExtractor]:
        """Get appropriate extractor for URL"""
        try:
            # First try domain-based lookup
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            if domain in self.domain_map:
                return self.domain_map[domain]
            
            # Fallback to pattern matching
            for extractor in self.extractors:
                if extractor.detect_platform(url):
                    return extractor
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting extractor for {url}: {e}")
            return None
    
    def detect_platform(self, url: str) -> Optional[Platform]:
        """Detect platform from URL"""
        extractor = self.get_extractor(url)
        if extractor:
            return Platform(extractor.platform_name)
        return None
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms"""
        return [extractor.platform_name for extractor in self.extractors]


# Global extractor factory
_extractor_factory: Optional[ExtractorFactory] = None


def get_extractor_factory() -> ExtractorFactory:
    """Get the global extractor factory"""
    global _extractor_factory
    if _extractor_factory is None:
        _extractor_factory = ExtractorFactory()
        # Register extractors will be done in __init__.py
    return _extractor_factory
