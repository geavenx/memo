"""Configuration management for Memo."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import click

from .defaults import get_default_config


class ConfigManager:
    """Manages configuration for Memo."""

    def __init__(self) -> None:
        self._config_cache: Optional[Dict[str, Any]] = None

    def get_config_path(self) -> Path:
        """Get the configuration file path, checking project directory first, then home directory."""
        project_config = Path(".memo.json")
        if project_config.exists():
            return project_config

        home_config = Path.home() / ".memo.json"
        return home_config

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or return default config."""
        if self._config_cache is not None:
            return self._config_cache

        config_path = self.get_config_path()

        try:
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = json.load(f)
                    default_config = get_default_config()
                    # Deep merge to preserve nested structures
                    merged_config = self._deep_merge(default_config, config)
                    self._config_cache = merged_config
                    return merged_config
            else:
                config = get_default_config()
                self._config_cache = config
                return config
        except (json.JSONDecodeError, IOError) as e:
            click.echo(f"Warning: Error loading config file: {e}")
            click.echo("Using default configuration.")
            config = get_default_config()
            self._config_cache = config
            return config

    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file."""
        config_path = self.get_config_path()

        try:
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            self._config_cache = config  # Update cache
            return True
        except IOError as e:
            click.echo(f"Error saving config file: {e}")
            return False

    def get_config_value(self, key: str) -> Any:
        """Get a configuration value by key (supports dot notation)."""
        config = self.load_config()

        if "." in key:
            keys = key.split(".")
            value = config
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return None
            return value
        else:
            return config.get(key)

    def set_config_value(self, key: str, value: Any) -> bool:
        """Set a configuration value by key (supports dot notation)."""
        config = self.load_config()

        if "." in key:
            keys = key.split(".")
            temp_config = config
            for k in keys[:-1]:
                if k not in temp_config:
                    temp_config[k] = {}
                temp_config = temp_config[k]

            # Try to convert value to appropriate type
            converted_value = self._convert_value(value)
            temp_config[keys[-1]] = converted_value
        else:
            converted_value = self._convert_value(value)
            config[key] = converted_value

        return self.save_config(config)

    def reset_config(self, key: Optional[str] = None) -> bool:
        """Reset configuration to defaults."""
        if key:
            default_config = get_default_config()
            current_config = self.load_config()

            if "." in key:
                keys = key.split(".")
                default_value = default_config
                current_value = current_config

                for k in keys[:-1]:
                    if k in default_value:
                        default_value = default_value[k]
                    else:
                        return False

                    if k not in current_value:
                        current_value[k] = {}
                    current_value = current_value[k]

                if keys[-1] in default_value:
                    current_value[keys[-1]] = default_value[keys[-1]]
                    return self.save_config(current_config)
                else:
                    return False
            else:
                if key in default_config:
                    current_config[key] = default_config[key]
                    return self.save_config(current_config)
                else:
                    return False
        else:
            default_config = get_default_config()
            return self.save_config(default_config)

    def _deep_merge(
        self, default: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = default.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _convert_value(self, value: str) -> Any:
        """Convert string value to appropriate type."""
        if isinstance(value, str):
            try:
                if value.lower() in ["true", "false"]:
                    return value.lower() == "true"
                elif value.isdigit():
                    return int(value)
                else:
                    return value
            except (ValueError, AttributeError):
                return value
        return value
