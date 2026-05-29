#!/usr/bin/env python3
"""
tool-scan-map-secrets — Fail-closed secret pattern scan for codebase map markdown.

Scans *.md under --dir (default .planning/codebase/). Exit 0 when clean; exit 1
with file:line references on match. Invoked from map-codebase workflow step 6.
"""
import argparse
import pathlib
import re
import sys

SECRET_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"sk_live_[a-zA-Z0-9]+"),
    re.compile(r"sk_test_[a-zA-Z0-9]+"),
    re.compile(r"ghp_[a-zA-Z0-9]{36}"),
    re.compile(r"gho_[a-zA-Z0-9]{36}"),
    re.compile(r"glpat-[a-zA-Z0-9_-]+"),
    re.compile(r"AKIA[A-Z0-9]{16}"),
    re.compile(r"xox[baprs]-[a-zA-Z0-9-]+"),
    re.compile(r"-----BEGIN.*PRIVATE KEY"),
    re.compile(r"eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\."),
]


def scan_file(path: pathlib.Path) -> list[str]:
    """Return list of file:line:snippet matches."""
    hits = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return hits
    for lineno, line in enumerate(lines, start=1):
        for pattern in SECRET_PATTERNS:
            if pattern.search(line):
                snippet = line.strip()[:80]
                hits.append(f"{path}:{lineno}:{snippet}")
                break
    return hits


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan codebase map markdown for secret patterns."
    )
    parser.add_argument(
        "--dir",
        default=".planning/codebase/",
        help="Directory of map *.md files (default: .planning/codebase/)",
    )
    args = parser.parse_args()

    target = pathlib.Path(args.dir)
    if not target.is_dir():
        print(f"ERROR: {target} is not a directory", file=sys.stderr)
        sys.exit(1)

    all_hits: list[str] = []
    for md_file in sorted(target.glob("*.md")):
        all_hits.extend(scan_file(md_file.resolve()))

    if all_hits:
        for hit in all_hits:
            print(hit, file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
