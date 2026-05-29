# Phase 1: Tooling Foundation - Pattern Map

**Mapped:** 2026-05-21
**Files analyzed:** 9 (6 primary + 3 test)
**Analogs found:** 3 / 9 (SKILL.md files have a codebase analog; Python scripts and tests have none — RESEARCH.md patterns apply)

---

## File Classification

| New File | Role | Data Flow | Closest Analog | Match Quality |
|----------|------|-----------|----------------|---------------|
| `mise-en-place/tool-env-check/SKILL.md` | skill / invocation-contract | agent-instruction | `.cursor/skills/gsd-fast/SKILL.md` | structural-match (frontmatter + adapter block identical; execution body differs) |
| `mise-en-place/tool-env-check/env_check.py` | CLI utility | request-response | none | no analog — use RESEARCH.md Pattern 5 |
| `mise-en-place/tool-context-builder/SKILL.md` | skill / invocation-contract | agent-instruction | `.cursor/skills/gsd-fast/SKILL.md` | structural-match |
| `mise-en-place/tool-context-builder/context_builder.py` | CLI utility | file-I/O + batch | none | no analog — use RESEARCH.md Patterns 3 & 4 |
| `mise-en-place/tool-planning-scaffold/SKILL.md` | skill / invocation-contract | agent-instruction | `.cursor/skills/gsd-fast/SKILL.md` | structural-match |
| `mise-en-place/tool-planning-scaffold/planning_scaffold.py` | CLI utility | file-I/O + CRUD | none | no analog — use RESEARCH.md Patterns 1 & 2 |
| `mise-en-place/tool-env-check/test_env_check.py` | test | unit | none | no analog — pytest standard patterns |
| `mise-en-place/tool-context-builder/test_context_builder.py` | test | unit | none | no analog — pytest standard patterns |
| `mise-en-place/tool-planning-scaffold/test_planning_scaffold.py` | test | unit | none | no analog — pytest standard patterns |

---

## Pattern Assignments

### `mise-en-place/tool-*/SKILL.md` (skill, agent-instruction)

**Analog:** `.cursor/skills/gsd-fast/SKILL.md`

**Key structural insight:** All project SKILL.md files share identical frontmatter + `<cursor_skill_adapter>` boilerplate. The `tool-*` SKILL.md deviates in one critical way: the `<execution_context>` block in GSD skills points to a `.cursor/get-shit-done/workflows/*.md` file. `tool-*` skills have no separate workflow file — the SKILL.md itself contains the complete invocation contract directly in `<process>`.

**Frontmatter pattern** (lines 1-4 of gsd-fast/SKILL.md):
```markdown
---
name: gsd-fast
description: "Execute a trivial task inline — no subagents, no planning overhead"
---
```

**cursor_skill_adapter block** (lines 6-28 of gsd-fast/SKILL.md — copy verbatim, change skill name in line 8 only):
```markdown
<cursor_skill_adapter>
## A. Skill Invocation
- This skill is invoked when the user mentions `gsd-fast` or describes a task matching this skill.
- Treat all user text after the skill mention as `{{GSD_ARGS}}`.
- If no arguments are present, treat `{{GSD_ARGS}}` as empty.

## B. User Prompting
When the workflow needs user input, prompt the user conversationally:
- Present options as a numbered list in your response text
- Ask the user to reply with their choice
- For multi-select, ask for comma-separated numbers

## C. Tool Usage
Use these Cursor tools when executing GSD workflows:
- `Shell` for running commands (terminal operations)
- `StrReplace` for editing existing files
- `Read`, `Write`, `Glob`, `Grep`, `Task`, `WebSearch`, `WebFetch`, `TodoWrite` as needed

## D. Subagent Spawning
When the workflow needs to spawn a subagent:
- Use `Task(subagent_type="generalPurpose", ...)`
- The `model` parameter maps to Cursor's model options (e.g., "fast")
</cursor_skill_adapter>
```

