# Phase 3: Brownfield Codebase Onboarding - Pattern Map

**Mapped:** 2026-05-22
**Files analyzed:** 8 new/modified files
**Analogs found:** 8 / 8

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `mise-en-place/tool-detect-brownfield/detect_brownfield.py` | utility | file-I/O, transform | `mise-en-place/tool-context-builder/context_builder.py` + GSD `init.cjs` | exact (path walk + detection) |
| `mise-en-place/tool-detect-brownfield/test_detect_brownfield.py` | test | batch | `mise-en-place/tool-context-builder/test_context_builder.py` | exact |
| `mise-en-place/tool-detect-brownfield/SKILL.md` | hook/config | request-response | `mise-en-place/tool-context-builder/SKILL.md` | exact |
| `mise-en-place/map-codebase/SKILL.md` | hook/provider | event-driven (parallel agents) | `.cursor/skills/gsd-map-codebase/SKILL.md` + `mise-en-place/spec-phase/SKILL.md` | role-match |
| `mise-en-place/spec-phase/SKILL.md` | hook/provider | request-response | `mise-en-place/spec-phase/SKILL.md` (self-extend) | exact |
| `mise-en-place/tool-validate-spec/validate_spec.py` | utility | file-I/O, transform | `mise-en-place/tool-validate-spec/validate_spec.py` (self-extend) | exact |
| `mise-en-place/tool-validate-spec/test_validate_spec.py` | test | batch | `mise-en-place/tool-validate-spec/test_validate_spec.py` (self-extend) | exact |
| `mise-en-place/README.md` | config | N/A | `mise-en-place/README.md` (self-extend) | exact |

## Pattern Assignments

### `mise-en-place/tool-detect-brownfield/detect_brownfield.py` (utility, file-I/O + transform)

**Analog:** `mise-en-place/tool-context-builder/context_builder.py` (stdlib CLI shell, `--root` validation) + `.cursor/get-shit-done/bin/lib/init.cjs` (detection algorithm)

**Module docstring + shebang pattern** (lines 1-6 of `context_builder.py`):

```python
#!/usr/bin/env python3
"""
tool-context-builder — Assemble a pasteable markdown context packet.
Sections: (1) directory tree, (2) dependency list, (3) git summary, (4) key file previews.
Exit 0: always (graceful degradation if git unavailable or entry points absent).
"""
```

Adapt for detect: docstring describes JSON stdout contract; exit 0 on successful detection, exit 1 only on invalid `--root`.

**Imports pattern** (lines 7-11 of `context_builder.py`):

```python
import argparse
import fnmatch
import pathlib
import subprocess
import sys
```

For detect: use `argparse`, `json`, `pathlib`, `sys` only — no subprocess unless git commit stamp needed later.

**`--root` path validation** (lines 118-127 of `context_builder.py`):

```python
    root = pathlib.Path(args.root).resolve()
    cwd = pathlib.Path.cwd().resolve()
    # Only allow root == cwd or a descendant of cwd (root is under cwd).
    # Reject ancestor paths (e.g. --root /) to prevent unintended filesystem walks.
    if not (root == cwd or str(root).startswith(str(cwd) + "/")):
        print(f"ERROR: --root {root} is outside working directory {cwd}")
        sys.exit(1)
    if not root.is_dir():
        print(f"ERROR: --root {root} does not exist or is not a directory")
        sys.exit(1)
```

Copy verbatim — also available as `_validate_root()` in `planning_scaffold.py` lines 73-82.

**Skip dirs + depth-limited walk** (lines 13, 44-59 of `context_builder.py` + GSD `init.cjs` lines 424-436):

```python
ALWAYS_EXCLUDE = {".planning", ".git", "__pycache__", ".DS_Store", "node_modules"}
# Extend for detect (from GSD init.cjs):
SKIP_DIRS = ALWAYS_EXCLUDE | {".claude", ".codex", "target", "dist", "build"}
```

GSD detection core (port to Python):

```javascript
function findCodeFiles(dir, depth) {
  if (depth > 3) return false;
  // ... iterdir, check extension, recurse into non-skip dirs
}
```

**JSON stdout + graceful exit** (pattern from RESEARCH.md, aligned with `context_builder.py` always-exit-0 on success):

