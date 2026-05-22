---
phase: 3
slug: brownfield-codebase-onboarding
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-05-22
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (dev-only, established Phase 1) |
| **Config file** | none — pytest discovers `test_*.py` under `mise-en-place/` |
| **Quick run command** | `python3 -m pytest mise-en-place/tool-detect-brownfield/ mise-en-place/tool-validate-spec/ -x -q` |
| **Full suite command** | `python3 -m pytest mise-en-place/ -q` |
| **Estimated runtime** | ~8 seconds (22 baseline + new tests) |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest mise-en-place/tool-detect-brownfield/ mise-en-place/tool-validate-spec/ -x -q`
- **After every plan wave:** Run `python3 -m pytest mise-en-place/ -q`
- **Before `/gsd-verify-work`:** Full suite must be green **and** Manual UAT checklist complete (blocking)
- **Max feedback latency:** ~8 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | PROJ-02 | T-03-01 | `--root` path resolved; reject outside cwd via relative_to | unit | `pytest mise-en-place/tool-detect-brownfield/test_detect_brownfield.py::test_reject_root_outside_cwd -x` | ❌ W0 | ⬜ pending |
| 03-01-02 | 01 | 1 | PROJ-02 | — | Greenfield on empty tmp dir | unit | `pytest mise-en-place/tool-detect-brownfield/test_detect_brownfield.py::test_detect_greenfield_empty -x` | ❌ W0 | ⬜ pending |
| 03-01-03 | 01 | 1 | PROJ-02 | — | Empty scaffolded codebase dir → needs_codebase_map true | unit | `pytest mise-en-place/tool-detect-brownfield/test_detect_brownfield.py::test_needs_codebase_map_empty_scaffold -x` | ❌ W0 | ⬜ pending |
| 03-01-04 | 01 | 1 | PROJ-02 | — | STACK.md present → has_codebase_map true, needs_codebase_map false | unit | `pytest mise-en-place/tool-detect-brownfield/test_detect_brownfield.py::test_has_codebase_map_when_stack_md_present -x` | ❌ W0 | ⬜ pending |
| 03-01-05 | 01 | 1 | PROJ-02 | — | package.json only (no code files) → is_brownfield true | unit | `pytest mise-en-place/tool-detect-brownfield/test_detect_brownfield.py::test_brownfield_package_file_only -x` | ❌ W0 | ⬜ pending |
| 03-01-06 | 01 | 1 | PROJ-03 | T-03-03 | validate_spec rejects brownfield spec missing `## Already Built` | unit | `pytest mise-en-place/tool-validate-spec/test_validate_spec.py::test_brownfield_missing_already_built -x` | ❌ W0 | ⬜ pending |
| 03-01-07 | 01 | 1 | PROJ-03 | T-03-03 | validate_spec rejects brownfield spec missing `## To Build` | unit | `pytest mise-en-place/tool-validate-spec/test_validate_spec.py::test_brownfield_missing_to_build -x` | ❌ W0 | ⬜ pending |
| 03-01-08 | 01 | 1 | PROJ-03 | T-03-03 | Inverse rule: brownfield sections without project_type fail | unit | `pytest mise-en-place/tool-validate-spec/test_validate_spec.py::test_brownfield_sections_without_project_type_fails -x` | ❌ W0 | ⬜ pending |
| 03-01-09 | 01 | 1 | PROJ-03 | — | Brownfield missing greenfield REQUIRED_SECTION (## Problem) fails | unit | `pytest mise-en-place/tool-validate-spec/test_validate_spec.py::test_brownfield_missing_problem_section -x` | ❌ W0 | ⬜ pending |
| 03-01-10 | 01 | 1 | PROJ-03 | — | validate_spec passes brownfield approved spec with all sections | unit | `pytest mise-en-place/tool-validate-spec/test_validate_spec.py::test_brownfield_approved_passes -x` | ❌ W0 | ⬜ pending |
| 03-01-11 | 01 | 1 | PROJ-02/03 | — | Greenfield specs still pass without brownfield sections | regression | `pytest mise-en-place/tool-validate-spec/test_validate_spec.py -x` | ✅ | ⬜ pending |
| 03-02-01 | 02 | 2 | PROJ-02 | T-03-04 | map-codebase SKILL.md defines parallel mapper workflow + secret scanning | manual | Reviewer confirms 4-focus mapper pattern + `.planning/codebase/` output contract + scan_for_secrets | N/A | ⬜ pending |
| 03-02-02 | 02 | 2 | PROJ-02/03 | — | spec-phase Step 1.4 triggers detection → map when brownfield | manual | Reviewer confirms Step 1.4 branch in spec-phase/SKILL.md (not Step 0) | N/A | ⬜ pending |
| 03-02-03 | 02 | 2 | PROJ-03 | — | Q&A loads all seven map summaries; skips re-asking mapped facts | manual | Reviewer confirms all-seven preload + delta-focused Q&A instructions | N/A | ⬜ pending |
| 03-02-04 | 02 | 2 | PROJ-03 | — | SPEC assembly includes `## Already Built` + `## To Build` | manual | Reviewer confirms assembly rules in spec-phase/SKILL.md | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `mise-en-place/tool-detect-brownfield/detect_brownfield.py` — PROJ-02 detection contract
- [ ] `mise-en-place/tool-detect-brownfield/test_detect_brownfield.py` — unit tests with tmp_path fixtures
- [ ] `mise-en-place/tool-detect-brownfield/SKILL.md` — invocation contract
- [ ] Extend `validate_spec.py` + `test_validate_spec.py` — brownfield section gates + inverse rule (PROJ-03)
- [ ] `mise-en-place/map-codebase/SKILL.md` — mapper workflow (manual UAT for agent spawning)
- [ ] Extend `spec-phase/SKILL.md` — Step 1.4 + brownfield Q&A + assembly rules

*Existing pytest infrastructure from Phase 1–2 covers framework setup — no additional install needed.*

---

## Manual UAT — BLOCKING for `/gsd-verify-work`

> Phase verify **cannot pass** until every row in this checklist is complete. Automated pytest green is necessary but not sufficient.

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| map-codebase spawns parallel mapper sub-agents | PROJ-02 | Requires live Cursor Task tool | Run `/map-codebase` on this repo; verify 7 complete files (>20 lines each) written to `.planning/codebase/` |
| spec-phase Step 1.4 triggers mapping before Q&A on brownfield repo | PROJ-02 | Agent orchestration + sub-agent spawn | Run `/spec-phase` on this repo; confirm Step 1.4 detection → map → confirm gate → Q&A sequence |
| spec-phase Continue path re-runs Step 1.4 on brownfield repo with existing greenfield SPEC | PROJ-02 | Resume branch may bypass detection if not enforced | On brownfield repo with existing greenfield-format SPEC.md, choose Continue; verify Step 1.4 re-runs detection/mapping before Q&A |
| Q&A does not re-ask facts present in codebase map | PROJ-03 | Conversational judgment | During brownfield spec-phase, verify agent references all-seven map summaries and focuses on delta |
| SPEC.md separates Already Built vs To Build | PROJ-03 | Requires full spec-phase run | Complete brownfield spec-phase; verify two distinct sections with no mixing |
| Greenfield path unchanged | PROJ-01 regression | Requires empty-repo run | Run `/spec-phase` on empty tmp dir; confirm no Step 1.4 mapping step, standard five sections only |
| Invalid detect_brownfield JSON stops workflow | PROJ-02 | Error path requires simulated failure | Document expected ERROR behavior when stdout is not valid JSON (Step 1.4 must not proceed to Q&A) |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] Manual UAT checklist complete (blocking for phase verify)
- [ ] No watch-mode flags
- [ ] Feedback latency < 8s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
