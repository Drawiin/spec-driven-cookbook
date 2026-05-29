# Phase 2: Spec Phase — Greenfield - Pattern Map

**Mapped:** 2026-05-21
**Files analyzed:** 4
**Analogs found:** 4 / 4

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `mise-en-place/spec-phase/SKILL.md` | workflow skill | event-driven (multi-turn Q&A + sub-agent spawn) | `.cursor/skills/gsd-discuss-phase/SKILL.md` | role-match |
| `mise-en-place/tool-validate-spec/SKILL.md` | tool skill contract | request-response (CLI invocation) | `mise-en-place/tool-env-check/SKILL.md` | exact |
| `mise-en-place/tool-validate-spec/validate_spec.py` | implementation script | request-response (file read → exit code) | `mise-en-place/tool-planning-scaffold/planning_scaffold.py` | role-match |
| `mise-en-place/tool-validate-spec/test_validate_spec.py` | test file | N/A | `mise-en-place/tool-planning-scaffold/test_planning_scaffold.py` | exact |

---

## Pattern Assignments

### `mise-en-place/spec-phase/SKILL.md` (workflow skill, event-driven)

**Analog:** `.cursor/skills/gsd-discuss-phase/SKILL.md`

**What this file is:** Pure agent instructions — no Python companion. The SKILL.md IS the implementation. The agent reads this file and executes the Q&A flow, research sub-task spawning, and approval gate entirely through conversational turns and Cursor tools.

**How it differs from the analog:** `gsd-discuss-phase` covers a single GSD phase context-gathering flow. `spec-phase/SKILL.md` covers a full product spec workflow with five fixed Q&A categories, research sub-task spawning via the Task tool, SPEC.md assembly, and an in-flow approval gate with StrReplace patching. The agent instruction sections are more elaborate, but the SKILL.md document structure is identical.

**Front-matter + cursor_skill_adapter block** (lines 1–28 of analog — copy verbatim, change `name` and `description` only):
```markdown
---
name: spec-phase
description: "Structured deep-questioning flow → SPEC.md → explicit approval gate"
---

<cursor_skill_adapter>
## A. Skill Invocation
- This skill is invoked when the user mentions `spec-phase` or describes a task matching this skill.
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

**`<objective>` block pattern** (analog lines 30–42 — use same section name and narrative style):
```markdown
<objective>
Take a developer from an empty repo to an explicitly approved SPEC.md.

**How it works:**
1. Scaffold `.planning/` if needed
2. Check for existing SPEC.md (offer resume / restart / abort)
3. Run structured Q&A across five fixed categories
4. Optionally spawn research sub-agents for knowledge gaps
5. Assemble and write SPEC.md (status: draft)
6. Run in-flow approval gate — patch status to approved on "yes"

**Output:** `.planning/SPEC.md` with `status: approved` and five populated sections
</objective>
```

**`<process>` block pattern** (analog lines 59+ — workflow SKILL.md puts numbered steps here, not CLI commands):
```markdown
<process>
## Step 1: Startup
- Run: `python3 mise-en-place/tool-planning-scaffold/planning_scaffold.py scaffold`
- Also create `.planning/research/` if it does not exist.
- Check for `.planning/SPEC.md`. If found, read its front-matter status and ask:
  "An existing spec was found (status: `<status>`). Continue from here, start fresh, or abort?"
  - **continue** → skip to Step 4 (Approval Gate) if approved; skip to Step 3 if draft
  - **start fresh** → proceed from Step 2 (will overwrite)
  - **abort** → exit without changes

## Step 2: Q&A Flow — Category Spine
...
</process>
```

**Key structural rule:** Workflow SKILL.md files use `<objective>` and `<process>` XML-style tags (lowercase). The `cursor_skill_adapter` block is always the first section after front-matter. Never reference a Python CLI invocation in the `<process>` of a workflow skill — the process section contains agent instructions.

---

### `mise-en-place/tool-validate-spec/SKILL.md` (tool skill, request-response)

**Analog:** `mise-en-place/tool-env-check/SKILL.md`

**What this file is:** A short agent-facing contract documenting how to invoke the Python script. Four sections total: YAML front-matter, `cursor_skill_adapter`, `<objective>`, `<process>`.

**How it differs from the analog:** `tool-env-check` runs subprocess checks; `tool-validate-spec` reads a file and checks a YAML field. Both follow the identical document structure and exit-code contract format. Only the `name`, `description`, `<objective>`, and the CLI invocation line in `<process>` change.

**Complete structure to replicate** (full analog is 45 lines — replicate exactly, changing only the four items noted):
```markdown
---
name: tool-validate-spec                          # CHANGE from tool-env-check
description: "Check that SPEC.md exists and has status: approved before planning"  # CHANGE
---

