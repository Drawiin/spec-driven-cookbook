# Roadmap: Spec Driven Cookbook

## Overview

Build a meta-framework that takes a developer — solo, with Claude as the builder — from any problem statement to working, verifiable code: a deterministic tooling layer first, then the Spec → Plan → Execute pipeline with structured approval gates, a self-healing layer that catches failures and spec drift, brownfield onboarding for existing codebases, and finally a replication engine that packages the whole system into a self-contained `.cursor/` folder tailored for any new project in under five minutes.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Tooling Foundation** - CLI utilities, context builders, and environment checks bundled inside the skill folder
- [ ] **Phase 2: Spec Phase — Greenfield** - Structured deep-questioning flow, research sub-tasks, persisted spec file, and explicit approval gate on a clean context
- [ ] **Phase 3: Brownfield Codebase Onboarding** - Codebase mapping step that seeds the spec with what already exists vs. what is new
- [ ] **Phase 4: Plan Phase** - Spec-to-plan decomposition: atomic tasks, parallel plan streams, and explicit approval before execution
- [ ] **Phase 5: Execute Phase — Thin Orchestrator** - Thin orchestrator dispatches specialized workers in parallel waves; each worker receives only the context it needs; verification gates run at each execution boundary
- [ ] **Phase 6: Self-Healing Layer** - Per-task verifier, corrective re-run on failure, plan-level spec reconciliation, and stuck-agent detection
- [ ] **Phase 7: Replication Engine — Project Analysis** - Bootstrap command analyzes a target project, produces a profile via structured Q&A, and selects a starting template
- [ ] **Phase 8: Replication Engine — Output & Coding Template** - Generates the self-contained `.cursor/` folder and ships the coding template as the first standalone variant

## Phase Details

### Phase 1: Tooling Foundation
**Goal**: Developer has a working CLI toolkit for low-token framework operations, context assembly, and environment validation — all bundled inside the skill folder so generated variants are self-contained from day one
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: TOOL-01, TOOL-02, TOOL-04, TOOL-05
**Success Criteria** (what must be TRUE):
  1. Running the environment-check command from any project reports pass/fail on all prerequisites (git, node/python, cursor) in under 5 seconds
  2. Running the context-builder outputs a clean markdown file (directory tree, dependency list, git summary) ready to paste into an agent prompt without any manual editing
  3. CLI utilities can scaffold the `.planning/` directory, read/write framework artifacts, and format files idempotently
  4. All tool scripts ship inside the skill folder — moving the skill to a new project includes all utilities without any additional setup
**Plans**: TBD

### Phase 2: Spec Phase — Greenfield
**Goal**: Developer can spec any new project from scratch by running one command, working through a structured deep-questioning flow, optionally triggering research sub-tasks, and landing an explicitly approved spec file — the entire flow running on a clean context with only local files
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: SPEC-01, SPEC-02, SPEC-03, SPEC-04, SPEC-05, PROJ-01
**Success Criteria** (what must be TRUE):
  1. Developer can run `/spec-phase` on an empty repo and receive a structured Q&A that probes what to build, why, constraints, and success criteria
  2. Completing the Q&A produces a persisted `SPEC.md` capturing all gathered context in a durable, version-controlled format
  3. Developer can trigger one or more research sub-tasks during spec that gather domain knowledge; the spec is not finalized until research is incorporated
  4. The spec flow enforces an explicit approval gate — no planning command succeeds unless the spec has been approved by the developer
  5. The entire spec phase can be invoked with no prior session history; it reads only local files and produces only local files
**Plans**: TBD

### Phase 3: Brownfield Codebase Onboarding
**Goal**: Developer can run the framework on a repo with existing code, trigger an automatic codebase mapping step, and receive a spec that clearly distinguishes already-built capabilities from new requirements
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: PROJ-02, PROJ-03
**Success Criteria** (what must be TRUE):
  1. Running the framework on a non-empty repo detects existing code and triggers codebase mapping before the spec Q&A opens
  2. The codebase map (stack, structure, conventions, existing capabilities) is loaded into the spec context so the Q&A does not re-ask what already exists
  3. The produced spec file explicitly separates "already built" (validated capabilities) from "to build" (active requirements), with no mixing between the two sections
**Plans**: TBD

### Phase 4: Plan Phase
**Goal**: Developer can transform any approved spec into one or more parallel-ready, atomic task plans — each task carrying a single verifiable deliverable — behind an explicit approval gate on a clean context
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: PLAN-01, PLAN-02, PLAN-03, PLAN-04, PLAN-05
**Success Criteria** (what must be TRUE):
  1. Developer can run `/plan-phase` against an approved spec and receive one or more structured task plans
  2. Every task in every plan has exactly one deliverable that can be independently verified — no multi-output tasks
  3. Developer can generate multiple independent plans from one spec for parallel work streams that do not block each other
  4. The plan phase enforces an explicit approval gate — no execution command succeeds unless all plans have been approved
  5. The plan phase can run on a clean context — it reads only the spec file and local project files, with no dependency on prior session state
