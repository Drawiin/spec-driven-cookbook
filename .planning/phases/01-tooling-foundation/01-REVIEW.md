---
phase: 01-tooling-foundation
reviewed: 2026-05-21T20:04:00Z
depth: standard
files_reviewed: 10
files_reviewed_list:
  - mise-en-place/README.md
  - mise-en-place/tool-env-check/SKILL.md
  - mise-en-place/tool-env-check/env_check.py
  - mise-en-place/tool-env-check/test_env_check.py
  - mise-en-place/tool-context-builder/SKILL.md
  - mise-en-place/tool-context-builder/context_builder.py
  - mise-en-place/tool-context-builder/test_context_builder.py
  - mise-en-place/tool-planning-scaffold/SKILL.md
  - mise-en-place/tool-planning-scaffold/planning_scaffold.py
  - mise-en-place/tool-planning-scaffold/test_planning_scaffold.py
findings:
  critical: 0
  warning: 8
  info: 3
  total: 11
status: findings
---

# Phase 01: Code Review Report

**Reviewed:** 2026-05-21T20:04:00Z
**Depth:** standard
**Files Reviewed:** 10
**Status:** findings

## Summary

Three Python tools (env-check, context-builder, planning-scaffold) were reviewed against
their plan specs. Security controls (no `shell=True`, no `capture_output`, explicit arg arrays)
are correctly implemented in all scripts. Exit code conventions and SKILL.md contracts are
accurate. No critical bugs or data loss risks found.

Eight warnings were identified across the three scripts and one test file. The most impactful
are: a latent `IndexError` crash in `env_check.py` when a binary produces no output, a missing
`TimeoutExpired` handler in `context_builder.py` that contradicts the declared threat model,
a dependency-fallback logic bug in `context_builder.py`, and a dead security check in
`planning_scaffold.py` that provides a false sense of protection without actually validating
the `--root` argument.

Three info-level items: one unused import, one in-function import, and a boundary condition in
`write_artifact`.

---

## Warnings

### WR-01: IndexError crash when subprocess produces no output — `env_check.py`

**File:** `mise-en-place/tool-env-check/env_check.py:35,53,71`

**Issue:** All three version-extraction sites use `(r.stdout or r.stderr).splitlines()[0]`
without guarding against empty output. If a binary is present, exits 0, but writes nothing to
stdout or stderr, this raises an unhandled `IndexError` and crashes the script — printing a
Python traceback instead of showing `✗ <tool>: no output`. The crash also prevents subsequent
checks from running and makes exit code semantics undefined.

Affected lines: cursor subprocess (35), node fallback (53), generic path (71).

**Fix:**

```python
# Replace every version extraction site with a safe getter:
output = (r.stdout or r.stderr).strip()
ver = output.splitlines()[0].strip() if output else f"{cmd[0]}: no output"
return ("✓", ver)
```

---

### WR-02: `git_summary` crashes on `TimeoutExpired` — `context_builder.py`

**File:** `mise-en-place/tool-context-builder/context_builder.py:56`

**Issue:** The inner `run()` helper passes `timeout=10` to `subprocess.run` but never catches
`subprocess.TimeoutExpired`. The plan's threat model (T-02-03) explicitly requires graceful
fallback on timeout: *"graceful string return on TimeoutExpired"*. As written, a slow git
operation raises an unhandled exception, crashing the script even though the spec says it
should always exit 0.

**Fix:**

```python
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
```

---

### WR-03: Dependency fallback silently stops when first file is unreadable — `context_builder.py`

**File:** `mise-en-place/tool-context-builder/context_builder.py:127-135`

**Issue:** `break` is placed inside the `if dep_path.exists()` block but outside the
`try/except`. When `pyproject.toml` (the first candidate) exists but throws `UnicodeDecodeError`
or `OSError`, the exception is caught (leaving `dep_content = None`), and then `break`
immediately exits the loop — no further candidates are tried. The output shows
`_(none detected)_` even though `package.json` or `requirements.txt` may be readable.

