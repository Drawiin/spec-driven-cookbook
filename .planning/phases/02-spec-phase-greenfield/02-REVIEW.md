---
phase: 02-spec-phase-greenfield
reviewed: 2026-05-21T20:11:00-04:00
depth: standard
files_reviewed: 7
files_reviewed_list:
  - mise-en-place/tool-context-builder/context_builder.py
  - mise-en-place/tool-context-builder/test_context_builder.py
  - mise-en-place/tool-env-check/env_check.py
  - mise-en-place/tool-env-check/test_env_check.py
  - mise-en-place/tool-planning-scaffold/planning_scaffold.py
  - mise-en-place/tool-planning-scaffold/test_planning_scaffold.py
  - mise-en-place/README.md
findings:
  critical: 0
  warning: 5
  info: 3
  total: 8
status: issues_found
---

# Phase 02: Code Review Report

**Reviewed:** 2026-05-21T20:11:00-04:00
**Depth:** standard
**Files Reviewed:** 7 (3 source, 3 test, 1 doc)
**Status:** issues_found

## Summary

Three Python CLI tools reviewed: `context_builder.py`, `env_check.py`, and `planning_scaffold.py`, plus their corresponding test suites and SKILL.md files. The implementation is largely sound — no hardcoded secrets, no command injection vectors (all `subprocess.run` calls use list args), and path traversal protections are correctly implemented in `write_artifact`. The tools follow consistent patterns and stick to the stdlib.

Five warnings were found — all in the category of incomplete error handling rather than logic bugs. The most impactful is WR-03: `format_file` will throw an unhandled `UnicodeDecodeError` traceback when given a binary file, which is an advertised capability of the `format-file` subcommand. WR-01 is a subtle correctness issue: gitignore patterns containing `/` (path-specific entries like `docs/generated`) are silently mishandled due to stripping `/` and matching only against file names.

No critical issues found.

---

## Warnings

### WR-01: `is_excluded` silently mishandles path-specific gitignore patterns

**File:** `mise-en-place/tool-context-builder/context_builder.py:35`

**Issue:** `fnmatch.fnmatch(name, p.lstrip("/").rstrip("/"))` matches only against the entry's **name** component, not its full path. A `.gitignore` entry like `docs/generated` becomes the pattern `docs/generated` after stripping, and `fnmatch.fnmatch("generated", "docs/generated")` returns `False`. The directory is silently included in the tree even though it should be excluded. No error is raised; the tool just produces wrong output.

**Fix:**

```python
def is_excluded(name: str, patterns: list) -> bool:
    if name in ALWAYS_EXCLUDE:
        return True
    # Skip patterns that contain "/" — these are path-relative and cannot be
    # matched against a bare name; only support simple glob patterns here.
    return any(
        fnmatch.fnmatch(name, p.lstrip("/").rstrip("/"))
        for p in patterns
        if "/" not in p.strip("/")
    )
```

Alternatively, document explicitly in the SKILL.md and a code comment that path-specific gitignore entries (containing `/`) are intentionally unsupported in this MVP scope, so callers are not surprised.

---

### WR-02: `--root` validation allows ancestor paths all the way to `/`

**File:** `mise-en-place/tool-context-builder/context_builder.py:114`

**Issue:** The condition `root in cwd.parents` permits any ancestor of cwd, including `/`. If a caller passes `--root /` from inside `/home/user/project`, the validation passes. The tree builder would then attempt to walk the filesystem from root for up to `--depth` levels, generating enormous output or exposing unintended directories. The same logic is duplicated in `planning_scaffold.py:63`.

**Fix:** Restrict upward traversal to the immediate parent only, or add an explicit depth-from-ancestor cap:

```python
# Only allow root to be the cwd itself, or a direct/transitive child of cwd.
# Do not allow roots that are ancestors of cwd (prevents --root /).
if not (root == cwd or root in cwd.parents or cwd.is_relative_to(root)):
    # cwd.is_relative_to(root) means root is an ancestor of cwd — disallow.
    ...
```

Actually the simpler fix is to tighten to: root must equal cwd, or root must be a descendant of cwd (root is under cwd):

```python
if not (root == cwd or str(root).startswith(str(cwd) + "/")):
    print(f"ERROR: --root {root} is outside working directory {cwd}")
    sys.exit(1)
```

Note: the same fix should be applied to `_validate_root` in `planning_scaffold.py:59-66`.

---

### WR-03: `format_file` raises unhandled `UnicodeDecodeError` on binary files

**File:** `mise-en-place/tool-planning-scaffold/planning_scaffold.py:53`

**Issue:** `format_file` calls `path.read_text(encoding="utf-8")` with no exception handling. The `format-file` subcommand accepts any file path (documented in SKILL.md as "not restricted to `.planning/`"), so a caller passing a binary file receives a Python traceback rather than a clean `ERROR: ...` message and exit code 1. This breaks the tool's own contract: "Exit 1: error (details on stdout)."

