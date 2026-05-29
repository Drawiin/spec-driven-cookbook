# mise-en-place

A set of CLI tools that prepare the environment before a spec-driven workflow phase begins. The culinary metaphor: everything in place before cooking starts.

## Tools

### tool-env-check

Validates that all runtime prerequisites are present (git, python3, bun/node, cursor) before a phase runs. An agent reads `tool-env-check/SKILL.md` to understand how to invoke it.

### tool-context-builder

Assembles a pasteable markdown context packet from the current project: directory tree, dependency list, git summary, and key file previews. Feeds structured context into agent prompts.

### tool-planning-scaffold

Scaffolds and manages the `.planning/` directory structure. Provides idempotent scaffolding plus `read-artifact`, `write-artifact`, and `format-file` subcommands for planning artifact management.

### tool-validate-spec

Validates that `.planning/SPEC.md` exists, has `status: approved`, and contains all five required section headers before planning begins. When `project_type: brownfield`, also requires `## Already Built` and `## To Build`, rejects brownfield sections without matching frontmatter (inverse rule), and rejects identical bullets across those sections (dedup). Agent reads `tool-validate-spec/SKILL.md` for invocation contract.

```shell
python3 mise-en-place/tool-validate-spec/validate_spec.py
```

### tool-detect-brownfield

Detects brownfield vs greenfield via depth-limited file walk and package manifests. Prints JSON to stdout. `has_codebase_map` is true only when `.planning/codebase/STACK.md` exists — that does **not** imply a complete seven-file map (see `map-codebase` completeness gate).

```shell
python3 mise-en-place/tool-detect-brownfield/detect_brownfield.py [--root PATH]
```

### tool-scan-map-secrets

Fail-closed scan of `.planning/codebase/*.md` for secret patterns (API keys, tokens, PEM headers). Exit 1 with `file:line` references on match. Invoked from `map-codebase` step 6.

```shell
python3 mise-en-place/tool-scan-map-secrets/scan_map_secrets.py --dir .planning/codebase/
```

### map-codebase

Parallel mapper workflow writing seven structured documents under `.planning/codebase/`. Runs `scan_map_secrets` after writes (fail-closed). Invokable standalone or from `spec-phase` Step 1.4. Agent reads `map-codebase/SKILL.md`.

### spec-phase

Structured deep-questioning workflow from an empty or existing repo to an explicitly approved SPEC.md. Step 1.4 runs brownfield detection and completeness-aware mapping before Q&A when code exists. Brownfield specs add `## Already Built` and `## To Build` with `project_type: brownfield`. Agent reads `spec-phase/SKILL.md` — no Python script (workflow skill only).

Invoked via `/spec-phase` or by mentioning spec-phase in conversation.

## Usage

Each tool has a `SKILL.md` that agents read, plus a Python script invoked via the Shell tool:

```shell
python3 mise-en-place/tool-<name>/<script>.py [args]
```

Exit code 0 = success. Exit code 1 = failure (details printed to stderr for detect, validate, and scan_map_secrets).

Example — check prerequisites before starting a phase:

```shell
python3 mise-en-place/tool-env-check/env_check.py
python3 mise-en-place/tool-detect-brownfield/detect_brownfield.py
python3 mise-en-place/tool-scan-map-secrets/scan_map_secrets.py --dir .planning/codebase/
```

Contract tests for workflow skills:

```shell
python3 -m pytest mise-en-place/spec-phase/test_spec_phase_contract.py mise-en-place/map-codebase/test_map_codebase_contract.py -q
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