<cursor_skill_adapter>
## A. Skill Invocation
...                                               # COPY VERBATIM — do not edit
</cursor_skill_adapter>

<objective>
Check that `.planning/SPEC.md` exists and carries `status: approved`.
Exit 0 = approved. Exit 1 = not approved or file missing (message to stderr).
</objective>                                      # CHANGE content only

<process>
Run from the project root:

```shell
python3 mise-en-place/tool-validate-spec/validate_spec.py [--spec PATH]
```

Exit code 0 = SPEC.md found and status is approved.
Exit code 1 = SPEC.md missing, no front-matter, or status is not approved.

The script prints a human-readable result to stdout (✓) or stderr (ERROR: ...).
Optional `--spec PATH` overrides the default `.planning/SPEC.md` lookup.
</process>                                        # CHANGE content only
```

---

### `mise-en-place/tool-validate-spec/validate_spec.py` (implementation script, request-response)

**Analog:** `mise-en-place/tool-planning-scaffold/planning_scaffold.py`

**What this file is:** A stdlib-only Python script that reads `.planning/SPEC.md`, parses the YAML front-matter, checks `status == approved`, and exits with a clear code and message.

**How it differs from the analog:** `planning_scaffold.py` creates directories and has multiple subcommands via `argparse`. `validate_spec.py` is simpler — single path of execution, one optional `--spec` argument, no subcommands. Both share the same stdlib import set (`pathlib`, `sys`, `argparse`) and the same exit-code pattern.

**Module docstring pattern** (analog lines 1–6 — copy format, change description):
```python
#!/usr/bin/env python3
"""
tool-validate-spec — Check that SPEC.md exists and has status: approved.
Exit 0: approved. Exit 1: not approved or file not found (message to stderr).
"""
```

**Import block pattern** (analog lines 7–9 — same three stdlib modules; drop `argparse` if no CLI args needed, but RESEARCH.md recommends keeping it for `--spec`):
```python
import argparse
import pathlib
import sys
```

**`argparse` setup pattern** (analog lines 70–94 — for a single optional arg, use this simpler form):
```python
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check that SPEC.md is approved before planning.",
    )
    parser.add_argument(
        "--spec",
        default=None,
        help="Path to SPEC.md (default: searches .planning/SPEC.md then SPEC.md)",
    )
    args = parser.parse_args()