**Divergence — tool-* process block (no workflow file):**

GSD skills delegate via:
```markdown
<execution_context>
@/path/to/workflow.md
</execution_context>

<process>
Execute end-to-end.
</process>
```

`tool-*` skills embed the contract directly — no `<execution_context>` pointer needed:
```markdown
<objective>
One-sentence description of what the tool does and when to use it.
</objective>

<process>
Run from the project root:

```shell
python3 mise-en-place/tool-<name>/<script>.py [args]
```

Exit code 0 = success. Exit code 1 = failure (details printed to stdout).

**Arguments:** (list argparse flags if any)

**Output:** (describe stdout format — markdown? line-by-line report?)
</process>
```

---

### `mise-en-place/tool-env-check/env_check.py` (CLI utility, request-response)

**Analog:** None in codebase. Use RESEARCH.md Pattern 5 (Cursor Detection) + Code Example (Environment Check Report Format).

**Script structure pattern** (from RESEARCH.md — verified stdlib patterns):
```python
#!/usr/bin/env python3
"""
tool-env-check — Validate runtime prerequisites before a phase begins.
Exit 0: all prerequisites pass. Exit 1: one or more missing.
"""
import os
import shutil
import subprocess
import sys

CHECKS = [
    ("git",     ["git", "--version"]),
    ("python3", ["python3", "--version"]),
    ("cursor",  ["cursor", "--version"]),
    # node/bun: check bun first, fall back to node
]

def run_check(name: str, cmd: list) -> tuple:
    """Returns (status_char, detail_line)."""
    # cursor: fast env-var path first
    if name == "cursor" and os.environ.get("CURSOR_TRACE_ID"):
        return "✓", "cursor (detected via CURSOR_TRACE_ID)"
    binary = cmd[0]
    if not shutil.which(binary):
        if binary == "node" and shutil.which("bun"):
            r = subprocess.run(["bun", "--version"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, timeout=3)
            ver = r.stdout.strip() if r.returncode == 0 else "unknown"
            return "✓", f"bun {ver} (node equivalent)"
        return "✗", f"{binary}: not found in PATH"
    try:
        r = subprocess.run(cmd,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           text=True, timeout=3)
        ver = (r.stdout or r.stderr).splitlines()[0].strip()
        return "✓", ver
    except subprocess.TimeoutExpired:
        return "✗", f"{binary}: timed out"

def main() -> None:
    all_pass = True
    print("## Environment Check\n")
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
```

**Critical rules from RESEARCH.md anti-patterns:**
- Use `stdout=subprocess.PIPE, stderr=subprocess.PIPE` instead of `capture_output=True` (Python 3.6 portability — TOOL-05)
- Pass `--no-pager` in all git subprocess calls to prevent hanging
- Always `sys.exit(1)` on failure — callers detect failure via exit code
- Never `shell=True` in subprocess calls (security: RESEARCH.md threat table)

---

### `mise-en-place/tool-context-builder/context_builder.py` (CLI utility, file-I/O + batch)

**Analog:** None in codebase. Use RESEARCH.md Patterns 3 (Git Summary), 4 (Gitignore-Aware Tree), and Code Examples (Entry-Point Detection, git summary format).

**Script structure pattern:**
```python
#!/usr/bin/env python3
"""
tool-context-builder — Assemble a pasteable markdown context packet.
Sections: (1) directory tree, (2) dependency list, (3) git summary, (4) key file previews.
Exit 0: always (graceful degradation if git unavailable).
"""
import argparse
import fnmatch
import pathlib
import subprocess
import sys
import textwrap

ALWAYS_EXCLUDE = {".planning", ".git", "__pycache__", ".DS_Store", "node_modules"}
ENTRY_POINT_CANDIDATES = [
    "README.md", "README.rst", "main.py", "app.py", "index.py",
    "pyproject.toml", "setup.py", "setup.cfg", "package.json",
    "index.js", "index.ts", "Makefile",
]

# ... load_gitignore_patterns(), is_excluded(), build_tree() per RESEARCH.md Pattern 4
# ... git_summary() per RESEARCH.md Pattern 3
# ... find_entry_points(), preview_file() per RESEARCH.md Code Examples
```

