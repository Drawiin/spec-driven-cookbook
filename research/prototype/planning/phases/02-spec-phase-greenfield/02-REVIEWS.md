---
phase: 2
reviewers: [orchestrator]
reviewed_at: 2026-05-22T00:00:00Z
plans_reviewed: [02-01-PLAN.md, 02-02-PLAN.md]
note: "External AI CLIs unavailable (gemini/claude/codex missing; cursor skipped in-session). Review conducted by orchestrator against plans, CONTEXT, RESEARCH, and Phase 1 patterns."
---

# Cross-AI Plan Review — Phase 2: Spec Phase — Greenfield

## Orchestrator Review

# Cross-AI Plan Review — Phase 2: Spec Phase — Greenfield (02-01, 02-02)

## Executive Summary

The two-plan wave structure is sound: Wave 1 delivers the hard exit-code gate (`validate_spec.py`) via TDD; Wave 2 delivers the agent-facing SKILL contracts. Locked decisions D-01–D-09 are traced into 02-02 with good fidelity, and the portable research path (`.planning/research/RESEARCH-<topic-slug>.md`) correctly overrides the stale D-04 phase-specific path in CONTEXT.md. The **critical gap** is a test/implementation mismatch in 02-01: `test_approved_spec_has_required_sections` expects section-header validation, but the GREEN task's `main()` only checks front-matter status — the test will fail after implementation unless section validation is added. Secondary gaps: no negative test for missing sections, no `mise-en-place/README.md` update for new tools, and weak automated proof that spec-phase SKILL behavior matches SPEC-01/05 (grep-only verification in 02-02).

---

## PLAN 02-01: tool-validate-spec (TDD)

### 1. Summary

Well-structured TDD plan with clear RED/GREEN tasks, stdlib-only constraint, and actionable stderr messages. Exit-code contract aligns with D-09. The fifth test (`test_approved_spec_has_required_sections`) creates a **spec/implementation divergence** — the GREEN task never instructs the executor to validate section headers, so the test cannot pass.

### 2. Strengths

- **TDD discipline** — tests written first; five named functions map to SPEC-04 behaviors
- **CRLF safety** — `.splitlines()` explicitly required (learned from Phase 1)
- **Portable SPEC paths** — `SPEC_CANDIDATES` searches `.planning/SPEC.md` then root `SPEC.md`
- **Threat model** — appropriate accept dispositions for local workflow tool
- **Parallel-safe** — Wave 1 blocks only 02-02; no file overlap

### 3. Concerns

| Severity | Concern |
|----------|---------|
| **HIGH** | **Test/implementation mismatch** — RED task defines `test_approved_spec_has_required_sections` asserting exit 0 when all five section headers present; GREEN task `main()` only validates front-matter `status == approved`. No `REQUIRED_SECTIONS` constant or body scan in implementation action. Test will fail at GREEN. |
| **MEDIUM** | **No negative section test** — Missing test for approved spec with missing section headers → should exit 1 with actionable stderr (SPEC-02 enforcement at gate level). |
| **MEDIUM** | **Section header canonical names** — Test uses `## Who It's For` and `## Out of Scope`; 02-02 SKILL template uses similar but Q&A categories say "Who it's for" / "Out-of-scope". Validator should document exact header strings (case-sensitive match) and align with spec-phase SKILL.md template. |
| **LOW** | **Import-at-module-level RED pattern** — Plan says import fails if validate_spec.py absent, making collection fail entirely. Consider `pytest.importorskip` or separate collection note; current approach is acceptable but may confuse executors. |
| **LOW** | **No subprocess smoke test** — Direct `main()` calls only; argparse wiring untested (though script has no args). |

### 4. Suggestions

- Add to GREEN task: `REQUIRED_SECTIONS = ["## Problem", "## Who It's For", "## Constraints", "## Success Criteria", "## Out of Scope"]` (exact strings). After status check, scan body for each header; if any missing, print `ERROR: SPEC.md missing required section: {name}` to stderr and exit 1.
- Add RED test `test_approved_spec_missing_section_exits_one`: status approved but omit `## Constraints` → exit 1, stderr contains "missing required section".
- Document canonical section headers in both `validate_spec.py` docstring and `tool-validate-spec/SKILL.md`.
- Add `test_approved_spec_has_required_sections` to must_haves truths explicitly.

### 5. Risk Assessment

**Overall: MEDIUM** — Core exit-code logic is straightforward; **section validation omission** is a blocking implementation bug in the plan text itself.

---

## PLAN 02-02: SKILL.md contracts (spec-phase + tool-validate-spec)

### 1. Summary

Comprehensive spec-phase workflow with all five steps, both research trigger modes, portable research paths, and approval gate StrReplace. tool-validate-spec SKILL follows Phase 1 adapter pattern. Verification relies heavily on grep — no behavioral test that spec-phase instructions produce valid SPEC.md. Missing README documentation for new tools.

