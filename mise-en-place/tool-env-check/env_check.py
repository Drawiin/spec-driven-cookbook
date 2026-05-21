#!/usr/bin/env python3
"""
tool-env-check — Validate runtime prerequisites before a phase begins.
Exit 0: all prerequisites pass. Exit 1: one or more missing.
"""
import os
import shutil
import subprocess
import sys
from typing import Tuple

CHECKS = [
    ("git",     ["git", "--version"]),
    ("python3", ["python3", "--version"]),
    ("bun/node", ["bun", "--version"]),
    ("cursor",  ["cursor", "--version"]),
]


def run_check(name: str, cmd: list) -> Tuple[str, str]:
    """Returns (status_char, detail_str) where status_char is '✓' or '✗'."""
    # Cursor fast-path: env var takes precedence over subprocess
    if name == "cursor":
        if os.environ.get("CURSOR_TRACE_ID"):
            return ("✓", "cursor (detected via CURSOR_TRACE_ID)")
        if shutil.which("cursor") is not None:
            try:
                r = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=3,
                )
                ver = (r.stdout or r.stderr).splitlines()[0].strip()
                return ("✓", ver)
            except subprocess.TimeoutExpired:
                return ("✗", "cursor: timed out")
        return ("✗", "cursor: not found in PATH")

    # bun/node: try bun first, fall back to node
    if cmd[0] == "bun":
        if shutil.which("bun") is None:
            if shutil.which("node") is not None:
                try:
                    r = subprocess.run(
                        ["node", "--version"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=3,
                    )
                    ver = (r.stdout or r.stderr).splitlines()[0].strip()
                    return ("✓", ver)
                except subprocess.TimeoutExpired:
                    return ("✗", "node: timed out")
            return ("✗", "bun/node: not found in PATH")

    # Generic check
    if shutil.which(cmd[0]) is None:
        return ("✗", f"{cmd[0]}: not found in PATH")

    try:
        r = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3,
        )
        ver = (r.stdout or r.stderr).splitlines()[0].strip()
        return ("✓", ver)
    except subprocess.TimeoutExpired:
        return ("✗", f"{cmd[0]}: timed out")


def main() -> None:
    print("## Environment Check\n")
    all_pass = True
    for name, cmd in CHECKS:
        status, detail = run_check(name, cmd)
        print(f"  {status} {name}: {detail}")
        if status == "✗":
            all_pass = False
    print()
    print("PASS" if all_pass else "FAIL — missing prerequisites above")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
