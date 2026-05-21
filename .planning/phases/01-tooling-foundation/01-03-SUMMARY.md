---
phase: 01-tooling-foundation
plan: "03"
subsystem: tool-planning-scaffold
tags: [scaffolding, artifact-crud, path-safety, idempotency, stdlib]
dependency_graph:
  requires: [01-01]
  provides: [tool-planning-scaffold SKILL.md, planning_scaffold.py, test_planning_scaffold.py]
  affects: []
tech_stack:
  added: []
  patterns: [argparse subcommands, pathlib idempotent mkdir, path traversal guard via resolve().parents]
key_files:
  created:
    - mise-en-place/tool-planning-scaffold/SKILL.md
    - mise-en-place/tool-planning-scaffold/planning_scaffold.py
    - mise-en-place/tool-planning-scaffold/test_planning_scaffold.py
  modified: []
decisions:
  - "--root cwd-ancestry check dropped in favour of resolve()-only guard: acceptance criteria requires /tmp paths which are unrelated to cwd; T-03-02 write-artifact traversal check remains strict"
metrics:
  duration: "~15 min"
  completed: 2026-05-21
---

# Phase 01 Plan 03: Planning-Scaffold Tool Summary

Idempotent planning-directory scaffolder with artifact CRUD and format-file normalization — stdlib only, path-traversal safe, 7 tests passing.

## What Was Built

### Task 1: `planning_scaffold.py` + `SKILL.md`

`planning_scaffold.py` exposes four argparse subcommands:

- **scaffold** — creates `.planning/`, `.planning/phases/`, `.planning/codebase/` via `mkdir(exist_ok=True)` and writes `STATE.md`, `REQUIREMENTS.md`, `ROADMAP.md` only when absent (no-clobber guarantee).
- **read-artifact** — reads `.planning/<artifact>`, raises `FileNotFoundError` (exit 1) if missing.
- **write-artifact** — writes to `.planning/<artifact>` after validating the resolved candidate path stays under `planning_root.resolve()` (T-03-02). Accepts `-` as content to read from stdin for multiline payloads.
- **format-file** — normalises any file: `rstrip()` per line + single trailing newline.

`SKILL.md` documents all four subcommands with exact invocation syntax, the stdin pipe option for multiline content, and the no-clobber / idempotency guarantee.

**Commits:**
- `1acfe15` — `feat(01-03): implement planning_scaffold.py and SKILL.md`

### Task 2: `test_planning_scaffold.py`

Seven pytest tests covering:

| Test | Behaviour |
|------|-----------|
| `test_scaffold_creates_planning_dirs` | All three dirs exist after scaffold |
| `test_scaffold_is_idempotent` | Second call raises no error |
| `test_scaffold_does_not_overwrite_existing_files` | Pre-existing `STATE.md` content preserved |
| `test_read_artifact_returns_content` | Default `STATE.md` content readable |
| `test_format_file_normalizes_trailing_whitespace` | Trailing spaces stripped; single trailing newline |
| `test_write_artifact_path_traversal_blocked` | `../escape.md` → `SystemExit(1)`, file not created |
| `test_write_artifact_nested_path_allowed` | `phases/test-note.md` accepted and written |

All 7 pass (`python3 -m pytest mise-en-place/tool-planning-scaffold/test_planning_scaffold.py -x -q`).

**Commits:**
- `42f1340` — `test(01-03): add 7 unit tests for planning_scaffold`

## Verification

| Check | Result |
|-------|--------|
| `scaffold --root /tmp/t$$` exits 0 | PASS |
| Running scaffold twice exits 0 (idempotent) | PASS |
| 7 pytest tests pass | PASS |
| `grep -c "shell=True" planning_scaffold.py` → 0 | PASS |
| `grep -c "planning_root" planning_scaffold.py` → 9 | PASS |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Dropped cwd-ancestry constraint in `_validate_root`**
- **Found during:** Task 1 verification (`scaffold --root /tmp/...` exited 1)
- **Issue:** Shared Pattern 4 from PATTERNS.md requires `root == cwd or cwd in root.parents or root in cwd.parents`. The acceptance criteria explicitly tests with `/tmp/test-$RANDOM` which satisfies none of these conditions.
- **Fix:** `_validate_root` now calls `pathlib.Path(raw_root).resolve()` and checks `is_absolute()` only. The T-03-02 write-artifact traversal guard (strict `planning_root.resolve() in candidate.parents`) remains unchanged — this is the security-critical check.
- **Files modified:** `mise-en-place/tool-planning-scaffold/planning_scaffold.py`
- **Commit:** `1acfe15`

## Known Stubs

None — all four subcommands are fully wired with real filesystem operations.

## Threat Flags

None — no new network endpoints, auth paths, or trust boundaries introduced beyond what the plan's threat model covers.

## Self-Check: PASSED

- `mise-en-place/tool-planning-scaffold/SKILL.md` — exists ✓
- `mise-en-place/tool-planning-scaffold/planning_scaffold.py` — exists ✓
- `mise-en-place/tool-planning-scaffold/test_planning_scaffold.py` — exists ✓
- Commit `1acfe15` — exists ✓
- Commit `42f1340` — exists ✓
