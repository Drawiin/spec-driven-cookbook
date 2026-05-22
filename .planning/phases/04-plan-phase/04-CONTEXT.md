# Phase 4: Plan Phase - Context

**Gathered:** 2026-05-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Build `/plan-phase` — a workflow that reads an approved `.planning/SPEC.md`, runs mandatory research and a plan-checker revision loop, and produces one or more parallel-ready PLAN.md files with atomic todo-style tasks, Mermaid dependency graphs, and an explicit approval gate that blocks execution until all plans are approved.

</domain>

<decisions>
## Implementation Decisions

### Plan Decomposition
- **D-01:** Single plan by default — one `{phase}-01-PLAN.md` unless the developer explicitly requests multiple streams.
- **D-02:** Split trigger is conversational — developer says "split into X and Y" or "two parallel plans" during plan-phase (no required CLI flag in MVP).
- **D-03:** Parallel plans must have no cross-plan `depends_on` — shared or blocking work belongs in a prior-wave plan, not split across parallel streams.
- **D-04:** Before writing any PLAN.md on a split, agent previews proposed plan names, scope per stream, and wave assignment; developer confirms first.

### Atomic Task Contract
- **D-05:** Structured-soft enforcement — SKILL.md requires verification criteria per task; `tool-validate-plan` checks presence only, not atomicity count or sizing.
- **D-06:** Task format is markdown todos: `[STATUS] TASKID - Title` (not GSD `<task>` XML blocks).
- **D-07:** TASKID scheme: `{plan}-{task}` — e.g. `04-01-T1`, `04-01-T2` within plan `04-01`.
- **D-08:** STATUS uses text tags: `[PENDING]`, `[IN_PROGRESS]`, `[DONE]` (not checkbox-only `[ ]` / `[x]`).
- **D-09:** Verification criteria are nested checkbox sub-bullets under each task: `  - [ ] Verify: <single observable outcome>`.
- **D-10:** Task sizing: one file or one script per task — e.g. "create validate_plan.py" is one task; script + tests are two.
- **D-11:** `tool-validate-plan` checks: plan has ≥1 todo line matching `[STATUS] TASKID` pattern and each task has a `Verify:` sub-bullet.
- **D-12:** Task dependencies expressed two ways: (a) `Depends: {TASKID}` sub-bullet under the task; (b) Mermaid dependency graph at plan top.
- **D-13:** Mermaid graph placement: immediately after `## Objective`, before the task list.
- **D-14:** All tasks written as `[PENDING]` at plan creation; execute-phase updates status.
- **D-15:** Minimal YAML frontmatter per PLAN.md: `status`, `phase`, `plan`, `requirements[]` only — lighter than full GSD frontmatter from Phases 1–3.

### Approval Gate
- **D-16:** Hybrid gate — all plans written as `status: draft`; agent presents summary; single "approve all" confirmation flips every plan to `status: approved`.
- **D-17:** In-flow approval mirrors spec-phase (Phase 2 D-08): present plan content (or summary + paths), ask "Approve? (yes / edit / abort)".
- **D-18:** `status: draft | approved` lives in each PLAN.md YAML frontmatter; approve-all runs StrReplace `status: draft` → `status: approved` on every plan file.
- **D-19:** Belt-and-suspenders: `tool-validate-plan` exits non-zero if ANY plan in the phase directory is not approved or fails todo-format checks; exec-phase (Phase 5) must call it before dispatch.
- **D-20:** Entry gate (deferred from Phase 2): plan-phase startup MUST call `python3 mise-en-place/tool-validate-spec/validate_spec.py` and block if spec is not approved.

### Plan-Phase Orchestration Depth
- **D-21:** Full loop — mandatory research → generate plan(s) → plan-checker sub-agent review → revise up to 3 cycles → present to developer for approval gate.
- **D-22:** Plan-checker runs as a Task sub-agent (`generalPurpose`, fresh context); writes review to `{phase}-REVIEWS.md`.
- **D-23:** Mandatory research before first plan draft — spawn researcher sub-agents (GSD 4-researcher pattern); research output feeds planner.
- **D-24:** Max 3 plan-checker revision cycles; escalate unresolved issues to developer (same cap as GSD plan-checker).

