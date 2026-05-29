---
type: community
cohesion: 0.13
members: 27
---

# Brownfield Detection Tests

**Cohesion:** 0.13 - loosely connected
**Members:** 27 nodes

## Members
- [[--root outside cwd → exit 1.]] - rationale - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[Brownfield without .planningcodebase → needs_codebase_map true.]] - rationale - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[Code at depth 4 must not be detected.]] - rationale - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[Code under node_modules must not count.]] - rationale - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[CompletedProcess]] - code - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[Empty dir → is_brownfield false.]] - rationale - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[Empty scaffold dir without STACK.md → needs map, has_codebase_map false.]] - rationale - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[Path_1]] - code - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[Repo with source files → is_brownfield true.]] - rationale - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[STACK.md present → has_codebase_map true, needs_codebase_map false.]] - rationale - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[Symlink to outside dir must not count toward has_existing_code.]] - rationale - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[Tests for detect_brownfield.py]] - rationale - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[_parse_json()]] - code - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[_run_detect()]] - code - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[package.json only → is_brownfield true.]] - rationale - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[str_2]] - code - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[test_brownfield_package_file_only()]] - code - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[test_detect_brownfield.py]] - code - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[test_detect_brownfield_with_py_files()]] - code - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[test_detect_greenfield_empty()]] - code - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[test_has_codebase_map_when_stack_md_present()]] - code - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[test_max_depth_limits_walk()]] - code - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[test_needs_codebase_map()]] - code - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[test_needs_codebase_map_empty_scaffold()]] - code - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[test_reject_root_outside_cwd()]] - code - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[test_skip_dirs_excludes_node_modules()]] - code - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
- [[test_symlink_outside_root_not_followed()]] - code - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Brownfield_Detection_Tests
SORT file.name ASC
```
