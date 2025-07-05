"""Tests for configuration management."""

import tempfile
from pathlib import Path
from unittest.mock import patch


from memo.config import ConfigManager, get_default_config


class TestConfigManager:
    """Test cases for ConfigManager."""

    def test_get_default_config(self):
        """Test that default config has expected structure."""
        config = get_default_config()

        assert "default_model" in config
        assert "interactive_mode" in config
        assert "commit_rules" in config
        assert "project_structure_context" in config
        assert "commit_history_analysis" in config

        # Test commit rules structure
        commit_rules = config["commit_rules"]
        assert "max_subject_length" in commit_rules
        assert "require_scope" in commit_rules
        assert "allowed_types" in commit_rules
        assert "custom_rules" in commit_rules

    def test_load_config_no_file(self):
        """Test loading config when no file exists."""
        manager = ConfigManager()

        with patch.object(manager, "get_config_path") as mock_path:
            mock_path.return_value = Path("/nonexistent/path/.memo.json")
            config = manager.load_config()

            # Should return default config
            assert config == get_default_config()

    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        manager = ConfigManager()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        with patch.object(manager, "get_config_path") as mock_path:
            mock_path.return_value = temp_path

            # Test saving
            test_config = {"default_model": "test-model", "interactive_mode": False}
            result = manager.save_config(test_config)
            assert result is True

            # Test loading
            manager._config_cache = None  # Clear cache
            loaded_config = manager.load_config()

            # Should merge with defaults
            expected = get_default_config()
            expected.update(test_config)
            assert loaded_config == expected

        # Cleanup
        temp_path.unlink()

    def test_set_config_value(self):
        """Test setting configuration values."""
        manager = ConfigManager()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        with patch.object(manager, "get_config_path") as mock_path:
            mock_path.return_value = temp_path

            # Test simple key
            result = manager.set_config_value("default_model", "test-model")
            assert result is True

            # Test nested key
            result = manager.set_config_value("commit_rules.max_subject_length", "50")
            assert result is True

            # Verify values were set
            config = manager.load_config()
            assert config["default_model"] == "test-model"
            assert config["commit_rules"]["max_subject_length"] == 50

        # Cleanup
        temp_path.unlink()

    def test_get_config_value(self):
        """Test getting configuration values."""
        manager = ConfigManager()
        manager._config_cache = {
            "default_model": "test-model",
            "commit_rules": {"max_subject_length": 72},
        }

        # Test simple key
        value = manager.get_config_value("default_model")
        assert value == "test-model"

        # Test nested key
        value = manager.get_config_value("commit_rules.max_subject_length")
        assert value == 72

        # Test nonexistent key
        value = manager.get_config_value("nonexistent")
        assert value is None

    def test_reset_config(self):
        """Test resetting configuration."""
        manager = ConfigManager()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        with patch.object(manager, "get_config_path") as mock_path:
            mock_path.return_value = temp_path

            # Set some custom values
            manager.set_config_value("default_model", "custom-model")
            manager.set_config_value("interactive_mode", False)

            # Reset everything
            result = manager.reset_config()
            assert result is True

            # Should be back to defaults
            config = manager.load_config()
            assert config == get_default_config()

        # Cleanup
        temp_path.unlink()