**Output format:** Four markdown sections printed to stdout, separated by `---`. Designed to be pasted directly into an agent prompt.

**Sections must appear in order:**
1. `## Directory Tree` — 3-level tree, gitignore-aware, `.planning/` always excluded
2. `## Dependencies` — content of `pyproject.toml`, `package.json`, or `requirements.txt` if present; else `_(none detected)_`
3. `## Git Summary` — branch, last 10 commits, uncommitted changes (via `git --no-pager`)
4. `## Key Files` — first 20 lines of up to 5 entry-point files

**argparse flags:**
- `--root PATH` — project root (default: cwd); resolved to absolute, asserted within cwd (security)
- `--depth N` — tree depth (default: 3, per D-05)

---

### `mise-en-place/tool-planning-scaffold/planning_scaffold.py` (CLI utility, file-I/O + CRUD)

**Analog:** None in codebase. Use RESEARCH.md Patterns 1 (Idempotent Scaffolding) and 2 (Artifact Read/Write).

**Script structure pattern:**
```python
#!/usr/bin/env python3
"""
tool-planning-scaffold — Scaffold .planning/ directory structure idempotently.
Also provides read-artifact, write-artifact, and format-file subcommands.
Exit 0: success. Exit 1: error (details on stdout).
"""
import argparse
import json
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
        if not target.exists():          # never clobber existing files (RESEARCH.md Pitfall 4)
            target.write_text(content, encoding="utf-8")

def read_artifact(planning_root: pathlib.Path, artifact: str) -> str:
    path = planning_root / artifact
    if not path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}")
    return path.read_text(encoding="utf-8")

def write_artifact(planning_root: pathlib.Path, artifact: str, content: str) -> None:
    path = planning_root / artifact
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def format_file(path: pathlib.Path) -> None:
    """Normalize: strip trailing whitespace per line + ensure single trailing newline."""
    text = path.read_text(encoding="utf-8")
    lines = [line.rstrip() for line in text.splitlines()]
    normalized = "\n".join(lines).rstrip("\n") + "\n"
    path.write_text(normalized, encoding="utf-8")
```

**argparse subcommands:**
- `scaffold [--root PATH]` — create `.planning/` tree (default subcommand)
- `read-artifact <artifact> [--root PATH]` — print artifact to stdout
- `write-artifact <artifact> <content> [--root PATH]` — write content to artifact
- `format-file <file>` — normalize trailing whitespace + trailing newline

**Security check:** Validate `--root` resolves to absolute path; assert artifact path stays under `.planning/` before any write (RESEARCH.md threat table).

---

### Test files (unit, pytest)

**Analog:** None in codebase. Use pytest standard patterns.

**Test file structure pattern:**
```python
"""Tests for <module_name>.py"""
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# --- Fixtures ---

@pytest.fixture
def tmp_project(tmp_path):
    """Minimal project root with no .planning/ yet."""
    return tmp_path

# --- Tests ---

def test_<behavior_description>(tmp_project):
    """<Test describes behavior, not code>."""
    # Arrange
    ...
    # Act
    ...
    # Assert
    assert ...
```

**Co-location rule:** Each test file lives in the same directory as the script it tests:
- `mise-en-place/tool-env-check/test_env_check.py`
- `mise-en-place/tool-context-builder/test_context_builder.py`
- `mise-en-place/tool-planning-scaffold/test_planning_scaffold.py`

**Test runner:** `python3 -m pytest mise-en-place/ -x -q`

