"""Tests for env_check.py"""
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from env_check import main, run_check


def test_exits_zero_when_all_checks_pass():
    """main() exits 0 when all subprocess checks return successfully."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "git version 2.50.1\n"
    mock_result.stderr = ""

    with patch("env_check.shutil.which", return_value="/usr/bin/git"), \
         patch("env_check.subprocess.run", return_value=mock_result), \
         patch.dict("os.environ", {}, clear=False):
        # Remove CURSOR_TRACE_ID if present so cursor check uses subprocess path
        env_backup = os.environ.pop("CURSOR_TRACE_ID", None)
        try:
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
        finally:
            if env_backup is not None:
                os.environ["CURSOR_TRACE_ID"] = env_backup


def test_exits_one_when_git_missing():
    """main() exits 1 when git is not found in PATH."""
    def which_side_effect(binary):
        if binary == "git":
            return None
        return f"/usr/bin/{binary}"

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "version 1.0\n"
    mock_result.stderr = ""

    with patch("env_check.shutil.which", side_effect=which_side_effect), \
         patch("env_check.subprocess.run", return_value=mock_result):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


def test_completes_in_under_five_seconds():
    """env_check.py completes in under 5 seconds (SC-1 timing requirement)."""
    pytest.importorskip("shutil")
    if shutil.which("git") is None or shutil.which("python3") is None:
        pytest.skip("integration timing test requires git and python3 in PATH")

    script = Path(__file__).parent / "env_check.py"
    start = time.time()
    subprocess.run(
        ["python3", str(script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10,
    )
    elapsed = time.time() - start
    assert elapsed < 5.0, f"env_check.py took {elapsed:.2f}s — exceeds 5s limit"


def test_cursor_detected_via_env_var():
    """run_check returns ✓ for cursor when CURSOR_TRACE_ID is set, without subprocess."""
    with patch.dict("os.environ", {"CURSOR_TRACE_ID": "mock-trace-id"}):
        status_char, detail_str = run_check("cursor", ["cursor", "--version"])
    assert status_char == "✓"
    assert "CURSOR_TRACE_ID" in detail_str
