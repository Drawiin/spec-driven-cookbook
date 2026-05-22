# Phase 4: Plan Phase - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-22
**Phase:** 4-Plan Phase
**Areas discussed:** Plan decomposition trigger, Atomic task contract, Approval gate scope, Plan-phase depth

---

## Plan Decomposition Trigger

| Option | Description | Selected |
|--------|-------------|----------|
| Single plan by default | One PLAN.md unless developer explicitly requests multiple streams | ✓ |
| Agent proposes splits | Reads spec, suggests 2+ streams; developer accepts/edits/rejects | |
| Always ask upfront | First step always "How many work streams?" | |

**Follow-up decisions:**

| Question | Selected |
|----------|----------|
| How to request a split? | Conversational ("split into X and Y") |
| Independence criteria for parallel plans? | No cross-plan depends_on |
| Review before writing split plans? | Preview first — names, scope, wave assignment |

---

## Atomic Task Contract

| Option | Description | Selected |
|--------|-------------|----------|
| Hard rule + validator | Reject multi-output tasks | |
| Skill guidance only | No Python enforcement | |
| Structured but soft | SKILL.md requires criteria; validator checks presence only | ✓ |

**Follow-up decisions:**

| Question | Selected |
|----------|----------|
| Task format | Markdown todo: `[STATUS] TASKID - Title` |
| TASKID scheme | `{plan}-{task}` (e.g. 04-01-T1) |
| STATUS values | Text tags: [PENDING], [IN_PROGRESS], [DONE] |
| Verification criteria location | Inline nested checkbox under each task |
| Task sizing | One file or one script per task |
| Validator checks | Presence only (todo pattern + Verify sub-bullet) |
| Task dependencies | Depends: line per task + Mermaid graph |
| Mermaid placement | Top of plan, after ## Objective |
| Initial status at creation | All [PENDING] |
| Verify sub-bullet format | Nested checkbox: `  - [ ] Verify: ...` |
| YAML frontmatter | Minimal: status, phase, plan, requirements[] |

---

## Approval Gate Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Hybrid — approve all | All plans draft; one summary; single approve-all | ✓ |
| Per-plan gate | Each PLAN.md approved individually | |
| Single manifest | One PLANS.md index file | |

**Follow-up decisions:**

| Question | Selected |
|----------|----------|
| Approval interaction | Mirror spec-phase: yes / edit / abort |
| Status field location | status in each PLAN.md YAML |
| Execute blocking | tool-validate-plan checks all plans approved + format |

---

## Plan-Phase Depth

| Option | Description | Selected |
|--------|-------------|----------|
| MVP | Read spec → generate → approve; no sub-agents | |
| Research optional | MVP + optional research sub-tasks | |
| Full loop | Research + plan-checker revision loop | ✓ |

**Follow-up decisions:**

| Question | Selected |
|----------|----------|
| Plan-checker implementation | Task sub-agent → writes {phase}-REVIEWS.md |
| Research in plan-phase | Mandatory (GSD 4-researcher pattern) |
| Revision cap | Max 3 checker cycles, then escalate |

---

## Claude's Discretion

- Research topic selection for mandatory researchers
- Plan-checker review dimensions within 3-cycle cap
- Split-preview wording and when to proactively suggest splits

## Deferred Ideas

None captured during discussion.
