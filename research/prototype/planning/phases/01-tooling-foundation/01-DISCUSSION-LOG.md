# Phase 1: Tooling Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-21
**Phase:** 1-Tooling Foundation
**Areas discussed:** Implementation Language, Skill Bundling Structure, Context-Builder Output Design, Invocation Interface

---

## Implementation Language

| Option | Description | Selected |
|--------|-------------|----------|
| Python | Widely available on macOS without extra setup; readable syntax; good stdlib for file ops and git | ✓ |
| Node.js | Already required by GSD (.cjs runtime present); consistent with the existing framework tooling | |
| Both | Python for data-heavy ops, Node.js for framework integration scripts | |
| You decide | Pick the best fit | |

**User's choice:** Python

**Follow-up — Python version / stdlib constraint:**

| Option | Description | Selected |
|--------|-------------|----------|
| stdlib only | No pip installs; tools work out of the box on any Python 3.x install | ✓ |
| stdlib + common packages | Allow things like `rich` or `click` if they add real value | |
| You decide | Use whatever makes sense | |

**User's choice:** stdlib only
**Notes:** Full portability — zero install friction across any Python 3.x environment.

---

## Skill Bundling Structure

| Option | Description | Selected |
|--------|-------------|----------|
| mise-en-place/bin/ | Tools are first content in the cookbook's mise-en-place directory | |
| Dedicated skill (sdc-tools/) | Self-contained skill module with SKILL.md and a bin/ subdirectory | |
| Inline scripts in existing skill | Embed tools directly inside a workflow skill's folder | |

**User's choice (freeform):** "Each skill should have the necessary tools. In case we have a tool that can be used in more than one skill, we could have a simple wrapper skill around it."

**Follow-up — Shared skill naming:**

**User's choice (freeform):** "Depend on the tool — ideally with a skill name that matches the tool, but they could have a prefix that makes it easy to identify they are a skill wrapper around a tool."

**Follow-up — Prefix selection:**

| Option | Description | Selected |
|--------|-------------|----------|
| sdc-tool- | Project-scoped and explicit | |
| tool- | Shorter, readable | ✓ |
| You decide | | |

**Notes:** Pattern: tools co-located with the skill that uses them; shared tools get `tool-<name>` prefixed skills (e.g. `tool-env-check`, `tool-context-builder`).

---

## Context-Builder Output Design

| Option | Description | Selected |
|--------|-------------|----------|
| 2 levels deep | Enough to see structure without noise | |
| 3 levels deep | Shows more of the shape; still manageable | ✓ |
| Configurable | Default 2, user can pass --depth N | |

**User's choice:** 3 levels deep

**Follow-up — Exclusion rules:**

| Option | Description | Selected |
|--------|-------------|----------|
| Standard ignores | .git/, node_modules/, __pycache__/, .env*, build/, dist/ | |
| Standard + .planning/ | Hide framework internals from the pasted context | ✓ |
| Gitignore-aware | Respect the project's .gitignore file | ✓ |

**User's choice:** B + C (gitignore-aware AND excludes .planning/)

**Follow-up — Output sections:**

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal | Directory tree + dependency list + git summary | |
| Minimal + key file previews | Above + first 20 lines of entry points | ✓ |
| You decide | Include what makes the most useful agent prompt | |

**Notes:** Entry-point detection heuristic left to Claude's discretion.

---

## Invocation Interface

| Option | Description | Selected |
|--------|-------------|----------|
| Shell directly | `python tool.py` from terminal | |
| Cursor skill commands | Each tool exposed as a /command in Cursor | ✓ |
| Both layers | Python scripts runnable standalone AND exposed as skill commands | |

**User's choice:** Cursor skill commands

**Follow-up — Skill invocation mechanism:**

| Option | Description | Selected |
|--------|-------------|----------|
| Shell tool call | SKILL.md instructs agent to run .py file via Shell tool | |
| Agent reads + executes | Skill loads script content; agent follows instructions | |

**User's choice (freeform):** "Not sure — probably A + B. The skill itself knows how to perform the action; the agent invokes the skill to perform the actions relevant to it."

**Notes:** SKILL.md is the contract: it tells the agent what to do (including Shell-calling the Python script). Agents that need the capability read the `tool-*` SKILL.md and execute those steps.

---

## Claude's Discretion

- Entry-point detection heuristic for key file previews (README.md, main.py, index.js, pyproject.toml, etc.)
- Exact git summary format (last N commits, branch, status)

## Deferred Ideas

None — discussion stayed within phase scope.
