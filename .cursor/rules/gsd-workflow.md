# GSD Workflow — Spec Driven Cookbook

## Project

**Spec Driven Cookbook** — A meta-framework for spec-driven AI-assisted development.
- Thin orchestrator + specialized worker sub-agents
- Phases: Spec → Plan → Execute
- Self-healing per task, with plan-level spec reconciliation
- Replication engine generates project-specific variants

## Current State

- **Current Phase**: 1 — Tooling Foundation
- **State file**: `.planning/STATE.md`
- **Project context**: `.planning/PROJECT.md`
- **Requirements**: `.planning/REQUIREMENTS.md` (33 v1 requirements)
- **Roadmap**: `.planning/ROADMAP.md` (8 phases)

## GSD Commands

Use these commands to drive development:

```
/gsd-discuss-phase 1   — gather context, clarify approach before planning
/gsd-plan-phase 1      — create execution plans for Phase 1
/gsd-execute-phase 1   — execute plans for Phase 1
/gsd-progress          — show current state and what's next
```

## Workflow Enforcement

- **No skipping phases**: Spec must be approved before planning; plan must be approved before execution
- **Atomic commits**: Each plan task gets its own commit
- **No drive-by refactors**: Change only what the current plan task requires
- **Verification gates**: Lint, tests, and schema checks must pass before advancing
- **Clean context**: Each phase/worker reads only local files — no dependency on prior session state
