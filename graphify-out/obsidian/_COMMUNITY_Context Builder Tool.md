---
type: community
cohesion: 0.13
members: 26
---

# Context Builder Tool

**Cohesion:** 0.13 - loosely connected
**Members:** 26 nodes

## Members
- [[Directories matching gitignore patterns (but not ALWAYS_EXCLUDE) are excluded.]] - rationale - mise-en-place/tool-context-builder/test_context_builder.py
- [[Minimal project root with no .gitignore or .planning.]] - rationale - mise-en-place/tool-context-builder/test_context_builder.py
- [[Output has exactly four sections separated by '---' in the correct order (D-07,]] - rationale - mise-en-place/tool-context-builder/test_context_builder.py
- [[Path_3]] - code - mise-en-place/tool-context-builder/context_builder.py
- [[Running the script produces all four required section headers in stdout.]] - rationale - mise-en-place/tool-context-builder/test_context_builder.py
- [[Tests for context_builder.py]] - rationale - mise-en-place/tool-context-builder/test_context_builder.py
- [[The .planning directory is never present in build_tree output (D-06).]] - rationale - mise-en-place/tool-context-builder/test_context_builder.py
- [[bool_1]] - code - mise-en-place/tool-context-builder/context_builder.py
- [[build_tree()]] - code - mise-en-place/tool-context-builder/context_builder.py
- [[context_builder.py]] - code - mise-en-place/tool-context-builder/context_builder.py
- [[find_entry_points()]] - code - mise-en-place/tool-context-builder/context_builder.py
- [[git_summary()]] - code - mise-en-place/tool-context-builder/context_builder.py
- [[int]] - code - mise-en-place/tool-context-builder/context_builder.py
- [[is_excluded()]] - code - mise-en-place/tool-context-builder/context_builder.py
- [[load_gitignore_patterns returns an empty list when no .gitignore exists (no exce]] - rationale - mise-en-place/tool-context-builder/test_context_builder.py
- [[load_gitignore_patterns()]] - code - mise-en-place/tool-context-builder/context_builder.py
- [[main()_4]] - code - mise-en-place/tool-context-builder/context_builder.py
- [[preview_file()]] - code - mise-en-place/tool-context-builder/context_builder.py
- [[str_5]] - code - mise-en-place/tool-context-builder/context_builder.py
- [[test_context_builder.py]] - code - mise-en-place/tool-context-builder/test_context_builder.py
- [[test_gitignore_patterns_applied()]] - code - mise-en-place/tool-context-builder/test_context_builder.py
- [[test_missing_gitignore_graceful()]] - code - mise-en-place/tool-context-builder/test_context_builder.py
- [[test_output_contains_all_four_sections()]] - code - mise-en-place/tool-context-builder/test_context_builder.py
- [[test_output_section_order_and_separators()]] - code - mise-en-place/tool-context-builder/test_context_builder.py
- [[test_planning_dir_excluded_from_tree()]] - code - mise-en-place/tool-context-builder/test_context_builder.py
- [[tmp_project()_1]] - code - mise-en-place/tool-context-builder/test_context_builder.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Context_Builder_Tool
SORT file.name ASC
```
