"""
Configuration management for Andalus Downloader Backend API
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from .logger import get_logger

logger = get_logger()


@dataclass
class DownloadConfig:
    """Download configuration settings"""
    max_concurrent_downloads: int = 3
    default_output_path: str = "downloads"
    default_quality: str = "best"
    default_format: str = "mp4"
    enable_thumbnails: bool = True
    enable_subtitles: bool = False
    max_retries: int = 3
    timeout_seconds: int = 300


@dataclass
class NetworkConfig:
    """Network configuration settings"""
    max_connections: int = 100
    max_connections_per_host: int = 10
    request_timeout: int = 30
    rate_limit_delay: float = 1.0
    max_rate_limit_delay: float = 30.0
    enable_proxy: bool = False
    proxy_url: Optional[str] = None


@dataclass
class APIConfig:
    """API server configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False
    log_level: str = "INFO"
    enable_cors: bool = True
    cors_origins: list = None


@dataclass
class DatabaseConfig:
    """Database configuration"""
    db_path: str = "andalus_downloader.db"
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    max_backups: int = 7


@dataclass
class AppConfig:
    """Main application configuration"""
    download: DownloadConfig
    network: NetworkConfig
    api: APIConfig
    database: DatabaseConfig
    
    def __post_init__(self):
        if self.api.cors_origins is None:
            self.api.cors_origins = ["*"]


class ConfigManager:
    """Configuration manager for the application"""
    
    def __init__(self, config_file: str = "config/settings.json"):
        # Use production config if ENVIRONMENT is set to production
        if os.getenv('ENVIRONMENT') == 'production':
            config_file = "config/production.json"
        self.config_file = Path(config_file)
        self.config: AppConfig = self._load_config()
    
    def _load_config(self) -> AppConfig:
        """Load configuration from file or create default"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Create config objects from loaded data
                download_config = DownloadConfig(**data.get('download', {}))
                network_config = NetworkConfig(**data.get('network', {}))
                api_config = APIConfig(**data.get('api', {}))
                database_config = DatabaseConfig(**data.get('database', {}))
                
                config = AppConfig(
                    download=download_config,
                    network=network_config,
                    api=api_config,
                    database=database_config
                )
                
                logger.info(f"Loaded configuration from {self.config_file}")
                return config
            else:
                # Create default configuration
                config = AppConfig(
                    download=DownloadConfig(),
                    network=NetworkConfig(),
                    api=APIConfig(),
                    database=DatabaseConfig()
                )
                
                # Save default configuration
                self._save_config(config)
                logger.info(f"Created default configuration at {self.config_file}")
                return config
                
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.info("Using default configuration")
            return AppConfig(
                download=DownloadConfig(),
                network=NetworkConfig(),
                api=APIConfig(),
                database=DatabaseConfig()
            )
    
    def _save_config(self, config: AppConfig) -> None:
        """Save configuration to file"""
        try:
            # Create config directory if it doesn't exist
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert config to dictionary
            config_dict = {
                'download': asdict(config.download),
                'network': asdict(config.network),
                'api': asdict(config.api),
                'database': asdict(config.database)
            }
            
            # Save to file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved configuration to {self.config_file}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def get_config(self) -> AppConfig:
        """Get current configuration"""
        return self.config
    
    def update_config(self, **kwargs) -> None:
        """Update configuration with new values"""
        try:
            # Update configuration sections
            for section, values in kwargs.items():
                if hasattr(self.config, section):
                    section_config = getattr(self.config, section)
                    for key, value in values.items():
                        if hasattr(section_config, key):
                            setattr(section_config, key, value)
                        else:
                            logger.warning(f"Unknown config key: {section}.{key}")
                else:
                    logger.warning(f"Unknown config section: {section}")
            
            # Save updated configuration
            self._save_config(self.config)
            logger.info("Configuration updated successfully")
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
    
    def get_env_overrides(self) -> Dict[str, Any]:
        """Get configuration overrides from environment variables"""
        overrides = {}
        
        # API configuration overrides
        if os.getenv('HOST') or os.getenv('API_HOST'):
            overrides.setdefault('api', {})['host'] = os.getenv('API_HOST', os.getenv('HOST', '0.0.0.0'))
        if os.getenv('PORT') or os.getenv('API_PORT'):
            port = os.getenv('API_PORT', os.getenv('PORT', '8000'))
            overrides.setdefault('api', {})['port'] = int(port)
        if os.getenv('WORKERS'):
            overrides.setdefault('api', {})['workers'] = int(os.getenv('WORKERS'))
        if os.getenv('LOG_LEVEL'):
            overrides.setdefault('api', {})['log_level'] = os.getenv('LOG_LEVEL')
        if os.getenv('RELOAD'):
            overrides.setdefault('api', {})['reload'] = os.getenv('RELOAD').lower() == 'true'
        if os.getenv('ENABLE_CORS'):
            overrides.setdefault('api', {})['enable_cors'] = os.getenv('ENABLE_CORS').lower() == 'true'
        
        # Download configuration overrides
        if os.getenv('MAX_CONCURRENT_DOWNLOADS'):
            overrides.setdefault('download', {})['max_concurrent_downloads'] = int(os.getenv('MAX_CONCURRENT_DOWNLOADS'))
        if os.getenv('DEFAULT_OUTPUT_PATH') or os.getenv('DOWNLOADS_PATH'):
            path = os.getenv('DOWNLOADS_PATH', os.getenv('DEFAULT_OUTPUT_PATH'))
            overrides.setdefault('download', {})['default_output_path'] = path
        if os.getenv('DEFAULT_QUALITY'):
            overrides.setdefault('download', {})['default_quality'] = os.getenv('DEFAULT_QUALITY')
        
        # Database configuration overrides
        if os.getenv('DATABASE_PATH'):
            overrides.setdefault('database', {})['db_path'] = os.getenv('DATABASE_PATH')
        
        # Network configuration overrides
        if os.getenv('PROXY_URL'):
            overrides.setdefault('network', {})['proxy_url'] = os.getenv('PROXY_URL')
            overrides.setdefault('network', {})['enable_proxy'] = True
        
        return overrides
    
    def apply_env_overrides(self) -> None:
        """Apply environment variable overrides to configuration"""
        overrides = self.get_env_overrides()
        if overrides:
            self.update_config(**overrides)
            logger.info("Applied environment variable overrides")


# Global configuration manager
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
        _config_manager.apply_env_overrides()
    return _config_manager


def get_config() -> AppConfig:
    """Get the current application configuration"""
    return get_config_manager().get_config()
