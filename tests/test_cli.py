"""Tests for CLI interface."""

from unittest.mock import patch, MagicMock

from click.testing import CliRunner

from memo.cli import cli


class TestCLI:
    """Test cases for CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_help(self):
        """Test CLI help output."""
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Memo" in result.output
        assert "generate" in result.output
        assert "config" in result.output
        assert "status" in result.output

    @patch("memo.cli.GitOperations")
    @patch("memo.cli.ConfigManager")
    @patch("memo.cli.get_ai_provider")
    def test_generate_command_success(
        self, mock_get_provider, mock_config_manager, mock_git_ops
    ):
        """Test successful generate command."""
        # Setup mocks
        mock_git = mock_git_ops.return_value
        mock_git.is_git_repository.return_value = True
        mock_git.get_staged_diff.return_value = ("diff content", None)

        mock_config = mock_config_manager.return_value
        mock_config.load_config.return_value = {
            "default_model": "gemini-2.0-flash",
            "interactive_mode": False,
            "commit_rules": {
                "allowed_types": ["feat", "fix"],
                "max_subject_length": 72,
                "require_scope": False,
                "custom_rules": [],
            },
            "project_structure_context": True,
            "commit_history_analysis": True,
        }

        mock_provider = MagicMock()
        mock_provider.is_available.return_value = True
        mock_provider.generate_message.return_value = "feat: add new feature"
        mock_get_provider.return_value = mock_provider

        # Run command
        result = self.runner.invoke(cli, ["generate", "--no-interactive"])

        assert result.exit_code == 0
        assert "feat: add new feature" in result.output

    @patch("memo.cli.GitOperations")
    def test_generate_command_not_git_repo(self, mock_git_ops):
        """Test generate command when not in a git repository."""
        mock_git = mock_git_ops.return_value
        mock_git.is_git_repository.return_value = False

        result = self.runner.invoke(cli, ["generate"])

        assert result.exit_code == 0
        assert "Not a git repository" in result.output

    @patch("memo.cli.GitOperations")
    @patch("memo.cli.ConfigManager")
    def test_generate_command_no_staged_changes(
        self, mock_config_manager, mock_git_ops
    ):
        """Test generate command with no staged changes."""
        mock_git = mock_git_ops.return_value
        mock_git.is_git_repository.return_value = True
        mock_git.get_staged_diff.return_value = (None, "No staged changes found")

        mock_config = mock_config_manager.return_value
        mock_config.load_config.return_value = {"default_model": "gemini-2.0-flash"}

        result = self.runner.invoke(cli, ["generate"])

        assert result.exit_code == 0
        assert "No staged changes found" in result.output

    @patch("memo.cli.ConfigManager")
    def test_config_show_command(self, mock_config_manager):
        """Test config show command."""
        mock_config = mock_config_manager.return_value
        mock_config.load_config.return_value = {
            "default_model": "gemini-2.0-flash",
            "interactive_mode": True,
        }

        result = self.runner.invoke(cli, ["config", "show"])

        assert result.exit_code == 0
        assert "default_model" in result.output
        assert "gemini-2.0-flash" in result.output

    @patch("memo.cli.ConfigManager")
    def test_config_set_command(self, mock_config_manager):
        """Test config set command."""
        mock_config = mock_config_manager.return_value
        mock_config.set_config_value.return_value = True

        result = self.runner.invoke(
            cli, ["config", "set", "default_model", "gpt-4.1-mini"]
        )

        assert result.exit_code == 0
        assert "Configuration updated" in result.output
        mock_config.set_config_value.assert_called_once_with(
            "default_model", "gpt-4.1-mini"
        )

    @patch("memo.cli.ConfigManager")
    def test_config_reset_command(self, mock_config_manager):
        """Test config reset command."""
        mock_config = mock_config_manager.return_value
        mock_config.reset_config.return_value = True

        result = self.runner.invoke(cli, ["config", "reset"])

        assert result.exit_code == 0
        assert "Configuration reset to defaults" in result.output
        mock_config.reset_config.assert_called_once_with(None)

    @patch("memo.cli.GitOperations")
    @patch("memo.cli.ConfigManager")
    @patch("memo.cli.get_ai_provider")
    def test_status_command(self, mock_get_provider, mock_config_manager, mock_git_ops):
        """Test status command."""
        # Setup mocks
        mock_git = mock_git_ops.return_value
        mock_git.is_git_repository.return_value = True
        mock_git.get_staged_diff.return_value = ("diff content", None)

        mock_config = mock_config_manager.return_value
        mock_config.load_config.return_value = {
            "default_model": "gemini-2.0-flash",
            "interactive_mode": True,
        }

        mock_provider = MagicMock()
        mock_provider.is_available.return_value = True
        mock_get_provider.return_value = mock_provider

        # Run command
        result = self.runner.invoke(cli, ["status"])

        assert result.exit_code == 0
        assert "🔧 Memo Status" in result.output
        assert "Git repository: Found" in result.output
        assert "Default model: gemini-2.0-flash" in result.output
