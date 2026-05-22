---
name: tool-detect-brownfield
description: "Detect brownfield vs greenfield projects and whether a codebase map is needed"
---

<cursor_skill_adapter>
## A. Skill Invocation
- This skill is invoked when the user mentions `tool-detect-brownfield` or describes a task matching this skill.
- Treat all user text after the skill mention as `{{GSD_ARGS}}`.
- If no arguments are present, treat `{{GSD_ARGS}}` as empty.

## B. User Prompting
When the workflow needs user input, prompt the user conversationally:
- Present options as a numbered list in your response text
- Ask the user to reply with their choice
- For multi-select, ask for comma-separated numbers

## C. Tool Usage
Use these Cursor tools when executing GSD workflows:
- `Shell` for running commands (terminal operations)
- `StrReplace` for editing existing files
- `Read`, `Write`, `Glob`, `Grep`, `Task`, `WebSearch`, `WebFetch`, `TodoWrite` as needed

## D. Subagent Spawning
When the workflow needs to spawn a subagent:
- Use `Task(subagent_type="generalPurpose", ...)`
- The `model` parameter maps to Cursor's model options (e.g., "fast")
</cursor_skill_adapter>

<objective>
Determine whether the project root has existing code (brownfield) and whether a codebase map must be created before spec Q&A.
</objective>

<process>
Run from the project root:

```shell
python3 mise-en-place/tool-detect-brownfield/detect_brownfield.py [--root PATH]
```

**Arguments:**
- `--root PATH` — project root to analyze (default: cwd). Must be cwd or a descendant of cwd (`relative_to` containment). Walk uses `follow_symlinks=False`.

**Stdout (JSON, exit 0 on successful detection):**

| Field | Meaning |
|-------|---------|
| `is_brownfield` | `true` when source files or package manifests exist |
| `has_existing_code` | Code files found within depth 3 (extensions from GSD init heuristic) |
| `has_package_file` | Root has package.json, requirements.txt, etc. |
| `has_codebase_map` | `.planning/codebase/STACK.md` exists as a file |
| `needs_codebase_map` | Brownfield and no STACK.md marker |
| `code_extensions_found` | Sorted list of extensions detected |

**Exit codes:**
- `0` — detection completed (brownfield or greenfield)
- `1` — invalid `--root` (stderr `ERROR:` prefix)

**Critical distinction:** `has_codebase_map` means only that `STACK.md` exists. A **complete map** requires all seven canonical files (`STACK.md`, `ARCHITECTURE.md`, `CONVENTIONS.md`, `STRUCTURE.md`, `TESTING.md`, `INTEGRATIONS.md`, `CONCERNS.md`), each with more than 20 lines. `map-codebase` and `spec-phase` Step 1.4 enforce completeness; this tool does not.
</process>
