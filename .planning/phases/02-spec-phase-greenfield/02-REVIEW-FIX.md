---
phase: 02-spec-phase-greenfield
fixed_at: 2026-05-21T20:30:00-04:00
review_path: .planning/phases/02-spec-phase-greenfield/02-REVIEW.md
iteration: 1
findings_in_scope: 8
fixed: 8
skipped: 0
status: all_fixed
---

# Phase 02: Code Review Fix Report

**Fixed at:** 2026-05-21T20:30:00-04:00
**Source review:** .planning/phases/02-spec-phase-greenfield/02-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 8
- Fixed: 8
- Skipped: 0

## Fixed Issues

### WR-01: `is_excluded` silently mishandles path-specific gitignore patterns

**Files modified:** `mise-en-place/tool-context-builder/context_builder.py`
**Commit:** `5e71e3b`
**Applied fix:** Added `if "/" not in p.strip("/")` guard to the `any()` generator in `is_excluded`, so patterns containing a path separator (e.g. `docs/generated`) are skipped entirely rather than being matched incorrectly against bare entry names.

---

### WR-02: `--root` validation allows ancestor paths all the way to `/`

**Files modified:** `mise-en-place/tool-context-builder/context_builder.py`, `mise-en-place/tool-planning-scaffold/planning_scaffold.py`
**Commit:** `a7a981c`
**Applied fix:** Replaced the permissive `root in cwd.parents` check with `str(root).startswith(str(cwd) + "/")` in both files. This now only allows `root == cwd` or a descendant of cwd — ancestor paths (e.g. `--root /`) are rejected with a clear error message and `sys.exit(1)`.

---

### WR-03: `format_file` raises unhandled `UnicodeDecodeError` on binary files

**Files modified:** `mise-en-place/tool-planning-scaffold/planning_scaffold.py`
**Commit:** `e025998`
**Applied fix:** Wrapped both `path.read_text()` and `path.write_text()` in try/except blocks. `UnicodeDecodeError` on read produces `ERROR: file is not valid UTF-8 (binary?): {path}`; `OSError` on read or write produces `ERROR: cannot read/write file: {exc}`. Both exit with code 1, consistent with the tool contract.

---

### WR-04: `read_artifact` `OSError` propagates as unhandled exception

**Files modified:** `mise-en-place/tool-planning-scaffold/planning_scaffold.py`
**Commit:** `83477d7`
**Applied fix:** Added a try/except `(OSError, UnicodeDecodeError)` block inside `read_artifact()` that re-raises as `OSError` with context. Updated the `main()` `read-artifact` handler to catch `(FileNotFoundError, OSError)` instead of just `FileNotFoundError`, so all read errors produce a clean exit-1 message.

---

### WR-05: `subprocess.run` only catches `TimeoutExpired`, not `OSError`

**Files modified:** `mise-en-place/tool-env-check/env_check.py`
**Commit:** `a044519`
**Applied fix:** Added `OSError` to the `except` tuple in all three invocation paths (cursor path, bun/node fallback path, and generic check path). Each now returns `("✗", "{cmd}: failed to execute")` on `OSError`, matching the existing `TimeoutExpired` pattern.

---

### IN-01: File preview breaks markdown fences when content contains triple backticks

**Files modified:** `mise-en-place/tool-context-builder/context_builder.py`
**Commit:** `fea4e65`
**Applied fix:** Changed the fence delimiter in `preview_file` from ` ``` ` to `~~~`. Tilde fences are CommonMark-compliant and do not nest with backtick fences, so previewing a file that contains ` ``` ` on a bare line no longer corrupts the context packet.

---

### IN-02: `test_output_contains_all_four_sections` does not assert exit code

**Files modified:** `mise-en-place/tool-context-builder/test_context_builder.py`
**Commit:** `104bdeb`
**Applied fix:** Added `assert result.returncode == 0, f"Script exited {result.returncode}: {result.stderr}"` as the first assertion, before the four section-header assertions. This ensures a non-zero exit code is caught even when partial output includes the expected headers.

---

### IN-03: Manual `CURSOR_TRACE_ID` backup/restore in test is redundant

**Files modified:** `mise-en-place/tool-env-check/test_env_check.py`
**Commit:** `4680e67`
**Applied fix:** Removed the explicit `env_backup = os.environ.pop(...)` / `finally: os.environ["CURSOR_TRACE_ID"] = env_backup` block and the surrounding try/finally. Replaced with a single `os.environ.pop("CURSOR_TRACE_ID", None)` inside the `patch.dict` context — the `patch.dict` context manager already restores the original environment (including `CURSOR_TRACE_ID`) on exit.

---

_Fixed: 2026-05-21T20:30:00-04:00_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
