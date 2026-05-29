# Phase 2: Spec Phase — Greenfield - Context

**Gathered:** 2026-05-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Build a single command (`/spec-phase`) that takes a developer from an empty repo to an explicitly approved `SPEC.md` — covering a hybrid structured Q&A flow, optional research sub-tasks spawned as separate Cursor agents, and an in-flow approval gate that flips the spec's YAML status before planning is allowed to proceed.

</domain>

<decisions>
## Implementation Decisions

### Q&A Structure
- **D-01:** Hybrid flow — fixed category spine always covered in order: Problem → Who it's for → Constraints → Success Criteria → Out-of-scope. Agent probes within each category (up to 3 follow-up turns) when answers are vague or underspecified.
- **D-02:** Category advances after 3 turns OR when the agent determines the answer is specific enough. The agent decides — not the user.

### Research Sub-tasks
- **D-03:** Both trigger modes supported: (a) agent-suggested — at end of Q&A, if the agent detects knowledge gaps it proposes one or more research sub-tasks; user accepts/skips. (b) user-requested — user can say "research X" at any point during Q&A to spawn a sub-task immediately.
- **D-04:** Research form: spawned Cursor sub-agent (Task tool) with a fresh context. Sub-agent writes a `RESEARCH.md` file in `.planning/phases/02-spec-phase-greenfield/`. Main spec flow reads that file before finalizing SPEC.md — main context never makes external calls directly (preserves clean-context constraint).
- **D-05:** Multiple research sub-tasks may run; each produces its own `RESEARCH-<topic>.md`. All are read before the spec is finalized.

### SPEC.md Format
- **D-06:** Minimal section set — five mandatory sections only: Problem, Who it's for, Constraints, Success Criteria, Out-of-scope. Enough for planning, nothing extra.
- **D-07:** YAML front-matter header with `status: draft | approved`, `version`, `date`. The approval gate reads and writes this field. Example:
  ```yaml
  ---
  status: draft
  version: 1
  date: 2026-05-21
  ---
  ```

### Approval Gate
- **D-08:** In-flow approval — at the end of the spec Q&A (after any research is incorporated), the agent presents the full SPEC.md content and asks "Approve? (yes / edit / abort)". On "yes," the agent writes `status: approved` into the YAML front-matter. On "edit," returns to the relevant section. On "abort," saves as draft and exits.
- **D-09:** Belt-and-suspenders enforcement: (a) plan-phase SKILL.md instructs the agent to verify spec `status == approved` before proceeding; (b) Python validation script (e.g., `tool-validate-spec`) reads SPEC.md, checks status, and exits non-zero with a clear error if not approved. Planning cannot proceed past the script check.

### Claude's Discretion
- Exact wording of Q&A prompts within each category — agent should follow natural conversation patterns.
- Detection heuristic for "vague answer" (when to follow up vs. advance) — agent judgment.
- Format of the research sub-task prompt passed to the spawned sub-agent.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Requirements
- `.planning/REQUIREMENTS.md` — SPEC-01 through SPEC-05, PROJ-01 define the full requirement set for this phase
- `.planning/ROADMAP.md` — Phase 2 success criteria (the five numbered items are the acceptance gates)

### Project Decisions
- `.planning/PROJECT.md` — Key Decisions table (Cursor-only, file-based state, tools inside skill folder, Python stdlib-only)

### Phase 1 Foundation (Reuse)
- `.planning/phases/01-tooling-foundation/01-CONTEXT.md` — D-01 through D-09: tool naming conventions, skill bundling pattern, invocation interface contract

### Existing Tools (Available for Reuse)
- `mise-en-place/tool-env-check/SKILL.md` — env check tool pattern to follow
- `mise-en-place/tool-planning-scaffold/SKILL.md` — planning scaffold tool; this phase's output goes into `.planning/`
- `mise-en-place/tool-planning-scaffold/planning_scaffold.py` — may have utilities for reading/writing `.planning/` files

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `mise-en-place/tool-planning-scaffold/planning_scaffold.py` — reads/writes `.planning/` artifacts; check for reusable file I/O helpers before writing new ones
- `mise-en-place/tool-env-check/env_check.py` — reference for Python stdlib-only, exit-code-based validation pattern (applicable to `tool-validate-spec`)
- `mise-en-place/tool-context-builder/context_builder.py` — reference for reading local project files and outputting structured markdown

### Established Patterns
- **Skill = SKILL.md + implementation file(s):** Every tool is a `tool-<name>/SKILL.md` entry point + `<name>.py` implementation. Phase 2 spec tool follows this exactly.
- **Python stdlib-only:** Zero pip dependencies — Phase 2 validation script and any helpers must follow this constraint.
- **Exit-code contract:** Tools exit 0 on success, non-zero on failure, with a clear message printed to stderr. Plan-phase script relies on this.
- **`mise-en-place/` as output home:** All new skills/tools land here.

### Integration Points
- `mise-en-place/spec-phase/` — new skill directory for the spec phase command and its implementation
- `mise-en-place/tool-validate-spec/` — new tool skill for the Python approval gate check
- `.planning/phases/02-spec-phase-greenfield/` — where SPEC.md, RESEARCH-*.md files are written during execution

</code_context>

<specifics>
## Specific Ideas

- "Mise en place" metaphor: spec phase = gathering all your ingredients and knowing what you're cooking before you start. The SPEC.md is the recipe card.
- The sub-agent research pattern mirrors the GSD researcher sub-agent model — fresh context, writes to a file, main flow reads the output. Deliberately parallel to existing patterns in the framework.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 2-Spec Phase — Greenfield*
*Context gathered: 2026-05-21*
