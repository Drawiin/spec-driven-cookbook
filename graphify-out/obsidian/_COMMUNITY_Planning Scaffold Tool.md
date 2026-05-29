---
type: community
cohesion: 0.11
members: 30
---

# Planning Scaffold Tool

**Cohesion:** 0.11 - loosely connected
**Members:** 30 nodes

## Members
- [[Idempotent mkdir exist_ok=True + conditional file writes.]] - rationale - mise-en-place/tool-planning-scaffold/planning_scaffold.py
- [[Minimal project root with no .planning yet.]] - rationale - mise-en-place/tool-planning-scaffold/test_planning_scaffold.py
- [[Normalize strip trailing whitespace per line + ensure single trailing newline.]] - rationale - mise-en-place/tool-planning-scaffold/planning_scaffold.py
- [[Path]] - code - mise-en-place/tool-planning-scaffold/planning_scaffold.py
- [[Resolve root and reject paths outside the working directory.]] - rationale - mise-en-place/tool-planning-scaffold/planning_scaffold.py
- [[Running scaffold() twice raises no error and leaves .planning intact.]] - rationale - mise-en-place/tool-planning-scaffold/test_planning_scaffold.py
- [[Tests for planning_scaffold.py]] - rationale - mise-en-place/tool-planning-scaffold/test_planning_scaffold.py
- [[_validate_root()]] - code - mise-en-place/tool-planning-scaffold/planning_scaffold.py
- [[format_file()]] - code - mise-en-place/tool-planning-scaffold/planning_scaffold.py
- [[format_file() strips trailing spaces and ensures a single trailing newline.]] - rationale - mise-en-place/tool-planning-scaffold/test_planning_scaffold.py
- [[main()]] - code - mise-en-place/tool-planning-scaffold/planning_scaffold.py
- [[planning_scaffold.py]] - code - mise-en-place/tool-planning-scaffold/planning_scaffold.py
- [[read_artifact()]] - code - mise-en-place/tool-planning-scaffold/planning_scaffold.py
- [[read_artifact() returns the default content written by scaffold().]] - rationale - mise-en-place/tool-planning-scaffold/test_planning_scaffold.py
- [[scaffold()]] - code - mise-en-place/tool-planning-scaffold/planning_scaffold.py
- [[scaffold() creates the expected .planning directory tree.]] - rationale - mise-en-place/tool-planning-scaffold/test_planning_scaffold.py
- [[scaffold() never clobbers files that already exist.]] - rationale - mise-en-place/tool-planning-scaffold/test_planning_scaffold.py
- [[str]] - code - mise-en-place/tool-planning-scaffold/planning_scaffold.py
- [[test_format_file_normalizes_trailing_whitespace()]] - code - mise-en-place/tool-planning-scaffold/test_planning_scaffold.py
- [[test_planning_scaffold.py]] - code - mise-en-place/tool-planning-scaffold/test_planning_scaffold.py
- [[test_read_artifact_returns_content()]] - code - mise-en-place/tool-planning-scaffold/test_planning_scaffold.py
- [[test_scaffold_creates_planning_dirs()]] - code - mise-en-place/tool-planning-scaffold/test_planning_scaffold.py
- [[test_scaffold_does_not_overwrite_existing_files()]] - code - mise-en-place/tool-planning-scaffold/test_planning_scaffold.py
- [[test_scaffold_is_idempotent()]] - code - mise-en-place/tool-planning-scaffold/test_planning_scaffold.py
- [[test_write_artifact_nested_path_allowed()]] - code - mise-en-place/tool-planning-scaffold/test_planning_scaffold.py
- [[test_write_artifact_path_traversal_blocked()]] - code - mise-en-place/tool-planning-scaffold/test_planning_scaffold.py
- [[tmp_project()]] - code - mise-en-place/tool-planning-scaffold/test_planning_scaffold.py
- [[write_artifact()]] - code - mise-en-place/tool-planning-scaffold/planning_scaffold.py
- [[write_artifact() accepts valid subpaths within .planning.]] - rationale - mise-en-place/tool-planning-scaffold/test_planning_scaffold.py
- [[write_artifact() rejects artifact paths that escape .planning root.]] - rationale - mise-en-place/tool-planning-scaffold/test_planning_scaffold.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Planning_Scaffold_Tool
SORT file.name ASC
```