```

**Path resolution + error exit pattern** (analog lines 96–109 — adapt for file-not-found rather than directory-not-found):
```python
    # Resolve spec path
    if args.spec:
        spec_path = pathlib.Path(args.spec)
        if not spec_path.exists():
            print(
                f"ERROR: {spec_path} not found.",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        for candidate in SPEC_CANDIDATES:
            if candidate.exists():
                spec_path = candidate
                break
        else:
            print(
                "ERROR: SPEC.md not found in .planning/ or project root.\n"
                "Run /spec-phase first to create and approve a spec.",
                file=sys.stderr,
            )
            sys.exit(1)
```

**`sys.exit()` success pattern** (analog line 99 — use same positive confirmation format):
```python
    print(f"✓ SPEC.md approved (version {version}, {date})")
    sys.exit(0)
```

**`if __name__ == "__main__":` guard** (analog lines 127–128 — always present):
```python
if __name__ == "__main__":
    main()
```

**File I/O pattern** (analog `read_artifact` function lines 34–38 — same `read_text(encoding="utf-8")`):
```python
text = spec_path.read_text(encoding="utf-8")
```

**YAML front-matter parser** (new function, no analog in codebase — use RESEARCH.md Pattern 2 exactly):
```python
def parse_frontmatter(text: str) -> dict:
    """Parse flat YAML front-matter. Returns {} if none found or malformed."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end].strip()
    result = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result
```
Note: Use `.splitlines()` not `.split("\n")` — handles Windows `\r\n` endings correctly (Pitfall 2 in RESEARCH.md).

---

### `mise-en-place/tool-validate-spec/test_validate_spec.py` (test file)

**Analog:** `mise-en-place/tool-planning-scaffold/test_planning_scaffold.py`

**What this file is:** pytest unit tests for `validate_spec.py`. Tests cover: approved spec exits 0, draft spec exits 1, missing file exits 1, malformed front-matter exits 1.

**How it differs from the analog:** `test_planning_scaffold.py` tests directory creation and file I/O helpers by calling them directly. `test_validate_spec.py` tests the `main()` function and `parse_frontmatter()` helper using temporary SPEC.md files written to `tmp_path`. Both use the same `sys.path.insert` import trick, the same `tmp_path` fixture, and the same `pytest.raises(SystemExit)` exit-code assertion pattern.

**Module docstring + import block** (analog lines 1–9 — copy exactly, change module name):
```python
"""Tests for validate_spec.py"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from validate_spec import main, parse_frontmatter
```

**`tmp_path`-based fixture pattern** (analog lines 14–17 — SPEC.md tests need a `tmp_spec` helper):
```python
@pytest.fixture
def approved_spec(tmp_path):
    """Write an approved SPEC.md to tmp_path/.planning/SPEC.md."""
    planning = tmp_path / ".planning"
    planning.mkdir()
    spec = planning / "SPEC.md"
    spec.write_text(
        "---\nstatus: approved\nversion: 1\ndate: 2026-05-21\n---\n\n# Spec\n",
        encoding="utf-8",
    )
    return spec
```

**`pytest.raises(SystemExit)` + exit code assertion pattern** (analog lines 28–34, 66–70 — replicate for every exit-code test):
```python
def test_approved_spec_exits_zero(approved_spec, monkeypatch):
    """main() exits 0 when SPEC.md status is approved."""
    monkeypatch.chdir(approved_spec.parent.parent)  # set cwd to tmp project root
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0
```

```python
def test_draft_spec_exits_one(tmp_path, monkeypatch):
    """main() exits 1 when SPEC.md status is draft."""
    planning = tmp_path / ".planning"
    planning.mkdir()
    (planning / "SPEC.md").write_text(
        "---\nstatus: draft\nversion: 1\ndate: 2026-05-21\n---\n\n# Spec\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
```

**Direct function test pattern** (analog lines 47–53 — test `parse_frontmatter` directly, not via `main()`):
```python
def test_parse_frontmatter_returns_empty_dict_on_missing_delimiters():
    """parse_frontmatter returns {} when no --- block is present."""
    result = parse_frontmatter("# Just a heading\n\nNo front-matter here.\n")
    assert result == {}
```

**Test naming convention:** `test_<what>_<expected outcome>` (same as analog — e.g., `test_scaffold_creates_planning_dirs`, `test_scaffold_is_idempotent`). For validate_spec tests: `test_approved_spec_exits_zero`, `test_draft_spec_exits_one`, `test_missing_spec_exits_one`, `test_malformed_frontmatter_exits_one`.

---

## Shared Patterns

### SKILL.md Front-Matter + `cursor_skill_adapter` Block
**Source:** `mise-en-place/tool-env-check/SKILL.md` lines 1–28
**Apply to:** Both `spec-phase/SKILL.md` and `tool-validate-spec/SKILL.md`
```markdown
---
name: <skill-name>
description: "<one-line description>"
---

<cursor_skill_adapter>
## A. Skill Invocation
- This skill is invoked when the user mentions `<skill-name>` or describes a task matching this skill.
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

### Exit-Code Contract (Python scripts)
**Source:** `mise-en-place/tool-env-check/env_check.py` lines 86–96 and `mise-en-place/tool-planning-scaffold/planning_scaffold.py` lines 69–128
**Apply to:** `validate_spec.py`

The project-wide contract is: exit 0 = success, exit 1 = failure with a human-readable message. Success messages go to stdout; error messages go to stderr. The final line of `main()` is always `sys.exit(0)` on the success path; error paths use `sys.exit(1)` inline with a `print(..., file=sys.stderr)`.

```python
# Success path (env_check.py analog lines 95-96)
print("✓ SPEC.md approved (version {version}, {date})")
sys.exit(0)

# Error path (planning_scaffold.py analog lines 45-46)
print(f"ERROR: <specific actionable message>", file=sys.stderr)
sys.exit(1)
```

### `sys.path.insert` Import Trick (test files)
**Source:** `mise-en-place/tool-planning-scaffold/test_planning_scaffold.py` lines 7–9
**Apply to:** `test_validate_spec.py`
```python
sys.path.insert(0, str(Path(__file__).parent))
from validate_spec import main, parse_frontmatter
```
This pattern allows pytest to import the sibling `.py` file without installing the package. Copy verbatim, changing only the module name.

### `pathlib` + `encoding="utf-8"` File Reads
**Source:** `mise-en-place/tool-planning-scaffold/planning_scaffold.py` lines 35–38, 53–56
**Apply to:** `validate_spec.py`
```python
# All file reads in this codebase use pathlib + explicit UTF-8 encoding
text = path.read_text(encoding="utf-8")
```
Never use `open()` with default encoding — the project uses `pathlib.Path.read_text(encoding="utf-8")` exclusively.

---

## No Analog Found

All four files have analogs. No entries in this section.

---

## Metadata

**Analog search scope:** `mise-en-place/` (all subdirectories), `.cursor/skills/gsd-discuss-phase/`
**Files read:** 8 (4 SKILL.md, 3 `.py`, 1 test file as primary analogs)
**Pattern extraction date:** 2026-05-21