**Key behaviors to cover per RESEARCH.md Validation Architecture:**
- `env_check.py`: exits 0 when all prerequisites present; exits 1 when one missing (mock `shutil.which`)
- `context_builder.py`: produces valid markdown with all 4 sections; `.planning/` excluded from tree
- `planning_scaffold.py`: creates `.planning/` dirs idempotently (run twice = no error); does not overwrite existing files

---

## Shared Patterns

### 1. Script Entry Point (all three `.py` files)
**Source:** RESEARCH.md Summary (D-01 — stdlib only, self-contained)
**Apply to:** `env_check.py`, `context_builder.py`, `planning_scaffold.py`
```python
if __name__ == "__main__":
    main()
```
Every script is invokable directly (`python3 script.py`) and importable for testing. `main()` handles `argparse` setup and calls domain functions.

### 2. Exit Code Convention (all three `.py` files)
**Source:** RESEARCH.md anti-patterns (Non-zero exit code swallowed)
**Apply to:** All scripts
```python
sys.exit(0)   # success
sys.exit(1)   # failure — details already printed to stdout
```
Callers (agents reading SKILL.md) detect failure via exit code without parsing stdout.

### 3. Subprocess Safety (env_check.py, context_builder.py)
**Source:** RESEARCH.md anti-patterns (Pitfall 2 + Security threat table)
**Apply to:** Any script calling git or external binaries
```python
# Always: --no-pager, explicit arg arrays (never shell=True), PIPE not capture_output
result = subprocess.run(
    ["git", "--no-pager", "log", "--oneline", "-10"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    timeout=10,
    cwd=str(root),
)
```

### 4. Path Safety (context_builder.py, planning_scaffold.py)
**Source:** RESEARCH.md Security Domain (path traversal mitigation)
**Apply to:** Any script accepting `--root` or path arguments
```python
root = pathlib.Path(args.root).resolve()
cwd = pathlib.Path.cwd().resolve()
# Assert root is under cwd (or is cwd) before any read/write
if not (root == cwd or cwd in root.parents or root in cwd.parents):
    print(f"ERROR: --root {root} is outside working directory {cwd}")
    sys.exit(1)
```

### 5. File Read Convention (all scripts)
**Source:** RESEARCH.md anti-patterns (Path.open() vs Path.read_text())
**Apply to:** All `Path.read_text()` calls
```python
# Always explicit encoding — avoids OS locale differences on Python 3.9
content = path.read_text(encoding="utf-8")
```

### 6. SKILL.md cursor_skill_adapter Block
**Source:** `.cursor/skills/gsd-fast/SKILL.md` lines 6-28
**Apply to:** All three `mise-en-place/tool-*/SKILL.md` files
Copy the `<cursor_skill_adapter>` block verbatim; change only the skill name in Section A line 1.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `mise-en-place/tool-env-check/env_check.py` | CLI utility | request-response | No Python scripts exist in this repo — first application code |
| `mise-en-place/tool-context-builder/context_builder.py` | CLI utility | file-I/O + batch | Same — no Python scripts exist |
| `mise-en-place/tool-planning-scaffold/planning_scaffold.py` | CLI utility | file-I/O + CRUD | Same — no Python scripts exist |
| `mise-en-place/tool-env-check/test_env_check.py` | test | unit | No test files exist in this repo |
| `mise-en-place/tool-context-builder/test_context_builder.py` | test | unit | Same |
| `mise-en-place/tool-planning-scaffold/test_planning_scaffold.py` | test | unit | Same |

**For all "no analog" files:** RESEARCH.md Code Examples and Pattern sections are the authoritative reference — they are verified against local environment probes and contain complete, runnable code fragments.

---

## Metadata

**Analog search scope:** `.cursor/skills/*/SKILL.md` (67 files), `**/*.py` (0 files found — confirmed no Python in repo)
**Files scanned:** 70 (67 SKILL.md + gsd-tools.cjs header + CONTEXT.md + RESEARCH.md)
**Pattern extraction date:** 2026-05-21