```python
import json

def main() -> None:
    # ... detection logic ...
    result = {
        "is_brownfield": has_code or has_package_file,
        "has_existing_code": has_code,
        "has_package_file": has_package_file,
        "has_codebase_map": (root / ".planning" / "codebase").is_dir(),
        "needs_codebase_map": (has_code or has_package_file) and not has_map,
        "code_extensions_found": sorted(extensions_found),
    }
    print(json.dumps(result, indent=2))
    sys.exit(0)  # detection success always 0; only path errors exit 1
```

**Error handling pattern** (stderr + exit 1, from `validate_spec.py` lines 60-66):

```python
        print(
            "ERROR: SPEC.md not found in .planning/ or project root.\n"
            "Run /spec-phase first to create and approve a spec.",
            file=sys.stderr,
        )
        sys.exit(1)
```

Use same `ERROR:` prefix and actionable message for invalid `--root`.

---

### `mise-en-place/tool-detect-brownfield/test_detect_brownfield.py` (test, batch)

**Analog:** `mise-en-place/tool-context-builder/test_context_builder.py` + `mise-en-place/tool-planning-scaffold/test_planning_scaffold.py`

**Imports + sys.path pattern** (lines 1-10 of `test_context_builder.py`):

```python
"""Tests for context_builder.py"""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
```

**tmp_path fixture for isolated project roots** (lines 15-18 of `test_context_builder.py`):

```python
@pytest.fixture
def tmp_project(tmp_path):
    """Minimal project root with no .gitignore or .planning/."""
    return tmp_path
```

**Subprocess integration test pattern** (lines 24-39 of `test_context_builder.py`):

```python
def test_output_contains_all_four_sections(tmp_project):
    (tmp_project / "README.md").write_text("# Test Project\n", encoding="utf-8")
    script = Path(__file__).parent / "context_builder.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(tmp_project),
    )
    assert result.returncode == 0, f"Script exited {result.returncode}: {result.stderr}"
```

For detect: create `(tmp_project / "src" / "main.py")` for brownfield; empty tmp for greenfield; assert JSON keys and `needs_codebase_map`.

**Direct function unit test pattern** (from `test_planning_scaffold.py` lines 24-29):

```python
def test_scaffold_creates_planning_dirs(tmp_project):
    scaffold(tmp_project)
    assert (tmp_project / ".planning").is_dir()
    assert (tmp_project / ".planning" / "codebase").is_dir()
```

Test `find_code_files()` / `has_package_file()` directly with tmp fixtures before subprocess tests.

**Exit code assertion pattern** (from `test_validate_spec.py` lines 37-39):

```python
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0
```

---

### `mise-en-place/tool-detect-brownfield/SKILL.md` (hook/config, request-response)

**Analog:** `mise-en-place/tool-context-builder/SKILL.md`

**Frontmatter pattern** (lines 1-4):

```yaml
---
name: tool-context-builder
description: "Assemble a pasteable markdown context packet from the project's directory, dependencies, git history, and key file previews"
---
```

**cursor_skill_adapter block** (lines 6-28): copy verbatim from any existing tool SKILL.md — identical across all `mise-en-place/tool-*/SKILL.md`.

**Invocation + exit contract** (lines 34-52 of `tool-context-builder/SKILL.md`):

```markdown
<process>
Run from the project root:

```shell
python3 mise-en-place/tool-context-builder/context_builder.py [--root PATH] [--depth N]
```

**Arguments:**
- `--root PATH` — project root directory to snapshot (default: current working directory)

Exit code 0 = success (always — the script degrades gracefully if git is unavailable or entry points are not found).
```

Adapt: document JSON stdout schema, list detection fields, note exit 0 on successful detection vs exit 1 on path error.

---

### `mise-en-place/map-codebase/SKILL.md` (hook/provider, event-driven)

**Analog:** `.cursor/skills/gsd-map-codebase/SKILL.md` (orchestration) + `mise-en-place/spec-phase/SKILL.md` (cookbook workflow conventions)

**Frontmatter + cursor_skill_adapter** (from `gsd-map-codebase/SKILL.md` lines 1-28): use cookbook naming `map-codebase`, not `gsd-map-codebase`.

**Objective + sub-agent write-directly pattern** (lines 30-36 of `gsd-map-codebase/SKILL.md`):

```markdown
<objective>
Analyze existing codebase using parallel gsd-codebase-mapper agents to produce structured codebase documents.

Each mapper agent explores a focus area and **writes documents directly** to `.planning/codebase/`. The orchestrator only receives confirmations, keeping context usage minimal.

Output: .planning/codebase/ folder with 7 structured documents about the codebase state.
</objective>
```

