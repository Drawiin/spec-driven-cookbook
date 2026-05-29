---
source_file: "mise-en-place/tool-planning-scaffold/planning_scaffold.py"
type: "code"
community: "Planning Scaffold Tool"
location: "L24"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Planning_Scaffold_Tool
---

# scaffold()

## Connections
- [[Idempotent mkdir exist_ok=True + conditional file writes.]] - `rationale_for` [EXTRACTED]
- [[Path]] - `references` [EXTRACTED]
- [[main()]] - `calls` [EXTRACTED]
- [[planning_scaffold.py]] - `contains` [EXTRACTED]
- [[test_read_artifact_returns_content()]] - `calls` [INFERRED]
- [[test_scaffold_creates_planning_dirs()]] - `calls` [INFERRED]
- [[test_scaffold_does_not_overwrite_existing_files()]] - `calls` [INFERRED]
- [[test_scaffold_is_idempotent()]] - `calls` [INFERRED]
- [[test_write_artifact_nested_path_allowed()]] - `calls` [INFERRED]
- [[test_write_artifact_path_traversal_blocked()]] - `calls` [INFERRED]

#graphify/code #graphify/INFERRED #community/Planning_Scaffold_Tool