# Platform-specific extractors
from .base import get_extractor_factory
from .youtube import YouTubeExtractor
from .vimeo import VimeoExtractor
from .soundcloud import SoundCloudExtractor
from .dailymotion import DailymotionExtractor
from .generic import GenericExtractor

# Initialize and register extractors
def initialize_extractors():
    """Initialize and register all platform extractors"""
    factory = get_extractor_factory()
    
    # Register extractors in order of preference (most specific first)
    factory.register_extractor(YouTubeExtractor())
    factory.register_extractor(VimeoExtractor())
    factory.register_extractor(SoundCloudExtractor())
    factory.register_extractor(DailymotionExtractor())
    
    # Generic extractor should be last (fallback for ANY website)
    factory.register_extractor(GenericExtractor())
    
    return factory

# Auto-initialize when module is imported
initialize_extractors()
