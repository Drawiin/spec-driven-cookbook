# Phase 1: Tooling Foundation - Context

**Gathered:** 2026-05-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Build standalone Python CLI scripts for environment checking, context assembly, and planning directory scaffolding — wrapped as Cursor skill commands — all bundled inside the skill folder so generated project variants are self-contained from day one.

</domain>

<decisions>
## Implementation Decisions

### Language
- **D-01:** All tool scripts written in Python, stdlib only — zero pip install dependencies; works out of the box on any Python 3.x install.

### Skill Bundling Structure
- **D-02:** Tools are co-located with the skill that uses them. Each tool that is shared across multiple skills gets its own dedicated `tool-` prefixed skill (e.g. `tool-env-check`, `tool-context-builder`).
- **D-03:** Each `tool-*` skill contains a `SKILL.md` (the "how to use this" contract) and the Python script(s) that implement the tool. No monolithic utility dump.
- **D-04:** Skill naming convention for tool wrappers: `tool-<name>` prefix makes it immediately obvious these are tool skills, not workflow or planning skills.

### Context-Builder Output
- **D-05:** Directory tree depth: 3 levels.
- **D-06:** Exclusion rules: respects the project's `.gitignore` file AND explicitly excludes `.planning/` — framework internals do not appear in the pasted context.
- **D-07:** Output sections: (1) directory tree, (2) dependency list, (3) git summary, (4) key file previews — first ~20 lines of detected entry points (README, main script, etc.).

### Invocation Interface
- **D-08:** Tools are exposed as Cursor skill commands. Each tool's `SKILL.md` instructs the agent to invoke the tool by running the Python script via the Shell tool.
- **D-09:** Agents that need a tool capability read the relevant `tool-*` skill's `SKILL.md` and follow its instructions — the SKILL.md is the contract; the Python script is the implementation.

### Claude's Discretion
- Entry-point detection heuristic for key file previews (README.md, main.py, index.js, pyproject.toml, etc.) — standard patterns are fine.
- Exact git summary format (last N commits, branch, status) — keep it concise and useful for an agent prompt.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Requirements
- `.planning/REQUIREMENTS.md` — TOOL-01, TOOL-02, TOOL-04, TOOL-05 define the full requirement set for this phase
- `.planning/ROADMAP.md` — Phase 1 success criteria (the four numbered items are the acceptance gates)

### Project Decisions
- `.planning/PROJECT.md` — Key Decisions table (Cursor-only, file-based state, tools inside skill folder)

### Research Inputs
- `research/topics/auxiliary-tooling.md` — Cross-framework analysis of deterministic tooling patterns worth adopting
- `research/SUMMARY.md` — Top-10 patterns including thin-orchestrator and context-discipline patterns that inform tool design

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None — this is a documentation-only repository; no Python scripts or CLI tools exist yet. Phase 1 creates the first application code.

### Established Patterns
- GSD's `.cjs` tool scripts (`.cursor/get-shit-done/bin/`) demonstrate the "tools bundled inside the framework folder" pattern — same approach applied here with Python + `tool-*` skills.
- GSD's `SKILL.md` pattern: skill file as the invocation contract + separate implementation file. Phase 1 follows this pattern exactly.

### Integration Points
- `mise-en-place/` — the cookbook's future output home; the `tool-*` skills produced in Phase 1 are the first real content.
- `.planning/` — the planning scaffolder tool (TOOL-01) reads/writes here; must be idempotent.

</code_context>

<specifics>
## Specific Ideas

- The culinary "mise en place" metaphor applies directly to Phase 1: having tools ready before the cooking starts.
- Tool skill naming examples confirmed: `tool-env-check`, `tool-context-builder`.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 1-Tooling Foundation*
*Context gathered: 2026-05-21*
