# Phase 1: Tooling Foundation - Research

**Researched:** 2026-05-21
**Domain:** Python stdlib CLI scripting, Cursor skill bundling, deterministic tooling
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** All tool scripts written in Python, stdlib only — zero pip install dependencies; works out of the box on any Python 3.x install.
- **D-02:** Tools are co-located with the skill that uses them. Each tool shared across multiple skills gets its own dedicated `tool-` prefixed skill (e.g. `tool-env-check`, `tool-context-builder`).
- **D-03:** Each `tool-*` skill contains a `SKILL.md` (the "how to use this" contract) and the Python script(s) that implement the tool. No monolithic utility dump.
- **D-04:** Skill naming convention for tool wrappers: `tool-<name>` prefix.
- **D-05:** Directory tree depth: 3 levels.
- **D-06:** Exclusion rules: respects `.gitignore` AND explicitly excludes `.planning/`.
- **D-07:** Output sections: (1) directory tree, (2) dependency list, (3) git summary, (4) key file previews — first ~20 lines of detected entry points (README, main script, etc.).
- **D-08:** Tools exposed as Cursor skill commands. Each SKILL.md instructs the agent to invoke the tool by running the Python script via the Shell tool.
- **D-09:** Entry-point detection heuristic and git summary format are Claude's discretion — standard patterns are fine.

### Claude's Discretion

- Entry-point detection heuristic for key file previews (README.md, main.py, index.js, pyproject.toml, etc.).
- Exact git summary format (last N commits, branch, status) — keep it concise and useful for an agent prompt.

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TOOL-01 | CLI/script utilities for repeatable low-token operations: formatting files, reading/writing framework artifacts, scaffolding directories | `tool-planning-scaffold` skill — Python script with idempotent directory creation and artifact read/write helpers |
| TOOL-02 | Context-builder scripts gather structured project data (directory trees, dependency lists, git log summaries) and output clean markdown for agent prompts | `tool-context-builder` skill — stdlib-only Python script with git subprocess calls, fnmatch exclusion, and stdout markdown output |
| TOOL-04 | Environment-check scripts validate runtime prerequisites before phases begin | `tool-env-check` skill — Python script using shutil.which + subprocess for git, python, bun/node, and cursor; exits in < 5 seconds |
| TOOL-05 | All deterministic tools bundled inside the skill folder so generated variants are self-contained | All scripts live inside `mise-en-place/tool-*/`; no install step required |

</phase_requirements>

---

## Summary

