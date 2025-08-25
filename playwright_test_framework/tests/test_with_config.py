"""
Example test showing how to use configuration with the API client.
"""

import pytest
import pytest_asyncio
from framework.api_client import APIClient
from framework.config import Config


class TestAPIWithConfig:
    """Test class demonstrating configuration usage."""

    @pytest_asyncio.fixture
    async def api_client_with_config_file(self):
        """API client loaded from YAML config file."""
        async with APIClient(config_file="config.yaml") as client:
            yield client

    @pytest_asyncio.fixture
    async def api_client_with_manual_config(self):
        """API client with manually set configuration."""
        # Instead of passing a config object, we override with constructor params
        async with APIClient(
            base_url="https://jsonplaceholder.typicode.com",
            headers={"Custom-Test": "manual-config"}
        ) as client:
            yield client

    @pytest_asyncio.fixture
    async def api_client_override_config(self):
        """API client that overrides config with constructor params."""
        async with APIClient(
            config_file="config.yaml",
            base_url="https://httpbin.org",  # Override the config file URL
            headers={"Custom-Header": "test-value"}  # Add extra header
        ) as client:
            yield client

    @pytest.mark.asyncio
    async def test_config_file_loading(self, api_client_with_config_file):
        """Test that config file is loaded properly."""
        response = await api_client_with_config_file.get("/posts/1")
        assert response.is_successful()

        # Verify the User-Agent from config is being used
        # (We can't easily check this without intercepting, but the test passes if config loaded)

    @pytest.mark.asyncio
    async def test_manual_config(self, api_client_with_manual_config):
        """Test using manual configuration via constructor."""
        response = await api_client_with_manual_config.get("/posts/1")
        assert response.is_successful()

    @pytest.mark.asyncio
    async def test_config_override(self, api_client_override_config):
        """Test overriding config with constructor parameters."""
        # This hits httpbin.org instead of jsonplaceholder due to override
        response = await api_client_override_config.get("/get")
        assert response.is_successful()

        data = await response.json()
        # httpbin.org echoes back headers, so we can verify our custom header
        assert "Custom-Header" in data["headers"]
        assert data["headers"]["Custom-Header"] == "test-value"


class TestConfigurationClass:
    """Test the configuration class itself."""

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        assert config.timeout == 30
        assert config.retry_count == 3
        assert "User-Agent" in config.default_headers

    def test_config_file_loading(self):
        """Test loading config from YAML file."""
        config = Config(config_file="config.yaml")
        assert config.base_url == "https://jsonplaceholder.typicode.com"
        assert config.timeout == 30

    def test_config_repr(self):
        """Test config string representation."""
        config = Config()
        repr_str = repr(config)
        assert "Config(" in repr_str
        assert "base_url" in repr_str