### Claude's Discretion
- Exact wording of split-preview and approval prompts.
- Research topic selection when spawning mandatory researchers.
- Plan-checker review dimensions (within the 3-cycle cap).
- Heuristic for when agent should proactively suggest a split vs. stay single-plan.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Requirements
- `.planning/REQUIREMENTS.md` — PLAN-01 through PLAN-05 define the full requirement set for this phase
- `.planning/ROADMAP.md` — Phase 4 success criteria (the five numbered items are the acceptance gates)

### Project Decisions
- `.planning/PROJECT.md` — Key Decisions table (Cursor-only, file-based state, tools inside skill folder, wave-based parallelism)

### Prior Phase Context (Reuse)
- `.planning/phases/01-tooling-foundation/01-CONTEXT.md` — D-01 through D-09: tool naming, skill bundling, Python stdlib-only, exit-code contract
- `.planning/phases/02-spec-phase-greenfield/02-CONTEXT.md` — D-08/D-09: approval gate pattern, validate_spec.py belt-and-suspenders; plan-phase wiring deferred here

### Existing Tools (Available for Reuse)
- `mise-en-place/tool-validate-spec/validate_spec.py` — entry gate; must pass before plan-phase proceeds
- `mise-en-place/tool-validate-spec/SKILL.md` — invocation contract for validate_spec.py
- `mise-en-place/tool-planning-scaffold/planning_scaffold.py` — read/write `.planning/` artifacts
- `mise-en-place/spec-phase/SKILL.md` — reference for approval gate UX (yes/edit/abort) and research sub-agent pattern

### Plan Format Reference (Prior Phases — adapt, do not copy verbatim)
- `.planning/phases/02-spec-phase-greenfield/02-02-PLAN.md` — prior GSD-style plan with frontmatter + must_haves (Phase 4 uses lighter todo format per D-06/D-15)
- `.planning/phases/03-brownfield-codebase-onboarding/03-01-PLAN.md` — wave/depends_on patterns for multi-plan phases

### Research Inputs
- `research/frameworks/gsd.md` — GSD plan-phase: researchers → planner → plan-checker 3× loop
- `research/topics/self-healing-and-verification.md` — plan-checker loop and convergence patterns
- `research/topics/workflow-and-orchestration.md` — artifact flow: CONTEXT → RESEARCH → PLAN

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `mise-en-place/tool-validate-spec/validate_spec.py` — template for `tool-validate-plan`: stdlib-only, exit-code contract, section/pattern validation
- `mise-en-place/tool-planning-scaffold/planning_scaffold.py` — `write-artifact` / `read-artifact` for PLAN.md I/O under `.planning/phases/`
- `mise-en-place/spec-phase/SKILL.md` — research sub-agent spawn pattern (Task tool, writes to `.planning/research/`)

### Established Patterns
- **Skill + tool pairing:** workflow skill (`plan-phase/SKILL.md`) + validation tool (`tool-validate-plan/validate_plan.py`) — same as spec-phase + validate-spec
- **Approval gate:** in-flow yes/edit/abort + Python script enforcement — replicate from Phase 2
- **Phase artifact home:** `.planning/phases/{slug}/` for `{NN}-{MM}-PLAN.md`, `{phase}-RESEARCH.md`, `{phase}-REVIEWS.md`
- **Python stdlib-only:** zero pip dependencies for all new tools

### Integration Points
- `mise-en-place/plan-phase/` — new workflow skill (no Python script; orchestration only)
- `mise-en-place/tool-validate-plan/` — new validation tool skill + `validate_plan.py`
- `mise-en-place/README.md` — document new tools (TOOL-05 self-contained discoverability)
- Phase 5 exec-phase will consume approved PLAN.md files and call `validate_plan.py` before dispatch

</code_context>

<specifics>
## Specific Ideas

- Task list format inspired by todo trackers: `[PENDING] 04-01-T1 - Add validate_plan.py` with nested verify checkboxes — lighter and more scannable than GSD XML task blocks.
- Mermaid graph at top gives at-a-glance dependency view before reading individual task Depends: lines.
- Full GSD-style depth (mandatory research + 3× plan-checker) chosen deliberately — Phase 4 is the quality gate before execution, not a thin MVP stub.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 4-Plan Phase*
*Context gathered: 2026-05-22*
