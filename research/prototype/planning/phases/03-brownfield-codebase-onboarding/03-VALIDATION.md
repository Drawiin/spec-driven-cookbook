---
phase: 3
slug: brownfield-codebase-onboarding
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-05-22
revised: 2026-05-22
revision_note: "Cross-AI review replan — dedup gate, symlink/DoS tests, scan_map_secrets, contract tests, SC traceability"
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (dev-only, established Phase 1) |
| **Config file** | none — pytest discovers `test_*.py` under `mise-en-place/` |
| **Quick run command** | `python3 -m pytest mise-en-place/tool-detect-brownfield/ mise-en-place/tool-validate-spec/ mise-en-place/tool-scan-map-secrets/ -x -q` |
| **Contract test command** | `python3 -m pytest mise-en-place/spec-phase/test_spec_phase_contract.py mise-en-place/map-codebase/test_map_codebase_contract.py -x -q` |
| **Full suite command** | `python3 -m pytest mise-en-place/ -q` |
| **Estimated runtime** | ~12 seconds (22 baseline + new Wave 1 + contract tests) |

---

## ROADMAP Success Criteria Reference

| ID | Criterion |
|----|-----------|
| **SC1** | Running the framework on a non-empty repo detects existing code and triggers codebase mapping before the spec Q&A opens |
| **SC2** | The codebase map (stack, structure, conventions, existing capabilities) is loaded into the spec context so the Q&A does not re-ask what already exists |
| **SC3** | The produced spec file explicitly separates "already built" from "to build", with no mixing between the two sections |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest mise-en-place/tool-detect-brownfield/ mise-en-place/tool-validate-spec/ mise-en-place/tool-scan-map-secrets/ -x -q`
- **After Wave 2 SKILL tasks:** Also run contract test command
- **After every plan wave:** Run `python3 -m pytest mise-en-place/ -q`
- **Before `/gsd-verify-work`:** Full suite must be green **and** Manual UAT checklist complete (blocking)
- **Max feedback latency:** ~12 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | SC | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-----|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | SC1 | PROJ-02 | T-03-01 | `--root` path resolved; reject outside cwd via relative_to | unit | `pytest mise-en-place/tool-detect-brownfield/test_detect_brownfield.py::test_reject_root_outside_cwd -x` | ❌ W0 | ⬜ pending |
| 03-01-02 | 01 | 1 | SC1 | PROJ-02 | — | Greenfield on empty tmp dir | unit | `pytest mise-en-place/tool-detect-brownfield/test_detect_brownfield.py::test_detect_greenfield_empty -x` | ❌ W0 | ⬜ pending |
| 03-01-03 | 01 | 1 | SC1 | PROJ-02 | — | Empty scaffolded codebase dir → needs_codebase_map true | unit | `pytest mise-en-place/tool-detect-brownfield/test_detect_brownfield.py::test_needs_codebase_map_empty_scaffold -x` | ❌ W0 | ⬜ pending |
| 03-01-04 | 01 | 1 | SC1 | PROJ-02 | — | STACK.md present → has_codebase_map true, needs_codebase_map false | unit | `pytest mise-en-place/tool-detect-brownfield/test_detect_brownfield.py::test_has_codebase_map_when_stack_md_present -x` | ❌ W0 | ⬜ pending |
| 03-01-05 | 01 | 1 | SC1 | PROJ-02 | — | package.json only (no code files) → is_brownfield true | unit | `pytest mise-en-place/tool-detect-brownfield/test_detect_brownfield.py::test_brownfield_package_file_only -x` | ❌ W0 | ⬜ pending |
| 03-01-06 | 01 | 1 | SC3 | PROJ-03 | T-03-03 | validate_spec rejects brownfield spec missing `## Already Built` | unit | `pytest mise-en-place/tool-validate-spec/test_validate_spec.py::test_brownfield_missing_already_built -x` | ❌ W0 | ⬜ pending |
| 03-01-07 | 01 | 1 | SC3 | PROJ-03 | T-03-03 | validate_spec rejects brownfield spec missing `## To Build` | unit | `pytest mise-en-place/tool-validate-spec/test_validate_spec.py::test_brownfield_missing_to_build -x` | ❌ W0 | ⬜ pending |
| 03-01-08 | 01 | 1 | SC3 | PROJ-03 | T-03-03 | Inverse rule: brownfield sections without project_type fail | unit | `pytest mise-en-place/tool-validate-spec/test_validate_spec.py::test_brownfield_sections_without_project_type_fails -x` | ❌ W0 | ⬜ pending |
| 03-01-09 | 01 | 1 | SC3 | PROJ-03 | — | Brownfield missing greenfield REQUIRED_SECTION (## Problem) fails | unit | `pytest mise-en-place/tool-validate-spec/test_validate_spec.py::test_brownfield_missing_problem_section -x` | ❌ W0 | ⬜ pending |
| 03-01-10 | 01 | 1 | SC3 | PROJ-03 | — | validate_spec passes brownfield approved spec with all sections | unit | `pytest mise-en-place/tool-validate-spec/test_validate_spec.py::test_brownfield_approved_passes -x` | ❌ W0 | ⬜ pending |
| 03-01-11 | 01 | 1 | SC1/SC3 | PROJ-02/03 | — | Greenfield specs still pass without brownfield sections | regression | `pytest mise-en-place/tool-validate-spec/test_validate_spec.py -x` | ✅ | ⬜ pending |
| 03-01-12 | 01 | 1 | SC3 | PROJ-03 | T-03-03 | Dedup: identical bullet in Already Built and To Build fails | unit | `pytest mise-en-place/tool-validate-spec/test_validate_spec.py::test_brownfield_duplicate_bullet_in_both_sections_fails -x` | ❌ W0 | ⬜ pending |
| 03-01-13 | 01 | 1 | SC1 | PROJ-02 | T-03-01 | Symlink outside root not followed during walk | unit | `pytest mise-en-place/tool-detect-brownfield/test_detect_brownfield.py::test_symlink_outside_root_not_followed -x` | ❌ W0 | ⬜ pending |
| 03-01-14 | 01 | 1 | SC1 | PROJ-02 | T-03-02 | max_depth=3 excludes files beyond depth 3 | unit | `pytest mise-en-place/tool-detect-brownfield/test_detect_brownfield.py::test_max_depth_limits_walk -x` | ❌ W0 | ⬜ pending |
| 03-01-15 | 01 | 1 | SC1 | PROJ-02 | T-03-02 | SKIP_DIRS excludes node_modules from detection | unit | `pytest mise-en-place/tool-detect-brownfield/test_detect_brownfield.py::test_skip_dirs_excludes_node_modules -x` | ❌ W0 | ⬜ pending |
| 03-01-16 | 01 | 1 | SC1 | PROJ-02 | T-03-04 | scan_map_secrets exits 1 on API-key pattern in map file | unit | `pytest mise-en-place/tool-scan-map-secrets/test_scan_map_secrets.py -x` | ❌ W0 | ⬜ pending |
| 03-02-01 | 02 | 2 | SC1 | PROJ-02 | T-03-04 | map-codebase SKILL defines parallel mapper + scan_map_secrets gate | contract | `pytest mise-en-place/map-codebase/test_map_codebase_contract.py -x` | ❌ W2 | ⬜ pending |
| 03-02-02 | 02 | 2 | SC1 | PROJ-02/03 | — | spec-phase Step 1.4 after scaffold, before Q&A (not Step 0) | contract | `pytest mise-en-place/spec-phase/test_spec_phase_contract.py::test_step_1_4_after_scaffold_before_qa -x` | ❌ W2 | ⬜ pending |
| 03-02-03 | 02 | 2 | SC1/SC2 | PROJ-02 | T-03-07 | Completeness gate + stub STACK remap documented in Step 1.4 | contract | `pytest mise-en-place/spec-phase/test_spec_phase_contract.py::test_completeness_gate_documented -x` | ❌ W2 | ⬜ pending |
| 03-02-04 | 02 | 2 | SC2 | PROJ-03 | — | All seven map filenames preloaded in spec-phase | contract | `pytest mise-en-place/spec-phase/test_spec_phase_contract.py::test_all_seven_map_filenames_preloaded -x` | ❌ W2 | ⬜ pending |
| 03-02-05 | 02 | 2 | SC3 | PROJ-03 | — | SPEC assembly includes Already Built + To Build sections | contract | `pytest mise-en-place/spec-phase/test_spec_phase_contract.py::test_brownfield_sections_in_assembly -x` | ❌ W2 | ⬜ pending |
| 03-02-06a | 02 | 2 | SC1 | PROJ-02 | — | Continue branch documented in spec-phase SKILL | contract | `pytest mise-en-place/spec-phase/test_spec_phase_contract.py::test_continue_branch_documented -x` | ❌ W2 | ⬜ pending |
| 03-02-06b | 02 | 2 | SC1 | PROJ-02 | — | Invalid JSON from detect_brownfield stops workflow | contract | `pytest mise-en-place/spec-phase/test_spec_phase_contract.py::test_invalid_json_stops_workflow -x` | ❌ W2 | ⬜ pending |
| 03-01-17 | 01 | 1 | SC1 | PROJ-02 | — | Brownfield repo with .py files → is_brownfield true | unit | `pytest mise-en-place/tool-detect-brownfield/test_detect_brownfield.py::test_detect_brownfield_with_py_files -x` | ❌ W0 | ⬜ pending |
| 03-01-18 | 01 | 1 | SC1 | PROJ-02 | — | Brownfield without map → needs_codebase_map true | unit | `pytest mise-en-place/tool-detect-brownfield/test_detect_brownfield.py::test_needs_codebase_map -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `mise-en-place/tool-detect-brownfield/detect_brownfield.py` — PROJ-02 detection contract
- [ ] `mise-en-place/tool-detect-brownfield/test_detect_brownfield.py` — unit tests with tmp_path fixtures including symlink + DoS bounds
- [ ] `mise-en-place/tool-detect-brownfield/SKILL.md` — invocation contract; has_codebase_map ≠ complete map documented
- [ ] Extend `validate_spec.py` + `test_validate_spec.py` — brownfield section gates + inverse rule + bullet dedup (SC3)
- [ ] `mise-en-place/tool-scan-map-secrets/scan_map_secrets.py` — fail-closed secret scan (T-03-04)
- [ ] `mise-en-place/map-codebase/SKILL.md` — mapper workflow with scan_map_secrets invocation
- [ ] Extend `spec-phase/SKILL.md` — Step 1.4 + brownfield Q&A + assembly + Continue/stale-map policies
- [ ] `mise-en-place/spec-phase/test_spec_phase_contract.py` — SKILL structure contract tests
- [ ] `mise-en-place/map-codebase/test_map_codebase_contract.py` — map-codebase SKILL contract tests

*Existing pytest infrastructure from Phase 1–2 covers framework setup — no additional install needed.*

---

## Manual UAT — BLOCKING for `/gsd-verify-work`

> Phase verify **cannot pass** until every row in this checklist is complete. Automated pytest + contract tests are necessary but not sufficient for SC2 behavioral proof.

| Behavior | SC | Requirement | Why Manual | Test Instructions |
|----------|-----|-------------|------------|-------------------|
| map-codebase spawns parallel mapper sub-agents | SC1 | PROJ-02 | Requires live Cursor Task tool | Run `/map-codebase` on this repo; verify 7 complete files (>20 lines each) written to `.planning/codebase/`; scan_map_secrets exits 0 |
| spec-phase Step 1.4 triggers mapping before Q&A on brownfield repo | SC1 | PROJ-02 | Agent orchestration + sub-agent spawn | Run `/spec-phase` on this repo; confirm Step 1.4 detection → map → confirm gate → Q&A sequence |
| spec-phase Continue path re-runs Step 1.4 on brownfield repo with existing greenfield SPEC | SC1 | PROJ-02 | Resume branch may bypass detection if not enforced | On brownfield repo with existing greenfield-format SPEC.md, choose Continue; verify Step 1.4 re-runs detection/mapping before Q&A |
| spec-phase Continue path re-maps on brownfield SPEC with stale/partial map | SC1 | PROJ-02 | Stale map policy is workflow-level | On brownfield repo with existing brownfield-format SPEC but outdated codebase_map_commit or partial map (<7 files >20 lines), choose Continue; verify mapping re-runs before Q&A |
| Q&A does not re-ask facts present in codebase map | SC2 | PROJ-03 | Conversational judgment | During brownfield spec-phase, verify agent references all-seven map summaries and focuses on delta |
| SPEC.md separates Already Built vs To Build with no duplicate bullets | SC3 | PROJ-03 | Requires full spec-phase run + validate_spec | Complete brownfield spec-phase; verify two distinct sections; run validate_spec — duplicate bullets must fail |
| Greenfield path unchanged | — | PROJ-01 regression | Requires empty-repo run | Run `/spec-phase` on empty tmp dir; confirm no Step 1.4 mapping step, standard five sections only |
| Invalid detect_brownfield JSON stops workflow | SC1 | PROJ-02 | Error path requires simulated failure | Document expected ERROR behavior when stdout is not valid JSON (Step 1.4 must not proceed to Q&A) |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] SC1/SC2/SC3 traceability column populated for every task
- [ ] T-03-02 mapped to unit tests (03-01-14, 03-01-15)
- [ ] Wave 2 contract tests replace grep-only verification for SKILL structure
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] Manual UAT checklist complete (blocking for phase verify)
- [ ] No watch-mode flags
- [ ] Feedback latency < 12s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
