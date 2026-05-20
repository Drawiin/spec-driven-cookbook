# Spec Driven Cookbook

## What This Is

A meta-framework for spec-driven AI-assisted software development, built on a thin orchestrator + specialized worker sub-agents model. It is designed to self-replicate: the generic version is a complete, working coding framework, and a built-in replication engine generates project-specific tailored copies — stripping it down to only the agents, tools, and workflows each project actually needs. The culinary metaphor runs throughout: "mise en place" (everything prepared and in place before cooking) is the philosophy.

## Core Value

A developer can take any project — greenfield or existing — from a problem statement to working, verifiable code in a reliable, repeatable way, and can bootstrap that process for any new project in under 5 minutes.

## Requirements

### Validated

- ✓ Research on 7 existing spec-driven frameworks completed — `research/` dossier — existing
- ✓ Codebase map documented — `.planning/codebase/` — existing

### Active

- [ ] Generic coding framework: Spec → Plan → Execute phases with thin orchestrator + specialized workers
- [ ] Context discipline: each sub-agent receives only the context it needs (no context bloat)
- [ ] Self-healing layer: verifier catches wrong output and re-runs; watchdog detects stuck/hallucinating agents; spec-drift reconciliation checks built output vs. spec
- [ ] Deterministic tooling: CLI/Python scripts as escape hatches (git ops, file mutations), verification gates (lint, test, schema), and context builders (structured data fed into agent prompts)
- [ ] Replication engine: analysis of target project + structured Q&A + pre-made templates → generates tailored `.cursor/` folder (skills + agents + `cursor.md`)
- [ ] Coding template: the first and primary template — full coding capability (the generic framework itself)
- [ ] Works for greenfield projects (empty repo → working code without micromanaging)
- [ ] Works for brownfield projects (existing codebase → analyzied, mapped, extended)
- [ ] Generated project-specific variant is usable in < 5 minutes

### Out of Scope

- Multi-runtime support (Claude Code, Codex, Gemini) — deferred; v1 is Cursor only
- Pre-made templates beyond the coding template — deferred; one template first, then expand
- Distribution / open-source packaging — personal use tool for now; no npm publish or install story
- Non-coding agent templates (analysis-only agents, no-code tooling) — deferred to future templates

## Context

Built from extensive research on 7 existing frameworks (GSD, TLC spec-driven, Graphify, GitHub Spec Kit, OpenSpec, Task Master, BMAD-METHOD) — key patterns to incorporate:

- **Thin orchestrator**: orchestrator only routes/dispatches, never does heavy work itself (from GSD/TLC research)
- **Fresh sub-agent contexts**: each worker gets a minimal, purpose-built context (prevents context rot)
- **File-based state**: `.planning/` folder as the single source of truth, version-controlled
- **Wave-based parallelism**: independent tasks run in parallel waves; dependent tasks gate on prior wave
- **Supply-chain defense / package legitimacy**: verify before using external dependencies
- **Spec-first**: the spec is the contract; plan and execution derive from it, not the other way

The culinary metaphor guides naming and structure: `mise-en-place` = preparation phase, "recipes" = reusable workflow templates, "cookbook" = the library of patterns.

## Constraints

- **Runtime**: Cursor only — no multi-runtime adapter layer for v1
- **Language**: Tooling (CLI/scripts) written in Python or Node.js (user's stack)
- **No databases**: all state is file-based (`.planning/`, `.cursor/`) — must be version-control friendly
- **Self-contained**: generated project variants must work without network dependencies on the generic framework at runtime

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Cursor-only for v1 | Avoid premature adapter complexity; ship something usable fast | — Pending |
| Single coding template for v1 | Validate the replication engine before building more templates | — Pending |
| Heavy tooling lives inside the skill | Skills are portable; bundling scripts inside them keeps variants self-contained | — Pending |
| File-based state over databases | Version-control friendly, inspectable, no infrastructure required | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-20 after initialization*