**Cookbook adaptation:** use `Task(subagent_type="generalPurpose")` per `spec-phase/SKILL.md` lines 24-27 — cookbook v1 does not ship `gsd-codebase-mapper` in `mise-en-place/`.

**Parallel agent assignment** (lines 78-89 of `gsd-map-codebase/SKILL.md`):

```markdown
<process>
1. Check if .planning/codebase/ already exists (offer to refresh or skip)
2. Create .planning/codebase/ directory structure
3. Spawn 4 parallel gsd-codebase-mapper agents:
   - Agent 1: tech focus → writes STACK.md, INTEGRATIONS.md
   - Agent 2: arch focus → writes ARCHITECTURE.md, STRUCTURE.md
   - Agent 3: quality focus → writes CONVENTIONS.md, TESTING.md
   - Agent 4: concerns focus → writes CONCERNS.md
4. Wait for agents to complete, collect confirmations (NOT document contents)
5. Verify all 7 documents exist with line counts
```

**check_existing user prompt** (from `.cursor/get-shit-done/workflows/map-codebase.md` lines 88-104):

```markdown
What's next?
1. Refresh - Delete existing and remap codebase
2. Update - Keep existing, only update specific documents
3. Skip - Use existing codebase map as-is
```

**Scaffold before map** (from `spec-phase/SKILL.md` lines 40-44):

```shell
python3 mise-en-place/tool-planning-scaffold/planning_scaffold.py scaffold
```

**Seed mappers with raw snapshot** (from `spec-phase/SKILL.md` Step 3 research pattern, lines 91-105):

```shell
python3 mise-en-place/tool-context-builder/context_builder.py
```

Append stdout to sub-agent prompts as optional raw snapshot.

**Sub-agent prompt skeleton** (from RESEARCH.md, aligned with `spec-phase/SKILL.md` research sub-agent contract):

