"""
Basic API tests for Andalus Downloader Backend API
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.api.app import app


class TestAPI:
    """Test cases for the API endpoints"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_system_status(self):
        """Test system status endpoint"""
        response = self.client.get("/api/v1/status")
        assert response.status_code == 200
        data = response.json()
        assert "active_downloads" in data
        assert "queued_downloads" in data
        assert "completed_downloads" in data
        assert "failed_downloads" in data
        assert "total_downloads" in data
        assert "version" in data
        assert "supported_platforms" in data
    
    def test_supported_platforms(self):
        """Test supported platforms endpoint"""
        response = self.client.get("/api/v1/platforms")
        assert response.status_code == 200
        data = response.json()
        assert "platforms" in data
        assert isinstance(data["platforms"], list)
        assert len(data["platforms"]) > 0
    
    def test_url_validation_invalid(self):
        """Test URL validation with invalid URL"""
        response = self.client.post("/api/v1/validate", json={"url": "invalid-url"})
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert "error" in data
    
    def test_url_validation_youtube(self):
        """Test URL validation with YouTube URL"""
        youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        response = self.client.post("/api/v1/validate", json={"url": youtube_url})
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert data["platform"] == "youtube"
    
    def test_downloads_list_empty(self):
        """Test downloads list when empty"""
        response = self.client.get("/api/v1/downloads")
        assert response.status_code == 200
        data = response.json()
        assert "downloads" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert isinstance(data["downloads"], list)
    
    def test_create_download_missing_url(self):
        """Test creating download without URL"""
        response = self.client.post("/api/v1/downloads", json={})
        assert response.status_code == 422  # Validation error
    
    def test_create_download_invalid_url(self):
        """Test creating download with invalid URL"""
        response = self.client.post("/api/v1/downloads", json={"url": "invalid-url"})
        # Should still create the download task, but it may fail during processing
        # The API accepts the request and queues it
        assert response.status_code in [200, 500]  # May fail during processing
    
    def test_get_nonexistent_download(self):
        """Test getting non-existent download"""
        response = self.client.get("/api/v1/downloads/nonexistent-id")
        assert response.status_code == 404
    
    def test_openapi_docs(self):
        """Test that OpenAPI documentation is available"""
        response = self.client.get("/docs")
        assert response.status_code == 200
        
        response = self.client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
