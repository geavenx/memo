"""Tests for environment management."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch


from memo.config.environment import EnvironmentManager


class TestEnvironmentManager:
    """Test cases for EnvironmentManager."""

    def test_auth_config_path_creation(self):
        """Test that auth config path is created correctly."""
        env_manager = EnvironmentManager()
        auth_path = env_manager.get_auth_config_path()
        
        assert auth_path.name == "auth.json"
        assert auth_path.parent.name == "memo"
        assert "share" in str(auth_path)

    def test_set_and_get_api_key(self):
        """Test setting and getting API keys."""
        env_manager = EnvironmentManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            auth_path = Path(temp_dir) / "auth.json"
            
            with patch.object(env_manager, 'get_auth_config_path', return_value=auth_path):
                # Test setting API key
                success = env_manager.set_api_key("openai", "test-key-123")
                assert success
                
                # Test getting API key
                api_key = env_manager.get_api_key("openai")
                assert api_key == "test-key-123"
                
                # Test that auth.json was created with correct structure
                assert auth_path.exists()
                with open(auth_path, 'r') as f:
                    config = json.load(f)
                    assert config["providers"]["openai"]["api_key"] == "test-key-123"

    def test_remove_api_key(self):
        """Test removing API keys."""
        env_manager = EnvironmentManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            auth_path = Path(temp_dir) / "auth.json"
            
            with patch.object(env_manager, 'get_auth_config_path', return_value=auth_path):
                # Set an API key first
                env_manager.set_api_key("openai", "test-key-123")
                
                # Remove the API key
                success = env_manager.remove_api_key("openai")
                assert success
                
                # Verify it's removed
                api_key = env_manager.get_api_key("openai")
                assert api_key is None

    def test_list_configured_providers(self):
        """Test listing configured providers."""
        env_manager = EnvironmentManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            auth_path = Path(temp_dir) / "auth.json"
            
            with patch.object(env_manager, 'get_auth_config_path', return_value=auth_path):
                # Mock empty environment variables for clean test
                with patch.dict(os.environ, {"OPENAI_API_KEY": "", "GOOGLE_API_KEY": ""}, clear=False):
                    # Initially no providers configured
                    providers = env_manager.list_configured_providers()
                    assert not providers["openai"]
                    assert not providers["google"]
                    
                    # Set OpenAI key
                    env_manager.set_api_key("openai", "test-key-123")
                    
                    # Clear cache to test fresh load
                    env_manager._auth_config_cache = None
                    
                    providers = env_manager.list_configured_providers()
                    assert providers["openai"]
                    assert not providers["google"]

    def test_invalid_provider(self):
        """Test setting API key for invalid provider."""
        env_manager = EnvironmentManager()
        
        success = env_manager.set_api_key("invalid", "test-key")
        assert not success

    def test_get_api_key_source(self):
        """Test getting API key source."""
        env_manager = EnvironmentManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            auth_path = Path(temp_dir) / "auth.json"
            
            with patch.object(env_manager, 'get_auth_config_path', return_value=auth_path):
                # Test auth config source
                env_manager.set_api_key("openai", "test-key-123")
                source = env_manager.get_api_key_source("openai")
                assert source == "auth_config"
                
                # Test environment variable source
                with patch.dict(os.environ, {"GOOGLE_API_KEY": "env-key"}):
                    source = env_manager.get_api_key_source("google")
                    assert source == "environment"

    def test_environment_variable_priority(self):
        """Test that environment variables have priority over auth config."""
        env_manager = EnvironmentManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            auth_path = Path(temp_dir) / "auth.json"
            
            with patch.object(env_manager, 'get_auth_config_path', return_value=auth_path):
                # Set API key in auth config
                env_manager.set_api_key("openai", "auth-key-123")
                
                # Mock environment variable (higher priority)
                with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key-456"}):
                    # Create new instance to test loading
                    new_env_manager = EnvironmentManager()
                    
                    with patch.object(new_env_manager, 'get_auth_config_path', return_value=auth_path):
                        new_env_manager.load_environment_variables()
                        
                        # Environment variable should take precedence
                        assert os.getenv("OPENAI_API_KEY") == "env-key-456"