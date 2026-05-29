---
name: tool-planning-scaffold
description: "Scaffold the .planning/ directory structure and read/write framework artifacts idempotently"
---

<cursor_skill_adapter>
## A. Skill Invocation
- This skill is invoked when the user mentions `tool-planning-scaffold` or describes a task matching this skill.
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
Scaffold the `.planning/` directory tree for a new project and provide CRUD subcommands for reading, writing, and normalizing planning artifacts — all idempotent and safe to run on an existing repo.
</objective>

<process>
Run from the project root:

```shell
python3 mise-en-place/tool-planning-scaffold/planning_scaffold.py <subcommand> [args]
```

Exit code 0 = success. Exit code 1 = error (details printed to stdout).

**Subcommands:**

### scaffold [--root PATH]

Create the `.planning/` directory tree under `PATH` (default: current working directory). Creates `.planning/`, `.planning/phases/`, and `.planning/codebase/`, and writes minimal default files (`STATE.md`, `REQUIREMENTS.md`, `ROADMAP.md`) only if they do not already exist.

**Safe to run repeatedly** — never overwrites existing files. Running scaffold on a repo that already has `.planning/` is a no-op for existing files.

```shell
python3 mise-en-place/tool-planning-scaffold/planning_scaffold.py scaffold
python3 mise-en-place/tool-planning-scaffold/planning_scaffold.py scaffold --root /path/to/project
```

### read-artifact \<artifact\> [--root PATH]

Print the contents of `.planning/<artifact>` to stdout. Exits 1 if the artifact does not exist.

```shell
python3 mise-en-place/tool-planning-scaffold/planning_scaffold.py read-artifact STATE.md
python3 mise-en-place/tool-planning-scaffold/planning_scaffold.py read-artifact phases/01-foo/PLAN.md --root /path/to/project
```

### write-artifact \<artifact\> \<content\> [--root PATH]

Write `<content>` to `.planning/<artifact>`. Overwrites if the file already exists (intentional — use `read-artifact` first if you need to inspect). Parent directories are created automatically.

**Path safety:** artifact paths that attempt to escape `.planning/` (e.g. `../secret.md`) are rejected with exit code 1.

**Multiline content:** the `<content>` positional argument is a shell string — multiline content may break shell quoting. Two options:

1. Pass `-` as content to read from stdin:
   ```shell
   echo "$CONTENT" | python3 mise-en-place/tool-planning-scaffold/planning_scaffold.py write-artifact STATE.md -
   ```
2. Write to a temp file and use `read-artifact` to inspect the result.

```shell
python3 mise-en-place/tool-planning-scaffold/planning_scaffold.py write-artifact STATE.md "# Project State\n\n"
```

### format-file \<file\>

Normalize a file in place: strip trailing whitespace from every line and ensure exactly one trailing newline. Idempotent — running it twice on the same file produces no change.

Note: `format-file` accepts any file path — it is not restricted to `.planning/`. The developer is responsible for providing a valid path.

```shell
python3 mise-en-place/tool-planning-scaffold/planning_scaffold.py format-file .planning/STATE.md
python3 mise-en-place/tool-planning-scaffold/planning_scaffold.py format-file README.md
```

</process>
