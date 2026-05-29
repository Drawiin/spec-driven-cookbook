"""Tests for scan_map_secrets.py"""
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent / "scan_map_secrets.py"


def _run_scan(directory: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--dir", str(directory)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def test_scan_map_secrets_clean_exits_zero(tmp_path):
    """Benign map file → exit 0."""
    (tmp_path / "STACK.md").write_text(
        "# Stack\n\n## Languages\n\nPython 3.9+\n",
        encoding="utf-8",
    )
    result = _run_scan(tmp_path)
    assert result.returncode == 0, result.stderr


def test_scan_map_secrets_detects_api_key_exits_one(tmp_path):
    """Fake ghp_ token pattern → exit 1 with file path in stderr."""
    bad = tmp_path / "STACK.md"
    bad.write_text(
        "# Stack\n\nToken: ghp_abcdefghijklmnopqrstuvwxyz1234567890AB\n",
        encoding="utf-8",
    )
    result = _run_scan(tmp_path)
    assert result.returncode == 1
    assert "STACK.md" in result.stderr or str(bad) in result.stderr
