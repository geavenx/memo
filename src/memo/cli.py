"""Main CLI interface for Memo."""

import json
from typing import Optional

import click

from .ai.prompts import PromptBuilder
from .ai.providers import get_ai_provider
from .config import ConfigManager
from .git.operations import GitOperations
from .interactive.mode import InteractiveMode


@click.group()
@click.version_option(version="0.1.0", prog_name="Memo")
def cli() -> None:
    """Memo - AI-powered conventional commit message generator."""
    pass


@cli.command()
@click.option(
    "--model",
    default=None,
    help="AI model to use for generating commit messages. Options: gemini-2.0-flash, gemini-2.5-pro, gpt-4.1-mini",
)
@click.option(
    "--no-interactive",
    is_flag=True,
    help="Disable interactive mode and just output the commit message",
)
def generate(model: Optional[str], no_interactive: bool) -> None:
    """Generate a conventional commit message."""
    config_manager = ConfigManager()
    git_ops = GitOperations()

    # Check if we're in a git repository
    if not git_ops.is_git_repository():
        click.echo(
            "❌ Error: Not a git repository. Initialize git first with 'git init'."
        )
        return

    # Load configuration
    config = config_manager.load_config()

    # Use provided model or default from config
    if model is None:
        model = config["default_model"]

        if model is None:
            return

    # Get staged diff
    diff_content, error = git_ops.get_staged_diff()
    if error:
        click.echo(f"❌ {error}")
        return

    # Get AI provider
    ai_provider = get_ai_provider(model)
    if not ai_provider:
        return

    if not ai_provider.is_available():
        click.echo(
            f"❌ Error: {model} provider is not available. Check your API key configuration."
        )
        return

    # Build prompt and generate message
    prompt_builder = PromptBuilder(config)
    prompt = prompt_builder.build_prompt(diff_content)
    commit_message = ai_provider.generate_message(prompt)

    if not commit_message:
        click.echo("❌ Failed to generate commit message.")
        return

    # Handle interactive mode or just output message
    interactive_enabled = config["interactive_mode"] and not no_interactive

    if interactive_enabled:
        interactive_mode = InteractiveMode(config_manager, git_ops)
        interactive_mode.handle_interactive_mode(commit_message, diff_content, model)
    else:
        click.echo(commit_message)


@cli.command()
@click.argument("action", type=click.Choice(["show", "set", "reset"]))
@click.argument("key", required=False)
@click.argument("value", required=False)
def config(action: str, key: Optional[str], value: Optional[str]) -> None:
    """Manage configuration. Actions: show, set, reset."""
    config_manager = ConfigManager()

    if action == "show":
        if key:
            config_value = config_manager.get_config_value(key)
            if config_value is not None:
                click.echo(f"{key}: {config_value}")
            else:
                click.echo(f"Configuration key '{key}' not found.")
        else:
            current_config = config_manager.load_config()
            click.echo("Current configuration:")
            click.echo(json.dumps(current_config, indent=2))

    elif action == "set":
        if not key or not value:
            click.echo("Usage: memo config set <key> <value>")
            click.echo("Example: memo config set default_model gemini-2.5-pro")
            click.echo("Example: memo config set commit_rules.max_subject_length 50")
            return

        if config_manager.set_config_value(key, value):
            click.echo(f"✅ Configuration updated: {key} = {value}")
        else:
            click.echo("❌ Failed to save configuration.")

    elif action == "reset":
        if config_manager.reset_config(key):
            if key:
                click.echo(f"✅ Configuration key '{key}' reset to default.")
            else:
                click.echo("✅ Configuration reset to defaults.")
        else:
            if key:
                click.echo(f"❌ Configuration key '{key}' not found.")
            else:
                click.echo("❌ Failed to save configuration.")


@cli.command()
def status() -> None:
    """Show the current status of Memo."""
    config_manager = ConfigManager()
    git_ops = GitOperations()

    click.echo("🔧 Memo Status")
    click.echo("=" * 50)

    # Git repository status
    if git_ops.is_git_repository():
        click.echo("✅ Git repository: Found")

        # Check for staged changes
        diff_content, error = git_ops.get_staged_diff()
        if diff_content:
            click.echo("✅ Staged changes: Ready for commit")
        else:
            click.echo("⚠️  Staged changes: None found")
    else:
        click.echo("❌ Git repository: Not found")

    # Configuration
    config = config_manager.load_config()
    click.echo(f"🤖 Default model: {config['default_model']}")
    click.echo(
        f"🔄 Interactive mode: {'Enabled' if config['interactive_mode'] else 'Disabled'}"
    )

    # AI provider availability
    click.echo("\n🔌 AI Provider Status:")
    for model_name in ["gemini-2.0-flash", "gemini-2.5-pro", "gpt-4.1-mini"]:
        provider = get_ai_provider(model_name)
        if provider and provider.is_available():
            click.echo(f"✅ {model_name}: Available")
        else:
            click.echo(f"❌ {model_name}: Not available (check API key)")


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