**Plans**: TBD

### Phase 5: Execute Phase — Thin Orchestrator
**Goal**: Developer can run any approved plan and have a thin orchestrator dispatch specialized workers in parallel waves; each worker receives a minimal context packet; independent tasks run concurrently; verification gates block progress on failures; workers can be invoked cold from local files alone
**Mode:** mvp
**Depends on**: Phases 1, 4
**Requirements**: EXEC-01, EXEC-02, EXEC-03, EXEC-04, EXEC-05, TOOL-03
**Success Criteria** (what must be TRUE):
  1. Running `/exec-phase` dispatches workers per task; the orchestrator performs zero implementation work — it only routes, sequences, and dispatches
  2. Each worker receives a minimal context packet containing only its task description, the task's relevant local files, and nothing more
  3. Independent tasks in a plan are dispatched in parallel; tasks with declared dependencies block until their prerequisite workers complete
  4. A worker can be invoked cold — all required state is read from local files at startup; no live session history is needed
  5. Verification scripts (lint, tests, schema validation) run automatically at each execution gate and block the orchestrator from advancing if they fail
**Plans**: TBD

### Phase 6: Self-Healing Layer
**Goal**: Failed tasks are automatically re-run with the verifier's failure report attached; plan-level reconciliation catches spec drift before marking a plan complete; stuck or hallucinating agents are aborted and surfaced before they waste execution budget
**Mode:** mvp
**Depends on**: Phase 5
**Requirements**: HEAL-01, HEAL-02, HEAL-03, HEAL-04
**Success Criteria** (what must be TRUE):
  1. After every worker task completes, an automatic verifier checks its output against the task's declared deliverable criteria and reports pass or fail
  2. A failing task triggers an automatic corrective re-run with the verifier's failure report prepended to the new worker prompt — no developer intervention needed
  3. When all tasks in a plan complete, a reconciliation step compares the cumulative output against the full spec and flags any drift before the plan is marked done
  4. If a worker exceeds the configured timeout or produces no detectable progress, the orchestrator aborts the worker and surfaces the failure with enough diagnostic context for the developer to act
**Plans**: TBD

### Phase 7: Replication Engine — Project Analysis
**Goal**: Developer can run a bootstrap command on any target project, receive an automated project profile (stack, patterns, recommended agents), refine it through structured Q&A, and select a pre-made template as the starting point for their generated variant
**Mode:** mvp
**Depends on**: Phases 1, 5
**Requirements**: REPL-01, REPL-02, REPL-03
**Success Criteria** (what must be TRUE):
  1. Running `/bootstrap` on a target project produces a project profile listing the detected stack, existing patterns, and recommended agent types without requiring any manual input upfront
  2. The bootstrap flow presents structured, targeted questions to the developer to confirm or override the generated profile before output is written
  3. Developer can select a pre-made template as the base for their generated variant; the selection is reflected in the final output
**Plans**: TBD

### Phase 8: Replication Engine — Output & Coding Template
**Goal**: Developer receives a self-contained `.cursor/` folder — skills, agent definitions, and a `cursor.md` instruction file — that works standalone with no runtime dependency on the generic framework; the "coding" template ships as the first complete pre-made variant
**Mode:** mvp
**Depends on**: Phase 7
**Requirements**: REPL-04, REPL-05, REPL-06
**Success Criteria** (what must be TRUE):
  1. After bootstrap completes, the output is a `.cursor/` folder containing skills, agent definitions, and a `cursor.md` instruction file tailored to the project's stack and selected template
  2. The generated variant has zero runtime dependency on the generic framework — it can be dropped into any project and work immediately as a standalone tool
  3. The "coding" template is a complete, functional copy of the full generic framework (all agents, all tools, all workflows) that serves both as a usable standalone coding assistant and as the reference implementation for all future templates
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Tooling Foundation | 0/TBD | Not started | - |
| 2. Spec Phase — Greenfield | 0/TBD | Not started | - |
| 3. Brownfield Codebase Onboarding | 0/TBD | Not started | - |
| 4. Plan Phase | 0/TBD | Not started | - |
| 5. Execute Phase — Thin Orchestrator | 0/TBD | Not started | - |
| 6. Self-Healing Layer | 0/TBD | Not started | - |
| 7. Replication Engine — Project Analysis | 0/TBD | Not started | - |
| 8. Replication Engine — Output & Coding Template | 0/TBD | Not started | - |
