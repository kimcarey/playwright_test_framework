"""
Configuration management for the API testing framework.
Loads settings from YAML files and environment variables.
"""

import os
import yaml
from typing import Dict, Any, Optional


class Config:
    """
    Simple configuration class that loads settings from YAML files
    and environment variables.
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_file: Path to YAML config file (e.g., 'config.yaml')
        """
        # Set defaults
        self.base_url = ""
        self.timeout = 30
        self.default_headers = {
            "User-Agent": "Playwright-Test-Framework/1.0"
        }
        self.retry_count = 3
        self.log_level = "INFO"

        # Load from YAML file if provided
        if config_file:
            self._load_from_yaml(config_file)

        # Override with environment variables if present
        self._load_from_environment()

    def _load_from_yaml(self, config_file: str):
        """Load configuration from a YAML file."""
        try:
            with open(config_file, 'r') as file:
                data = yaml.safe_load(file)

            if not data:
                return

            # Load each setting if it exists in the YAML
            self.base_url = data.get('base_url', self.base_url)
            self.timeout = data.get('timeout', self.timeout)
            self.retry_count = data.get('retry_count', self.retry_count)
            self.log_level = data.get('log_level', self.log_level)

            # Merge headers
            if 'default_headers' in data:
                self.default_headers.update(data['default_headers'])

        except FileNotFoundError:
            raise ValueError(f"Config file not found: {config_file}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file {config_file}: {e}")

    def _load_from_environment(self):
        """Load secrets from environment variables."""
        # Only handle secrets, not configuration
        if os.getenv('API_KEY'):
            self.default_headers['Authorization'] = f"Bearer {os.getenv('API_KEY')}"

        if os.getenv('API_SECRET'):
            # Could be used for signing requests, etc.
            pass  # Store as needed for your specific use case

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration as a dictionary."""
        return {
            'base_url': self.base_url,
            'timeout': self.timeout,
            'default_headers': self.default_headers,
            'retry_count': self.retry_count,
            'log_level': self.log_level
        }

    def __repr__(self):
        """String representation of config (safe - no secrets)."""
        safe_headers = self.default_headers.copy()
        if 'Authorization' in safe_headers:
            safe_headers['Authorization'] = '***HIDDEN***'

        return f"Config(base_url='{self.base_url}', timeout={self.timeout}, headers={safe_headers})"