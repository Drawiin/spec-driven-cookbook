---
name: map-codebase
description: "Analyze an existing codebase into seven structured documents under .planning/codebase/"
---

<cursor_skill_adapter>
## A. Skill Invocation
- This skill is invoked when the user mentions `map-codebase` or describes mapping an existing codebase.
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
- Do NOT pass the `model` parameter — use the Cursor default model
</cursor_skill_adapter>

<objective>
Parallel mapper sub-agents write seven structured codebase documents to `.planning/codebase/`. The orchestrator receives confirmations only, not full document bodies. A fail-closed secret scan and completeness gate run before downstream spec Q&A.
</objective>

<process>

## Step 1: Scaffold

```shell
python3 mise-en-place/tool-planning-scaffold/planning_scaffold.py scaffold
```

## Step 2: check_existing

If `.planning/codebase/` contains any files, present:

> (1) Refresh — delete and remap  
> (2) Update specific docs  
> (3) Skip — use existing map  

On **Skip**: when git is available, compare `codebase_map_commit` in existing SPEC frontmatter (if any) to `git rev-parse HEAD`. If they differ, warn the map may be stale before proceeding.

## Step 3: Optional context snapshot

```shell
python3 mise-en-place/tool-context-builder/context_builder.py
```

Append stdout to mapper prompts as raw structural context. Never include secret **values** from denied paths; redact to `(redacted — existence only)` if `.env` or credential paths appear.

## Step 4: Parallel mappers

Spawn four `Task(subagent_type="generalPurpose")` mappers in parallel:

| Focus | Output files |
|-------|----------------|
| tech | `STACK.md`, `INTEGRATIONS.md` |
| arch | `ARCHITECTURE.md`, `STRUCTURE.md` |
| quality | `CONVENTIONS.md`, `TESTING.md` |
| concerns | `CONCERNS.md` |

Each prompt must include: focus area, absolute output paths under `.planning/codebase/`, and embedded section outlines below. Sub-agents use the Write tool; orchestrator only confirms completion.

**STACK.md:** ## Languages, ## Runtime, ## Frameworks, ## Key Dependencies, ## Configuration

**ARCHITECTURE.md:** ## Overview, ## Layers, ## Data Flow, ## Key Patterns

**STRUCTURE.md:** ## Directory Layout, ## Entry Points, ## Key Modules

**CONVENTIONS.md:** ## Naming, ## Code Style, ## Error Handling, ## Testing Conventions

**TESTING.md:** ## Test Framework, ## Test Layout, ## Running Tests, ## Coverage

**INTEGRATIONS.md:** ## External Services, ## APIs, ## Data Stores

**CONCERNS.md:** ## Known Issues, ## Tech Debt, ## Security Notes

## Step 5: Security rules

**Deny read** (note existence only, never echo values): `.env`, `.env.*`, `credentials.json`, `*.pem`, `secrets.*`, `**/secrets/**`, `id_rsa`, `id_ed25519`

## Step 6: Secret gate (fail-closed)

```shell
python3 mise-en-place/tool-scan-map-secrets/scan_map_secrets.py --dir .planning/codebase/
```

If exit 1: STOP — show stderr, require user to redact flagged content. Do not commit or continue to spec-phase Q&A. Manual grep alone is insufficient; exit code is the gate.

## Step 7: Completeness gate

Verify **all seven** files exist: `STACK.md`, `ARCHITECTURE.md`, `CONVENTIONS.md`, `STRUCTURE.md`, `TESTING.md`, `INTEGRATIONS.md`, `CONCERNS.md`.

Each file must have **more than 20 lines**. If any file is missing or under 20 lines: FAIL with retry prompt — do not proceed with a partial or stub map. Stub `STACK.md` alone does not satisfy completeness even when `detect_brownfield` reports `has_codebase_map: true`.

## Optional --fast mode

For repos with fewer than five source files, a single agent may write all seven files. Default remains four parallel mappers.

</process>