**Fix:**

```python
def format_file(path: pathlib.Path) -> None:
    """Normalize: strip trailing whitespace per line + ensure single trailing newline."""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"ERROR: file is not valid UTF-8 (binary?): {path}")
        sys.exit(1)
    except OSError as exc:
        print(f"ERROR: cannot read file: {exc}")
        sys.exit(1)
    lines = [line.rstrip() for line in text.splitlines()]
    normalized = "\n".join(lines).rstrip("\n") + "\n"
    try:
        path.write_text(normalized, encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: cannot write file: {exc}")
        sys.exit(1)
```

---

### WR-04: `read_artifact` `OSError` (e.g. permission denied) propagates as unhandled exception

**File:** `mise-en-place/tool-planning-scaffold/planning_scaffold.py:38`

**Issue:** `read_artifact` only raises `FileNotFoundError`, and `main()` only catches `FileNotFoundError`. If the artifact file exists but is not readable (permissions denied, stale NFS mount, etc.), `path.read_text()` raises `OSError`, which escapes `main()` as an unhandled exception. Again, this violates the "Exit 1: error (details on stdout)" contract.

**Fix:**

```python
def read_artifact(planning_root: pathlib.Path, artifact: str) -> str:
    path = planning_root / artifact
    if not path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}")
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise OSError(f"Cannot read artifact {path}: {exc}") from exc
```

And in `main()`:

```python
        try:
            content = read_artifact(planning_root, args.artifact)
            print(content, end="")
        except (FileNotFoundError, OSError) as exc:
            print(str(exc))
            sys.exit(1)
```

---

### WR-05: `subprocess.run` in `env_check.py` generic path only catches `TimeoutExpired`, not `OSError`

**File:** `mise-en-place/tool-env-check/env_check.py:69`

**Issue:** After `shutil.which(cmd[0])` confirms the binary is in PATH, `subprocess.run` is called with only `subprocess.TimeoutExpired` caught. If the binary exists in PATH but cannot be executed at the moment of the call (permissions revoked, kernel exec limit, NFS issue), `subprocess.run` raises `OSError`. This propagates as an unhandled exception traceback out of `main()`. The same gap exists in the bun/node fallback path (line 48) and the cursor path (line 28).

**Fix** — add `OSError` to the except clause in all three invocation paths:

```python
    except (subprocess.TimeoutExpired, OSError):
        return ("✗", f"{cmd[0]}: failed to execute")
```

---

## Info

### IN-01: File preview breaks markdown fences when content contains triple backticks

**File:** `mise-en-place/tool-context-builder/context_builder.py:99`

**Issue:** `preview_file` wraps file content in a triple-backtick fence (```` ``` ````). If a previewed file (e.g. a `README.md` or `Makefile`) contains a bare ```` ``` ```` on its own line, the markdown code fence terminates early and corrupts the context packet for all subsequent content. This is a cosmetic correctness issue, not a security concern.

**Fix:** Use a tilde fence (`~~~`) instead, which is less likely to appear in source files and does not nest with backtick fences. Or indent the content by 4 spaces to use indented code blocks:

```python
    return f"### `{path.name}`\n~~~\n{content}\n~~~\n"
```

---

### IN-02: `test_output_contains_all_four_sections` does not assert exit code

**File:** `mise-en-place/tool-context-builder/test_context_builder.py:28`

**Issue:** The test asserts section headers appear in stdout but does not check `result.returncode`. If the script exits non-zero but happens to print partial output including the headers, the test passes while masking a regression.

**Fix:**

```python
    assert result.returncode == 0, f"Script exited {result.returncode}: {result.stderr}"
    assert "## Directory Tree" in result.stdout
    # ...
```

---

### IN-03: Manual `CURSOR_TRACE_ID` backup/restore in test is redundant

**File:** `mise-en-place/tool-env-check/test_env_check.py:27`

**Issue:** `patch.dict("os.environ", {}, clear=False)` already captures and restores the full environment on context exit. The explicit `env_backup = os.environ.pop("CURSOR_TRACE_ID", None)` / restore block inside the same `with` statement is redundant and adds noise. When the `patch.dict` context exits, `CURSOR_TRACE_ID` is automatically restored to its original value.

**Fix:** Remove the manual backup/restore and instead delete the key from the patched env:

```python
    with patch("env_check.shutil.which", return_value="/usr/bin/git"), \
         patch("env_check.subprocess.run", return_value=mock_result), \
         patch.dict("os.environ", {}, clear=False):
        os.environ.pop("CURSOR_TRACE_ID", None)  # ensure cursor fast-path is inactive
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
```

---

_Reviewed: 2026-05-21T20:11:00-04:00_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
