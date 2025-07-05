"""Tests for git operations."""

from unittest.mock import patch, MagicMock
import subprocess


from memo.git.operations import GitOperations
from memo.git.analyzer import CommitHistoryAnalyzer, DiffAnalyzer


class TestGitOperations:
    """Test cases for GitOperations."""

    def test_get_staged_diff_success(self):
        """Test successful staged diff retrieval."""
        git_ops = GitOperations()

        mock_result = MagicMock()
        mock_result.stdout = "diff --git a/file.py b/file.py\n+added line"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            diff, error = git_ops.get_staged_diff()

            mock_run.assert_called_once_with(
                ["git", "diff", "--staged"], capture_output=True, text=True, check=True
            )
            assert diff == "diff --git a/file.py b/file.py\n+added line"
            assert error is None

    def test_get_staged_diff_no_changes(self):
        """Test staged diff when no changes are staged."""
        git_ops = GitOperations()

        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            diff, error = git_ops.get_staged_diff()

            assert diff is None
            assert "No staged changes found" in error

    def test_commit_with_message_success(self):
        """Test successful commit with message."""
        git_ops = GitOperations()

        mock_result = MagicMock()
        mock_result.stdout = "[main 1234567] test commit"

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            success, output = git_ops.commit_with_message("test commit")

            mock_run.assert_called_once_with(
                ["git", "commit", "-m", "test commit"],
                capture_output=True,
                text=True,
                check=True,
            )
            assert success is True
            assert output == "[main 1234567] test commit"

    def test_is_git_repository_true(self):
        """Test git repository detection when in a git repo."""
        git_ops = GitOperations()

        mock_result = MagicMock()
        mock_result.stdout = ".git"

        with patch("subprocess.run", return_value=mock_result):
            result = git_ops.is_git_repository()
            assert result is True

    def test_is_git_repository_false(self):
        """Test git repository detection when not in a git repo."""
        git_ops = GitOperations()

        with patch(
            "subprocess.run", side_effect=subprocess.CalledProcessError(1, "git")
        ):
            result = git_ops.is_git_repository()
            assert result is False


class TestCommitHistoryAnalyzer:
    """Test cases for CommitHistoryAnalyzer."""

    def test_analyze_commit_history_success(self):
        """Test successful commit history analysis."""
        analyzer = CommitHistoryAnalyzer()

        mock_result = MagicMock()
        mock_result.stdout = (
            "feat(auth): add login\nfix(api): handle error\ndocs: update readme"
        )

        with patch("subprocess.run", return_value=mock_result):
            result = analyzer.analyze_commit_history()

            assert "types" in result
            assert "scopes" in result
            assert "examples" in result
            assert result["types"]["feat"] == 1
            assert result["types"]["fix"] == 1
            assert result["types"]["docs"] == 1
            assert result["scopes"]["auth"] == 1
            assert result["scopes"]["api"] == 1

    def test_analyze_commit_history_no_commits(self):
        """Test commit history analysis with no commits."""
        analyzer = CommitHistoryAnalyzer()

        mock_result = MagicMock()
        mock_result.stdout = ""

        with patch("subprocess.run", return_value=mock_result):
            result = analyzer.analyze_commit_history()

            assert result["types"] == {}
            assert result["scopes"] == {}
            assert result["examples"] == []


class TestDiffAnalyzer:
    """Test cases for DiffAnalyzer."""

    def test_analyze_diff_context(self):
        """Test diff context analysis."""
        analyzer = DiffAnalyzer()

        diff_content = """diff --git a/src/file1.py b/src/file1.py
new file mode 100644
index 0000000..abc123
--- /dev/null
+++ b/src/file1.py
@@ -0,0 +1,5 @@
+def hello():
+    return "world"
diff --git a/src/file2.js b/src/file2.js
index 123..456 789
--- a/src/file2.js
+++ b/src/file2.js
@@ -1,3 +1,4 @@
 console.log("hello");
+console.log("world");
-console.log("old");"""

        result = analyzer.analyze_diff_context(diff_content)

        assert len(result["files_changed"]) == 2
        assert "src/file1.py" in result["files_changed"]
        assert "src/file2.js" in result["files_changed"]
        assert result["change_summary"]["new_files"] == 1
        assert result["change_summary"]["additions"] == 3  # +def, +return, +console.log
        assert result["change_summary"]["deletions"] == 1  # -console.log
        assert result["file_types"]["py"] == 1
        assert result["file_types"]["js"] == 1
        assert result["is_large_change"] is False  # Small changeset

    def test_analyze_large_diff(self):
        """Test analysis of large diff."""
        analyzer = DiffAnalyzer()

        # Create a large diff content
        diff_lines = [
            "diff --git a/file{}.py b/file{}.py".format(i, i) for i in range(10)
        ]
        diff_lines.extend(["+added line"] * 60)  # 60 additions

        diff_content = "\n".join(diff_lines)

        result = analyzer.analyze_diff_context(diff_content)

        assert result["is_large_change"] is True  # More than 50 changes