```markdown
Sub-agent prompt must include:
- **Focus:** tech | arch | quality | concerns
- **Output files:** list of `.planning/codebase/*.md` paths (write directly with Write tool)
- **Template sections:** `.cursor/get-shit-done/templates/codebase/<name>.md`
- **Rules:** concrete file paths with backticks; current state only; mark uncertain [unverified]; confirm paths + line counts only in final message
```

**Template format reference** (from `.planning/codebase/STACK.md` lines 1-14 — live output in this repo):

```markdown
# Technology Stack

**Analysis Date:** 2026-05-20

## Languages

**Primary:**
- Markdown — all documentation...
```

**Flags:** optional `--fast` single-agent mode per `gsd-map-codebase/SKILL.md` lines 42-46.

---

### `mise-en-place/spec-phase/SKILL.md` (hook/provider, request-response — extend)

**Analog:** `mise-en-place/spec-phase/SKILL.md` (self) + `gsd-map-codebase` check_existing flow

**Existing Step 1 startup** (lines 36-63): keep unchanged; insert new **Step 0** before Step 1 (or between scaffold and Q&A per RESEARCH.md).

**Sub-agent spawning convention** (lines 24-27):

```markdown
## D. Subagent Spawning
When the workflow needs to spawn a subagent:
- Use `Task(subagent_type="generalPurpose", ...)`
- Do NOT pass the `model` parameter — use the Cursor default model
```

**Step 0 brownfield branch** (from RESEARCH.md — insert before Step 2 Q&A):

```markdown
## Step 0: Brownfield Detection (before Q&A)

1. Run detection:
   python3 mise-en-place/tool-detect-brownfield/detect_brownfield.py

2. Parse JSON from stdout.

3. If `is_brownfield` is false → continue to Step 2 (greenfield Q&A).

4. If `is_brownfield` is true:
   a. If `needs_codebase_map` is true → run map-codebase workflow (read map-codebase/SKILL.md)
   b. If map exists → offer (1) Refresh (2) Skip (3) Update specific docs
   c. Read `.planning/codebase/STACK.md`, `ARCHITECTURE.md`, `STRUCTURE.md`
   d. Present 3–5 bullet summary of detected capabilities; ask user to confirm/correct
   e. Continue to Step 2 with brownfield mode: do NOT re-ask stack/structure already in map
```

**SPEC.md assembly extension** (lines 109-141 — extend frontmatter + body):

```yaml
---
status: draft
version: 1
date: YYYY-MM-DD
project_type: brownfield   # or greenfield (default)
codebase_map_commit: abc1234  # optional
---
```

Add sections before existing five (brownfield only):

```markdown
## Already Built
## To Build
## Problem
...
```

Keep header canonical forms matching `validate_spec.py` `REQUIRED_SECTIONS`.

**Approval gate unchanged** (lines 143-151): same yes/edit/abort flow; validate_spec handles brownfield sections when `project_type: brownfield`.

---

### `mise-en-place/tool-validate-spec/validate_spec.py` (utility, file-I/O — extend)

**Analog:** `mise-en-place/tool-validate-spec/validate_spec.py` (self)

**Frontmatter parser** (lines 32-50): reuse as-is — already handles arbitrary keys; `project_type` reads via `fm.get("project_type", "greenfield")`.

**Section gate loop** (lines 93-99):

```python
    for header in REQUIRED_SECTIONS:
        if header not in text:
            print(
                f"ERROR: SPEC.md missing required section: {header}",
                file=sys.stderr,
            )
            sys.exit(1)
```

**Brownfield extension** (conditional, after greenfield checks):

```python
BROWNFIELD_SECTIONS = [
    "## Already Built",
    "## To Build",
]

    project_type = fm.get("project_type", "greenfield")
    if project_type == "brownfield":
        for header in BROWNFIELD_SECTIONS:
            if header not in text:
                print(
                    f"ERROR: brownfield SPEC.md missing: {header}",
                    file=sys.stderr,
                )
                sys.exit(1)
```

**Success stdout** (lines 101-104): extend message optionally with `project_type`.

**Critical:** do NOT add brownfield sections to `REQUIRED_SECTIONS` — keep greenfield default path unchanged (Pitfall 4 in RESEARCH.md).

---

### `mise-en-place/tool-validate-spec/test_validate_spec.py` (test, batch — extend)

**Analog:** `mise-en-place/tool-validate-spec/test_validate_spec.py` (self)

**Helper factory pattern** (lines 9-25):

```python
CANONICAL_SECTIONS = [
    "## Problem",
    "## Who It's For",
    "## Constraints",
    "## Success Criteria",
    "## Out of Scope",
]

def _spec_body(include_sections=None):
    sections = include_sections if include_sections is not None else CANONICAL_SECTIONS
    lines = ["---", "status: approved", "version: 1", "date: 2026-05-22", "---", ""]
    for header in sections:
        lines.append(header)
        lines.append("Placeholder content.")
        lines.append("")
    return "\n".join(lines)
```

**Extend helper** for brownfield:

```python
def _brownfield_spec_body(include_brownfield=True):
    lines = ["---", "status: approved", "version: 1", "date: 2026-05-22",
             "project_type: brownfield", "---", ""]
    if include_brownfield:
        lines += ["## Already Built", "Existing auth.", "",
                  "## To Build", "Add billing.", ""]
    lines += [h + "\nPlaceholder." for h in CANONICAL_SECTIONS]
    return "\n".join(lines)
```

**tmp_path + monkeypatch.chdir pattern** (lines 28-39):

```python
def test_approved_spec_exits_zero(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    planning = tmp_path / ".planning"
    planning.mkdir()
    (planning / "SPEC.md").write_text(_spec_body(), encoding="utf-8")
    from validate_spec import main
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0
```

Add tests: brownfield missing `## Already Built` exits 1; greenfield without brownfield sections still exits 0 (regression).

**stderr assertion pattern** (lines 102-117):

```python
    err = capsys.readouterr().err
    assert "missing required section" in err
    assert "## Constraints" in err
```

---

### `mise-en-place/README.md` (config — extend)

**Analog:** `mise-en-place/README.md` (self)

**Tool entry pattern** (lines 7-29):

```markdown
### tool-env-check

Validates that all runtime prerequisites are present (git, python3, bun/node, cursor) before a phase runs. An agent reads `tool-env-check/SKILL.md` to understand how to invoke it.
```

Add entries for `tool-detect-brownfield`, `map-codebase`, and note `spec-phase` brownfield support.

**Usage block** (lines 33-47):

```shell
python3 mise-en-place/tool-<name>/<script>.py [args]
```

Exit code 0 = success. Exit code 1 = failure (details printed to stdout).

Note: validate_spec and detect_brownfield print errors to stderr — match actual behavior in new entries.

**Development section** (lines 49-63): unchanged pytest commands; mention new test directory in quick-run example.

---

## Shared Patterns

### `--root` Path Validation (ASVS V5)
**Source:** `mise-en-place/tool-context-builder/context_builder.py` lines 118-127, `planning_scaffold.py` `_validate_root()` lines 73-82
**Apply to:** `detect_brownfield.py`

```python
    root = pathlib.Path(args.root).resolve()
    cwd = pathlib.Path.cwd().resolve()
    if not (root == cwd or str(root).startswith(str(cwd) + "/")):
        print(f"ERROR: --root {root} is outside working directory {cwd}")
        sys.exit(1)
    if not root.is_dir():
        print(f"ERROR: --root {root} does not exist or is not a directory")
        sys.exit(1)
```

### Stdlib-Only Python Tool Shell
**Source:** all `mise-en-place/tool-*/` scripts
**Apply to:** `detect_brownfield.py`

```python
#!/usr/bin/env python3
"""tool-<name> — one-line purpose. Exit 0: success. Exit 1: failure."""
import argparse
import pathlib
import sys

