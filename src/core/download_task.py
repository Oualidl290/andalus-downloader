"""
Download task implementation for Andalus Downloader Backend API
"""
import asyncio
import os
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from datetime import datetime
import uuid

from .models import DownloadTask, DownloadStatus, DownloadProgress, Platform
from .database import get_database
from ..utils.logger import get_logger

logger = get_logger()


class DownloadTaskManager:
    """Manages individual download tasks"""
    
    def __init__(self, task_data: DownloadTask):
        self.task = task_data
        self.progress_callback: Optional[Callable] = None
        self.status_callback: Optional[Callable] = None
        self._cancelled = False
        self._paused = False
        self._download_process: Optional[asyncio.subprocess.Process] = None
    
    def set_progress_callback(self, callback: Callable) -> None:
        """Set callback for progress updates"""
        self.progress_callback = callback
    
    def set_status_callback(self, callback: Callable) -> None:
        """Set callback for status updates"""
        self.status_callback = callback
    
    async def start_download(self) -> bool:
        """Start the download process"""
        try:
            logger.info(f"Starting download: {self.task.id} - {self.task.url}")
            
            # Update status to downloading
            await self._update_status(DownloadStatus.DOWNLOADING)
            self.task.started_at = datetime.utcnow()
            
            # Save initial state to database
            db = await get_database()
            await db.update_download(self.task.id, {
                'status': DownloadStatus.DOWNLOADING.value,
                'started_at': self.task.started_at.isoformat()
            })
            
            # Start the actual download process
            success = await self._execute_download()
            
            if success and not self._cancelled:
                await self._update_status(DownloadStatus.COMPLETED)
                self.task.completed_at = datetime.utcnow()
                self.task.progress = 100.0
                
                # Update database
                await db.update_download(self.task.id, {
                    'status': DownloadStatus.COMPLETED.value,
                    'completed_at': self.task.completed_at.isoformat(),
                    'progress': 100.0
                })
                
                logger.info(f"Download completed: {self.task.id}")
                return True
            else:
                if not self._cancelled:
                    await self._update_status(DownloadStatus.FAILED)
                    await db.update_download(self.task.id, {
                        'status': DownloadStatus.FAILED.value,
                        'error_message': 'Download failed'
                    })
                return False
                
        except Exception as e:
            logger.error(f"Download failed: {self.task.id} - {e}")
            await self._update_status(DownloadStatus.FAILED)
            self.task.error_message = str(e)
            
            # Update database
            db = await get_database()
            await db.update_download(self.task.id, {
                'status': DownloadStatus.FAILED.value,
                'error_message': str(e)
            })
            
            return False
    
    async def pause_download(self) -> bool:
        """Pause the download"""
        try:
            self._paused = True
            
            if self._download_process:
                self._download_process.terminate()
            
            await self._update_status(DownloadStatus.PAUSED)
            
            # Update database
            db = await get_database()
            await db.update_download(self.task.id, {
                'status': DownloadStatus.PAUSED.value
            })
            
            logger.info(f"Download paused: {self.task.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause download {self.task.id}: {e}")
            return False
    
    async def resume_download(self) -> bool:
        """Resume the download"""
        try:
            self._paused = False
            await self._update_status(DownloadStatus.DOWNLOADING)
            
            # Update database
            db = await get_database()
            await db.update_download(self.task.id, {
                'status': DownloadStatus.DOWNLOADING.value
            })
            
            # Restart download process
            success = await self._execute_download()
            
            logger.info(f"Download resumed: {self.task.id}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to resume download {self.task.id}: {e}")
            return False
    
    async def cancel_download(self) -> bool:
        """Cancel the download"""
        try:
            self._cancelled = True
            
            if self._download_process:
                self._download_process.terminate()
                await self._download_process.wait()
            
            await self._update_status(DownloadStatus.CANCELLED)
            
            # Clean up partial files
            if self.task.file_path and os.path.exists(self.task.file_path):
                try:
                    os.remove(self.task.file_path)
                    logger.info(f"Cleaned up partial file: {self.task.file_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up partial file: {e}")
            
            # Update database
            db = await get_database()
            await db.update_download(self.task.id, {
                'status': DownloadStatus.CANCELLED.value
            })
            
            logger.info(f"Download cancelled: {self.task.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel download {self.task.id}: {e}")
            return False
    
    async def _execute_download(self) -> bool:
        """Execute the actual download using yt-dlp"""
        try:
            import yt_dlp
            from pathlib import Path
            
            # Set up output directory
            output_path = self.task.metadata.get('output_path', 'downloads')
            Path(output_path).mkdir(parents=True, exist_ok=True)
            
            # Configure yt-dlp options
            ydl_opts = {
                'outtmpl': f'{output_path}/%(title)s.%(ext)s',
                'format': self._get_format_selector(),
                'noplaylist': True,
                'extract_flat': False,
                'writethumbnail': False,
                'writeinfojson': False,
                'quiet': True,
                'no_warnings': True,
            }
            
            # Add progress hook
            ydl_opts['progress_hooks'] = [self._progress_hook]
            
            # Handle audio extraction
            if self.task.metadata.get('extract_audio', False):
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.task.format or 'mp3',
                    'preferredquality': '192',
                }]
            
            # Download with yt-dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.task.url, download=False)
                
                # Update task with extracted info
                if info:
                    self.task.title = info.get('title', self.task.title)
                    self.task.duration = info.get('duration', self.task.duration)
                    self.task.thumbnail_url = info.get('thumbnail', self.task.thumbnail_url)
                    self.task.file_size = info.get('filesize') or info.get('filesize_approx')
                
                # Start actual download
                if not self._cancelled and not self._paused:
                    ydl.download([self.task.url])
                    
                    # Find downloaded file
                    downloaded_file = self._find_downloaded_file(output_path, info)
                    if downloaded_file:
                        self.task.file_path = str(downloaded_file)
                        logger.info(f"Download completed: {downloaded_file}")
                        return True
                    else:
                        logger.error("Downloaded file not found")
                        return False
                
                return False
            
        except Exception as e:
            logger.error(f"Download execution failed: {e}")
            self.task.error_message = str(e)
            return False
    
    def _get_format_selector(self) -> str:
        """Get yt-dlp format selector based on quality preference"""
        quality = self.task.quality
        if not quality or quality == 'best':
            return 'best'
        elif quality == 'worst':
            return 'worst'
        elif quality == 'audio_only':
            return 'bestaudio'
        elif quality.endswith('p'):
            # Specific resolution like 1080p, 720p
            height = quality[:-1]
            return f'best[height<={height}]'
        else:
            return 'best'
    
    def _progress_hook(self, d):
        """Progress hook for yt-dlp"""
        try:
            if d['status'] == 'downloading':
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                
                if total > 0:
                    percentage = (downloaded / total) * 100
                    self.task.progress = percentage
                    self.task.downloaded_size = downloaded
                    self.task.file_size = total
                    
                    # Create progress update
                    progress = DownloadProgress(
                        downloaded_bytes=downloaded,
                        total_bytes=total,
                        percentage=percentage,
                        speed=d.get('speed'),
                        eta=d.get('eta'),
                        status=DownloadStatus.DOWNLOADING
                    )
                    
                    # Call progress callback
                    if self.progress_callback:
                        asyncio.create_task(self.progress_callback(self.task.id, progress))
            
            elif d['status'] == 'finished':
                self.task.progress = 100.0
                self.task.file_path = d.get('filename')
                logger.info(f"Download finished: {d.get('filename')}")
                
        except Exception as e:
            logger.error(f"Progress hook error: {e}")
    
    def _find_downloaded_file(self, output_path: str, info: dict) -> Optional[Path]:
        """Find the downloaded file"""
        try:
            output_dir = Path(output_path)
            title = info.get('title', 'download')
            ext = info.get('ext', 'mp4')
            
            # Try exact filename first
            expected_file = output_dir / f"{title}.{ext}"
            if expected_file.exists():
                return expected_file
            
            # Search for files with similar names
            for file_path in output_dir.glob(f"*{title[:20]}*"):
                if file_path.is_file():
                    return file_path
            
            # Fallback: get the most recent file
            files = [f for f in output_dir.iterdir() if f.is_file()]
            if files:
                return max(files, key=lambda f: f.stat().st_mtime)
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding downloaded file: {e}")
            return None
    
    async def _update_status(self, status: DownloadStatus) -> None:
        """Update task status and notify callbacks"""
        self.task.status = status
        
        if self.status_callback:
            await self.status_callback(self.task.id, status)
    
    def get_progress(self) -> DownloadProgress:
        """Get current download progress"""
        return DownloadProgress(
            downloaded_bytes=self.task.downloaded_size,
            total_bytes=self.task.file_size,
            percentage=self.task.progress,
            status=self.task.status
        )
    
    def is_active(self) -> bool:
        """Check if download is currently active"""
        return self.task.status in [DownloadStatus.DOWNLOADING, DownloadStatus.PENDING]
    
    def is_completed(self) -> bool:
        """Check if download is completed"""
        return self.task.status == DownloadStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if download failed"""
        return self.task.status == DownloadStatus.FAILED
