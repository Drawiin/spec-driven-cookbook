"""Tests for planning_scaffold.py"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from planning_scaffold import format_file, read_artifact, scaffold, write_artifact


# --- Fixtures ---


@pytest.fixture
def tmp_project(tmp_path):
    """Minimal project root with no .planning/ yet."""
    return tmp_path


# --- Tests ---


def test_scaffold_creates_planning_dirs(tmp_project):
    """scaffold() creates the expected .planning/ directory tree."""
    scaffold(tmp_project)
    assert (tmp_project / ".planning").is_dir()
    assert (tmp_project / ".planning" / "phases").is_dir()
    assert (tmp_project / ".planning" / "codebase").is_dir()


def test_scaffold_is_idempotent(tmp_project):
    """Running scaffold() twice raises no error and leaves .planning/ intact."""
    scaffold(tmp_project)
    scaffold(tmp_project)
    assert (tmp_project / ".planning").is_dir()


def test_scaffold_does_not_overwrite_existing_files(tmp_project):
    """scaffold() never clobbers files that already exist."""
    (tmp_project / ".planning").mkdir()
    (tmp_project / ".planning" / "STATE.md").write_text("custom content", encoding="utf-8")
    scaffold(tmp_project)
    assert (tmp_project / ".planning" / "STATE.md").read_text(encoding="utf-8") == "custom content"


def test_read_artifact_returns_content(tmp_project):
    """read_artifact() returns the default content written by scaffold()."""
    scaffold(tmp_project)
    planning_root = tmp_project / ".planning"
    result = read_artifact(planning_root, "STATE.md")
    assert "Project State" in result


def test_format_file_normalizes_trailing_whitespace(tmp_project):
    """format_file() strips trailing spaces and ensures a single trailing newline."""
    test_file = tmp_project / "test.md"
    test_file.write_text("line one   \nline two\n\n", encoding="utf-8")
    format_file(test_file)
    content = test_file.read_text(encoding="utf-8")
    assert content == "line one\nline two\n"


def test_write_artifact_path_traversal_blocked(tmp_project):
    """write_artifact() rejects artifact paths that escape .planning/ root."""
    scaffold(tmp_project)
    planning_root = tmp_project / ".planning"
    with pytest.raises(SystemExit) as exc_info:
        write_artifact(planning_root, "../escape.md", "evil content")
    assert exc_info.value.code == 1
    assert not (tmp_project / "escape.md").exists()


def test_write_artifact_nested_path_allowed(tmp_project):
    """write_artifact() accepts valid subpaths within .planning/."""
    scaffold(tmp_project)
    planning_root = tmp_project / ".planning"
    write_artifact(planning_root, "phases/test-note.md", "# Test Note\n")
    target = planning_root / "phases" / "test-note.md"
    assert target.exists()
    assert "# Test Note" in target.read_text(encoding="utf-8")
