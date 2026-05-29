---
phase: 4
reviewers: [composer-in-session]
reviewed_at: 2026-05-22T00:00:00Z
plans_reviewed: [04-01-PLAN.md, 04-02-PLAN.md]
cli_availability_note: >
  --all requested. Detected CLIs: cursor only (skipped — running inside Cursor for independence).
  gemini, claude, codex, coderabbit, opencode, qwen, ollama, lm_studio, llama_cpp: missing.
  Review below is in-session fallback by Composer; not adversarial cross-AI.
---

# Cross-AI Plan Review — Phase 4

> **CLI status:** No external AI CLIs available. Install at least one for true cross-AI review:
> - [Gemini CLI](https://github.com/google-gemini/gemini-cli)
> - [Codex CLI](https://github.com/openai/codex)
> - [Claude Code](https://github.com/anthropics/claude-code)
> - [OpenCode](https://opencode.ai)
> - [Qwen Code](https://github.com/nicepkg/qwen-code)
>
> Re-run `/gsd-review 4 --all` after installing.

---

## Composer (In-Session) Review

### 1. Summary

Phase 4 plans are well-structured and faithfully map locked decisions D-01 through D-24 onto a sensible two-wave delivery: Wave 1 builds the stdlib `validate_plan.py` gate (TDD, mirroring Phase 2's `validate_spec.py`), Wave 2 delivers the user-facing `plan-phase/SKILL.md` orchestration with contract tests and README updates. The wave ordering is correct, reuse patterns are explicit, and threat models are proportionate. The primary gap is **soft enforcement of PLAN-02 atomicity** — the plans acknowledge this (D-05/D-11) but leave no automated or plan-checker hook strong enough to prevent multi-deliverable tasks from slipping through, which could undermine Phase 5 exec-phase assumptions.

### 2. Strengths

- **Clear wave dependency:** 04-02 correctly blocks on 04-01; `validate_plan.py` exists before the approval gate documents it.
- **Proven TDD pattern:** 04-01 mirrors `validate_spec.py` — copy `parse_frontmatter`, fixture helpers, 10 exit-code tests, RED→GREEN→SKILL — low invention risk.
- **Decision traceability:** Every D-* decision in 04-CONTEXT.md maps to a specific step in 04-02 Task 1; must_haves truths are testable.
- **Dual-format awareness:** Plans explicitly warn against conflating GSD execution plans (04-01/04-02 themselves) with todo-format end-user plans — documented in RESEARCH and 04-02 interfaces.
- **Belt-and-suspenders gates:** D-19/D-20 entry (`validate_spec`) and exit (`validate_plan`) gates are wired in both SKILL and contract tests.
- **Threat models:** Path traversal (T-04-01), ReDoS (T-04-02), and SKILL tampering (T-04-04) are addressed with appropriate dispositions.
- **Contract test depth:** 17 assertions in 04-02 Task 2 exceed Phase 2 spec-phase contract coverage for workflow structure.

### 3. Concerns

| Severity | Concern |
|----------|---------|
| **HIGH** | **PLAN-02 atomicity is soft-only.** D-05/D-11 limit `validate_plan.py` to Verify: *presence*, not single-deliverable sizing. D-10 task-sizing guidance lives only in SKILL prose and plan-checker discretion — no contract test, no validator check, no plan-checker rubric item for "one file / one script per task." Phase 5 workers may receive multi-output tasks that pass all gates. |
| **HIGH** | **Filename pattern collision.** Both GSD execution plans and end-user todo plans use `{phase}-{NN}-PLAN.md` in `.planning/phases/{slug}/`. Running `validate_plan.py --phase-dir` on a directory containing GSD XML plans (like this phase's own 04-01/04-02 files) will fail with "no tasks." Plans should document **when NOT to invoke** validate_plan (GSD execution dirs) vs when to (todo-format output from `/plan-phase`). |
| **MEDIUM** | **04-02 Task 1 is monolithic.** One task writes the entire SKILL.md covering 24 decisions and 6 steps — high context-load and easy to miss a D-* during execution. Consider splitting into Step 1–3 / Step 4–6 tasks if executor struggles. |
| **MEDIUM** | **No CONTEXT.md creation step.** Plan-checker prompt references `{phase}-CONTEXT.md if exists`, but plan-phase SKILL has no step to create or gather CONTEXT (unlike discuss-phase). Brownfield or complex specs may lack locked decisions for the checker. |
| **MEDIUM** | **`_task_has_verify` edge cases.** Verify scan stops at next TASK_LINE or `## ` header. Tasks with blank lines, code blocks, or `###` sub-headers between task line and Verify could false-fail. Tests don't cover these boundaries. |
| **MEDIUM** | **`test_all_pending_at_creation` is weak.** Accepts any `[PENDING]` presence without asserting D-14 language ("at creation", "written as [PENDING]"). Easy to pass with incidental mention. |
| **LOW** | **`planning_scaffold.py scaffold` at Step 1.** Unclear interaction when phase dir already exists with artifacts. May overwrite or conflict — no acceptance criteria for idempotent startup. |
| **LOW** | **Research output path differs from spec-phase.** Plan-phase writes consolidated `{phase}-RESEARCH.md` only (RESEARCH A3); spec-phase uses `.planning/research/` per-topic files. Documented but could confuse agents familiar with spec-phase. |

### 4. Suggestions

1. **Add plan-checker rubric item for atomicity (D-10):** In 04-02 Step 4 checker prompt, require explicit BLOCKER if any task names multiple files/scripts or bundles implementation + tests in one task.
2. **Document validate_plan scope boundary in 04-01 SKILL task:** Add explicit note — "For todo-format plans produced by `/plan-phase` only. Do not run against GSD execution plan directories (gsd-executor format with `<task>` XML)."
3. **Add contract test `test_task_atomicity_guidance_documented`:** Assert SKILL contains D-10 sizing language ("one file" AND "one script" AND "two tasks" or equivalent).
4. **Add validate_plan test for GSD-format plan rejection:** Fixture with `<task type="auto">` and no `[PENDING]` lines → exit 1 with actionable "no todo tasks found" — clarifies format expectation.
5. **Strengthen `test_all_pending_at_creation`:** Require step text stating tasks are written as `[PENDING]` at creation time, not just token presence.
6. **Optional CONTEXT gathering sub-step:** After Step 1 entry gate, if `{phase}-CONTEXT.md` missing and SPEC complexity warrants it, prompt developer for locked decisions or spawn brief discuss sub-step before research.
7. **Add Verify boundary test:** Task line → blank line → Verify sub-bullet — confirm pass/fail behavior matches intent and document in validate_plan.py docstring.

### 5. Risk Assessment

**Overall: MEDIUM**

**Justification:** Implementation path is well-trodden (Phase 2 analogs, stdlib-only, TDD). Wave ordering and dependency on 04-01 are sound. Risk concentrates in **semantic gaps** — atomicity enforcement and format collision — that won't fail tests but could degrade Phase 5 exec quality. The monolithic SKILL task adds execution risk but is recoverable via plan-checker loop. No security or dependency risks beyond accepted path-traversal mitigations.

**Requirement coverage:**

| Requirement | Covered by | Gap |
|-------------|-----------|-----|
| PLAN-01 | 04-02 SKILL Steps 1–6 | — |
| PLAN-02 | D-09/D-10 SKILL text | No hard enforcement |
| PLAN-03 | D-02/D-03 split + preview | Soft — conversational only |
| PLAN-04 | D-16–D-19 approve-all + validate_plan | — |
| PLAN-05 | Step 1 clean-context note | Contract test is string-match only |

---

## Consensus Summary

> Single reviewer (in-session). "Consensus" reflects internal consistency checks across 04-01, 04-02, 04-CONTEXT, and 04-RESEARCH — not multi-AI agreement.

### Agreed Strengths

- Two-wave split (tool first, skill second) is the right decomposition.
- TDD + contract-test strategy matches established Phase 2 patterns.
- Locked decisions D-01–D-24 are comprehensively mapped in plan text.

### Agreed Concerns (priority order)

1. PLAN-02 atomicity relies on prose/checker discretion — no automated guard.
2. GSD vs todo `{NN}-PLAN.md` naming collision needs explicit validate_plan scope docs.
3. Monolithic SKILL.md task increases miss risk for individual D-* decisions.

### Divergent Views

N/A — single reviewer session.

---

## Recommended Next Steps

1. **Optional:** Incorporate suggestions via `/gsd-plan-phase 4 --reviews`
2. **Or proceed:** `/gsd-execute-phase 4` if HIGH concerns are accepted as known limitations (D-05 intentional scope)
3. **For true cross-AI review:** Install gemini/claude/codex CLI and re-run `/gsd-review 4 --all`
