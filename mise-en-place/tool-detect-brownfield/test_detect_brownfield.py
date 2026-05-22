"""Tests for detect_brownfield.py"""
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import pytest

SCRIPT = Path(__file__).parent / "detect_brownfield.py"


def _run_detect(cwd: Path, root: Optional[Path] = None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(SCRIPT)]
    if root is not None:
        cmd.extend(["--root", str(root)])
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(cwd),
    )


def _parse_json(stdout: str) -> dict:
    return json.loads(stdout)


def test_detect_brownfield_with_py_files(tmp_path):
    """Repo with source files → is_brownfield true."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hi')\n", encoding="utf-8")
    result = _run_detect(tmp_path)
    assert result.returncode == 0, result.stderr
    data = _parse_json(result.stdout)
    assert data["is_brownfield"] is True
    assert data["has_existing_code"] is True


def test_detect_greenfield_empty(tmp_path):
    """Empty dir → is_brownfield false."""
    result = _run_detect(tmp_path)
    assert result.returncode == 0, result.stderr
    data = _parse_json(result.stdout)
    assert data["is_brownfield"] is False
    assert data["has_existing_code"] is False


def test_needs_codebase_map(tmp_path):
    """Brownfield without .planning/codebase/ → needs_codebase_map true."""
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    result = _run_detect(tmp_path)
    data = _parse_json(result.stdout)
    assert data["is_brownfield"] is True
    assert data["needs_codebase_map"] is True
    assert data["has_codebase_map"] is False


def test_needs_codebase_map_empty_scaffold(tmp_path):
    """Empty scaffold dir without STACK.md → needs map, has_codebase_map false."""
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / ".planning" / "codebase").mkdir(parents=True)
    result = _run_detect(tmp_path)
    data = _parse_json(result.stdout)
    assert data["has_codebase_map"] is False
    assert data["needs_codebase_map"] is True


def test_has_codebase_map_when_stack_md_present(tmp_path):
    """STACK.md present → has_codebase_map true, needs_codebase_map false."""
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    stack = tmp_path / ".planning" / "codebase" / "STACK.md"
    stack.parent.mkdir(parents=True)
    stack.write_text("# Stack\n\nPython 3.\n", encoding="utf-8")
    result = _run_detect(tmp_path)
    data = _parse_json(result.stdout)
    assert data["has_codebase_map"] is True
    assert data["needs_codebase_map"] is False


def test_brownfield_package_file_only(tmp_path):
    """package.json only → is_brownfield true."""
    (tmp_path / "package.json").write_text('{"name": "x"}\n', encoding="utf-8")
    result = _run_detect(tmp_path)
    data = _parse_json(result.stdout)
    assert data["is_brownfield"] is True
    assert data["has_package_file"] is True
    assert data["has_existing_code"] is False


def test_reject_root_outside_cwd(tmp_path):
    """--root outside cwd → exit 1."""
    outside = tmp_path.parent
    result = _run_detect(tmp_path, root=outside)
    assert result.returncode == 1
    assert "ERROR" in result.stderr


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlinks not supported")
def test_symlink_outside_root_not_followed(tmp_path):
    """Symlink to outside dir must not count toward has_existing_code."""
    real_outside = tmp_path.parent / "outside_code_detect"
    real_outside.mkdir(exist_ok=True)
    (real_outside / "secret.py").write_text("x=1\n", encoding="utf-8")
    link_dir = tmp_path / "src"
    link_dir.mkdir()
    try:
        os.symlink(real_outside, link_dir / "outside", target_is_directory=True)
    except OSError:
        pytest.skip("could not create symlink")
    result = _run_detect(tmp_path)
    data = _parse_json(result.stdout)
    assert data["has_existing_code"] is False
    assert data["is_brownfield"] is False


def test_max_depth_limits_walk(tmp_path):
    """Code at depth 4 must not be detected."""
    deep = tmp_path / "a" / "b" / "c" / "d"
    deep.mkdir(parents=True)
    (deep / "deep.py").write_text("x=1\n", encoding="utf-8")
    result = _run_detect(tmp_path)
    data = _parse_json(result.stdout)
    assert data["has_existing_code"] is False


def test_skip_dirs_excludes_node_modules(tmp_path):
    """Code under node_modules must not count."""
    nm = tmp_path / "node_modules" / "pkg"
    nm.mkdir(parents=True)
    (nm / "index.js").write_text("module.exports = {}\n", encoding="utf-8")
    result = _run_detect(tmp_path)
    data = _parse_json(result.stdout)
    assert data["has_existing_code"] is False
