"""Project structure analysis utilities for Memo."""

import os


class ProjectStructureAnalyzer:
    """Analyzes project structure to provide context for commit messages."""

    def get_project_structure(self, path: str = ".", indent: str = "") -> str:
        """Get the project structure as a string."""
        structure = ""
        try:
            for item in os.listdir(path):
                if item.startswith("."):
                    continue
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    structure += f"{indent}{item}/\n"
                    structure += self.get_project_structure(item_path, indent + "  ")
                else:
                    structure += f"{indent}{item}\n"
            return structure
        except (OSError, PermissionError):
            return ""