### 2. Strengths

- **Decision traceability** — Each step references D-01–D-09; five-category spine in exact order
- **Portability fix** — Research output to `.planning/research/` with explicit ban on `phases/02-spec-phase-greenfield` paths
- **Idempotent approval** — Pitfall 6 handled (skip StrReplace if already approved)
- **Existing SPEC detection** — Pitfall 4 resume/overwrite/abort flow in Step 1
- **Belt-and-suspenders** — D-09 referenced in Step 5 with validate_spec.py reminder

### 3. Concerns

| Severity | Concern |
|----------|---------|
| **MEDIUM** | **No mise-en-place/README.md update** — Phase 1 added README listing all tools; Phase 2 adds `tool-validate-spec` and `spec-phase` but no plan task updates README. TOOL-05 / SC-4 "self-contained skill folder" gap. |
| **MEDIUM** | **CONTEXT D-04 stale path** — CONTEXT still says `.planning/phases/02-spec-phase-greenfield/` for research; plan correctly uses `.planning/research/`. Planner should add a note in spec-phase SKILL or update CONTEXT during execution to record the override rationale. |
| **MEDIUM** | **Grep-only verification for SKILL.md** — Acceptance criteria count string occurrences; no golden-fixture test that a sample Q&A produces valid SPEC.md structure. Acceptable for MVP if 02-VALIDATION.md manual checks cover SPEC-01/05. |
| **LOW** | **Research sub-agent model unspecified** — Task tool spawn says `generalPurpose` but no model guidance; executor may pick wrong model. Add "use default model" or omit model param explicitly. |
| **LOW** | **Step 1 scaffold vs spec-only needs** — `planning_scaffold.py scaffold` creates full `.planning/` tree including `phases/` and `codebase/` — correct per PROJ-01 but heavier than minimal spec-only scaffold. Acceptable; document idempotency. |
| **LOW** | **No `.planning/research/` creation explicit** — Step 1 says scaffold creates `.planning/research/` but Phase 1 scaffold may only create `phases/` and `codebase/`. Verify `planning_scaffold.py` actually creates `research/` or add mkdir instruction in Step 3. |

### 4. Suggestions

- Add Task 3 (or extend Task 2): Update `mise-en-place/README.md` with entries for `tool-validate-spec` and `spec-phase` (invocation one-liners).
- In Step 3, add: "Ensure `.planning/research/` exists — run `mkdir -p .planning/research` if scaffold does not create it."
- Cross-reference `REQUIRED_SECTIONS` from validate_spec.py in spec-phase Step 4 template (exact header strings must match validator).
- Add to 02-VALIDATION.md manual row: "Run /spec-phase on empty tmp repo" if not already present.

### 5. Risk Assessment

**Overall: LOW–MEDIUM** — SKILL.md plans are thorough; **README gap** and **research dir creation** are the main execution risks.

---

## Cross-Cutting Analysis

### Phase goal coverage

| Success criterion | Plans coverage | Gap |
|-------------------|----------------|-----|
| SC-1 structured Q&A | 02-02 Step 2 | grep-only proof |
| SC-2 persisted SPEC.md | 02-02 Step 4 | no fixture test |
| SC-3 research sub-tasks | 02-02 Step 3 | research/ dir creation unverified |
| SC-4 approval gate | 02-01 + 02-02 Step 5 | section validation missing in 02-01 GREEN |
| SC-5 clean context | 02-02 Step 1 note | adequate |

### Requirement coverage

| REQ-ID | Covered by | Gap |
|--------|-----------|-----|
| SPEC-01 | 02-02 | manual verification only |
| SPEC-02 | 02-01 test + 02-02 template | implementation missing section check |
| SPEC-03 | 02-02 Step 3 | adequate |
| SPEC-04 | 02-01 + 02-02 | fix section validation |
| SPEC-05 | 02-02 Step 1 | adequate |
| PROJ-01 | 02-02 Step 1 scaffold | verify research/ subdir |

---

## Consensus Summary

### Agreed Strengths

- Two-wave plan structure with clear dependency (validator before SKILL contracts)
- Portable research paths (not phase-specific)
- TDD for validate_spec.py with explicit exit-code contract
- Comprehensive five-step spec-phase workflow with approval gate

### Agreed Concerns (highest priority)

1. **HIGH: 02-01 GREEN task must implement REQUIRED_SECTIONS validation** — test already expects it
2. **MEDIUM: Add negative test for missing sections** in 02-01
3. **MEDIUM: Update mise-en-place/README.md** with new tools in 02-02
4. **MEDIUM: Verify/create `.planning/research/` directory** in spec-phase workflow
5. **LOW: Align section header canonical strings** across validator, SKILL template, and tests

### Divergent Views

None — single reviewer (orchestrator); external CLIs unavailable for independent second opinion.

---
