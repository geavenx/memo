"""Environment variable management for Memo."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

import click
from dotenv import load_dotenv


class EnvironmentManager:
    """Manages environment variables from multiple sources with priority order."""

    def __init__(self):
        self._auth_config_cache: Optional[Dict] = None
        self._loaded = False

    def load_environment_variables(self) -> None:
        """Load environment variables from all sources in priority order."""
        if self._loaded:
            return

        # 1. Load from .env files (lowest priority)
        self._load_dotenv_files()

        # 2. Load from CLI auth config (highest priority)
        self._load_auth_config_to_env()

        self._loaded = True

    def _load_dotenv_files(self) -> None:
        """Load .env files in order of priority."""
        env_locations = [
            Path.cwd() / ".env",  # Current working directory
            Path.home() / ".env",  # User home directory
            Path.home() / ".memo" / ".env",  # User config directory
        ]

        for env_path in env_locations:
            if env_path.exists():
                load_dotenv(env_path, override=False)

    def _load_auth_config_to_env(self) -> None:
        """Load API keys from auth.json into environment variables."""
        auth_config = self.load_auth_config()
        if not auth_config:
            return

        providers = auth_config.get("providers", {})

        # Map provider names to environment variable names
        provider_env_map = {
            "openai": "OPENAI_API_KEY",
            "google": "GOOGLE_API_KEY",
        }

        for provider, env_var in provider_env_map.items():
            if provider in providers and "api_key" in providers[provider]:
                # Only set if not already set (system env vars have priority)
                if not os.getenv(env_var):
                    os.environ[env_var] = providers[provider]["api_key"]

    def get_auth_config_path(self) -> Path:
        """Get the path to the auth configuration file."""
        auth_dir = Path.home() / ".local" / "share" / "memo"
        auth_dir.mkdir(parents=True, exist_ok=True)
        return auth_dir / "auth.json"

    def load_auth_config(self) -> Optional[Dict]:
        """Load authentication configuration from auth.json."""
        if self._auth_config_cache is not None:
            return self._auth_config_cache

        auth_path = self.get_auth_config_path()

        try:
            if auth_path.exists():
                with open(auth_path, "r") as f:
                    config = json.load(f)
                    self._auth_config_cache = config
                    return config
            else:
                return None
        except (json.JSONDecodeError, IOError) as e:
            click.echo(f"Warning: Error loading auth config: {e}")
            return None

    def save_auth_config(self, config: Dict) -> bool:
        """Save authentication configuration to auth.json."""
        auth_path = self.get_auth_config_path()

        try:
            with open(auth_path, "w") as f:
                json.dump(config, f, indent=2)
            self._auth_config_cache = config  # Update cache
            return True
        except IOError as e:
            click.echo(f"Error saving auth config: {e}")
            return False

    def set_api_key(self, provider: str, api_key: str) -> bool:
        """Set API key for a specific provider."""
        valid_providers = ["openai", "google"]
        if provider not in valid_providers:
            click.echo(
                f"Error: Invalid provider '{provider}'. Valid providers: {', '.join(valid_providers)}"
            )
            return False

        config = self.load_auth_config() or {"providers": {}}

        if "providers" not in config:
            config["providers"] = {}

        config["providers"][provider] = {"api_key": api_key}

        if self.save_auth_config(config):
            # Update environment variable immediately
            env_var_map = {
                "openai": "OPENAI_API_KEY",
                "google": "GOOGLE_API_KEY",
            }
            if provider in env_var_map:
                os.environ[env_var_map[provider]] = api_key
            return True

        return False

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider."""
        config = self.load_auth_config()
        if not config:
            return None

        providers = config.get("providers", {})
        if provider in providers:
            return providers[provider].get("api_key")

        return None

    def remove_api_key(self, provider: str) -> bool:
        """Remove API key for a specific provider."""
        config = self.load_auth_config()
        if not config:
            return False

        providers = config.get("providers", {})
        if provider in providers:
            del providers[provider]
            return self.save_auth_config(config)

        return False

    def list_configured_providers(self) -> Dict[str, bool]:
        """List all configured providers and their availability."""
        config = self.load_auth_config()
        providers = config.get("providers", {}) if config else {}

        # Check both auth config and environment variables
        result = {}
        all_providers = ["openai", "google"]

        for provider in all_providers:
            has_auth_config = provider in providers and "api_key" in providers[provider]

            # Check environment variables
            env_var_map = {
                "openai": "OPENAI_API_KEY",
                "google": "GOOGLE_API_KEY",
            }
            has_env_var = bool(os.getenv(env_var_map.get(provider, "")))

            result[provider] = has_auth_config or has_env_var

        return result

    def get_api_key_source(self, provider: str) -> Optional[str]:
        """Get the source of an API key (auth_config, env_var, or dotenv)."""
        env_var_map = {
            "openai": "OPENAI_API_KEY",
            "google": "GOOGLE_API_KEY",
        }

        env_var = env_var_map.get(provider)
        if not env_var:
            return None

        # Check if it's from auth config
        config = self.load_auth_config()
        if config and config.get("providers", {}).get(provider, {}).get("api_key"):
            return "auth_config"

        # Check if it's from environment variable
        if os.getenv(env_var):
            return "environment"

        return None


# Global instance
_env_manager = EnvironmentManager()


def get_environment_manager() -> EnvironmentManager:
    """Get the global environment manager instance."""
    return _env_manager


def load_environment_variables() -> None:
    """Load environment variables from all sources."""
    _env_manager.load_environment_variables()
