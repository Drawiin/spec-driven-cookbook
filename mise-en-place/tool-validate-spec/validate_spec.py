#!/usr/bin/env python3
"""
tool-validate-spec — Check that SPEC.md exists, has status: approved, and contains all required section headers.

Exit 0: approved with valid sections.
Exit 1: not approved, missing file, malformed front-matter, or missing section (message to stderr).

Required sections (exact match):
  ## Problem
  ## Who It's For
  ## Constraints
  ## Success Criteria
  ## Out of Scope
"""
import pathlib
import sys

SPEC_CANDIDATES = [
    pathlib.Path(".planning/SPEC.md"),
    pathlib.Path("SPEC.md"),
]

REQUIRED_SECTIONS = [
    "## Problem",
    "## Who It's For",
    "## Constraints",
    "## Success Criteria",
    "## Out of Scope",
]


def parse_frontmatter(text: str) -> dict:
    """Parse YAML-like front-matter between --- markers."""
    if not text.startswith("---"):
        return {}

    end = text.find("\n---", 3)
    if end == -1:
        return {}

    block = text[3:end].strip()
    result = {}
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        result[key.strip()] = value.strip()
    return result


def main() -> None:
    spec_path = None
    for candidate in SPEC_CANDIDATES:
        if candidate.exists():
            spec_path = candidate
            break

    if spec_path is None:
        print(
            "ERROR: SPEC.md not found in .planning/ or project root.\n"
            "Run /spec-phase first to create and approve a spec.",
            file=sys.stderr,
        )
        sys.exit(1)

    text = spec_path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)

    if not fm:
        print(
            f"ERROR: {spec_path} has no valid YAML front-matter.\n"
            "Expected format:\n"
            "---\n"
            "status: approved\n"
            "version: 1\n"
            "date: YYYY-MM-DD\n"
            "---",
            file=sys.stderr,
        )
        sys.exit(1)

    status = fm.get("status", "")
    if status != "approved":
        print(
            f"ERROR: SPEC.md status is '{status}' — must be 'approved' before planning.\n"
            "Run /spec-phase and complete the approval gate.",
            file=sys.stderr,
        )
        sys.exit(1)

    for header in REQUIRED_SECTIONS:
        if header not in text:
            print(
                f"ERROR: SPEC.md missing required section: {header}",
                file=sys.stderr,
            )
            sys.exit(1)

    print(
        f"✓ SPEC.md approved (version {fm.get('version', '?')}, {fm.get('date', '?')})"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
