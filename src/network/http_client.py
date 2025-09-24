"""
HTTP client with connection pooling and rate limiting for Andalus Downloader Backend API
"""
import asyncio
import aiohttp
import time
from typing import Dict, Optional, Any, List
from urllib.parse import urlparse
import random

from ..utils.logger import get_logger

logger = get_logger()


class RateLimiter:
    """Rate limiter for HTTP requests per domain"""
    
    def __init__(self):
        self.domain_limits: Dict[str, Dict[str, Any]] = {}
        self.default_delay = 1.0  # Default delay between requests
        self.max_delay = 30.0     # Maximum delay
    
    def get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            return urlparse(url).netloc.lower()
        except:
            return "unknown"
    
    async def wait_if_needed(self, url: str) -> None:
        """Wait if rate limiting is needed for this domain"""
        domain = self.get_domain(url)
        current_time = time.time()
        
        if domain not in self.domain_limits:
            self.domain_limits[domain] = {
                'last_request': 0,
                'delay': self.default_delay,
                'consecutive_errors': 0
            }
        
        domain_info = self.domain_limits[domain]
        time_since_last = current_time - domain_info['last_request']
        
        if time_since_last < domain_info['delay']:
            wait_time = domain_info['delay'] - time_since_last
            logger.debug(f"Rate limiting {domain}: waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
        
        domain_info['last_request'] = time.time()
    
    def on_success(self, url: str) -> None:
        """Called when request succeeds - reduce delay"""
        domain = self.get_domain(url)
        if domain in self.domain_limits:
            domain_info = self.domain_limits[domain]
            domain_info['consecutive_errors'] = 0
            # Gradually reduce delay on success
            domain_info['delay'] = max(self.default_delay, domain_info['delay'] * 0.9)
    
    def on_error(self, url: str, status_code: Optional[int] = None) -> None:
        """Called when request fails - increase delay"""
        domain = self.get_domain(url)
        if domain not in self.domain_limits:
            self.domain_limits[domain] = {
                'last_request': 0,
                'delay': self.default_delay,
                'consecutive_errors': 0
            }
        
        domain_info = self.domain_limits[domain]
        domain_info['consecutive_errors'] += 1
        
        # Increase delay based on error type and consecutive errors
        if status_code == 429:  # Too Many Requests
            domain_info['delay'] = min(self.max_delay, domain_info['delay'] * 2)
        elif status_code and 500 <= status_code < 600:  # Server errors
            domain_info['delay'] = min(self.max_delay, domain_info['delay'] * 1.5)
        else:
            domain_info['delay'] = min(self.max_delay, domain_info['delay'] * 1.2)
        
        logger.warning(f"Rate limiter: increased delay for {domain} to {domain_info['delay']:.2f}s")


class HTTPClient:
    """HTTP client with connection pooling, rate limiting, and retry logic"""
    
    def __init__(self, max_connections: int = 100, max_connections_per_host: int = 10):
        self.rate_limiter = RateLimiter()
        self.max_retries = 3
        self.retry_delay = 1.0
        
        # User agents to rotate
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        # Connection configuration
        connector = aiohttp.TCPConnector(
            limit=max_connections,
            limit_per_host=max_connections_per_host,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        # Default timeout
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': random.choice(self.user_agents)}
        )
    
    async def close(self) -> None:
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("HTTP client session closed")
    
    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get headers with random user agent"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    async def get(self, url: str, headers: Optional[Dict[str, str]] = None, 
                  params: Optional[Dict[str, Any]] = None, **kwargs) -> aiohttp.ClientResponse:
        """Make GET request with rate limiting and retries"""
        return await self._request('GET', url, headers=headers, params=params, **kwargs)
    
    async def post(self, url: str, data: Optional[Any] = None, json: Optional[Any] = None,
                   headers: Optional[Dict[str, str]] = None, **kwargs) -> aiohttp.ClientResponse:
        """Make POST request with rate limiting and retries"""
        return await self._request('POST', url, data=data, json=json, headers=headers, **kwargs)
    
    async def head(self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> aiohttp.ClientResponse:
        """Make HEAD request with rate limiting and retries"""
        return await self._request('HEAD', url, headers=headers, **kwargs)
    
    async def _request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make HTTP request with rate limiting, retries, and error handling"""
        headers = self._get_headers(kwargs.pop('headers', None))
        
        for attempt in range(self.max_retries + 1):
            try:
                # Apply rate limiting
                await self.rate_limiter.wait_if_needed(url)
                
                # Make request
                async with self.session.request(method, url, headers=headers, **kwargs) as response:
                    # Check for rate limiting or server errors
                    if response.status == 429:
                        self.rate_limiter.on_error(url, response.status)
                        if attempt < self.max_retries:
                            wait_time = self.retry_delay * (2 ** attempt) + random.uniform(0, 1)
                            logger.warning(f"Rate limited on {url}, retrying in {wait_time:.2f}s")
                            await asyncio.sleep(wait_time)
                            continue
                    
                    elif 500 <= response.status < 600:
                        self.rate_limiter.on_error(url, response.status)
                        if attempt < self.max_retries:
                            wait_time = self.retry_delay * (2 ** attempt)
                            logger.warning(f"Server error {response.status} on {url}, retrying in {wait_time:.2f}s")
                            await asyncio.sleep(wait_time)
                            continue
                    
                    # Success or client error (don't retry client errors)
                    if response.status < 500:
                        self.rate_limiter.on_success(url)
                    
                    return response
            
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on {url} (attempt {attempt + 1})")
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                raise
            
            except aiohttp.ClientError as e:
                logger.warning(f"Client error on {url}: {e} (attempt {attempt + 1})")
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                raise
        
        # If we get here, all retries failed
        raise Exception(f"Failed to make request to {url} after {self.max_retries + 1} attempts")
    
    async def download_file(self, url: str, file_path: str, 
                           progress_callback: Optional[callable] = None) -> bool:
        """Download file with progress tracking"""
        try:
            await self.rate_limiter.wait_if_needed(url)
            
            headers = self._get_headers()
            async with self.session.get(url, headers=headers) as response:
                if response.status != 200:
                    logger.error(f"Failed to download {url}: HTTP {response.status}")
                    return False
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0
                
                with open(file_path, 'wb') as file:
                    async for chunk in response.content.iter_chunked(8192):
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        
                        if progress_callback:
                            await progress_callback(downloaded_size, total_size)
                
                logger.info(f"Downloaded {url} to {file_path} ({downloaded_size} bytes)")
                return True
        
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return False


# Global HTTP client instance
_http_client: Optional[HTTPClient] = None


async def get_http_client() -> HTTPClient:
    """Get the global HTTP client instance"""
    global _http_client
    if _http_client is None:
        _http_client = HTTPClient()
    return _http_client


async def close_http_client() -> None:
    """Close the global HTTP client"""
    global _http_client
    if _http_client:
        await _http_client.close()
        _http_client = None
