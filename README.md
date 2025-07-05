# Memo

A CLI tool to generate conventional commit messages using AI, with full awareness
of staged changes and project context.

## Quick Start

### Installation

Using uv (recommended):

```bash
git clone https://github.com/geavenx/memo.git
cd memo
uv tool install .
```

Or with pip:

```bash
git clone https://github.com/geavenx/memo.git
cd memo
pip install .
```

### Basic Usage

1. Stage your changes:

    ```bash
    git add .
    ```

2. Generate a commit message:

    ```bash
    memo generate
    ```

3. Follow the interactive prompts to review, edit, or commit.

## Features

- **AI-Powered Generation**: Uses OpenAI GPT or Google Gemini models to generate meaningful commit messages
- **Context-Aware**: Analyzes staged changes, project structure, and commit history for relevant messages
- **Conventional Commits**: Follows the conventional commit specification
- **Interactive Mode**: Review and edit generated messages before committing
- **Flexible Configuration**: Customize behavior through project-specific or global configuration files
- **Multiple AI Models**: Support for various AI providers and models

## Installation

### Using uv (Recommended)

```bash
git clone https://github.com/geavenx/memo.git
cd memo
uv tool install .
```

### Using pip

```bash
git clone https://github.com/geavenx/memo.git
cd memo
pip install .
```

### Development Installation

```bash
git clone https://github.com/geavenx/memo.git
cd memo
uv sync
```

## API Keys Setup

Memo provides flexible API key management for AI providers.

### Option 1: CLI Management (Recommended)

Use the built-in authentication commands for secure, persistent storage:

```bash
# Set your API keys
memo auth set openai sk-your-openai-api-key
memo auth set google your-google-api-key

# Verify configuration
memo auth list
```

### Option 2: Environment Variables

```bash
export OPENAI_API_KEY="your-openai-api-key"
export GOOGLE_API_KEY="your-google-api-key"
```

### Option 3: .env Files

Create a `.env` file in your project, home directory, or `~/.memo/`:

```bash
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-api-key
```

**Note**: CLI-managed keys work anywhere you run memo, even when installed globally with `uv tool install` or `pip install`.

## Usage

### Generate Commit Messages

Basic usage:

```bash
memo generate
```

With specific AI model:

```bash
memo generate --model gpt-4.1-mini
memo generate --model gemini-2.5-pro
```

Non-interactive mode (output only):

```bash
memo generate --no-interactive
```

### Configuration Management

View current configuration:

```bash
memo config show
```

Set configuration values:

```bash
memo config set default_model gemini-2.5-pro
memo config set commit_rules.max_subject_length 50
```

Reset configuration:

```bash
memo config reset
```

### API Key Management

Manage API keys securely through the CLI:

```bash
# Set API keys
memo auth set openai sk-your-api-key
memo auth set google your-google-api-key

# View configured keys (masked)
memo auth show
memo auth show openai

# List provider status
memo auth list

# Remove keys
memo auth remove openai
```

### System Status

Check system status:

```bash
memo status
```

Shows git repository status, configuration, AI provider availability, and authentication status.

## Configuration

Memo supports flexible configuration through JSON files. You can configure:

- AI model selection
- Interactive mode behavior
- Conventional commit rules
- Project structure context
- Commit history analysis

### Configuration Files

- **Project-specific**: `.memo.json` in your project directory
- **User-global**: `~/.memo.json` in your home directory

### Quick Configuration Example

Create a `.memo.json` file in your project:

```json
{
  "default_model": "gemini-2.5-pro",
  "interactive_mode": true,
  "commit_rules": {
    "max_subject_length": 72,
    "require_scope": true
  }
}
```

For comprehensive configuration options and examples, see the [Configuration Guide](docs/configuration.md).

## Supported AI Models

- **gemini-2.0-flash** (default): Fast, efficient Google Gemini model
- **gemini-2.5-pro**: Advanced Google Gemini model
- **gpt-4.1-mini**: OpenAI GPT model

## Interactive Mode

When enabled (default), Memo presents options after generating a commit message:

1. **Accept**: Commit immediately with the generated message
2. **Regenerate**: Generate a new message
3. **Edit**: Open git's commit editor with the generated message
4. **Deny**: Exit without committing

## Examples

### Basic Workflow

```bash
# Make changes to your code
git add .
memo generate
# Follow interactive prompts
```

### Team Project Setup

```bash
# Create project configuration
echo '{
  "default_model": "gemini-2.5-pro",
  "commit_rules": {
    "require_scope": true,
    "max_subject_length": 72
  }
}' > .memo.json

# Commit the configuration
git add .memo.json
git commit -m "feat: add memo configuration for team standards"
```

### Scripting

```bash
# Non-interactive mode for scripts
memo generate --no-interactive > commit_message.txt
git commit -F commit_message.txt
```

## Development

### Prerequisites

- Python 3.11+
- uv package manager

### Setup

```bash
git clone <repository-url>
cd memo
uv sync
```

### Running Tests

```bash
uv run pytest tests/
```

### Code Quality

```bash
# Linting
uvx ruff check --fix .

# Formatting
uvx ruff format .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests and linting
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- For usage questions, see the [Configuration Guide](docs/configuration.md)
- For detailed usage examples, see [docs/usage.md](docs/usage.md)
- For bugs and feature requests, open an issue
