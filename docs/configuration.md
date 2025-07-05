# Configuration Guide

Memo supports flexible configuration through JSON files that allow you to customize the behavior of the AI-powered commit message generator. This guide covers all aspects of configuration management in Memo.

## Configuration Files

Memo uses a dual-level configuration system:

1. **Project-specific configuration**: `.memo.json` in your project directory
2. **User-global configuration**: `~/.memo.json` in your home directory

The project-specific configuration takes precedence over the user-global configuration, allowing you to customize settings per project while maintaining personal defaults.

## Configuration Structure

### Complete Configuration Schema

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

### Configuration Options

#### `default_model`
- **Type**: String
- **Default**: `"gemini-2.0-flash"`
- **Description**: The AI model to use for generating commit messages
- **Valid Values**:
  - `"gemini-2.0-flash"`: Fast, efficient Google Gemini model (recommended)
  - `"gemini-2.5-pro"`: More advanced Google Gemini model
  - `"gpt-4.1-mini"`: OpenAI GPT model

#### `interactive_mode`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Controls whether to use interactive mode after generating a commit message
- **When enabled**: Shows options to accept, regenerate, edit, or deny the generated message
- **When disabled**: Outputs the commit message directly without prompting

#### `commit_rules`
Configuration for conventional commit message rules:

##### `max_subject_length`
- **Type**: Integer
- **Default**: `72`
- **Description**: Maximum length for commit message subject line
- **Range**: Typically 50-72 characters

##### `require_scope`
- **Type**: Boolean
- **Default**: `false`
- **Description**: Whether to require a scope in commit messages (e.g., `feat(api): add endpoint`)

##### `allowed_types`
- **Type**: Array of strings
- **Default**: `["feat", "fix", "docs", "style", "refactor", "perf", "test", "build", "ci", "chore", "revert"]`
- **Description**: List of allowed commit types following conventional commit standards
- **Standard Types**:
  - `feat`: New features
  - `fix`: Bug fixes
  - `docs`: Documentation changes
  - `style`: Code style changes (formatting, etc.)
  - `refactor`: Code refactoring
  - `perf`: Performance improvements
  - `test`: Adding or updating tests
  - `build`: Build system changes
  - `ci`: CI/CD changes
  - `chore`: Maintenance tasks
  - `revert`: Reverting previous commits

##### `custom_rules`
- **Type**: Array of strings
- **Default**: `[]`
- **Description**: Additional custom rules for commit messages that will be included in the AI prompt
- **Example**: `["Always include ticket number in footer", "Use present tense verbs"]`

#### `project_structure_context`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Whether to include project structure information in the AI prompt
- **When enabled**: Provides context about project organization to generate more relevant commit messages
- **Performance**: May increase AI processing time for large projects

#### `commit_history_analysis`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Whether to analyze commit history to learn project-specific patterns
- **When enabled**: Analyzes recent commits to understand project conventions and generate consistent messages
- **Benefits**: Improves commit message style consistency within the project

## Configuration Management

### Viewing Configuration

Show the complete current configuration:
```bash
memo config show
```

Show a specific configuration value:
```bash
memo config show default_model
memo config show commit_rules.max_subject_length
```

### Setting Configuration

Set a top-level configuration value:
```bash
memo config set default_model gemini-2.5-pro
memo config set interactive_mode false
```

Set nested configuration values using dot notation:
```bash
memo config set commit_rules.max_subject_length 50
memo config set commit_rules.require_scope true
```

### Resetting Configuration

Reset all configuration to defaults:
```bash
memo config reset
```

Reset a specific configuration key:
```bash
memo config reset default_model
memo config reset commit_rules.max_subject_length
```

## Configuration Precedence

Configuration values are resolved in the following order:

1. **Command-line options** (e.g., `--model` flag)
2. **Project-specific configuration** (`.memo.json` in project directory)
3. **User-global configuration** (`~/.memo.json` in home directory)
4. **Built-in defaults**

## Environment Variables

Memo requires API keys for AI providers. Set these environment variables:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export GOOGLE_API_KEY="your-google-api-key"
```

You can also create a `.env` file in your project directory:
```
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-api-key
```

## Configuration Examples

### Minimal Project Configuration

For a simple project with basic customization:
```json
{
  "default_model": "gpt-4.1-mini",
  "commit_rules": {
    "max_subject_length": 50
  }
}
```

### Team Project Configuration

For a team project with strict conventions:
```json
{
  "default_model": "gemini-2.5-pro",
  "interactive_mode": true,
  "commit_rules": {
    "max_subject_length": 72,
    "require_scope": true,
    "allowed_types": ["feat", "fix", "docs", "test", "chore"],
    "custom_rules": [
      "Include ticket number in footer format: Closes #123",
      "Use imperative mood in subject line",
      "Capitalize first letter of subject"
    ]
  },
  "project_structure_context": true,
  "commit_history_analysis": true
}
```

### Performance-Optimized Configuration

For large projects where speed is important:
```json
{
  "default_model": "gemini-2.0-flash",
  "interactive_mode": false,
  "commit_rules": {
    "max_subject_length": 72,
    "require_scope": false
  },
  "project_structure_context": false,
  "commit_history_analysis": false
}
```

### Personal Global Configuration

Example `~/.memo.json` for personal defaults:
```json
{
  "default_model": "gemini-2.0-flash",
  "interactive_mode": true,
  "commit_rules": {
    "max_subject_length": 72,
    "require_scope": false,
    "custom_rules": [
      "Use present tense in commit messages",
      "Keep descriptions concise and clear"
    ]
  }
}
```

## Configuration File Management

### Creating Configuration Files

Create a project-specific configuration:
```bash
echo '{"default_model": "gemini-2.5-pro"}' > .memo.json
```

Create a user-global configuration:
```bash
echo '{"default_model": "gpt-4.1-mini"}' > ~/.memo.json
```

### Configuration Validation

Memo automatically validates configuration files on load. Invalid configurations will fall back to defaults with a warning message.

### Backup and Migration

Since configuration files are simple JSON, you can easily:
- **Backup**: Copy `.memo.json` files
- **Share**: Commit `.memo.json` to version control for team consistency
- **Migrate**: Move configuration files between projects or machines

## Troubleshooting

### Common Configuration Issues

#### Configuration Not Loading
- Check JSON syntax with a validator
- Ensure file permissions allow reading
- Verify file location (project directory vs home directory)

#### Invalid Configuration Values
- Check that model names are spelled correctly
- Ensure boolean values are `true` or `false` (not `"true"` or `"false"`)
- Verify array syntax for `allowed_types` and `custom_rules`

#### API Key Issues
- Ensure environment variables are set correctly
- Check that API keys are valid and have appropriate permissions
- Verify `.env` file format (no spaces around `=`)

### Debugging Configuration

Use the status command to check configuration and API key availability:
```bash
memo status
```

This will show:
- Current configuration values
- API key availability
- Git repository status
- Staged changes status

## Best Practices

1. **Project-specific configuration**: Use `.memo.json` in project repositories to maintain team consistency
2. **Global defaults**: Set personal preferences in `~/.memo.json`
3. **Version control**: Commit `.memo.json` to share team conventions
4. **Security**: Never commit API keys; use environment variables or `.env` files (add `.env` to `.gitignore`)
5. **Testing**: Use `memo config show` to verify configuration before generating commits
6. **Documentation**: Document project-specific rules in your README or contributing guidelines