"""
Main entry point for Andalus Downloader Backend API
"""
import uvicorn
import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.logger import get_logger, set_log_level
from src.utils.config import get_config
from src.api.app import app

# Configure logging
logger = get_logger()


def main():
    """Main function to start the API server"""
    # Load configuration
    config = get_config()
    
    # Set log level from configuration
    set_log_level(config.api.log_level)
    
    logger.info("Starting Andalus Downloader Backend API Server")
    logger.info(f"Version: {getattr(__import__('src'), '__version__', '1.0.0')}")
    
    # Log configuration
    logger.info(f"Server configuration:")
    logger.info(f"  Host: {config.api.host}")
    logger.info(f"  Port: {config.api.port}")
    logger.info(f"  Reload: {config.api.reload}")
    logger.info(f"  Workers: {config.api.workers}")
    logger.info(f"  Log Level: {config.api.log_level}")
    logger.info(f"  CORS Enabled: {config.api.enable_cors}")
    logger.info(f"  Max Concurrent Downloads: {config.download.max_concurrent_downloads}")
    logger.info(f"  Default Output Path: {config.download.default_output_path}")
    
    # Create output directory if it doesn't exist
    Path(config.download.default_output_path).mkdir(parents=True, exist_ok=True)
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=config.api.host,
        port=config.api.port,
        reload=config.api.reload,
        workers=config.api.workers if not config.api.reload else 1,
        log_level=config.api.log_level.lower(),
        access_log=True
    )


if __name__ == "__main__":
    main()
