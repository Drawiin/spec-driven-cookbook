---
phase: 01-tooling-foundation
fixed_at: 2026-05-21T20:50:00Z
review_path: .planning/phases/01-tooling-foundation/01-REVIEW.md
iteration: 1
findings_in_scope: 11
fixed: 11
skipped: 0
status: all_fixed
---

# Phase 01: Code Review Fix Report

**Fixed at:** 2026-05-21T20:50:00Z
**Source review:** .planning/phases/01-tooling-foundation/01-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 11
- Fixed: 11
- Skipped: 0

## Fixed Issues

### WR-01: IndexError crash when subprocess produces no output — `env_check.py`

**Files modified:** `mise-en-place/tool-env-check/env_check.py`
**Commit:** 95c31c9
**Applied fix:** All three version-extraction sites (cursor path, bun/node fallback, generic path) replaced with safe output guard: `output = (r.stdout or r.stderr).strip()` followed by `ver = output.splitlines()[0].strip() if output else f"{cmd[0]}: no output"`.

---

### WR-02: `git_summary` crashes on `TimeoutExpired` — `context_builder.py`

**Files modified:** `mise-en-place/tool-context-builder/context_builder.py`
**Commit:** 95c31c9
**Applied fix:** Added `except subprocess.TimeoutExpired: return ""` to the inner `run()` helper inside `git_summary`.

---

### WR-03: Dependency fallback silently stops when first file is unreadable — `context_builder.py`

**Files modified:** `mise-en-place/tool-context-builder/context_builder.py`
**Commit:** 95c31c9
**Applied fix:** Moved `break` inside the `try` block so the dependency-file loop only exits on a successful read; a `UnicodeDecodeError` or `OSError` now continues to the next candidate.

---

### WR-04: `load_gitignore_patterns` can crash on unreadable `.gitignore` — `context_builder.py`

**Files modified:** `mise-en-place/tool-context-builder/context_builder.py`
**Commit:** 95c31c9
**Applied fix:** Wrapped `gi.read_text()` in `try/except (UnicodeDecodeError, OSError): return []`.

---

### WR-05: `--root` directory existence not validated before use — `context_builder.py`

**Files modified:** `mise-en-place/tool-context-builder/context_builder.py`
**Commit:** 95c31c9
**Applied fix:** Added `if not root.is_dir(): print(f"ERROR: --root {root} does not exist or is not a directory"); sys.exit(1)` after the traversal check.

---

### WR-06: `_validate_root` never rejects anything — `planning_scaffold.py`

**Files modified:** `mise-en-place/tool-planning-scaffold/planning_scaffold.py`
**Commit:** 95c31c9
**Applied fix:** Replaced dead `if not root.is_absolute()` guard with cwd-based check: `if not (root == cwd or cwd in root.parents or root in cwd.parents)`.

---

### WR-07: `test_gitignore_patterns_applied` is tautological — `test_context_builder.py`

**Files modified:** `mise-en-place/tool-context-builder/test_context_builder.py`
**Commit:** 95c31c9
**Applied fix:** Changed test directory from `node_modules` (in ALWAYS_EXCLUDE) to `vendor` (not in ALWAYS_EXCLUDE) so gitignore pattern logic is actually exercised.

---

### WR-08: Subprocess `returncode` not checked — `env_check.py`

**Files modified:** `mise-en-place/tool-env-check/env_check.py`
**Commit:** 95c31c9
**Applied fix:** All three subprocess paths now check `r.returncode != 0` and return `("✗", f"{cmd[0]}: exited {r.returncode}")` before extracting the version string.

---

### IN-01: `textwrap` imported but never used — `context_builder.py`

**Files modified:** `mise-en-place/tool-context-builder/context_builder.py`
**Commit:** 5d6504c
**Applied fix:** Removed `import textwrap` from module imports.

---

### IN-02: `import os` inside test function body — `test_env_check.py`

**Files modified:** `mise-en-place/tool-env-check/test_env_check.py`
**Commit:** 65c32ff
**Applied fix:** Moved `import os` to module top level alongside other standard-library imports; removed the inline `import os` from inside `test_exits_zero_when_all_checks_pass`.

---

### IN-03: `write_artifact` allows writing to `planning_root` itself — `planning_scaffold.py`

**Files modified:** `mise-en-place/tool-planning-scaffold/planning_scaffold.py`
**Commit:** 629891f
**Applied fix:** Changed boundary condition from `if candidate != resolved_root and resolved_root not in candidate.parents:` to `if resolved_root not in candidate.parents:` — now correctly rejects artifacts that resolve to the root directory itself.

---

_Fixed: 2026-05-21T20:50:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
