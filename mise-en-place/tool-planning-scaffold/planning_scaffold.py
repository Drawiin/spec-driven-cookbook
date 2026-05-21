#!/usr/bin/env python3
"""
tool-planning-scaffold — Scaffold .planning/ directory structure idempotently.
Also provides read-artifact, write-artifact, and format-file subcommands.
Exit 0: success. Exit 1: error (details on stdout).
"""
import argparse
import pathlib
import sys

PLANNING_DIRS = [
    ".planning",
    ".planning/phases",
    ".planning/codebase",
]

PLANNING_DEFAULTS = {
    "STATE.md":        "# Project State\n\n",
    "REQUIREMENTS.md": "# Requirements\n\n",
    "ROADMAP.md":      "# Roadmap\n\n",
}


def scaffold(root: pathlib.Path) -> None:
    """Idempotent: mkdir exist_ok=True + conditional file writes."""
    for d in PLANNING_DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)
    for name, content in PLANNING_DEFAULTS.items():
        target = root / ".planning" / name
        if not target.exists():  # never clobber existing files
            target.write_text(content, encoding="utf-8")


def read_artifact(planning_root: pathlib.Path, artifact: str) -> str:
    path = planning_root / artifact
    if not path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}")
    return path.read_text(encoding="utf-8")


def write_artifact(planning_root: pathlib.Path, artifact: str, content: str) -> None:
    candidate = (planning_root / artifact).resolve()
    resolved_root = planning_root.resolve()
    if candidate != resolved_root and resolved_root not in candidate.parents:
        print(f"ERROR: artifact path {artifact!r} escapes .planning/ root")
        sys.exit(1)
    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_text(content, encoding="utf-8")


def format_file(path: pathlib.Path) -> None:
    """Normalize: strip trailing whitespace per line + ensure single trailing newline."""
    text = path.read_text(encoding="utf-8")
    lines = [line.rstrip() for line in text.splitlines()]
    normalized = "\n".join(lines).rstrip("\n") + "\n"
    path.write_text(normalized, encoding="utf-8")


def _validate_root(raw_root: str) -> pathlib.Path:
    """Resolve root and reject paths outside the working directory."""
    root = pathlib.Path(raw_root).resolve()
    cwd = pathlib.Path.cwd().resolve()
    if not (root == cwd or cwd in root.parents or root in cwd.parents):
        print(f"ERROR: --root {raw_root!r} is outside working directory {cwd}")
        sys.exit(1)
    return root


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold and manage the .planning/ directory structure.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # scaffold subcommand
    p_scaffold = subparsers.add_parser("scaffold", help="Create .planning/ tree idempotently")
    p_scaffold.add_argument("--root", default=str(pathlib.Path.cwd()), help="Project root (default: cwd)")

    # read-artifact subcommand
    p_read = subparsers.add_parser("read-artifact", help="Print artifact content to stdout")
    p_read.add_argument("artifact", help="Path relative to .planning/ (e.g. STATE.md)")
    p_read.add_argument("--root", default=str(pathlib.Path.cwd()), help="Project root (default: cwd)")

    # write-artifact subcommand
    p_write = subparsers.add_parser("write-artifact", help="Write content to a .planning/ artifact")
    p_write.add_argument("artifact", help="Path relative to .planning/ (e.g. STATE.md)")
    p_write.add_argument("content", help="Content to write; use '-' to read from stdin")
    p_write.add_argument("--root", default=str(pathlib.Path.cwd()), help="Project root (default: cwd)")

    # format-file subcommand
    p_fmt = subparsers.add_parser("format-file", help="Normalize trailing whitespace and trailing newline")
    p_fmt.add_argument("file", help="File path to format (any file, not just .planning/)")

    args = parser.parse_args()

    if args.command == "scaffold":
        root = _validate_root(args.root)
        scaffold(root)
        print(f"Scaffolded .planning/ under {root}")

    elif args.command == "read-artifact":
        root = _validate_root(args.root)
        planning_root = root / ".planning"
        try:
            content = read_artifact(planning_root, args.artifact)
            print(content, end="")
        except FileNotFoundError as exc:
            print(str(exc))
            sys.exit(1)

    elif args.command == "write-artifact":
        root = _validate_root(args.root)
        planning_root = root / ".planning"
        content = sys.stdin.read() if args.content == "-" else args.content
        write_artifact(planning_root, args.artifact, content)
        print(f"Written: .planning/{args.artifact}")

    elif args.command == "format-file":
        path = pathlib.Path(args.file).resolve()
        if not path.exists():
            print(f"ERROR: file not found: {path}")
            sys.exit(1)
        format_file(path)
        print(f"Formatted: {path}")


if __name__ == "__main__":
    main()
