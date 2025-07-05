"""Prompt building for AI commit message generation."""

from typing import Any, Dict

from ..git.analyzer import CommitHistoryAnalyzer, DiffAnalyzer
from ..utils.project import ProjectStructureAnalyzer


class PromptBuilder:
    """Builds AI prompts for commit message generation."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.commit_analyzer = CommitHistoryAnalyzer()
        self.diff_analyzer = DiffAnalyzer()
        self.project_analyzer = ProjectStructureAnalyzer()

    def build_prompt(self, diff_content: str) -> str:
        """Build a comprehensive prompt for AI commit message generation."""
        rules = self.config["commit_rules"]

        # Build dynamic prompt based on configuration
        prompt = f"""Generate a conventional commit message based on the code changes below.

RULES:
1. Use format: <type>(<scope>): <subject>
2. Types: {", ".join(rules["allowed_types"])}
3. Keep it simple - most commits should be one line
4. Focus on WHY the change was made, not WHAT files changed
5. Use imperative mood ("add" not "added")
6. Subject line ≤ {rules["max_subject_length"]} characters
7. Only add body/footer if the change is complex or breaking"""

        if rules["require_scope"]:
            prompt += "\n8. Scope is REQUIRED - always include a scope in parentheses"

        if rules["custom_rules"]:
            prompt += "\n\nCUSTOM RULES:"
            for i, rule in enumerate(rules["custom_rules"], 9):
                prompt += f"\n{i}. {rule}"

        # Add commit history analysis if enabled
        if self.config.get("commit_history_analysis", True):
            history = self.commit_analyzer.analyze_commit_history()
            if history["examples"]:
                prompt += "\n\nRECENT COMMIT EXAMPLES FROM THIS REPOSITORY:"
                for example in history["examples"]:
                    prompt += f"\n- {example}"

                # Add pattern insights
                if history["types"]:
                    most_common_types = sorted(
                        history["types"].items(), key=lambda x: x[1], reverse=True
                    )[:3]
                    prompt += f"\n\nMOST COMMON COMMIT TYPES IN THIS REPO: {', '.join([t[0] for t in most_common_types])}"

                if history["scopes"]:
                    most_common_scopes = sorted(
                        history["scopes"].items(), key=lambda x: x[1], reverse=True
                    )[:3]
                    prompt += f"\nMOST COMMON SCOPES IN THIS REPO: {', '.join([s[0] for s in most_common_scopes])}"

                if history["avg_length"] > 0:
                    prompt += f"\nAVERAGE COMMIT LENGTH IN THIS REPO: {int(history['avg_length'])} characters"

        # Add project structure context if enabled
        if self.config.get("project_structure_context", True):
            try:
                structure = self.project_analyzer.get_project_structure()
                if structure:
                    prompt += f"\n\nPROJECT STRUCTURE:\n{structure[:500]}..."  # Limit to 500 chars
            except Exception:
                pass

        # Add multi-file analysis context
        diff_analysis = self.diff_analyzer.analyze_diff_context(diff_content)
        if diff_analysis["files_changed"]:
            prompt += (
                f"\n\nFILES CHANGED ({len(diff_analysis['files_changed'])} files):"
            )
            for file in diff_analysis["files_changed"][:10]:  # Limit to 10 files
                prompt += f"\n- {file}"

            if diff_analysis["is_large_change"]:
                prompt += "\n\nNOTE: This is a large changeset - focus on the overall purpose rather than individual changes."

            if diff_analysis["change_summary"]["new_files"] > 0:
                prompt += f"\n- {diff_analysis['change_summary']['new_files']} new files created"

            if diff_analysis["change_summary"]["deleted_files"] > 0:
                prompt += f"\n- {diff_analysis['change_summary']['deleted_files']} files deleted"

        prompt += """

STANDARD EXAMPLES:
- feat(auth): add user login validation
- fix(api): handle null response in user fetch
- docs: update installation instructions
- refactor(parser): simplify token extraction logic

Look at this diff and write a clear, concise commit message:

{diff_content}

Output only the commit message, no explanations."""

        return prompt.format(diff_content=diff_content)
