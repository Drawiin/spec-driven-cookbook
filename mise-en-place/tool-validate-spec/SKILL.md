---
name: tool-validate-spec
description: "Check that SPEC.md exists, has status: approved, and contains all required sections before planning begins"
---

<cursor_skill_adapter>
## A. Skill Invocation
- This skill is invoked when the user mentions `tool-validate-spec` or describes a task matching this skill.
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
Verify that `.planning/SPEC.md` exists, has `status: approved`, and contains all five required section headers. Exits 0 on success, exits 1 with an actionable error message on any failure.
</objective>

<process>
Run from the project root:

```shell
python3 mise-en-place/tool-validate-spec/validate_spec.py
```

**Exit code contract:**

- **Exit 0** — SPEC.md found, `status: approved`, and all required section headers present.
- **Exit 1** — Any failure: SPEC.md missing, malformed front-matter, status not yet approved, or missing required section header.

**Required section headers** (exact match, case-sensitive — must match `validate_spec.py` `REQUIRED_SECTIONS`):

- `## Problem`
- `## Who It's For`
- `## Constraints`
- `## Success Criteria`
- `## Out of Scope`

**When to invoke:** Run this before `/plan-phase` begins. If exit code is non-zero, the developer must complete `/spec-phase` and reach the approval gate before planning can proceed.

**Example success output (stdout):**

```
✓ SPEC.md approved (version 1, 2026-05-22)
```

**Example failure cases (stderr):**

| Condition | Message |
|-----------|---------|
| No SPEC.md | `ERROR: SPEC.md not found in .planning/ or project root.` |
| Draft status | `ERROR: SPEC.md status is 'draft' — must be 'approved' before planning.` |
| Malformed front-matter | `ERROR: .planning/SPEC.md has no valid YAML front-matter.` |
| Missing section | `ERROR: SPEC.md missing required section: ## Constraints` |

No arguments required. Searches `.planning/SPEC.md` then `SPEC.md` relative to the current working directory. Stdlib-only — no pip install required.
</process>