def main() -> None:
    ...

if __name__ == "__main__":
    main()
```

### Exit-Code Contract
**Source:** Phase 1/2 convention documented in `mise-en-place/README.md` lines 41-42
**Apply to:** all tools

- Exit 0 = success (detect: successful detection regardless of brownfield/greenfield result)
- Exit 1 = failure with actionable message on stderr

### SKILL.md Frontmatter + cursor_skill_adapter
**Source:** `mise-en-place/tool-env-check/SKILL.md` lines 1-28
**Apply to:** `tool-detect-brownfield/SKILL.md`, `map-codebase/SKILL.md`

Identical adapter block across all workflow and tool skills; only `name` and `description` change.

### Workflow Sub-Agent Spawning
**Source:** `mise-en-place/spec-phase/SKILL.md` lines 91-105
**Apply to:** `map-codebase/SKILL.md`, `spec-phase/SKILL.md` Step 0

```markdown
For each accepted research topic, use the **Task tool** to spawn a `generalPurpose` sub-agent. **Do NOT pass the `model` parameter** — use the Cursor default model.
```

Mappers write files directly; orchestrator reads summaries only (STACK + ARCHITECTURE + STRUCTURE for Q&A seed).

### Idempotent `.planning/` Scaffold
**Source:** `mise-en-place/tool-planning-scaffold/planning_scaffold.py` lines 11-31
**Apply to:** spec-phase Step 1, map-codebase pre-flight

```python
PLANNING_DIRS = [
    ".planning",
    ".planning/phases",
    ".planning/codebase",
]
```

Always run scaffold before detection/mapping — creates `.planning/codebase/` for mappers.

### Frontmatter Parsing for Conditional Validation
**Source:** `mise-en-place/tool-validate-spec/validate_spec.py` lines 32-50, 84-91
**Apply to:** `validate_spec.py` brownfield extension

```python
    fm = parse_frontmatter(text)
    status = fm.get("status", "")
    project_type = fm.get("project_type", "greenfield")
```

Default `project_type` to `"greenfield"` so existing specs pass without modification.

### Pytest tmp_path + monkeypatch
**Source:** `mise-en-place/tool-validate-spec/test_validate_spec.py`
**Apply to:** all new and extended tests

- `monkeypatch.chdir(tmp_path)` for cwd-relative tools
- `sys.path.insert(0, str(Path(__file__).parent))` for direct imports
- `pytest.raises(SystemExit)` for exit code assertions

### Seven-File Codebase Map Format
**Source:** `.planning/codebase/*.md` (live) + `.cursor/get-shit-done/templates/codebase/*.md`
**Apply to:** `map-codebase/SKILL.md` mapper prompts

Canonical set: `STACK.md`, `ARCHITECTURE.md`, `CONVENTIONS.md`, `STRUCTURE.md`, `TESTING.md`, `INTEGRATIONS.md`, `CONCERNS.md`

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|------|
| (none) | — | — | All Phase 3 files have direct analogs in Phase 1–2 tools or GSD reference workflows |

**Note:** `detect_brownfield.py` detection algorithm has no Python precedent in-repo — port from GSD `init.cjs` lines 406-474 using Python shell patterns from `context_builder.py`.

## Metadata

**Analog search scope:** `mise-en-place/`, `.cursor/skills/gsd-map-codebase/`, `.cursor/get-shit-done/workflows/map-codebase.md`, `.cursor/get-shit-done/bin/lib/init.cjs`, `.planning/codebase/`, `.cursor/get-shit-done/templates/codebase/`
**Files scanned:** 22
**Pattern extraction date:** 2026-05-22
