# Requirements: Spec Driven Cookbook

**Defined:** 2026-05-20
**Core Value:** A developer can take any project — greenfield or existing — from a problem statement to working, verifiable code in a reliable, repeatable way, and can bootstrap that process for any new project in under 5 minutes.

## v1 Requirements

### Spec Phase

- [ ] **SPEC-01**: User can initiate a spec phase that opens a structured deep-questioning flow
- [ ] **SPEC-02**: The spec phase produces a persisted spec file capturing what to build, why, constraints, and success criteria
- [ ] **SPEC-03**: Spec phase supports research sub-tasks (gathering domain knowledge before locking requirements)
- [ ] **SPEC-04**: Spec file must be explicitly approved by the user before planning begins
- [ ] **SPEC-05**: Spec phase works on a clean context — can be invoked with no prior session history, using only local files

### Plan Phase

- [ ] **PLAN-01**: User can initiate a plan phase that reads the approved spec and produces one or more executable task plans
- [ ] **PLAN-02**: Each plan decomposes into atomic tasks — each task has a single, clear, verifiable deliverable
- [ ] **PLAN-03**: Plan phase supports generating multiple parallel plans for independent work streams
- [ ] **PLAN-04**: Plan must be explicitly approved by the user before execution begins
- [ ] **PLAN-05**: Plan phase works on a clean context — uses only the spec file and local project files

### Execute Phase

- [ ] **EXEC-01**: A thin orchestrator reads the approved plan and dispatches specialized worker sub-agents to execute tasks
- [ ] **EXEC-02**: Orchestrator never does implementation work itself — it only routes, sequences, and dispatches
- [ ] **EXEC-03**: Each worker sub-agent receives only the context it needs: its task, relevant local files, and no more
- [ ] **EXEC-04**: Workers can be invoked on a clean slate — state is passed via local files only
- [ ] **EXEC-05**: Independent tasks in a plan are dispatched in parallel; dependent tasks wait for their prerequisite workers

### Self-Healing

- [ ] **HEAL-01**: After each worker task completes, a verifier checks the output against the task's deliverable criteria
- [ ] **HEAL-02**: If a task verification fails, a corrective re-run is triggered with the failure context attached to the worker prompt
- [ ] **HEAL-03**: At the end of a plan, a plan-level reconciliation checks the cumulative output against the full spec
- [ ] **HEAL-04**: Stuck-agent detection: if a worker exceeds a configured timeout or produces no progress, the orchestrator aborts and surfaces the failure

### Deterministic Tooling

- [ ] **TOOL-01**: Framework provides CLI/script utilities for repeatable low-token operations: formatting files, reading/writing framework artifacts, scaffolding directories
- [ ] **TOOL-02**: Context-builder scripts gather structured project data (directory trees, dependency lists, git log summaries) and output clean markdown for agent prompts
- [ ] **TOOL-03**: Verification scripts run automatically at execution gates: lint, tests, and schema validation
- [ ] **TOOL-04**: Environment-check scripts validate runtime prerequisites before phases begin
- [ ] **TOOL-05**: All deterministic tools are bundled inside the skill folder so generated variants are self-contained

### Replication Engine

- [ ] **REPL-01**: A bootstrap command exists that analyzes a target project and produces a project profile (stack, patterns, what agents are needed)
- [ ] **REPL-02**: Bootstrap flow presents structured questions to the user to confirm/customize the generated profile
- [ ] **REPL-03**: Bootstrap supports selecting a pre-made template as the starting point
- [ ] **REPL-04**: Output of bootstrap is a self-contained `.cursor/` folder: skills, agent definitions, and a `cursor.md` project instruction file
- [ ] **REPL-05**: Generated variant has no runtime dependency on the generic framework — it works standalone
- [ ] **REPL-06**: The "coding" pre-made template is a complete copy of the full generic framework (all agents, all tools, all workflows) — first template, built as we build the framework itself

### Greenfield & Brownfield Support

- [ ] **PROJ-01**: Framework works on empty repos — the spec phase can be the first thing run
- [ ] **PROJ-02**: Framework works on existing codebases — a codebase mapping step runs before the spec phase if code exists
- [ ] **PROJ-03**: Codebase map is used to seed the spec with what already exists (validated capabilities) vs. what is new (active requirements)

## v2 Requirements

### Multi-Runtime Support

- **RTME-01**: Framework generates variants for Claude Code runtime
- **RTME-02**: Framework generates variants for Codex / VS Code Copilot runtime
- **RTME-03**: Runtime adapter layer normalizes behavioral differences across runtimes

### Additional Templates

- **TMPL-01**: Analysis-agent template — read/query/report capabilities, no code-writing agents
- **TMPL-02**: Data-pipeline template — ETL, transformation, validation agents
- **TMPL-03**: Infrastructure template — IaC, deployment, environment management agents

### Distribution

- **DIST-01**: Framework can be installed via a single command (npm/pip/curl)
- **DIST-02**: Framework updates can be applied to existing generated variants without overwriting customizations

## Out of Scope

| Feature | Reason |
|---------|--------|
| Multi-runtime support (Claude Code, Codex) | Adds adapter complexity; ship Cursor v1 first |
| Non-coding templates (analysis, data, infra) | Validate replication engine on coding first |
| Open-source publishing / distribution packaging | Personal use tool for now; no install story needed |
| UI or web dashboard | File-based state is sufficient; a UI adds maintenance overhead |
| Cloud sync / remote state | Local files + git is the persistence model |

## Traceability

*Populated during roadmap creation — 2026-05-20.*

| Requirement | Phase | Status |
|-------------|-------|--------|
| TOOL-01 | Phase 1 | Pending |
| TOOL-02 | Phase 1 | Pending |
| TOOL-04 | Phase 1 | Pending |
| TOOL-05 | Phase 1 | Pending |
| SPEC-01 | Phase 2 | Pending |
| SPEC-02 | Phase 2 | Pending |
| SPEC-03 | Phase 2 | Pending |
| SPEC-04 | Phase 2 | Pending |
| SPEC-05 | Phase 2 | Pending |
| PROJ-01 | Phase 2 | Pending |
| PROJ-02 | Phase 3 | Pending |
| PROJ-03 | Phase 3 | Pending |
| PLAN-01 | Phase 4 | Pending |
| PLAN-02 | Phase 4 | Pending |
| PLAN-03 | Phase 4 | Pending |
| PLAN-04 | Phase 4 | Pending |
| PLAN-05 | Phase 4 | Pending |
| EXEC-01 | Phase 5 | Pending |
| EXEC-02 | Phase 5 | Pending |
| EXEC-03 | Phase 5 | Pending |
| EXEC-04 | Phase 5 | Pending |
| EXEC-05 | Phase 5 | Pending |
| TOOL-03 | Phase 5 | Pending |
| HEAL-01 | Phase 6 | Pending |
| HEAL-02 | Phase 6 | Pending |
| HEAL-03 | Phase 6 | Pending |
| HEAL-04 | Phase 6 | Pending |
| REPL-01 | Phase 7 | Pending |
| REPL-02 | Phase 7 | Pending |
| REPL-03 | Phase 7 | Pending |
| REPL-04 | Phase 8 | Pending |
| REPL-05 | Phase 8 | Pending |
| REPL-06 | Phase 8 | Pending |

**Coverage:**
- v1 requirements: 33 total
- Mapped to phases: 33 ✓
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-20*
*Last updated: 2026-05-20 after initial definition*
