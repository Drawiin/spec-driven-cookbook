---
name: tool-context-builder
description: "Assemble a pasteable markdown context packet from the project's directory, dependencies, git history, and key file previews"
---

<cursor_skill_adapter>
## A. Skill Invocation
- This skill is invoked when the user mentions `tool-context-builder` or describes a task matching this skill.
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
Produce a clean four-section markdown context packet — directory tree, dependency file, git summary, and key file previews — formatted for direct paste into an agent prompt without manual editing.
</objective>

<process>
Run from the project root:

```shell
python3 mise-en-place/tool-context-builder/context_builder.py [--root PATH] [--depth N]
```

**Arguments:**
- `--root PATH` — project root directory to snapshot (default: current working directory)
- `--depth N` — directory tree depth (default: 3)

**Output:** Printed to stdout as markdown with four sections separated by `---`:

1. `## Directory Tree` — gitignore-aware tree up to `--depth` levels deep
2. `## Dependencies` — content of `pyproject.toml`, `package.json`, or `requirements.txt` (first found); `_(none detected)_` if none present
3. `## Git Summary` — current branch, last 10 commits, and uncommitted changes (if any)
4. `## Key Files` — first 20 lines of up to 5 detected entry-point files

Exit code 0 = success (always — the script degrades gracefully if git is unavailable or entry points are not found).

**Notes:**
- Gitignore support is MVP-scope — only the top-level `.gitignore` is read (nested gitignore files in subdirectories are not processed).
- The ALWAYS_EXCLUDE set hard-blocks `.planning`, `.git`, `__pycache__`, `.DS_Store`, and `node_modules` regardless of gitignore.
</process>
