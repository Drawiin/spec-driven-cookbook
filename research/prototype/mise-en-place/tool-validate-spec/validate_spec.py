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

Brownfield (project_type: brownfield after normalization):
  ## Already Built
  ## To Build
  Inverse rule: brownfield sections in body require project_type brownfield.
  Dedup: identical bullets in Already Built and To Build are rejected.
"""
import pathlib
import re
import sys
from typing import Optional

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

BROWNFIELD_SECTIONS = [
    "## Already Built",
    "## To Build",
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


def _section_bullets(text: str, header: str) -> list[str]:
    """Extract bullet lines from a section until the next ## header."""
    if header not in text:
        return []
    start = text.index(header) + len(header)
    rest = text[start:]
    next_match = re.search(r"\n## ", rest)
    if next_match:
        rest = rest[: next_match.start()]
    bullets = []
    for line in rest.splitlines():
        stripped = line.strip()
        if stripped.startswith("-") or stripped.startswith("*"):
            bullets.append(stripped)
    return bullets


def _normalize_bullet(line: str) -> str:
    return re.sub(r"^[\-\*]\s*", "", line.strip()).lower()


def _duplicate_brownfield_bullets(text: str) -> Optional[str]:
    built = {_normalize_bullet(b) for b in _section_bullets(text, "## Already Built")}
    to_build = {_normalize_bullet(b) for b in _section_bullets(text, "## To Build")}
    built.discard("")
    to_build.discard("")
    overlap = built & to_build
    if overlap:
        return next(iter(overlap))
    return None


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

    project_type = fm.get("project_type", "greenfield").strip().lower()

    has_brownfield_section = any(h in text for h in BROWNFIELD_SECTIONS)
    if has_brownfield_section and project_type != "brownfield":
        print(
            "ERROR: SPEC.md contains brownfield sections but project_type is not brownfield",
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

    if project_type == "brownfield":
        for header in BROWNFIELD_SECTIONS:
            if header not in text:
                print(
                    f"ERROR: brownfield SPEC.md missing: {header}",
                    file=sys.stderr,
                )
                sys.exit(1)

        duplicate = _duplicate_brownfield_bullets(text)
        if duplicate:
            print(
                f"ERROR: duplicate items in Already Built and To Build: {duplicate}",
                file=sys.stderr,
            )
            sys.exit(1)

    msg = f"✓ SPEC.md approved (version {fm.get('version', '?')}, {fm.get('date', '?')})"
    if project_type == "brownfield":
        msg += " [brownfield]"
    print(msg)
    sys.exit(0)


if __name__ == "__main__":
    main()
