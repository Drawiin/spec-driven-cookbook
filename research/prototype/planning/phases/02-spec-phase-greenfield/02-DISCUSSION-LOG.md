# Phase 2: Spec Phase — Greenfield — Discussion Log

**Date:** 2026-05-21
**Status:** Complete

---

## Gray Areas Discussed

### 1. Q&A Structure

**Question asked:** How should the questioning flow work?
**Options presented:** Templated (fixed categories) / Adaptive (agent-driven) / Hybrid (fixed spine + agent probes within categories)
**Selection:** Hybrid

**Follow-up:** How many turns per category before moving on?
**Options presented:** One-shot / Up to 3 follow-ups / User signals when ready
**Selection:** Up to 3 follow-ups per category

**Decision captured:** Fixed category spine (Problem → Who → Constraints → Success Criteria → Out-of-scope). Agent probes within each category up to 3 turns when answers are vague. Agent decides when to advance.

---

### 2. Research Sub-tasks

**Question asked:** When/how does a research sub-task get triggered?
**Options presented:** Agent-suggests-at-end / User-command-anytime / Both
**Selection:** Both

**Follow-up:** What form does a research sub-task take?
**Options presented:** Spawned sub-agent (writes RESEARCH.md) / Inline web search (breaks clean-context) / Python script
**Selection:** Spawned sub-agent with fresh context → writes RESEARCH.md → main flow reads it

**Decision captured:** Dual trigger (agent gap-detection + user request). Sub-agent handles external lookups; main context stays clean. Multiple research files supported (`RESEARCH-<topic>.md`).

---

### 3. SPEC.md Format

**Question asked:** What mandatory sections does SPEC.md contain?
**Options presented:** Minimal (5 sections) / Medium (+ requirements + decisions) / Rich (+ personas + stories)
**Selection:** Minimal — Problem, Who it's for, Constraints, Success Criteria, Out-of-scope

**Follow-up:** Should SPEC.md have machine-readable metadata?
**Options presented:** YAML front-matter / Markdown header block / No metadata
**Selection:** YAML front-matter with `status`, `version`, `date`

**Decision captured:** Minimal five-section SPEC.md with YAML front-matter. Status field (`draft | approved`) is the approval gate's read/write target.

---

### 4. Approval Gate

**Question asked:** How does the approval gate work mechanically?
**Options presented:** Separate approve command / Agent-asks-in-flow / Manual edit by user
**Selection:** Agent-in-flow — at end of Q&A, agent presents SPEC.md and asks "Approve? (yes / edit / abort)"

**Follow-up:** How does the planning phase enforce the gate?
**Options presented:** Python validation script / SKILL.md instruction only / Both (belt-and-suspenders)
**Selection:** Both — SKILL.md instruction + Python `tool-validate-spec` script as hard gate

**Decision captured:** Approval is part of the spec flow (no separate command). Enforcement is belt-and-suspenders: agent instruction + Python hard-exit if status ≠ approved.

---

## Deferred Ideas

None.

---

## Claude's Discretion Items

- Exact Q&A prompt wording within each category
- "Vague answer" detection heuristic (when to follow up vs. advance)
- Research sub-task prompt format passed to spawned sub-agent