```python
# Current (buggy) — break fires whether or not read succeeded:
if dep_path.exists() and dep_path.is_file():
    try:
        dep_content = dep_path.read_text(encoding="utf-8")
        dep_name = dep_file
    except (UnicodeDecodeError, OSError):
        pass
    break  # <── always breaks on first found file
```

**Fix:** Move `break` inside the `try` block so the loop only stops when a successful read
occurred:

```python
if dep_path.exists() and dep_path.is_file():
    try:
        dep_content = dep_path.read_text(encoding="utf-8")
        dep_name = dep_file
        break   # only break on successful read
    except (UnicodeDecodeError, OSError):
        pass    # continue to next candidate
```

---

### WR-04: `load_gitignore_patterns` can crash on unreadable `.gitignore` — `context_builder.py`

**File:** `mise-en-place/tool-context-builder/context_builder.py:26`

**Issue:** `gi.read_text(encoding="utf-8")` is called without a try/except. If `.gitignore`
exists but is not valid UTF-8 (e.g., a binary blob, or a file saved in latin-1), it raises
`UnicodeDecodeError`, propagating unhandled through `main()` and crashing the script. The
spec says the tool degrades gracefully; `.gitignore` encoding failures are a real-world
occurrence.

**Fix:**

```python
def load_gitignore_patterns(root: pathlib.Path) -> list:
    gi = root / ".gitignore"
    if not gi.exists():
        return []
    try:
        lines = gi.read_text(encoding="utf-8").splitlines()
    except (UnicodeDecodeError, OSError):
        return []
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]
```

---

### WR-05: `--root` directory existence not validated before use — `context_builder.py`

**File:** `mise-en-place/tool-context-builder/context_builder.py:107-119`

**Issue:** After the path-relation check passes, there is no `root.exists()` or
`root.is_dir()` guard. Passing `--root /nonexistent` passes the traversal check and then
reaches `build_tree`, which calls `root.iterdir()`. This raises `FileNotFoundError` —
not caught by the `except PermissionError` in `build_tree` — producing an unhandled traceback
instead of a clear error message.

**Fix:**

```python
root = pathlib.Path(args.root).resolve()
cwd = pathlib.Path.cwd().resolve()
if not (root == cwd or cwd in root.parents or root in cwd.parents):
    print(f"ERROR: --root {root} is outside working directory {cwd}")
    sys.exit(1)
if not root.is_dir():
    print(f"ERROR: --root {root} does not exist or is not a directory")
    sys.exit(1)
```

---

### WR-06: `_validate_root` never rejects anything — `planning_scaffold.py`

**File:** `mise-en-place/tool-planning-scaffold/planning_scaffold.py:59-65`

**Issue:** The function's docstring states *"Rejects traversal tricks (e.g. ../../etc)"*, but
`pathlib.Path(...).resolve()` always returns an absolute path — so `if not root.is_absolute()`
is always `False`. The guard is dead code; no root path is ever rejected.

The plan (01-03-PLAN.md) required the same cwd-based validation as `context_builder.py`
(Shared Pattern 4): validate that root is within a parent/child relationship to cwd. That
check was never implemented. This means `--root /tmp/anything` is accepted silently for all
subcommands.

The practical impact is limited (write_artifact has its own guard; scaffold only creates
`.planning/` within root), but the false documentation and missing control are a correctness
and maintainability concern.

**Fix:**

```python
def _validate_root(raw_root: str) -> pathlib.Path:
    root = pathlib.Path(raw_root).resolve()
    cwd = pathlib.Path.cwd().resolve()
    if not (root == cwd or cwd in root.parents or root in cwd.parents):
        print(f"ERROR: --root {raw_root!r} is outside working directory {cwd}")
        sys.exit(1)
    return root
```

---

### WR-07: `test_gitignore_patterns_applied` is tautological — `test_context_builder.py`

