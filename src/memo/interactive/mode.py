"""Interactive mode handler for Memo."""

import click

from ..ai.prompts import PromptBuilder
from ..ai.providers import get_ai_provider
from ..config.manager import ConfigManager
from ..git.operations import GitOperations


class InteractiveMode:
    """Handles interactive mode for commit message generation."""

    def __init__(self, config_manager: ConfigManager, git_ops: GitOperations):
        self.config_manager = config_manager
        self.git_ops = git_ops

    def handle_interactive_mode(
        self, commit_message: str, diff_content: str, current_model: str
    ) -> None:
        """Handle interactive mode for commit message generation."""
        while True:
            self._display_message(commit_message)
            choice = self._get_user_choice()

            if choice == "1":
                self._handle_accept(commit_message)
                break
            elif choice == "2":
                result = self._handle_regenerate(diff_content, current_model)
                if result:
                    commit_message, current_model = result
            elif choice == "3":
                self._handle_edit()
                break
            elif choice == "4":
                self._handle_deny()
                break
            else:
                click.echo("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

    def _display_message(self, commit_message: str) -> None:
        """Display the commit message to the user."""
        click.echo("\n" + "=" * 60)
        click.echo("Generated Commit Message:")
        click.echo("=" * 60)
        click.echo(f"\n{commit_message}\n")
        click.echo("=" * 60)

        click.echo("\nWhat would you like to do?")
        click.echo("1. Accept - Commit with this message")
        click.echo("2. Regenerate - Generate a new message")
        click.echo("3. Edit - Open git commit editor (default)")
        click.echo("4. Deny - Exit without committing")

    def _get_user_choice(self) -> str:
        """Get user choice for interactive mode."""
        return click.prompt("\nEnter your choice (1-4)", default="3", type=str)

    def _handle_accept(self, commit_message: str) -> None:
        """Handle accept option - commit with generated message."""
        success, output = self.git_ops.commit_with_message(commit_message)
        if success:
            click.echo(f"\n✅ {output}")
        else:
            click.echo(f"\n❌ {output}")

    def _handle_regenerate(
        self, diff_content: str, current_model: str
    ) -> tuple[str, str] | None:
        """Handle regenerate option - generate new message with same or different model."""
        click.echo("\nAvailable models:")
        click.echo("1. gemini-2.0-flash")
        click.echo("2. gemini-2.5-pro")
        click.echo("3. gpt-4.1-mini")

        model_choice = click.prompt(
            f"\nSelect model (1-3, current: {current_model})", default="1", type=str
        )

        models = {"1": "gemini-2.0-flash", "2": "gemini-2.5-pro", "3": "gpt-4.1-mini"}

        selected_model = models.get(model_choice, current_model)
        click.echo(f"\nRegenerating with {selected_model}...")

        # Generate new message
        config = self.config_manager.load_config()
        ai_provider = get_ai_provider(selected_model)

        if not ai_provider or not ai_provider.is_available():
            click.echo("❌ Selected AI provider is not available. Check your API keys.")
            return None

        prompt_builder = PromptBuilder(config)
        prompt = prompt_builder.build_prompt(diff_content)
        new_message = ai_provider.generate_message(prompt)

        if new_message:
            return new_message, selected_model
        else:
            click.echo("❌ Failed to regenerate message. Keeping current message.")
            return None

    def _handle_edit(self) -> None:
        """Handle edit option - open git commit editor."""
        success, output = self.git_ops.open_commit_editor()
        if success:
            click.echo(f"\n✅ {output}")
        else:
            click.echo(f"\n❌ {output}")

    def _handle_deny(self) -> None:
        """Handle deny option - exit without committing."""
        click.echo("\n❌ Exiting without committing.")
