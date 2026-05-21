# mise-en-place

A set of CLI tools that prepare the environment before a spec-driven workflow phase begins. The culinary metaphor: everything in place before cooking starts.

## Tools

### tool-env-check

Validates that all runtime prerequisites are present (git, python3, bun/node, cursor) before a phase runs. An agent reads `tool-env-check/SKILL.md` to understand how to invoke it.

### tool-context-builder

Assembles a pasteable markdown context packet from the current project: directory tree, dependency list, git summary, and key file previews. Feeds structured context into agent prompts.

### tool-planning-scaffold

Scaffolds and manages the `.planning/` directory structure. Provides idempotent scaffolding plus `read-artifact`, `write-artifact`, and `format-file` subcommands for planning artifact management.

## Usage

Each tool has a `SKILL.md` that agents read, plus a Python script invoked via the Shell tool:

```shell
python3 mise-en-place/tool-<name>/<script>.py [args]
```

Exit code 0 = success. Exit code 1 = failure (details printed to stdout).

Example — check prerequisites before starting a phase:

```shell
python3 mise-en-place/tool-env-check/env_check.py
```

## Development

Tests use pytest. Install it once as a dev dependency (not bundled in the toolkit):

```shell
pip install pytest
```

Run all tool tests:

```shell
python3 -m pytest mise-en-place/ -x -q
```

pytest is a dev-only dependency and is **not** required at runtime. The tools themselves depend only on the Python standard library.
