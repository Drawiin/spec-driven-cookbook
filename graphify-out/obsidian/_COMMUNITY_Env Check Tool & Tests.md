---
type: community
cohesion: 0.14
members: 15
---

# Env Check Tool & Tests

**Cohesion:** 0.14 - loosely connected
**Members:** 15 nodes

## Members
- [[Returns (status_char, detail_str) where status_char is '✓' or '✗'.]] - rationale - mise-en-place/tool-env-check/env_check.py
- [[Tests for env_check.py]] - rationale - mise-en-place/tool-env-check/test_env_check.py
- [[env_check.py]] - code - mise-en-place/tool-env-check/env_check.py
- [[env_check.py completes in under 5 seconds (SC-1 timing requirement).]] - rationale - mise-en-place/tool-env-check/test_env_check.py
- [[main()_3]] - code - mise-en-place/tool-env-check/env_check.py
- [[main() exits 0 when all subprocess checks return successfully.]] - rationale - mise-en-place/tool-env-check/test_env_check.py
- [[main() exits 1 when git is not found in PATH.]] - rationale - mise-en-place/tool-env-check/test_env_check.py
- [[run_check returns ✓ for cursor when CURSOR_TRACE_ID is set, without subprocess.]] - rationale - mise-en-place/tool-env-check/test_env_check.py
- [[run_check()]] - code - mise-en-place/tool-env-check/env_check.py
- [[str_4]] - code - mise-en-place/tool-env-check/env_check.py
- [[test_completes_in_under_five_seconds()]] - code - mise-en-place/tool-env-check/test_env_check.py
- [[test_cursor_detected_via_env_var()]] - code - mise-en-place/tool-env-check/test_env_check.py
- [[test_env_check.py]] - code - mise-en-place/tool-env-check/test_env_check.py
- [[test_exits_one_when_git_missing()]] - code - mise-en-place/tool-env-check/test_env_check.py
- [[test_exits_zero_when_all_checks_pass()]] - code - mise-en-place/tool-env-check/test_env_check.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Env_Check_Tool__Tests
SORT file.name ASC
```
