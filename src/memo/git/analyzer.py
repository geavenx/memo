"""Git history and diff analysis for Memo."""

import subprocess
from typing import Any, Dict


class CommitHistoryAnalyzer:
    """Analyzes git commit history to understand patterns."""

    def analyze_commit_history(self, limit: int = 20) -> Dict[str, Any]:
        """Analyze recent commit messages to understand patterns."""
        try:
            result = subprocess.run(
                ["git", "log", f"--max-count={limit}", "--pretty=format:%s"],
                capture_output=True,
                text=True,
                check=True,
            )

            if not result.stdout.strip():
                return {"types": {}, "scopes": {}, "avg_length": 0, "examples": []}

            commits = result.stdout.strip().split("\n")

            # Analyze patterns
            patterns = {
                "types": {},
                "scopes": {},
                "avg_length": 0,
                "has_scope_pattern": 0,
                "examples": [],
            }

            valid_commits = []
            for commit in commits:
                commit = commit.strip()
                if commit and not commit.startswith("Merge"):
                    valid_commits.append(commit)

                    # Extract type and scope if present
                    if ":" in commit:
                        type_part = commit.split(":")[0].strip()
                        if "(" in type_part and ")" in type_part:
                            commit_type = type_part.split("(")[0].strip()
                            scope = type_part.split("(")[1].split(")")[0].strip()
                            patterns["scopes"][scope] = (
                                patterns["scopes"].get(scope, 0) + 1
                            )
                            patterns["has_scope_pattern"] += 1
                        else:
                            commit_type = type_part.strip()

                        patterns["types"][commit_type] = (
                            patterns["types"].get(commit_type, 0) + 1
                        )

            if valid_commits:
                patterns["avg_length"] = sum(len(c) for c in valid_commits) / len(
                    valid_commits
                )
                patterns["examples"] = valid_commits[:5]  # Take top 5 as examples

            return patterns

        except (subprocess.CalledProcessError, FileNotFoundError):
            return {"types": {}, "scopes": {}, "avg_length": 0, "examples": []}


class DiffAnalyzer:
    """Analyzes git diffs to provide context for commit messages."""

    def analyze_diff_context(self, diff_content: str) -> Dict[str, Any]:
        """Analyze the diff to provide better context for multi-file changes."""
        lines = diff_content.split("\n")

        analysis = {
            "files_changed": [],
            "change_summary": {
                "additions": 0,
                "deletions": 0,
                "files_modified": 0,
                "new_files": 0,
                "deleted_files": 0,
            },
            "file_types": {},
            "is_large_change": False,
        }

        current_file = None

        for line in lines:
            # Track file changes
            if line.startswith("diff --git"):
                parts = line.split()
                if len(parts) >= 4:
                    file_path = parts[3][2:]  # Remove 'b/' prefix
                    analysis["files_changed"].append(file_path)
                    current_file = file_path

                    # Track file types
                    if "." in file_path:
                        ext = file_path.split(".")[-1]
                        analysis["file_types"][ext] = (
                            analysis["file_types"].get(ext, 0) + 1
                        )

            elif line.startswith("new file mode"):
                analysis["change_summary"]["new_files"] += 1

            elif line.startswith("deleted file mode"):
                analysis["change_summary"]["deleted_files"] += 1

            elif line.startswith("+++") or line.startswith("---"):
                if current_file and not line.endswith("/dev/null"):
                    analysis["change_summary"]["files_modified"] += 1

            elif line.startswith("+") and not line.startswith("+++"):
                analysis["change_summary"]["additions"] += 1

            elif line.startswith("-") and not line.startswith("---"):
                analysis["change_summary"]["deletions"] += 1

        # Remove duplicates
        analysis["files_changed"] = list(set(analysis["files_changed"]))

        # Determine if it's a large change
        total_changes = (
            analysis["change_summary"]["additions"]
            + analysis["change_summary"]["deletions"]
        )
        analysis["is_large_change"] = (
            total_changes > 50 or len(analysis["files_changed"]) > 5
        )

        return analysis
