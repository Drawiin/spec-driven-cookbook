#!/usr/bin/env python3
"""
tool-context-builder — Assemble a pasteable markdown context packet.
Sections: (1) directory tree, (2) dependency list, (3) git summary, (4) key file previews.
Exit 0: always (graceful degradation if git unavailable or entry points absent).
"""
import argparse
import fnmatch
import pathlib
import subprocess
import sys

ALWAYS_EXCLUDE = {".planning", ".git", "__pycache__", ".DS_Store", "node_modules"}
ENTRY_POINT_CANDIDATES = [
    "README.md", "README.rst", "main.py", "app.py", "index.py",
    "pyproject.toml", "setup.py", "setup.cfg", "package.json",
    "index.js", "index.ts", "Makefile",
]


def load_gitignore_patterns(root: pathlib.Path) -> list:
    gi = root / ".gitignore"
    if not gi.exists():
        return []
    try:
        lines = gi.read_text(encoding="utf-8").splitlines()
    except (UnicodeDecodeError, OSError):
        return []
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def is_excluded(name: str, patterns: list) -> bool:
    if name in ALWAYS_EXCLUDE:
        return True
    # Skip patterns that contain "/" — these are path-relative and cannot be
    # matched against a bare name; only simple glob patterns are supported here.
    return any(
        fnmatch.fnmatch(name, p.lstrip("/").rstrip("/"))
        for p in patterns
        if "/" not in p.strip("/")
    )


def build_tree(root: pathlib.Path, patterns: list, depth: int = 3, prefix: str = "") -> list:
    if depth == 0:
        return []
    lines = []
    try:
        entries = sorted(root.iterdir(), key=lambda p: (p.is_file(), p.name))
    except PermissionError:
        return []
    visible = [e for e in entries if not is_excluded(e.name, patterns)]
    for i, entry in enumerate(visible):
        connector = "└── " if i == len(visible) - 1 else "├── "
        lines.append(f"{prefix}{connector}{entry.name}")
        if entry.is_dir():
            extension = "    " if i == len(visible) - 1 else "│   "
            lines.extend(build_tree(entry, patterns, depth - 1, prefix + extension))
    return lines


def git_summary(root: str) -> str:
    def run(args):
        try:
            r = subprocess.run(
                ["git", "--no-pager"] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10,
                cwd=root,
            )
            return r.stdout.strip() if r.returncode == 0 else ""
        except subprocess.TimeoutExpired:
            return ""

    branch = run(["rev-parse", "--abbrev-ref", "HEAD"])
    if not branch:
        return "_Not a git repository._\n"

    log = run(["log", "--oneline", "-10"])
    status = run(["status", "--short"])

    lines = [f"**Branch:** {branch}", "", "**Recent commits:**", "```", log, "```"]
    if status:
        lines += ["", "**Uncommitted changes:**", "```", status, "```"]
    return "\n".join(lines)


def find_entry_points(root: pathlib.Path, max_files: int = 5) -> list:
    found = []
    for candidate in ENTRY_POINT_CANDIDATES:
        p = root / candidate
        if p.exists() and p.is_file():
            found.append(p)
        if len(found) >= max_files:
            break
    return found


def preview_file(path: pathlib.Path, max_lines: int = 20) -> str:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()[:max_lines]
        content = "\n".join(lines)
        return f"### `{path.name}`\n```\n{content}\n```\n"
    except (UnicodeDecodeError, OSError):
        return f"### `{path.name}`\n_(binary or unreadable)_\n"


def main():
    parser = argparse.ArgumentParser(description="Assemble a markdown context packet.")
    parser.add_argument("--root", default=str(pathlib.Path.cwd()), type=str,
                        help="Project root directory (default: cwd)")
    parser.add_argument("--depth", default=3, type=int,
                        help="Directory tree depth (default: 3)")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    cwd = pathlib.Path.cwd().resolve()
    if not (root == cwd or cwd in root.parents or root in cwd.parents):
        print(f"ERROR: --root {root} is outside working directory {cwd}")
        sys.exit(1)
    if not root.is_dir():
        print(f"ERROR: --root {root} does not exist or is not a directory")
        sys.exit(1)

    patterns = load_gitignore_patterns(root)

    sections = []

    # Section 1: Directory Tree
    tree_lines = build_tree(root, patterns, depth=args.depth)
    tree_body = "\n".join(tree_lines) if tree_lines else "(empty)"
    sections.append("## Directory Tree\n\n```\n" + tree_body + "\n```")

    # Section 2: Dependencies
    dep_files = ["pyproject.toml", "package.json", "requirements.txt"]
    dep_content = None
    dep_name = None
    for dep_file in dep_files:
        dep_path = root / dep_file
        if dep_path.exists() and dep_path.is_file():
            try:
                dep_content = dep_path.read_text(encoding="utf-8")
                dep_name = dep_file
                break
            except (UnicodeDecodeError, OSError):
                pass
    if dep_content is not None:
        sections.append(f"## Dependencies\n\n### `{dep_name}`\n```\n{dep_content}\n```")
    else:
        sections.append("## Dependencies\n\n_(none detected)_")

    # Section 3: Git Summary
    sections.append("## Git Summary\n\n" + git_summary(str(root)))

    # Section 4: Key Files
    entry_points = find_entry_points(root)
    if entry_points:
        previews = "\n".join(preview_file(p) for p in entry_points)
        sections.append("## Key Files\n\n" + previews)
    else:
        sections.append("## Key Files\n\n_(no entry points detected)_")

    print("\n---\n".join(sections))
    sys.exit(0)


if __name__ == "__main__":
    main()
