#!/usr/bin/env python3
"""
tool-detect-brownfield — Detect whether a project root is brownfield (existing code).

Stdout: JSON with is_brownfield, has_existing_code, has_package_file, has_codebase_map,
needs_codebase_map, code_extensions_found.
Exit 0: successful detection (regardless of brownfield result).
Exit 1: invalid --root (outside cwd or not a directory).
"""
import argparse
import json
import os
import pathlib
import sys

CODE_EXTENSIONS = {
    ".ts", ".js", ".py", ".go", ".rs", ".swift", ".java",
    ".kt", ".kts", ".c", ".cpp", ".h", ".cs", ".rb", ".php",
    ".dart", ".m", ".mm", ".scala", ".groovy", ".lua", ".r", ".R",
    ".zig", ".ex", ".exs", ".clj",
}

SKIP_DIRS = {
    "node_modules", ".git", ".planning", ".claude", ".codex",
    "__pycache__", "target", "dist", "build", ".DS_Store",
}

PACKAGE_FILES = (
    "package.json",
    "requirements.txt",
    "Cargo.toml",
    "go.mod",
    "Package.swift",
    "build.gradle",
    "build.gradle.kts",
    "pom.xml",
    "Gemfile",
    "composer.json",
    "pubspec.yaml",
    "CMakeLists.txt",
    "Makefile",
    "build.zig",
    "mix.exs",
    "project.clj",
)

MAX_DEPTH = 3
CANONICAL_MAP_MARKER = pathlib.Path(".planning") / "codebase" / "STACK.md"


def _validate_root(root: pathlib.Path, cwd: pathlib.Path) -> None:
    try:
        root.relative_to(cwd)
    except ValueError:
        print(f"ERROR: --root {root} is outside working directory {cwd}", file=sys.stderr)
        sys.exit(1)
    if not root.is_dir():
        print(f"ERROR: --root {root} does not exist or is not a directory", file=sys.stderr)
        sys.exit(1)


def _has_package_file(root: pathlib.Path) -> bool:
    return any((root / name).is_file() for name in PACKAGE_FILES)


def _find_code_files(root: pathlib.Path) -> set[str]:
    """Walk root up to MAX_DEPTH; return set of extensions found."""
    found: set[str] = set()
    for dirpath, dirnames, filenames in os.walk(
        root, topdown=True, followlinks=False
    ):
        rel = pathlib.Path(dirpath)
        try:
            depth = len(rel.relative_to(root).parts)
        except ValueError:
            depth = 0
        if depth > MAX_DEPTH:
            dirnames.clear()
            continue
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            ext = pathlib.Path(name).suffix
            if ext in CODE_EXTENSIONS:
                found.add(ext)
    return found


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Detect brownfield vs greenfield project roots."
    )
    parser.add_argument(
        "--root",
        default=str(pathlib.Path.cwd()),
        help="Project root to analyze (default: cwd)",
    )
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    cwd = pathlib.Path.cwd().resolve()
    _validate_root(root, cwd)

    extensions_found = sorted(_find_code_files(root))
    has_existing_code = len(extensions_found) > 0
    has_package_file = _has_package_file(root)
    is_brownfield = has_existing_code or has_package_file

    map_marker = root / CANONICAL_MAP_MARKER
    has_codebase_map = map_marker.is_file()
    needs_codebase_map = is_brownfield and not has_codebase_map

    result = {
        "is_brownfield": is_brownfield,
        "has_existing_code": has_existing_code,
        "has_package_file": has_package_file,
        "has_codebase_map": has_codebase_map,
        "needs_codebase_map": needs_codebase_map,
        "code_extensions_found": extensions_found,
    }
    print(json.dumps(result, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
