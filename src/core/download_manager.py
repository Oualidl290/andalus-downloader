"""
Download manager and queue system for Andalus Downloader Backend API
"""
import asyncio
from typing import Dict, List, Optional, Callable
from datetime import datetime
import uuid

from .models import DownloadTask, DownloadStatus, DownloadProgress, DownloadRequest
from .download_task import DownloadTaskManager
from .database import get_database
from ..utils.logger import get_logger

logger = get_logger()


class DownloadManager:
    """Manages download queue and concurrent downloads"""
    
    def __init__(self, max_concurrent_downloads: int = 3):
        self.max_concurrent_downloads = max_concurrent_downloads
        self.active_downloads: Dict[str, DownloadTaskManager] = {}
        self.download_queue: List[str] = []  # Queue of download IDs
        self.progress_callbacks: List[Callable] = []
        self.status_callbacks: List[Callable] = []
        self._queue_processor_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self) -> None:
        """Start the download manager"""
        if self._running:
            return
        
        self._running = True
        logger.info("Starting download manager")
        
        # Load pending downloads from database
        await self._load_pending_downloads()
        
        # Start queue processor
        self._queue_processor_task = asyncio.create_task(self._process_queue())
        
        logger.info(f"Download manager started with max {self.max_concurrent_downloads} concurrent downloads")
    
    async def stop(self) -> None:
        """Stop the download manager"""
        if not self._running:
            return
        
        self._running = False
        logger.info("Stopping download manager")
        
        # Cancel queue processor
        if self._queue_processor_task:
            self._queue_processor_task.cancel()
            try:
                await self._queue_processor_task
            except asyncio.CancelledError:
                pass
        
        # Cancel all active downloads
        for download_id in list(self.active_downloads.keys()):
            await self.cancel_download(download_id)
        
        logger.info("Download manager stopped")
    
    def add_progress_callback(self, callback: Callable) -> None:
        """Add a progress update callback"""
        self.progress_callbacks.append(callback)
    
    def add_status_callback(self, callback: Callable) -> None:
        """Add a status update callback"""
        self.status_callbacks.append(callback)
    
    async def add_download(self, request: DownloadRequest) -> str:
        """Add a new download to the queue"""
        try:
            # Create download task
            task = DownloadTask(
                url=request.url,
                quality=request.quality,
                format=request.format,
                metadata={
                    'output_path': request.output_path,
                    'filename_template': request.filename_template,
                    'extract_audio': request.extract_audio,
                    'download_subtitles': request.download_subtitles
                }
            )
            
            # Save to database
            db = await get_database()
            await db.insert_download({
                'id': task.id,
                'url': task.url,
                'status': task.status.value,
                'quality': task.quality.value if task.quality else None,
                'format': task.format,
                'created_at': task.created_at.isoformat(),
                'metadata': task.metadata
            })
            
            # Add to queue
            self.download_queue.append(task.id)
            
            logger.info(f"Added download to queue: {task.id} - {task.url}")
            
            # Notify status callbacks
            await self._notify_status_callbacks(task.id, DownloadStatus.PENDING)
            
            return task.id
            
        except Exception as e:
            logger.error(f"Failed to add download: {e}")
            raise
    
    async def pause_download(self, download_id: str) -> bool:
        """Pause a download"""
        try:
            if download_id in self.active_downloads:
                success = await self.active_downloads[download_id].pause_download()
                if success:
                    await self._notify_status_callbacks(download_id, DownloadStatus.PAUSED)
                return success
            else:
                # Update database for queued download
                db = await get_database()
                success = await db.update_download(download_id, {
                    'status': DownloadStatus.PAUSED.value
                })
                if success:
                    await self._notify_status_callbacks(download_id, DownloadStatus.PAUSED)
                return success
                
        except Exception as e:
            logger.error(f"Failed to pause download {download_id}: {e}")
            return False
    
    async def resume_download(self, download_id: str) -> bool:
        """Resume a download"""
        try:
            if download_id in self.active_downloads:
                success = await self.active_downloads[download_id].resume_download()
                if success:
                    await self._notify_status_callbacks(download_id, DownloadStatus.DOWNLOADING)
                return success
            else:
                # Update database and add back to queue
                db = await get_database()
                success = await db.update_download(download_id, {
                    'status': DownloadStatus.PENDING.value
                })
                if success:
                    if download_id not in self.download_queue:
                        self.download_queue.append(download_id)
                    await self._notify_status_callbacks(download_id, DownloadStatus.PENDING)
                return success
                
        except Exception as e:
            logger.error(f"Failed to resume download {download_id}: {e}")
            return False
    
    async def cancel_download(self, download_id: str) -> bool:
        """Cancel a download"""
        try:
            # Remove from queue if present
            if download_id in self.download_queue:
                self.download_queue.remove(download_id)
            
            # Cancel active download
            if download_id in self.active_downloads:
                success = await self.active_downloads[download_id].cancel_download()
                del self.active_downloads[download_id]
                if success:
                    await self._notify_status_callbacks(download_id, DownloadStatus.CANCELLED)
                return success
            else:
                # Update database for queued download
                db = await get_database()
                success = await db.update_download(download_id, {
                    'status': DownloadStatus.CANCELLED.value
                })
                if success:
                    await self._notify_status_callbacks(download_id, DownloadStatus.CANCELLED)
                return success
                
        except Exception as e:
            logger.error(f"Failed to cancel download {download_id}: {e}")
            return False
    
    async def get_download_progress(self, download_id: str) -> Optional[DownloadProgress]:
        """Get progress for a specific download"""
        try:
            if download_id in self.active_downloads:
                return self.active_downloads[download_id].get_progress()
            else:
                # Get from database
                db = await get_database()
                download_data = await db.get_download(download_id)
                if download_data:
                    return DownloadProgress(
                        downloaded_bytes=download_data.get('downloaded_size', 0),
                        total_bytes=download_data.get('file_size'),
                        percentage=download_data.get('progress', 0.0),
                        status=DownloadStatus(download_data.get('status', 'pending'))
                    )
            return None
            
        except Exception as e:
            logger.error(f"Failed to get download progress {download_id}: {e}")
            return None
    
    async def get_downloads(self, status: Optional[DownloadStatus] = None, limit: int = 50, offset: int = 0) -> List[DownloadTask]:
        """Get downloads with optional filtering"""
        try:
            db = await get_database()
            status_str = status.value if status else None
            downloads_data = await db.get_downloads(status_str, limit, offset)
            
            downloads = []
            for data in downloads_data:
                task = DownloadTask(
                    id=data['id'],
                    url=data['url'],
                    title=data.get('title'),
                    platform=data.get('platform'),
                    status=DownloadStatus(data['status']),
                    progress=data.get('progress', 0.0),
                    file_path=data.get('file_path'),
                    file_size=data.get('file_size'),
                    downloaded_size=data.get('downloaded_size', 0),
                    format=data.get('format'),
                    quality=data.get('quality'),
                    thumbnail_url=data.get('thumbnail_url'),
                    duration=data.get('duration'),
                    created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.utcnow(),
                    started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
                    completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
                    error_message=data.get('error_message'),
                    metadata=data.get('metadata', {})
                )
                downloads.append(task)
            
            return downloads
            
        except Exception as e:
            logger.error(f"Failed to get downloads: {e}")
            return []
    
    async def get_system_status(self) -> Dict[str, int]:
        """Get system status information"""
        try:
            db = await get_database()
            
            # Count downloads by status
            all_downloads = await db.get_downloads(limit=10000)  # Get all downloads
            
            status_counts = {
                'active': 0,
                'queued': 0,
                'completed': 0,
                'failed': 0,
                'total': len(all_downloads)
            }
            
            for download in all_downloads:
                status = download.get('status', 'pending')
                if status in ['downloading']:
                    status_counts['active'] += 1
                elif status in ['pending', 'paused']:
                    status_counts['queued'] += 1
                elif status == 'completed':
                    status_counts['completed'] += 1
                elif status == 'failed':
                    status_counts['failed'] += 1
            
            return status_counts
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {'active': 0, 'queued': 0, 'completed': 0, 'failed': 0, 'total': 0}
    
    async def _load_pending_downloads(self) -> None:
        """Load pending downloads from database on startup"""
        try:
            db = await get_database()
            pending_downloads = await db.get_downloads(status='pending')
            paused_downloads = await db.get_downloads(status='paused')
            
            # Add pending downloads to queue
            for download in pending_downloads:
                self.download_queue.append(download['id'])
            
            # Add paused downloads to queue (they can be resumed)
            for download in paused_downloads:
                self.download_queue.append(download['id'])
            
            logger.info(f"Loaded {len(pending_downloads)} pending and {len(paused_downloads)} paused downloads")
            
        except Exception as e:
            logger.error(f"Failed to load pending downloads: {e}")
    
    async def _process_queue(self) -> None:
        """Process the download queue"""
        while self._running:
            try:
                # Check if we can start more downloads
                if (len(self.active_downloads) < self.max_concurrent_downloads and 
                    self.download_queue):
                    
                    download_id = self.download_queue.pop(0)
                    await self._start_download(download_id)
                
                # Clean up completed downloads
                completed_downloads = []
                for download_id, task_manager in self.active_downloads.items():
                    if not task_manager.is_active():
                        completed_downloads.append(download_id)
                
                for download_id in completed_downloads:
                    del self.active_downloads[download_id]
                    logger.info(f"Cleaned up completed download: {download_id}")
                
                # Wait before next iteration
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in queue processor: {e}")
                await asyncio.sleep(5)  # Wait longer on error
    
    async def _start_download(self, download_id: str) -> None:
        """Start a specific download"""
        try:
            # Get download data from database
            db = await get_database()
            download_data = await db.get_download(download_id)
            
            if not download_data:
                logger.error(f"Download not found in database: {download_id}")
                return
            
            # Create download task
            task = DownloadTask(
                id=download_data['id'],
                url=download_data['url'],
                title=download_data.get('title'),
                platform=download_data.get('platform'),
                status=DownloadStatus(download_data['status']),
                quality=download_data.get('quality'),
                format=download_data.get('format'),
                metadata=download_data.get('metadata', {})
            )
            
            # Create task manager
            task_manager = DownloadTaskManager(task)
            task_manager.set_progress_callback(self._on_progress_update)
            task_manager.set_status_callback(self._on_status_update)
            
            # Add to active downloads
            self.active_downloads[download_id] = task_manager
            
            # Start download in background
            asyncio.create_task(task_manager.start_download())
            
            logger.info(f"Started download: {download_id}")
            
        except Exception as e:
            logger.error(f"Failed to start download {download_id}: {e}")
    
    async def _on_progress_update(self, download_id: str, progress: DownloadProgress) -> None:
        """Handle progress updates from download tasks"""
        for callback in self.progress_callbacks:
            try:
                await callback(download_id, progress)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")
    
    async def _on_status_update(self, download_id: str, status: DownloadStatus) -> None:
        """Handle status updates from download tasks"""
        await self._notify_status_callbacks(download_id, status)
    
    async def _notify_status_callbacks(self, download_id: str, status: DownloadStatus) -> None:
        """Notify all status callbacks"""
        for callback in self.status_callbacks:
            try:
                await callback(download_id, status)
            except Exception as e:
                logger.error(f"Status callback error: {e}")


# Global download manager instance
_download_manager: Optional[DownloadManager] = None


async def get_download_manager() -> DownloadManager:
    """Get the global download manager instance"""
    global _download_manager
    if _download_manager is None:
        _download_manager = DownloadManager()
        await _download_manager.start()
    return _download_manager
