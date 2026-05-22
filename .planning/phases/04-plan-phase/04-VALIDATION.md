---
phase: 4
slug: plan-phase
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-05-22
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (established in Phases 1–3) |
| **Config file** | none — pytest auto-discovers `test_*.py` |
| **Quick run command** | `python3 -m pytest mise-en-place/tool-validate-plan/ -x -q` |
| **Full suite command** | `python3 -m pytest mise-en-place/ -q` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest mise-en-place/tool-validate-plan/ -x -q` (Wave 1) or `python3 -m pytest mise-en-place/plan-phase/ -x -q` (Wave 2)
- **After every plan wave:** Run `python3 -m pytest mise-en-place/ -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | PLAN-04 | T-04-01 | RED tests fail before validate_plan.py exists | unit | `grep -cE '^def test_' mise-en-place/tool-validate-plan/test_validate_plan.py && python3 -m pytest mise-en-place/tool-validate-plan/test_validate_plan.py -x -q 2>&1; test $? -ne 0` | ❌ W0 | ⬜ pending |
| 04-01-02 | 01 | 1 | PLAN-02/04 | T-04-01 | validate_plan exits 0 on approved plans with todo + Verify | unit | `python3 -m pytest mise-en-place/tool-validate-plan/test_validate_plan.py::test_all_approved_valid_plans_exits_zero -x` | ❌ W0 | ⬜ pending |
| 04-01-03 | 01 | 1 | PLAN-04 | — | validate_plan exits 1 on draft status | unit | `python3 -m pytest mise-en-place/tool-validate-plan/test_validate_plan.py::test_draft_plan_exits_one -x` | ❌ W0 | ⬜ pending |
| 04-01-04 | 01 | 1 | PLAN-02 | — | validate_plan exits 1 when task missing Verify sub-bullet | unit | `python3 -m pytest mise-en-place/tool-validate-plan/test_validate_plan.py::test_missing_verify_subbullet_exits_one -x` | ❌ W0 | ⬜ pending |
| 04-01-05 | 01 | 1 | PLAN-04 | T-04-01 | validate_plan rejects --phase-dir outside cwd | unit | `python3 -m pytest mise-en-place/tool-validate-plan/test_validate_plan.py::test_phase_dir_outside_cwd_exits_one -x` | ❌ W0 | ⬜ pending |
| 04-01-06 | 01 | 1 | PLAN-04 | — | Full tool-validate-plan suite green | integration | `python3 -m pytest mise-en-place/tool-validate-plan/ -x -q && python3 -m pytest mise-en-place/ -x -q` | ❌ W0 | ⬜ pending |
| 04-01-07 | 01 | 1 | PLAN-02 | — | SKILL.md documents invocation and D-11 scope boundary | manual | `grep -q "cursor_skill_adapter" mise-en-place/tool-validate-plan/SKILL.md && grep -q "Verify:" mise-en-place/tool-validate-plan/SKILL.md` | N/A | ⬜ pending |
| 04-02-01 | 02 | 2 | PLAN-01/05 | T-04-04 | SKILL.md documents validate_spec entry gate and six-step workflow | manual | `grep -q "validate_spec.py" mise-en-place/plan-phase/SKILL.md && grep -q "Step 1" mise-en-place/plan-phase/SKILL.md` | N/A | ⬜ pending |
| 04-02-02 | 02 | 2 | PLAN-01/03 | — | Contract tests assert research-before-plan and split/parallel rules | unit | `python3 -m pytest mise-en-place/plan-phase/test_plan_phase_contract.py -x -q` | ❌ W0 | ⬜ pending |
| 04-02-03 | 02 | 2 | PLAN-04 | T-04-04 | Contract tests assert approve-all gate and validate_plan confirmation | unit | `python3 -m pytest mise-en-place/plan-phase/test_plan_phase_contract.py::test_approval_gate_yes_edit_abort -x` | ❌ W0 | ⬜ pending |
| 04-02-04 | 02 | 2 | TOOL-05 | — | README documents tool-validate-plan and plan-phase | manual | `grep -q "### tool-validate-plan" mise-en-place/README.md && grep -q "### plan-phase" mise-en-place/README.md` | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `mise-en-place/tool-validate-plan/test_validate_plan.py` — 10 pytest functions for PLAN-02/PLAN-04 exit-code contract
- [ ] `mise-en-place/tool-validate-plan/validate_plan.py` — implementation under test
- [ ] `mise-en-place/plan-phase/test_plan_phase_contract.py` — contract tests for PLAN-01/03/05 SKILL structure

*Existing pytest infrastructure from Phases 1–3 covers framework setup — no additional install needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| plan-phase SKILL drives mandatory research before plan write | PLAN-01, D-23 | Requires live Cursor Task tool | Run `/plan-phase` on repo with approved SPEC.md; verify `{phase}-RESEARCH.md` exists before any `*-PLAN.md` is written |
| Plan-checker revision loop runs up to 3 cycles | D-21/D-24 | Requires live sub-agent spawn | Complete plan generation; verify `{phase}-REVIEWS.md` created and orchestrator revises on ISSUES FOUND |
| Approve-all gate flips all plans draft→approved | PLAN-04, D-16 | Requires live agent StrReplace after user confirms | Reach approval prompt, answer "yes", verify all `*-PLAN.md` have `status: approved` and validate_plan.py exits 0 |
| Conversational split preview before multi-plan write | PLAN-03, D-04 | Requires agent conversation | Say "split into frontend and backend"; verify preview before files written |
| End-user plans use todo format not GSD XML | PLAN-02, D-06 | Format is in generated artifacts | Inspect output PLAN.md — must contain `[PENDING]` lines and `Verify:` sub-bullets, not `<task>` XML |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 5s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
