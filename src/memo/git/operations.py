"""Git operations for Memo."""

import subprocess
from typing import Optional, Tuple


class GitOperations:
    """Handles git operations for Memo."""

    def get_staged_diff(self) -> Tuple[Optional[str], Optional[str]]:
        """Get the staged git diff."""
        try:
            result = subprocess.run(
                ["git", "diff", "--staged"], capture_output=True, text=True, check=True
            )

            if not result.stdout.strip():
                return (
                    None,
                    "No staged changes found. Stage your changes first with 'git add'.",
                )

            return result.stdout, result.stderr if result.stderr else None

        except subprocess.CalledProcessError as err:
            return None, f"Error running git command: {err}"
        except FileNotFoundError:
            return (
                None,
                "Error: Git command not found. Make sure git is installed in your system before you continue.",
            )

    def commit_with_message(self, message: str) -> Tuple[bool, str]:
        """Commit staged changes with the given message."""
        try:
            result = subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True,
                text=True,
                check=True,
            )

            output = result.stdout if result.stdout else "Committed successfully!"
            return True, output

        except subprocess.CalledProcessError as err:
            error_msg = f"Error committing: {err}"
            if err.stderr:
                error_msg += f"\n{err.stderr}"
            return False, error_msg

    def open_commit_editor(self) -> Tuple[bool, str]:
        """Open the git commit editor."""
        try:
            subprocess.run(["git", "commit"], check=True)
            return True, "Commit process completed!"

        except subprocess.CalledProcessError as err:
            return False, f"Git commit editor exited with error: {err}"

    def is_git_repository(self) -> bool:
        """Check if the current directory is a git repository."""
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
