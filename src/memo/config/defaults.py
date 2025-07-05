"""Default configuration for Memo."""

from typing import Any, Dict


def get_default_config() -> Dict[str, Any]:
    """Get the default configuration."""
    return {
        "default_model": "gemini-2.0-flash",
        "interactive_mode": True,
        "commit_rules": {
            "max_subject_length": 72,
            "require_scope": False,
            "allowed_types": [
                "feat",
                "fix",
                "docs",
                "style",
                "refactor",
                "perf",
                "test",
                "build",
                "ci",
                "chore",
                "revert",
            ],
            "custom_rules": [],
        },
        "project_structure_context": True,
        "commit_history_analysis": True,
    }
