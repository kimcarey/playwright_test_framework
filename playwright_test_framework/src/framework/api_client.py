"""
API Client wrapper around Playwright's async request functionality.
Provides a clean, easy-to-use interface for API testing with configuration support.
"""

from typing import Dict, Any, Optional, Union
from playwright.async_api import async_playwright, APIResponse
import json
import logging
from .config import Config

logger = logging.getLogger(__name__)


class APIClient:
    """
    A wrapper around Playwright's async API request functionality.
    Simplifies making HTTP requests and provides useful utilities for testing.
    """

    def __init__(self, base_url: str = "", headers: Optional[Dict[str, str]] = None,
                 config_file: Optional[str] = None):
        """
        Initialize the API client.

        Args:
            base_url: Base URL for all requests (overrides config)
            headers: Default headers (merged with config headers)
            config_file: Path to YAML configuration file
        """
        # Load configuration
        if config_file:
            self.config = Config(config_file)
        else:
            self.config = Config()  # Use defaults

        # Override config with constructor parameters
        self.base_url = base_url or self.config.base_url
        self.base_url = self.base_url.rstrip('/')  # Remove trailing slash

        # Merge headers: config headers + constructor headers
        self.default_headers = self.config.default_headers.copy()
        if headers:
            self.default_headers.update(headers)

        # Set up logging level
        logging.getLogger().setLevel(getattr(logging, self.config.log_level))

        self._playwright = None
        self._request_context = None

    async def __aenter__(self):
        """Async context manager entry - sets up Playwright"""
        self._playwright = await async_playwright().start()
        # For API testing, we don't need a browser - just use the request context directly
        self._request_context = await self._playwright.request.new_context(
            base_url=self.base_url,
            extra_http_headers=self.default_headers
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleans up Playwright"""
        if self._request_context:
            await self._request_context.dispose()
        if self._playwright:
            await self._playwright.stop()

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from base_url and endpoint"""
        if endpoint.startswith('http'):
            return endpoint  # Full URL provided
        endpoint = endpoint.lstrip('/')  # Remove leading slash
        return f"{self.base_url}/{endpoint}" if self.base_url else endpoint

    def _merge_headers(self, headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        """Merge default headers with request-specific headers"""
        merged = self.default_headers.copy()
        if headers:
            merged.update(headers)
        return merged

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None) -> 'APIResponseWrapper':
        """
        Make a GET request.

        Args:
            endpoint: API endpoint (e.g., '/users' or full URL)
            params: Query parameters
            headers: Additional headers for this request

        Returns:
            APIResponseWrapper object
        """
        url = self._build_url(endpoint)
        merged_headers = self._merge_headers(headers)

        logger.info(f"GET {url}")
        response = await self._request_context.get(
            url,
            params=params,
            headers=merged_headers
        )

        logger.info(f"Response: {response.status} {response.status_text}")
        return APIResponseWrapper(response)

    async def post(self, endpoint: str, data: Optional[Union[Dict, str]] = None,
             headers: Optional[Dict[str, str]] = None) -> 'APIResponseWrapper':
        """
        Make a POST request.

        Args:
            endpoint: API endpoint
            data: Request body (dict will be converted to JSON)
            headers: Additional headers for this request

        Returns:
            APIResponseWrapper object
        """
        url = self._build_url(endpoint)
        merged_headers = self._merge_headers(headers)

        # Handle JSON data
        if isinstance(data, dict):
            data = json.dumps(data)
            merged_headers.setdefault('Content-Type', 'application/json')

        logger.info(f"POST {url}")
        response = await self._request_context.post(
            url,
            data=data,
            headers=merged_headers
        )

        logger.info(f"Response: {response.status} {response.status_text}")
        return APIResponseWrapper(response)

    async def put(self, endpoint: str, data: Optional[Union[Dict, str]] = None,
            headers: Optional[Dict[str, str]] = None) -> 'APIResponseWrapper':
        """Make a PUT request."""
        url = self._build_url(endpoint)
        merged_headers = self._merge_headers(headers)

        if isinstance(data, dict):
            data = json.dumps(data)
            merged_headers.setdefault('Content-Type', 'application/json')

        logger.info(f"PUT {url}")
        response = await self._request_context.put(
            url,
            data=data,
            headers=merged_headers
        )

        logger.info(f"Response: {response.status} {response.status_text}")
        return APIResponseWrapper(response)

    async def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> 'APIResponseWrapper':
        """Make a DELETE request."""
        url = self._build_url(endpoint)
        merged_headers = self._merge_headers(headers)

        logger.info(f"DELETE {url}")
        response = await self._request_context.delete(
            url,
            headers=merged_headers
        )

        logger.info(f"Response: {response.status} {response.status_text}")
        return APIResponseWrapper(response)


class APIResponseWrapper:
    """
    Wrapper around Playwright's APIResponse to add convenience methods.
    Makes it easier to work with API responses in tests.
    """

    def __init__(self, response: APIResponse):
        self._response = response

    @property
    def status(self) -> int:
        """HTTP status code"""
        return self._response.status

    @property
    def status_text(self) -> str:
        """HTTP status text"""
        return self._response.status_text

    @property
    def headers(self) -> Dict[str, str]:
        """Response headers"""
        return self._response.headers

    async def json(self) -> Dict[str, Any]:
        """Parse response body as JSON"""
        return await self._response.json()

    async def text(self) -> str:
        """Get response body as text"""
        return await self._response.text()

    def is_successful(self) -> bool:
        """Check if status code indicates success (200-299)"""
        return 200 <= self.status < 300

    def is_client_error(self) -> bool:
        """Check if status code indicates client error (400-499)"""
        return 400 <= self.status < 500

    def is_server_error(self) -> bool:
        """Check if status code indicates server error (500-599)"""
        return 500 <= self.status < 600