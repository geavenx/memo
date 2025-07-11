"""Main CLI interface for Memo."""

import json
from typing import Optional

import click

from .ai.prompts import PromptBuilder
from .ai.providers import get_ai_provider
from .config import ConfigManager
from .config.environment import get_environment_manager
from .git.operations import GitOperations
from .interactive.mode import InteractiveMode


@click.group()
@click.version_option(version="1.0.0", prog_name="Memo")
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
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Show the prompt sent to the AI model",
)
def generate(model: Optional[str], no_interactive: bool, verbose: bool) -> None:
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
    
    # Show prompt if verbose mode is enabled
    if verbose:
        click.echo(f"\n{'='*60}")
        click.echo(f"PROMPT SENT TO {model.upper()}:")
        click.echo(f"{'='*60}")
        click.echo(prompt)
        click.echo(f"{'='*60}\n")
    
    commit_message = ai_provider.generate_message(prompt)

    if not commit_message:
        click.echo("❌ Failed to generate commit message.")
        return

    # Handle interactive mode or just output message
    interactive_enabled = config["interactive_mode"] and not no_interactive

    if interactive_enabled:
        interactive_mode = InteractiveMode(config_manager, git_ops, verbose)
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

    # Auth configuration status
    click.echo("\n🔐 Authentication Configuration:")
    env_manager = get_environment_manager()
    providers = env_manager.list_configured_providers()

    for provider, configured in providers.items():
        if configured:
            source = env_manager.get_api_key_source(provider)
            click.echo(f"✅ {provider}: Configured (source: {source})")
        else:
            click.echo(f"❌ {provider}: Not configured")


@cli.group()
def auth() -> None:
    """Manage API keys for AI providers."""
    pass


@auth.command()
@click.argument("provider", type=click.Choice(["openai", "google"]))
@click.argument("api_key")
def set(provider: str, api_key: str) -> None:
    """Set API key for a provider."""
    env_manager = get_environment_manager()

    if env_manager.set_api_key(provider, api_key):
        click.echo(f"✅ API key set for {provider}")
    else:
        click.echo(f"❌ Failed to set API key for {provider}")


@auth.command()
@click.argument("provider", type=click.Choice(["openai", "google"]), required=False)
def show(provider: Optional[str]) -> None:
    """Show configured API keys (masked for security)."""
    env_manager = get_environment_manager()

    if provider:
        api_key = env_manager.get_api_key(provider)
        source = env_manager.get_api_key_source(provider)

        if api_key:
            masked_key = (
                api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
            )
            click.echo(f"{provider}: {masked_key} (source: {source})")
        else:
            click.echo(f"{provider}: Not configured")
    else:
        # Show all providers
        providers = env_manager.list_configured_providers()
        click.echo("API Key Configuration:")
        click.echo("=" * 40)

        for prov, configured in providers.items():
            if configured:
                api_key = env_manager.get_api_key(prov)
                source = env_manager.get_api_key_source(prov)

                # Check if key is from auth config or environment
                if api_key:
                    masked_key = (
                        api_key[:8] + "..." + api_key[-4:]
                        if len(api_key) > 12
                        else "***"
                    )
                    click.echo(f"✅ {prov}: {masked_key} (source: {source})")
                else:
                    click.echo(f"✅ {prov}: Configured via environment")
            else:
                click.echo(f"❌ {prov}: Not configured")


@auth.command()
@click.argument("provider", type=click.Choice(["openai", "google"]))
def remove(provider: str) -> None:
    """Remove API key for a provider."""
    env_manager = get_environment_manager()

    if env_manager.remove_api_key(provider):
        click.echo(f"✅ API key removed for {provider}")
    else:
        click.echo(f"❌ No API key found for {provider} in auth config")


@auth.command()
def list() -> None:
    """List all configured providers."""
    env_manager = get_environment_manager()
    providers = env_manager.list_configured_providers()

    click.echo("Provider Status:")
    click.echo("=" * 30)

    for provider, configured in providers.items():
        status = "✅ Configured" if configured else "❌ Not configured"
        source = env_manager.get_api_key_source(provider) if configured else "none"
        click.echo(f"{provider}: {status} (source: {source})")


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