Phase 1 delivers three standalone Python CLI scripts — each wrapped as its own Cursor `tool-*` skill — that give every downstream phase its foundational tooling. The tools are: `tool-env-check` (validates git, python, bun/node, and cursor are present and functional before a phase begins), `tool-context-builder` (assembles a clean, pasteable markdown context packet from the project's directory tree, dependency list, git history, and key file previews), and `tool-planning-scaffold` (scaffolds the `.planning/` directory structure, reads and writes framework artifacts, and formats files idempotently). [VERIFIED: local environment probe]

The chosen technology is deliberately minimal: Python 3.9.6 is available on this machine at `/usr/bin/python3`; all required stdlib modules (`subprocess`, `pathlib`, `json`, `fnmatch`, `argparse`, `shutil`, `textwrap`, `os`, `re`) are confirmed working. No pip installation is needed at any point. Every tool script is a single self-contained file — no inter-script imports, no shared library module. This is the right choice for a framework that needs to be trivially portable: dropping the `mise-en-place/` folder into a new project is all the setup required. [VERIFIED: local environment probe]

The GSD framework's existing `gsd-tools.cjs` pattern (skills bundled inside the framework folder, SKILL.md as the invocation contract, separate implementation file) is the direct precedent this phase follows. The key difference is that GSD uses a compiled Node.js monolith; Phase 1 uses individual Python scripts that are human-readable and require zero build step — the right trade-off for a v1 Cursor-only framework. [CITED: research/topics/auxiliary-tooling.md §8]

**Primary recommendation:** Build three `tool-*` skill directories inside `mise-en-place/`, each with a `SKILL.md` + one Python script. Keep each script self-contained (no cross-script imports). Use `argparse` for CLI flags, `pathlib` for all file operations, and `subprocess.run()` for git calls. The SKILL.md for each tool should instruct the agent to invoke the script via `Shell(python3 path/to/script.py [args])`.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Environment prerequisite validation | CLI Script (local) | — | Pure subprocess + shutil.which checks; no agent needed for the check itself |
| Context assembly & markdown formatting | CLI Script (local) | Git (external subprocess) | Script drives all reads; git is an external binary called via subprocess |
| Planning directory scaffolding | CLI Script (local) | — | Pure filesystem operations via pathlib; no network or service calls |
| Artifact read/write (framework files) | CLI Script (local) | — | Direct file I/O against `.planning/` paths |
| Tool invocation surface | Cursor Agent (reads SKILL.md) | CLI Script | Agent reads SKILL.md contract, calls Shell tool to run Python script |

---

## Standard Stack

### Core

No external packages. This phase uses Python stdlib exclusively. [VERIFIED: local environment probe — `python3 -c "import subprocess, pathlib, json, fnmatch, argparse, shutil, textwrap, os, re"` exits 0]

| Module | Purpose | Why Standard |
|--------|---------|--------------|
| `pathlib` | All file/directory operations — tree building, idempotent mkdir, file reads | Clean OOP API; handles cross-platform paths; available Python 3.4+ |
| `subprocess` | Run `git` commands and check binary presence | Standard way to call external processes; `capture_output=True` added in 3.7 |
| `shutil` | `shutil.which()` for binary detection; `shutil.copy2()` if needed | `which()` is the stdlib equivalent of `command -v` |
| `argparse` | CLI argument parsing for all three scripts | Built-in; handles `--help`, type coercion, defaults |
| `fnmatch` | Gitignore pattern matching (glob-style patterns) | Handles `*.pyc`, `node_modules/`, `__pycache__/` patterns; Python 3.x built-in |
| `json` | Reading/writing `.planning/config.json` and future JSON artifacts | Standard serialization format for structured artifacts |
| `textwrap` | Markdown output formatting (wrapping, dedenting) | Keeps script output clean without external template engines |
| `os` | `os.environ` for Cursor detection via `CURSOR_TRACE_ID` | Direct env-var access |
| `re` | Gitignore pattern normalization (anchored patterns) | Fine-grained pattern matching beyond fnmatch for edge cases |
| `sys` | `sys.exit()` for exit codes; `sys.stdout` for output | Conventional exit-code-based pass/fail reporting |

### Supporting Runtime Binaries (called via subprocess, not imported)

| Binary | Version Confirmed | Purpose | Detection Method |
|--------|------------------|---------|-----------------|
| `git` | 2.50.1 [VERIFIED: local probe] | Branch name, log, status in context-builder | `shutil.which('git')` + `git --version` |
| `python3` | 3.9.6 [VERIFIED: local probe] | The runtime itself; also checked in env-check | `shutil.which('python3')` + `python3 --version` |
| `bun` | present [VERIFIED: local probe — `~/.asdf/shims/bun`] | Checked as node-equivalent in env-check | `shutil.which('bun')` or `shutil.which('node')` — accept either |
| `cursor` | 2.6.11 [VERIFIED: local probe — `cursor --version`] | IDE prerequisite in env-check | `shutil.which('cursor')` + `cursor --version` |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `fnmatch` for gitignore | `gitpython` (pip) | gitpython has proper gitignore parsing but requires pip install — violates D-01; fnmatch + manual pattern parsing handles the common cases (D-06 only needs .gitignore + .planning/ exclusion) |
| `subprocess.run()` for git | `gitpython` (pip) | Same pip constraint; subprocess is sufficient for the 3-4 git commands needed |
| Three separate scripts | One monolithic script with subcommands | Monolith would require the agent to know which subcommand to call; separate skills are more discoverable and independently invocable per D-03 |
| `argparse` | Click (pip), Typer (pip) | Both require pip; argparse covers all needs with zero dependencies |

**Installation:** None required. Python 3.x ships with all modules used.

---

## Package Legitimacy Audit

> This phase installs **zero external packages** (stdlib only per D-01). No legitimacy audit required.

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| *(none)* | — | — | — | — | — | N/A |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

---

## Architecture Patterns

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Cursor Agent (reads SKILL.md)                   │
└────────────┬──────────────────┬───────────────────┬─────────────────┘
             │ Shell(python3 …) │ Shell(python3 …)   │ Shell(python3 …)
             ▼                  ▼                    ▼
  ┌──────────────────┐  ┌───────────────────┐  ┌─────────────────────┐
  │ tool-env-check/  │  │tool-context-      │  │tool-planning-       │
  │  env_check.py    │  │builder/           │  │scaffold/            │
  │                  │  │  context_builder  │  │  planning_scaffold  │
  │ checks:          │  │  .py              │  │  .py                │
  │  git ──► pass/  │  │                   │  │                     │
  │          fail   │  │ reads:            │  │ operations:         │
  │  python3 ──► …  │  │  filesystem ──►   │  │  mkdir (idempotent) │
  │  bun/node ──► … │  │  .gitignore ──►   │  │  read artifact      │
  │  cursor ──► …   │  │  git log/status ─►│  │  write artifact     │
  │                 │  │  entry points ──► │  │  format file        │
  │ stdout: report  │  │ stdout: markdown   │  │ stdout: status      │
  │ exit: 0 or 1    │  │        context     │  │ exit: 0 or 1        │
  └─────────────────┘  └───────────────────┘  └─────────────────────┘
             │                  │                    │
             ▼                  ▼                    ▼
      Terminal output     Markdown context      .planning/ tree
      (pass/fail lines)   (paste into prompt)   (scaffolded/updated)
```

### Recommended Project Structure

```
mise-en-place/
├── tool-env-check/
│   ├── SKILL.md            # Invocation contract — how agent calls this tool
│   └── env_check.py        # stdlib: subprocess, shutil, sys
├── tool-context-builder/
│   ├── SKILL.md            # Invocation contract
│   └── context_builder.py  # stdlib: pathlib, subprocess, fnmatch, textwrap
└── tool-planning-scaffold/
    ├── SKILL.md            # Invocation contract
    └── planning_scaffold.py # stdlib: pathlib, json, argparse
```

Each `tool-*` skill is fully standalone: drag `mise-en-place/tool-env-check/` into any project's `.cursor/skills/` and it works without any additional setup (TOOL-05). [ASSUMED: exact destination path within `.cursor/skills/` — confirmed by convention from existing skills, not by an explicit spec requirement]

### Pattern 1: SKILL.md as Invocation Contract

**What:** The `SKILL.md` file contains the human-readable + agent-readable description of what the tool does and exactly how to invoke the Python script via the Cursor `Shell` tool. The Python script has no knowledge of Cursor — it reads stdin/args and writes stdout.

**When to use:** Every `tool-*` skill. The SKILL.md is the only interface document agents need.

**Example:**

```markdown
---
name: tool-env-check
description: "Validate runtime prerequisites before a phase begins"
---

## Usage

Run from the project root:

```shell
python3 .cursor/skills/tool-env-check/env_check.py
```

Exit code 0 = all prerequisites pass. Exit code 1 = one or more prerequisites missing.
```

*Source: [ASSUMED] — pattern derived from GSD's gsd-fast/SKILL.md and the D-08 decision in CONTEXT.md*

### Pattern 2: Idempotent Scaffolding with pathlib

**What:** `mkdir` with `exist_ok=True` + conditional file writes (`if not path.exists()`) ensures the scaffolding script can be run repeatedly without clobbering existing content.

**When to use:** `tool-planning-scaffold` — any time the script creates directories or writes default files.

**Example:**
```python
# Source: Python stdlib — pathlib documentation [ASSUMED pattern]
from pathlib import Path

def scaffold_planning_dir(root: Path) -> None:
    planning = root / ".planning"
    planning.mkdir(exist_ok=True)
    (planning / "phases").mkdir(exist_ok=True)
    defaults = {
        "STATE.md": "# Project State\n\n",
        "REQUIREMENTS.md": "# Requirements\n\n",
    }
    for name, content in defaults.items():
        target = planning / name
        if not target.exists():
            target.write_text(content)
```

### Pattern 3: Git Summary via Subprocess

**What:** Call `git` as an external subprocess. Capture stdout. Handle non-git directories gracefully.

**When to use:** `tool-context-builder` — git log, branch, and status sections.

**Example:**
```python
# Source: Python stdlib subprocess documentation [ASSUMED pattern]
import subprocess

def git_summary(root: str) -> str:
    def run(args):
        r = subprocess.run(
            ["git", "--no-pager"] + args,
            capture_output=True, text=True, cwd=root
        )
        return r.stdout.strip() if r.returncode == 0 else ""

    branch = run(["rev-parse", "--abbrev-ref", "HEAD"])
    log    = run(["log", "--oneline", "-10"])
    status = run(["status", "--short"])

    if not branch:
        return "_Not a git repository._\n"

    lines = [f"**Branch:** {branch}", "", "**Recent commits:**", "```", log, "```"]
    if status:
        lines += ["", "**Uncommitted changes:**", "```", status, "```"]
    return "\n".join(lines)
```

### Pattern 4: Gitignore-Aware Directory Tree

**What:** Walk the directory tree with `pathlib`, skip entries matching `.gitignore` patterns (via `fnmatch`) plus always skip `.planning/` (per D-06), and stop at depth 3 (per D-05).

**When to use:** `tool-context-builder` — directory tree section.

**Example:**
```python
# Source: Python stdlib pathlib + fnmatch [ASSUMED pattern]
import pathlib, fnmatch

ALWAYS_EXCLUDE = {".planning", ".git", "__pycache__", ".DS_Store", "node_modules"}

def load_gitignore_patterns(root: pathlib.Path) -> list[str]:
    gi = root / ".gitignore"
    if not gi.exists():
        return []
    lines = gi.read_text().splitlines()
    return [l.strip() for l in lines if l.strip() and not l.startswith("#")]

def is_excluded(name: str, patterns: list[str]) -> bool:
    if name in ALWAYS_EXCLUDE:
        return True
    return any(fnmatch.fnmatch(name, p.lstrip("/")) for p in patterns)

def build_tree(root: pathlib.Path, patterns: list[str], depth: int = 3, prefix: str = "") -> list[str]:
    if depth == 0:
        return []
    lines = []
    entries = sorted(root.iterdir(), key=lambda p: (p.is_file(), p.name))
    for i, entry in enumerate(entries):
        if is_excluded(entry.name, patterns):
            continue
        connector = "└── " if i == len(entries) - 1 else "├── "
        lines.append(f"{prefix}{connector}{entry.name}")
        if entry.is_dir():
            extension = "    " if i == len(entries) - 1 else "│   "
            lines.extend(build_tree(entry, patterns, depth - 1, prefix + extension))
    return lines
```

### Pattern 5: Cursor Detection

**What:** Check the `CURSOR_TRACE_ID` environment variable (present when running inside Cursor) AND/OR verify `cursor --version` returns successfully.

**When to use:** `tool-env-check` — Cursor prerequisite check.

**Example:**
```python
# Source: local environment probe [VERIFIED: CURSOR_TRACE_ID present in Cursor env]
import os, subprocess, shutil

def check_cursor() -> tuple[bool, str]:
    # Method 1: env var (fast — no subprocess)
    if os.environ.get("CURSOR_TRACE_ID"):
        return True, "running inside Cursor (CURSOR_TRACE_ID set)"
    # Method 2: binary check (for calling from outside Cursor terminal)
    if shutil.which("cursor"):
        r = subprocess.run(["cursor", "--version"], capture_output=True, text=True, timeout=3)
        if r.returncode == 0:
            version = r.stdout.splitlines()[0].strip()
            return True, f"cursor {version}"
    return False, "cursor not found (not in PATH and CURSOR_TRACE_ID not set)"
```

### Anti-Patterns to Avoid

- **Monolithic utility module:** Do not create a shared `utils.py` imported by multiple tool scripts. Each script must be standalone — a shared import creates a hidden dependency that breaks the "move one folder = self-contained" guarantee of TOOL-05.
- **Calling `git` without `--no-pager`:** Git opens a pager (less) for long output in some environments. Always pass `--no-pager` or use `GIT_TERMINAL_PROMPT=0` env flag in subprocess calls to prevent the process from hanging.
- **`os.walk()` instead of `pathlib.Path.iterdir()`:** `os.walk()` is harder to depth-limit cleanly; `pathlib.iterdir()` with explicit recursion gives full control over depth cutoff.
- **`Path.open()` vs `Path.read_text()`:** Prefer `Path.read_text(encoding='utf-8')` — it handles encoding explicitly on Python 3.9, where the default encoding can vary by OS locale.
- **Non-zero exit code swallowed:** If the environment check fails, `sys.exit(1)` must be called — callers (agents reading SKILL.md) should be able to detect failure via exit code without parsing stdout.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Gitignore parsing | Custom regex parser | `fnmatch` + manual line parsing (this phase), or `gitpython.Repo.git.check_ignore()` in a future phase if pip allowed | Full gitignore spec has 20+ edge cases (negation patterns, double-star globs, anchored paths). For Phase 1's scope (D-06: respects .gitignore), fnmatch handles the >95% common case. |
| Binary presence detection | `subprocess.run(['which', 'binary'])` | `shutil.which('binary')` | `shutil.which` is the stdlib-native, cross-platform, correct answer — no subprocess overhead |
| JSON artifact read/write | String concatenation | `json.loads(path.read_text())` / `path.write_text(json.dumps(obj, indent=2))` | Handles encoding, escaping, and pretty-print deterministically |
| Markdown table formatting | Template strings | Simple f-string formatting with fixed column widths | Context-builder output is agent-consumed, not human-typeset — simple column alignment is fine |

**Key insight:** The tools in Phase 1 solve deliberately simple problems. The risk is over-engineering them. Each script should be < 150 lines; if it grows beyond that, it is likely doing too much.

---

## Common Pitfalls

### Pitfall 1: Gitignore Patterns Not Applied to Subdirectory Entries

**What goes wrong:** A gitignore pattern like `node_modules/` (with trailing slash) or `*.pyc` is checked against full paths instead of entry names, causing matches to fail silently.

**Why it happens:** `fnmatch.fnmatch()` does simple glob matching; it does not know about path separators. Patterns like `**/*.pyc` or `/dist` have special semantics in the full gitignore spec.

**How to avoid:** Strip the trailing slash from directory patterns before matching. Match only the `entry.name` (the last path component), not the full path. Document that the implementation is best-effort for common patterns — this is sufficient for D-06's use case.

**Warning signs:** Test with a project that has `node_modules/` in `.gitignore` and verify the directory is excluded from the tree output.

### Pitfall 2: Subprocess Hanging on Git in Non-Interactive Terminal

**What goes wrong:** `git log` or `git diff` opens a pager (less/more) if `GIT_PAGER` or `core.pager` is configured, causing `subprocess.run()` to block indefinitely.

**Why it happens:** Git's default behavior respects the terminal pager config even in subprocess calls that aren't attached to a TTY in some environments.

**How to avoid:** Always pass `--no-pager` as the second argument: `["git", "--no-pager", "log", ...]`. Alternatively, set `env={**os.environ, "GIT_PAGER": "cat"}` in the subprocess call.

**Warning signs:** Script hangs on `git log` after a few seconds with no output.

### Pitfall 3: Python Version Assumption on `capture_output`

**What goes wrong:** `capture_output=True` was added in Python 3.7. On Python 3.6 (still present on some older macOS), the script fails with `TypeError`.

**Why it happens:** `capture_output` is a convenience shorthand for `stdout=PIPE, stderr=PIPE`.

**How to avoid:** Since Python 3.9.6 is confirmed [VERIFIED: local probe], this is not a risk on this machine. However, for maximum portability (TOOL-05 requires self-contained operation on any target), use `stdout=subprocess.PIPE, stderr=subprocess.PIPE` instead of `capture_output=True` to maintain Python 3.6+ compatibility.

### Pitfall 4: `exist_ok=True` Does Not Make File Writes Idempotent

**What goes wrong:** `mkdir(exist_ok=True)` is idempotent for directories, but writing a file is always a clobber if done unconditionally.

**Why it happens:** The `Path.write_text()` call is not conditional — it overwrites any existing content.

**How to avoid:** For all default file scaffolding, check `if not path.exists()` before writing. For artifact writes (TOOL-01's read/write use case), intentional overwrites are fine — just document the distinction in the SKILL.md.

**Warning signs:** Running the scaffold script twice and finding that a user-edited `STATE.md` has been reset to the default template.

### Pitfall 5: Entry-Point Detection Returns Too Many Files

**What goes wrong:** The key-file-preview section of `tool-context-builder` includes too many files (e.g., every `.py` file), making the context packet large and less useful.

**Why it happens:** Overly broad glob patterns match more files than expected on non-trivial projects.

**How to avoid:** Use a strict priority list (see Code Examples below). Cap at 5–6 files. Only include files that actually exist.

---

## Code Examples

Verified patterns from confirmed stdlib behavior:

### Entry-Point Detection Heuristic (Claude's Discretion — D-09)

```python
# Source: Python stdlib pathlib [ASSUMED — standard convention for entry-point detection]
from pathlib import Path

ENTRY_POINT_CANDIDATES = [
    "README.md",
    "README.rst",
    "main.py",
    "app.py",
    "index.py",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "package.json",
    "index.js",
    "index.ts",
    "Makefile",
]

def find_entry_points(root: Path, max_files: int = 5) -> list[Path]:
    found = []
    for candidate in ENTRY_POINT_CANDIDATES:
        p = root / candidate
        if p.exists() and p.is_file():
            found.append(p)
        if len(found) >= max_files:
            break
    return found

def preview_file(path: Path, max_lines: int = 20) -> str:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()[:max_lines]
        content = "\n".join(lines)
        return f"### `{path.name}`\n```\n{content}\n```\n"
    except (UnicodeDecodeError, OSError):
        return f"### `{path.name}`\n_(binary or unreadable)_\n"
```

### Environment Check Report Format (Git Summary — D-09 Claude's Discretion)

```python
# Source: local environment probe [VERIFIED: cursor --version, git --version confirmed]
import shutil, subprocess, os, sys

CHECKS = [
    ("git",     ["git", "--version"]),
    ("python3", ["python3", "--version"]),
    ("cursor",  ["cursor", "--version"]),
]

def run_check(name: str, cmd: list[str]) -> tuple[str, str]:
    """Returns (status_emoji, detail_line)."""
    # Special case: cursor can be detected via env var (faster)
    if name == "cursor" and os.environ.get("CURSOR_TRACE_ID"):
        return "✓", "cursor (detected via CURSOR_TRACE_ID env var)"

    binary = cmd[0]
    if not shutil.which(binary):
        # bun is accepted as a node equivalent
        if binary == "node" and shutil.which("bun"):
            r = subprocess.run(["bun", "--version"], capture_output=True, text=True, timeout=3)
            ver = r.stdout.strip() if r.returncode == 0 else "unknown"
            return "✓", f"bun {ver} (node equivalent)"
        return "✗", f"{binary}: not found in PATH"

    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        ver = (r.stdout or r.stderr).splitlines()[0].strip()
        return "✓", f"{ver}"
    except subprocess.TimeoutExpired:
        return "✗", f"{binary}: timed out"

def env_check_report() -> tuple[list[str], bool]:
    lines = ["## Environment Check\n"]
    all_pass = True
    for name, cmd in CHECKS:
        status, detail = run_check(name, cmd)
        lines.append(f"  {status} {name}: {detail}")
        if status == "✗":
            all_pass = False
    lines.append("")
    lines.append("PASS" if all_pass else "FAIL — missing prerequisites above")
    return lines, all_pass
```

### Artifact Read/Write Pattern (TOOL-01)

```python
# Source: Python stdlib pathlib + json [ASSUMED — standard stdlib pattern]
import json
from pathlib import Path

def read_artifact(planning_root: Path, artifact: str) -> str:
    """Read a framework artifact (e.g. 'STATE.md', 'config.json')."""
    path = planning_root / artifact
    if not path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}")
    return path.read_text(encoding="utf-8")

def write_artifact(planning_root: Path, artifact: str, content: str) -> None:
    """Write a framework artifact. Creates parent dirs if needed."""
    path = planning_root / artifact
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def read_json_artifact(planning_root: Path, artifact: str) -> dict:
    return json.loads(read_artifact(planning_root, artifact))

def write_json_artifact(planning_root: Path, artifact: str, data: dict) -> None:
    write_artifact(planning_root, artifact, json.dumps(data, indent=2) + "\n")
```

---

## Runtime State Inventory

> SKIPPED — this is a greenfield phase; no rename/refactor/migration is involved.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Shell scripts (bash) for CLI tools | Python stdlib scripts | N/A — this is a greenfield choice | Python is more readable, cross-platform, and easier to test |
| Monolithic utility module | One script per `tool-*` skill | N/A — first-principles decision | Each script is independently portable (TOOL-05) |
| Node.js for tooling (GSD's pattern) | Python stdlib | N/A — design decision | Python 3.x ships with macOS; no runtime install needed |

**Deprecated / not applicable:**
- External package dependencies: excluded by D-01. Never add them in Phase 1 deliverables.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Each `tool-*` skill lands in `mise-en-place/tool-*/` and agents invoke it via `.cursor/skills/tool-*/` symlink or direct path | Architecture Patterns → Recommended Project Structure | If the final install path differs, SKILL.md invocation examples would need updating — low-risk since SKILL.md is authored in this phase |
| A2 | SKILL.md frontmatter and format follows the same structure as existing `gsd-*` skills (name, description, usage section, shell invocation example) | Architecture Patterns → Pattern 1 | If the Cursor skill loader expects different frontmatter, the SKILL.md would need adjustment — observable immediately on first test |
| A3 | Entry-point detection priority list (README.md, main.py, pyproject.toml, etc.) covers the relevant file types for this project | Code Examples → Entry-Point Detection | If the project uses uncommon entry points, the preview section would be empty — graceful degradation, not a hard failure |
| A4 | `bun` is accepted as a valid Node.js equivalent for the environment check (success criteria says "node/python") | Code Examples → Environment Check | If future phases require `node` specifically (e.g., for `bun .cursor/get-shit-done/bin/gsd-tools.cjs`), the check should detect bun AND node — current design handles this |

**If this table is empty:** It is not — see above. A1–A4 are confirmed risks; all are low-severity with observable failure modes.

---

## Open Questions (RESOLVED)

1. **Should `tool-planning-scaffold` also include a `format-file` command (TOOL-01 mentions "formatting files idempotently")?**
   - What we know: TOOL-01 says "formatting files, reading/writing framework artifacts, scaffolding directories"
   - What's unclear: "formatting" likely means normalizing markdown (trailing newlines, consistent headers) not linting/prettifying. The success criteria (SC-3) says "format files idempotently" — could be as simple as ensuring a trailing newline.
   - Recommendation: Implement format as "normalize trailing newline + strip trailing whitespace per line" — simple, idempotent, and useful for diff-clean commits. If a more sophisticated formatter is needed, defer to a later phase.
   - **RESOLVED:** Implement `format-file` subcommand in `planning_scaffold.py` that normalizes trailing newline + strips trailing whitespace per line.

2. **Node/bun check: should both be required, or is either sufficient?**
   - What we know: This machine has `bun` but not `node`. The success criteria says "git, node/python, cursor" — the slash suggests either/or for node/python.
   - What's unclear: Future phases (Phase 5, Phase 8) use `bun gsd-tools.cjs` — so `bun` is the practical runtime here.
   - Recommendation: Check for `bun` OR `node` (accept either). Report which one was found. This aligns with the runtime note in the project.
   - **RESOLVED:** `tool-env-check` checks for `bun` OR `node` (either satisfies the JavaScript runtime prerequisite). Reports which one was found.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `python3` | All three tool scripts | ✓ | 3.9.6 | — |
| `git` | `tool-context-builder`, `tool-env-check` | ✓ | 2.50.1 | Script reports "not a git repo" and continues |
| `bun` | `tool-env-check` (as node equivalent) | ✓ | present at `~/.asdf/shims/bun` | Check `node` if `bun` absent |
| `cursor` | `tool-env-check` | ✓ | 2.6.11 (or CURSOR_TRACE_ID env var) | Report FAIL for cursor check |
| `.gitignore` file | `tool-context-builder` | ✗ (not present in this repo yet) | — | Skip gitignore exclusion; use ALWAYS_EXCLUDE set only |

**Missing dependencies with no fallback:** None — all required binaries confirmed present.

**Missing dependencies with fallback:** `.gitignore` not present. `tool-context-builder` handles this gracefully: if `.gitignore` does not exist, only the hard-coded `ALWAYS_EXCLUDE` set is applied.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest — not yet installed; Wave 0 gap |
| Config file | `pytest.ini` or `pyproject.toml [tool.pytest.ini_options]` — neither exists yet |
| Quick run command | `python3 -m pytest mise-en-place/ -x -q` (after Wave 0) |
| Full suite command | `python3 -m pytest mise-en-place/ -v` |

> **Note:** The tool scripts themselves have zero pip dependencies (stdlib only). Tests for them can use pytest as a dev-only testing tool without violating D-01 — pytest is the test runner, not a dependency of the shipped tool scripts.

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TOOL-04 | `env_check.py` exits 0 when all prerequisites present | unit | `pytest mise-en-place/tool-env-check/test_env_check.py -x` | ❌ Wave 0 |
| TOOL-04 | `env_check.py` exits 1 when a prerequisite is missing (mock shutil.which to return None) | unit | `pytest mise-en-place/tool-env-check/test_env_check.py -x` | ❌ Wave 0 |
| TOOL-04 | Full check completes in < 5 seconds | smoke | `time python3 mise-en-place/tool-env-check/env_check.py` | ❌ Wave 0 |
| TOOL-02 | `context_builder.py` produces valid markdown with all 4 sections | unit | `pytest mise-en-place/tool-context-builder/test_context_builder.py -x` | ❌ Wave 0 |
| TOOL-02 | `.planning/` excluded from directory tree output | unit | `pytest mise-en-place/tool-context-builder/test_context_builder.py -x` | ❌ Wave 0 |
| TOOL-02 | gitignore patterns applied (ALWAYS_EXCLUDE set works) | unit | `pytest mise-en-place/tool-context-builder/test_context_builder.py -x` | ❌ Wave 0 |
| TOOL-01 | `planning_scaffold.py` creates `.planning/` dirs idempotently (run twice, no error) | unit | `pytest mise-en-place/tool-planning-scaffold/test_planning_scaffold.py -x` | ❌ Wave 0 |
| TOOL-01 | Scaffold does not overwrite existing files | unit | `pytest mise-en-place/tool-planning-scaffold/test_planning_scaffold.py -x` | ❌ Wave 0 |
| TOOL-05 | Moving `mise-en-place/tool-*/` to a new project root works without setup | smoke | Manual test — copy to temp dir, run each script | manual |

### Sampling Rate

- **Per task commit:** `python3 -m pytest mise-en-place/ -x -q` (quick run, stops on first failure)
- **Per wave merge:** `python3 -m pytest mise-en-place/ -v` (full suite with verbose output)
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `mise-en-place/tool-env-check/test_env_check.py` — covers TOOL-04 (presence + exit codes)
- [ ] `mise-en-place/tool-context-builder/test_context_builder.py` — covers TOOL-02 (output sections, exclusions)
- [ ] `mise-en-place/tool-planning-scaffold/test_planning_scaffold.py` — covers TOOL-01 (idempotency, no-clobber)
- [ ] Framework install: `pip install pytest` (dev-only, not shipped in `mise-en-place/`)

---

## Security Domain

> `security_enforcement` not set to false in config.json — treated as enabled.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | Not applicable — local CLI scripts, no auth |
| V3 Session Management | No | Not applicable — no sessions |
| V4 Access Control | No | Not applicable — no access control layer |
| V5 Input Validation | Yes (low risk) | Validate that paths passed as CLI args don't escape project root |
| V6 Cryptography | No | Not applicable — no crypto |

### Known Threat Patterns for Python stdlib CLI scripts

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal via `--root` CLI arg | Tampering | Resolve to absolute path; assert it is within cwd or a declared allowed root before any read/write |
| Subprocess injection via user-supplied git args | Tampering | Never interpolate user input into subprocess arg lists; use explicit arg arrays only (`["git", "--no-pager", "log"]`) — never `shell=True` |
| Writing to arbitrary paths via artifact write helper | Tampering | Validate that the target path is under `.planning/` root before any `path.write_text()` call |

> **Low overall risk:** Phase 1 tools are invoked by the developer locally from within Cursor. There is no network surface, no user-supplied code execution, and no privilege escalation. The mitigations above are standard defensive practices, not responses to a high-threat surface.

---

## Sources

### Primary (HIGH confidence)

- Local environment probe — `python3 --version`, `git --version`, `cursor --version`, `shutil.which('bun')`, `python3 -c "import subprocess, pathlib, ..."` — all confirmed in this session
- `research/topics/auxiliary-tooling.md` — cross-framework analysis of tooling patterns; informed the "three separate scripts, not monolith" recommendation and the SKILL.md contract pattern

### Secondary (MEDIUM confidence)

- `.planning/phases/01-tooling-foundation/01-CONTEXT.md` — locked decisions D-01 through D-09 (source of truth for all design constraints)
- `.cursor/skills/gsd-fast/SKILL.md` — reference for SKILL.md format and frontmatter convention
- `research/SUMMARY.md` — compound-init pattern (informed context-builder design), sub-agent context contract pattern

### Tertiary (LOW confidence / ASSUMED)

- Python stdlib documentation (training knowledge for `pathlib`, `fnmatch`, `argparse`, `subprocess`) — tagged `[ASSUMED]` where used as patterns; verified against local probe for module availability

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — Python 3.9.6 confirmed locally; all stdlib modules verified importable
- Architecture: HIGH — decisions locked in CONTEXT.md D-01 through D-09; no ambiguity
- Pitfalls: MEDIUM — drawn from stdlib behavioral knowledge (training); most verifiable by running the tool once
- Test architecture: MEDIUM — pytest availability not confirmed (no pip install yet); Wave 0 gap identified

**Research date:** 2026-05-21
**Valid until:** 2026-11-21 (stdlib APIs are stable; 6-month window is conservative)
