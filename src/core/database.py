"""
Database management for Andalus Downloader Backend API
"""
import aiosqlite
import asyncio
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
import json

from ..utils.logger import get_logger

logger = get_logger()


class Database:
    """Async SQLite database manager"""
    
    def __init__(self, db_path: str = "andalus_downloader.db"):
        self.db_path = Path(db_path)
        self._connection: Optional[aiosqlite.Connection] = None
    
    async def connect(self) -> None:
        """Connect to the database"""
        try:
            self._connection = await aiosqlite.connect(self.db_path)
            await self._connection.execute("PRAGMA foreign_keys = ON")
            await self._connection.commit()
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from the database"""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("Disconnected from database")
    
    async def initialize_schema(self) -> None:
        """Initialize database schema"""
        if not self._connection:
            await self.connect()
        
        try:
            # Downloads table
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS downloads (
                    id TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    title TEXT,
                    platform TEXT,
                    status TEXT DEFAULT 'pending',
                    progress REAL DEFAULT 0.0,
                    file_path TEXT,
                    file_size INTEGER,
                    downloaded_size INTEGER DEFAULT 0,
                    format TEXT,
                    quality TEXT,
                    thumbnail_url TEXT,
                    duration INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT,
                    metadata TEXT  -- JSON string for additional metadata
                )
            """)
            
            # Settings table
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Download history table for completed downloads
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS download_history (
                    id TEXT PRIMARY KEY,
                    original_download_id TEXT,
                    url TEXT NOT NULL,
                    title TEXT,
                    platform TEXT,
                    file_path TEXT,
                    file_size INTEGER,
                    format TEXT,
                    quality TEXT,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (original_download_id) REFERENCES downloads (id)
                )
            """)
            
            # Create indexes for better performance
            await self._connection.execute("CREATE INDEX IF NOT EXISTS idx_downloads_status ON downloads(status)")
            await self._connection.execute("CREATE INDEX IF NOT EXISTS idx_downloads_platform ON downloads(platform)")
            await self._connection.execute("CREATE INDEX IF NOT EXISTS idx_downloads_created_at ON downloads(created_at)")
            await self._connection.execute("CREATE INDEX IF NOT EXISTS idx_settings_category ON settings(category)")
            
            await self._connection.commit()
            logger.info("Database schema initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            raise
    
    async def insert_download(self, download_data: Dict[str, Any]) -> str:
        """Insert a new download record"""
        if not self._connection:
            await self.connect()
        
        try:
            # Convert metadata dict to JSON string if present
            if 'metadata' in download_data and isinstance(download_data['metadata'], dict):
                download_data['metadata'] = json.dumps(download_data['metadata'])
            
            columns = ', '.join(download_data.keys())
            placeholders = ', '.join(['?' for _ in download_data])
            values = list(download_data.values())
            
            query = f"INSERT INTO downloads ({columns}) VALUES ({placeholders})"
            await self._connection.execute(query, values)
            await self._connection.commit()
            
            download_id = download_data.get('id')
            logger.info(f"Inserted download record: {download_id}")
            return download_id
            
        except Exception as e:
            logger.error(f"Failed to insert download: {e}")
            raise
    
    async def update_download(self, download_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a download record"""
        if not self._connection:
            await self.connect()
        
        try:
            # Convert metadata dict to JSON string if present
            if 'metadata' in update_data and isinstance(update_data['metadata'], dict):
                update_data['metadata'] = json.dumps(update_data['metadata'])
            
            set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])
            values = list(update_data.values()) + [download_id]
            
            query = f"UPDATE downloads SET {set_clause} WHERE id = ?"
            cursor = await self._connection.execute(query, values)
            await self._connection.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Updated download record: {download_id}")
                return True
            else:
                logger.warning(f"No download found with id: {download_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update download {download_id}: {e}")
            raise
    
    async def get_download(self, download_id: str) -> Optional[Dict[str, Any]]:
        """Get a download record by ID"""
        if not self._connection:
            await self.connect()
        
        try:
            cursor = await self._connection.execute(
                "SELECT * FROM downloads WHERE id = ?", (download_id,)
            )
            row = await cursor.fetchone()
            
            if row:
                # Convert row to dictionary
                columns = [description[0] for description in cursor.description]
                download_data = dict(zip(columns, row))
                
                # Parse metadata JSON string back to dict
                if download_data.get('metadata'):
                    try:
                        download_data['metadata'] = json.loads(download_data['metadata'])
                    except json.JSONDecodeError:
                        download_data['metadata'] = {}
                
                return download_data
            return None
            
        except Exception as e:
            logger.error(f"Failed to get download {download_id}: {e}")
            raise
    
    async def get_downloads(self, status: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get downloads with optional filtering"""
        if not self._connection:
            await self.connect()
        
        try:
            if status:
                query = "SELECT * FROM downloads WHERE status = ? ORDER BY created_at DESC LIMIT ? OFFSET ?"
                params = (status, limit, offset)
            else:
                query = "SELECT * FROM downloads ORDER BY created_at DESC LIMIT ? OFFSET ?"
                params = (limit, offset)
            
            cursor = await self._connection.execute(query, params)
            rows = await cursor.fetchall()
            
            # Convert rows to dictionaries
            columns = [description[0] for description in cursor.description]
            downloads = []
            
            for row in rows:
                download_data = dict(zip(columns, row))
                
                # Parse metadata JSON string back to dict
                if download_data.get('metadata'):
                    try:
                        download_data['metadata'] = json.loads(download_data['metadata'])
                    except json.JSONDecodeError:
                        download_data['metadata'] = {}
                
                downloads.append(download_data)
            
            return downloads
            
        except Exception as e:
            logger.error(f"Failed to get downloads: {e}")
            raise
    
    async def delete_download(self, download_id: str) -> bool:
        """Delete a download record"""
        if not self._connection:
            await self.connect()
        
        try:
            cursor = await self._connection.execute(
                "DELETE FROM downloads WHERE id = ?", (download_id,)
            )
            await self._connection.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Deleted download record: {download_id}")
                return True
            else:
                logger.warning(f"No download found with id: {download_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete download {download_id}: {e}")
            raise
    
    async def get_setting(self, key: str) -> Optional[str]:
        """Get a setting value"""
        if not self._connection:
            await self.connect()
        
        try:
            cursor = await self._connection.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            )
            row = await cursor.fetchone()
            return row[0] if row else None
            
        except Exception as e:
            logger.error(f"Failed to get setting {key}: {e}")
            raise
    
    async def set_setting(self, key: str, value: str, category: str = "general") -> None:
        """Set a setting value"""
        if not self._connection:
            await self.connect()
        
        try:
            await self._connection.execute("""
                INSERT OR REPLACE INTO settings (key, value, category, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (key, value, category))
            await self._connection.commit()
            logger.info(f"Set setting: {key} = {value}")
            
        except Exception as e:
            logger.error(f"Failed to set setting {key}: {e}")
            raise


# Global database instance
_db_instance: Optional[Database] = None


async def get_database() -> Database:
    """Get the global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
        await _db_instance.connect()
        await _db_instance.initialize_schema()
    return _db_instance
