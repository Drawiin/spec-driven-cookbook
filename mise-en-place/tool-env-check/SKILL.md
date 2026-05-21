---
name: tool-env-check
description: "Validate runtime prerequisites before a phase begins"
---

<cursor_skill_adapter>
## A. Skill Invocation
- This skill is invoked when the user mentions `tool-env-check` or describes a task matching this skill.
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
Check that git, python3, bun/node, and cursor are available before running a phase.
</objective>

<process>
Run from the project root:

```shell
python3 mise-en-place/tool-env-check/env_check.py
```

Exit code 0 = all prerequisites pass. Exit code 1 = one or more missing.

The script prints a human-readable report to stdout with ✓/✗ per check and a final PASS/FAIL line. No arguments required.
</process>
