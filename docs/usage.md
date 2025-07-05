# Memo Usage Guide

## Installation

Install Memo using pip:

```bash
pip install .
```

Or for development:

```bash
pip install -e .
```

## Basic Usage

### Generate Commit Messages

Generate a commit message for your staged changes:

```bash
memo generate
```

Generate with a specific AI model:

```bash
memo generate --model gpt-4.1-mini
memo generate --model gemini-2.5-pro
```

Generate without interactive mode (just output the message):

```bash
memo generate --no-interactive
```

### Configuration Management

Show current configuration:

```bash
memo config show
```

Show specific configuration value:

```bash
memo config show default_model
```

Set configuration values:

```bash
memo config set default_model gemini-2.5-pro
memo config set interactive_mode false
memo config set commit_rules.max_subject_length 50
```

Reset configuration to defaults:

```bash
memo config reset
memo config reset default_model
```

### System Status

Check the status of Memo:

```bash
memo status
```

This shows:

- Git repository status
- Staged changes status
- Current configuration
- AI provider availability

## Configuration

Memo supports project-specific and user-global configuration files.

### Configuration File Locations

1. **Project-specific**: `.memo.json` in the current directory
2. **User-global**: `~/.memo.json` in your home directory

Project-specific configuration takes precedence over user-global configuration.

### Configuration Options

```json
{
  "default_model": "gemini-2.0-flash",
  "interactive_mode": true,
  "commit_rules": {
    "max_subject_length": 72,
    "require_scope": false,
    "allowed_types": [
      "feat", "fix", "docs", "style", "refactor", 
      "perf", "test", "build", "ci", "chore", "revert"
    ],
    "custom_rules": []
  },
  "project_structure_context": true,
  "commit_history_analysis": true
}
```

#### Configuration Options Explained

- **default_model**: Default AI model to use (`gemini-2.0-flash`, `gemini-2.5-pro`, `gpt-4.1-mini`)
- **interactive_mode**: Enable interactive mode for reviewing/editing commit messages
- **commit_rules.max_subject_length**: Maximum length for commit message subject line
- **commit_rules.require_scope**: Whether scope is required in commit messages
- **commit_rules.allowed_types**: List of allowed commit types
- **commit_rules.custom_rules**: Additional custom rules for commit messages
- **project_structure_context**: Include project structure in AI prompt
- **commit_history_analysis**: Analyze commit history to learn patterns

## Interactive Mode

When interactive mode is enabled (default), after generating a commit message, you'll see:

```
============================================================
Generated Commit Message:
============================================================

feat(auth): add user authentication system

============================================================

What would you like to do?
1. Accept - Commit with this message
2. Regenerate - Generate a new message
3. Edit - Open git commit editor (default)
4. Deny - Exit without committing

Enter your choice (1-4) [3]:
```

### Options Explained

1. **Accept**: Commits immediately with the generated message
2. **Regenerate**: Generates a new message, optionally with a different AI model
3. **Edit**: Opens the standard git commit editor with the generated message as a starting point
4. **Deny**: Exits without committing

## Environment Variables

Set up your AI provider API keys:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export GOOGLE_API_KEY="your-google-api-key"
```

You can also use a `.env` file in your project directory:

```bash
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-api-key
```

## AI Models

### Supported Models

- **gemini-2.0-flash** (default): Fast, efficient Google Gemini model
- **gemini-2.5-pro**: More advanced Google Gemini model
- **gpt-4.1-mini**: OpenAI GPT model

### Model Selection

Models are automatically selected based on availability and configuration:

1. Command line `--model` option
2. Configuration file `default_model` setting
3. Built-in default (`gemini-2.0-flash`)

## Features

### Intelligent Context Analysis

Memo provides intelligent context to the AI models:

- **Commit History Analysis**: Learns from your repository's commit patterns
- **Multi-file Analysis**: Understands the scope of changes across multiple files
- **Project Structure**: Provides context about your project's organization
- **Diff Analysis**: Analyzes the actual changes to generate relevant messages

### Conventional Commit Format

Generated messages follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Customization

- Configure allowed commit types
- Set custom commit message rules
- Adjust maximum subject line length
- Enable/disable various context features

## Examples

### Basic Workflow

```bash
# Stage your changes
git add .

# Generate and commit
memo generate

# Follow interactive prompts to review/edit/commit
```

### Non-interactive Workflow

```bash
# Stage your changes
git add .

# Generate message only
memo generate --no-interactive

# Copy the output and use with git commit
git commit -m "feat(auth): add user authentication system"
```

### Project Configuration

Create a `.memo.json` file in your project:

```json
{
  "default_model": "gpt-4.1-mini",
  "commit_rules": {
    "require_scope": true,
    "max_subject_length": 50,
    "custom_rules": [
      "Always include ticket number in footer",
      "Use present tense for all commit messages"
    ]
  }
}
```

## Troubleshooting

### Common Issues

#### **"Not a git repository"**

- Make sure you're in a git repository: `git init`

#### **"No staged changes found"**

- Stage your changes first: `git add .`

#### **"API key not available"**

- Set up your API keys in environment variables or `.env` file
- Check with `memo status` to see which providers are available

#### **"Error generating commit message"**

- Check your internet connection
- Verify your API keys are valid
- Try a different AI model

### Getting Help

- Use `memo --help` for general help
- Use `memo <command> --help` for command-specific help
- Check `memo status` to diagnose configuration issues

