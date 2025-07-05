"""Configuration management for Memo."""

from .defaults import get_default_config
from .manager import ConfigManager

__all__ = ["ConfigManager", "get_default_config"]