**File:** `mise-en-place/tool-context-builder/test_context_builder.py:51-58`

**Issue:** The test uses `node_modules` as the directory to verify gitignore exclusion. However,
`node_modules` is a member of `ALWAYS_EXCLUDE` in `context_builder.py`. The directory would be
excluded from `build_tree` even if no gitignore patterns were loaded at all — the gitignore
path in `is_excluded` is never actually exercised by this test.

The test name, docstring, and assertion all claim to verify gitignore behavior, but they verify
`ALWAYS_EXCLUDE` behavior. If `load_gitignore_patterns` returned `[]` regardless of
`.gitignore`, this test would still pass.

**Fix:** Use a custom directory name that is not in `ALWAYS_EXCLUDE`:

```python
def test_gitignore_patterns_applied(tmp_project):
    """Directories matching gitignore patterns (but not ALWAYS_EXCLUDE) are excluded."""
    (tmp_project / "vendor").mkdir()  # 'vendor' is not in ALWAYS_EXCLUDE
    (tmp_project / ".gitignore").write_text("vendor/\n", encoding="utf-8")
    patterns = load_gitignore_patterns(tmp_project)
    tree = build_tree(tmp_project, patterns, depth=3)
    joined = "\n".join(tree)
    assert "vendor" not in joined
```

---

### WR-08: Subprocess `returncode` not checked — `env_check.py`

**File:** `mise-en-place/tool-env-check/env_check.py:64-74`

**Issue:** In the generic check path, after `subprocess.run` completes without a timeout, the
code extracts a version string and returns `("✓", ver)` regardless of `r.returncode`. A binary
that exits non-zero (broken installation, wrapper script failure) will be reported as present
and passing. The same applies to the cursor subprocess path (line 28) and node fallback (line
45).

This is a correctness issue: a tool that is present but non-functional reports as `✓`.

**Fix:** Treat non-zero returncode as failure:

```python
try:
    r = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=3,
    )
    if r.returncode != 0:
        return ("✗", f"{cmd[0]}: exited {r.returncode}")
    output = (r.stdout or r.stderr).strip()
    ver = output.splitlines()[0].strip() if output else f"{cmd[0]}: no output"
    return ("✓", ver)
except subprocess.TimeoutExpired:
    return ("✗", f"{cmd[0]}: timed out")
```

---

## Info

### IN-01: `textwrap` imported but never used — `context_builder.py`

**File:** `mise-en-place/tool-context-builder/context_builder.py:12`

**Issue:** `import textwrap` appears in the imports but `textwrap` is not referenced anywhere in
the file. Dead import adds minor noise.

**Fix:** Remove line 12 (`import textwrap`).

---

### IN-02: `import os` inside test function body — `test_env_check.py`

**File:** `mise-en-place/tool-env-check/test_env_check.py:26`

**Issue:** `import os` is placed inline inside `test_exits_zero_when_all_checks_pass` rather
than at the module top level. PEP 8 convention requires imports at the top of the file.

**Fix:** Move `import os` to the top of the file alongside the other standard-library imports.

---

### IN-03: `write_artifact` allows writing to `planning_root` itself — `planning_scaffold.py`

**File:** `mise-en-place/tool-planning-scaffold/planning_scaffold.py:44`

**Issue:** The path validation condition is:
```python
if candidate != resolved_root and resolved_root not in candidate.parents:
```
The first clause (`candidate != resolved_root`) means that if `artifact` resolves to exactly
`planning_root` itself (e.g., artifact `"."` or `""`), the check passes. Calling
`candidate.write_text(...)` on a directory raises `IsADirectoryError`, which is unhandled.

The guard should require that `planning_root` is a parent of `candidate` (not equal to it):

```python
if resolved_root not in candidate.parents:
    print(f"ERROR: artifact path {artifact!r} escapes .planning/ root")
    sys.exit(1)
```

---

_Reviewed: 2026-05-21T20:04:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
