"""Tests for context_builder.py"""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from context_builder import build_tree, load_gitignore_patterns, is_excluded, find_entry_points

# --- Fixtures ---


@pytest.fixture
def tmp_project(tmp_path):
    """Minimal project root with no .gitignore or .planning/."""
    return tmp_path


# --- Tests ---


def test_output_contains_all_four_sections(tmp_project):
    """Running the script produces all four required section headers in stdout."""
    (tmp_project / "README.md").write_text("# Test Project\n", encoding="utf-8")
    script = Path(__file__).parent / "context_builder.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(tmp_project),
    )
    assert "## Directory Tree" in result.stdout
    assert "## Dependencies" in result.stdout
    assert "## Git Summary" in result.stdout
    assert "## Key Files" in result.stdout


def test_planning_dir_excluded_from_tree(tmp_project):
    """The .planning/ directory is never present in build_tree output (D-06)."""
    (tmp_project / ".planning").mkdir()
    (tmp_project / ".planning" / "STATE.md").write_text("# State\n", encoding="utf-8")
    (tmp_project / "src").mkdir()
    tree = build_tree(tmp_project, [], depth=3)
    joined = "\n".join(tree)
    assert ".planning" not in joined


def test_gitignore_patterns_applied(tmp_project):
    """Directories matching gitignore patterns (but not ALWAYS_EXCLUDE) are excluded."""
    (tmp_project / "vendor").mkdir()  # 'vendor' is not in ALWAYS_EXCLUDE
    (tmp_project / ".gitignore").write_text("vendor/\n", encoding="utf-8")
    patterns = load_gitignore_patterns(tmp_project)
    tree = build_tree(tmp_project, patterns, depth=3)
    joined = "\n".join(tree)
    assert "vendor" not in joined


def test_missing_gitignore_graceful(tmp_project):
    """load_gitignore_patterns returns an empty list when no .gitignore exists (no exception)."""
    result = load_gitignore_patterns(tmp_project)
    assert result == []


def test_output_section_order_and_separators(tmp_project):
    """Output has exactly four sections separated by '---' in the correct order (D-07, SC-2)."""
    (tmp_project / "README.md").write_text("# Test Project\n", encoding="utf-8")
    script = Path(__file__).parent / "context_builder.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(tmp_project),
    )
    segments = result.stdout.split("\n---\n")
    assert len(segments) == 4, f"Expected 4 segments, got {len(segments)}: {segments}"
    assert segments[0].startswith("## Directory Tree")
    assert segments[1].startswith("## Dependencies")
    assert segments[2].startswith("## Git Summary")
    assert segments[3].startswith("## Key Files")
