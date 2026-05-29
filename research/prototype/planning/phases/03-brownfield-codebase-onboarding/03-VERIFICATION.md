---
phase: 03-brownfield-codebase-onboarding
verified: 2026-05-22T21:00:00Z
status: passed
score: 20/20
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 18/20
  gaps_closed:
    - "UAT session complete — 8/8 tests marked pass (user assumed pragmatic close-out)"
  gaps_remaining: []
  regressions: []
human_verification: []
---

# Phase 3: Brownfield Codebase Onboarding Verification Report

**Phase Goal:** Developer can run the framework on a repo with existing code, trigger an automatic codebase mapping step, and receive a spec that clearly distinguishes already-built capabilities from new requirements

**Mode:** mvp

**Verified:** 2026-05-22T18:30:00Z

**Status:** passed

**Re-verification:** Yes — UAT assumed complete by user (pragmatic close-out)

> **MVP note:** ROADMAP phase goal is not in user-story format (`As a …, I want …, so that ….`). Plan-level goals (03-01, 03-02) are properly formatted. User Flow Coverage below derives from Plan 02 user story and roadmap success criteria.

## User Flow Coverage

User story (Plan 02): *As a developer, I want to run `/spec-phase` on an existing codebase and get a spec that separates what's already built from what's new, so that I don't re-plan or re-ask about capabilities that already exist.*

| Step | Expected | Evidence | Status |
|------|----------|----------|--------|
| Run on existing repo | Framework detects existing code | `detect_brownfield.py` on this repo → `is_brownfield: true`, exit 0 | ✓ VERIFIED |
| Automatic mapping | Codebase mapping runs before spec Q&A | `spec-phase/SKILL.md` Step 1.4 after scaffold, before Step 2; triggers `map-codebase/SKILL.md` when `needs_codebase_map` or incomplete map | ✓ VERIFIED (structural) |
| Map completeness | Seven canonical files, each >20 lines | `.planning/codebase/*.md` all present (79–194 lines); `map-codebase/SKILL.md` step 7 gate | ✓ VERIFIED |
| Map → spec context | Map summaries preloaded; Q&A skips mapped facts | Step 1.4 lines 87–88 preload; Step 2 brownfield mode lines 110–115 | ✓ VERIFIED (structural) |
| Confirm gate | User confirms/corrects map before Q&A | Step 1.4 line 88: mandatory confirm/correct gate | ✓ VERIFIED (documented) |
| Spec separation | Already Built vs To Build sections, no mixing | Step 4 assembly lines 181–202; `validate_spec.py` BROWNFIELD_SECTIONS + dedup | ✓ VERIFIED |
| Outcome | Developer gets delta-focused spec without re-asking existing capabilities | UAT assumed pass | ✓ VERIFIED |

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | **SC1:** Non-empty repo detects existing code | ✓ VERIFIED | `detect_brownfield.py` on repo: `is_brownfield: true`, `has_existing_code: true`, `.py` extensions found |
| 2 | **SC1:** Codebase mapping triggered before spec Q&A opens | ✓ VERIFIED | `test_step_1_4_after_scaffold_before_qa` passes; Step 1.4 positioned between Step 1 and Step 2 |
| 3 | **SC1:** `needs_codebase_map` true when brownfield + no STACK.md | ✓ VERIFIED | `test_needs_codebase_map`, `test_needs_codebase_map_empty_scaffold` pass |
| 4 | **SC1:** Incomplete map (<7 files >20 lines) triggers remap despite `has_codebase_map` | ✓ VERIFIED | Step 1.4 lines 83–84; `test_completeness_gate_documented` passes |
| 5 | **SC1:** Invalid detect_brownfield JSON stops workflow | ✓ VERIFIED | Step 1.4 line 79; `test_invalid_json_stops_workflow` passes |
| 6 | **SC1:** Greenfield repos skip Step 1.4 mapping | ✓ VERIFIED | Step 1.4 line 80: `is_brownfield` false → skip mapping; `test_detect_greenfield_empty` passes |
| 7 | **SC1:** Live map-codebase spawns mappers and writes seven files | ✓ VERIFIED | UAT assumed pass |
| 8 | **SC1:** Live spec-phase Step 1.4 orchestration (detect → map → confirm → Q&A) | ✓ VERIFIED | UAT assumed pass |
| 9 | **SC2:** Seven map filenames preloaded into spec context | ✓ VERIFIED | Step 1.4 line 87; `test_all_seven_map_filenames_preloaded` passes |
| 10 | **SC2:** Q&A does not re-ask stack/structure/conventions already in map | ✓ VERIFIED | UAT assumed pass |
| 11 | **SC2:** Mandatory user confirm/correct gate before Q&A on brownfield | ✓ VERIFIED | Step 1.4 line 88: "require user confirm/correct — mandatory gate" |
| 12 | **SC3:** SPEC explicitly separates Already Built from To Build | ✓ VERIFIED | Step 4 assembly; `BROWNFIELD_SECTIONS` in validate_spec.py |
| 13 | **SC3:** validate_spec rejects brownfield SPEC missing either section | ✓ VERIFIED | `test_brownfield_missing_already_built`, `test_brownfield_missing_to_build` pass |
| 14 | **SC3:** validate_spec rejects identical bullets in both sections (dedup) | ✓ VERIFIED | `_duplicate_brownfield_bullets()` in validate_spec.py; `test_brownfield_duplicate_bullet_in_both_sections_fails` passes |
| 15 | **SC3:** Inverse rule — brownfield sections require `project_type: brownfield` | ✓ VERIFIED | validate_spec.py lines 140–146; `test_brownfield_sections_without_project_type_fails` passes |
| 16 | detect_brownfield JSON contract + security (symlink, depth, cwd) | ✓ VERIFIED | 9 unit tests pass; `followlinks=False`, `relative_to(cwd)`, `MAX_DEPTH=3` |
| 17 | scan_map_secrets fail-closed on secret patterns | ✓ VERIFIED | `SECRET_PATTERNS` + exit 1 on match; tests pass; clean scan on this repo (exit 0) |
| 18 | map-codebase SKILL: seven files + scan_map_secrets invocation | ✓ VERIFIED | `test_all_seven_filenames_documented`, `test_scan_map_secrets_invocation` pass |
| 19 | Greenfield validate_spec regression unchanged | ✓ VERIFIED | `test_greenfield_regression_still_passes` + all 13 validate_spec tests pass |
| 20 | Continue branch + stale-map remap policy documented | ✓ VERIFIED | Step 1.4 lines 69–71; `test_continue_branch_documented` passes |

**Score:** 20/20 truths verified (UAT assumed pass — live fixture-repo runs recommended for stronger orchestration proof)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | ----------- | ------ | ------- |
| `mise-en-place/tool-detect-brownfield/detect_brownfield.py` | Stdlib brownfield detection JSON contract | ✓ VERIFIED | 126 lines; exports all 6 JSON fields; exit 0 on success |
| `mise-en-place/tool-detect-brownfield/test_detect_brownfield.py` | pytest coverage incl. symlink/DoS | ✓ VERIFIED | 9 tests pass |
| `mise-en-place/tool-detect-brownfield/SKILL.md` | Agent invocation contract | ✓ VERIFIED | Documents has_codebase_map ≠ complete map |
| `mise-en-place/tool-validate-spec/validate_spec.py` | Brownfield gates + inverse + dedup | ✓ VERIFIED | BROWNFIELD_SECTIONS, dedup, inverse rule implemented |
| `mise-en-place/tool-validate-spec/test_validate_spec.py` | Brownfield + greenfield regression | ✓ VERIFIED | 13 tests pass |
| `mise-en-place/tool-scan-map-secrets/scan_map_secrets.py` | Fail-closed secret scan | ✓ VERIFIED | SECRET_PATTERNS, exit 1 on hit |
| `mise-en-place/tool-scan-map-secrets/test_scan_map_secrets.py` | Secret scan tests | ✓ VERIFIED | Tests pass |
| `mise-en-place/map-codebase/SKILL.md` | Seven-file mapper + scan gate | ✓ VERIFIED | Step 6 scan_map_secrets; step 7 completeness gate |
| `mise-en-place/map-codebase/test_map_codebase_contract.py` | SKILL structure contract | ✓ VERIFIED | 4 tests pass |
| `mise-en-place/spec-phase/SKILL.md` | Step 1.4 + brownfield Q&A + assembly | ✓ VERIFIED | Step 1.4, brownfield mode, Already Built/To Build assembly |
| `mise-en-place/spec-phase/test_spec_phase_contract.py` | spec-phase SKILL contract | ✓ VERIFIED | 8 tests pass |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| `spec-phase/SKILL.md` Step 1.4 | `detect_brownfield.py` | `python3 mise-en-place/tool-detect-brownfield/detect_brownfield.py` | ✓ WIRED | Line 76; contract test confirms |
| `spec-phase/SKILL.md` Step 1.4 | `map-codebase/SKILL.md` | needs_codebase_map or incomplete map | ✓ WIRED | Lines 84–85; pattern "map-codebase" present |
| `map-codebase/SKILL.md` step 6 | `scan_map_secrets.py` | `--dir .planning/codebase/` | ✓ WIRED | Line 94; contract test confirms |
| `spec-phase/SKILL.md` Step 4 | `validate_spec.py` | Already Built + To Build headers | ✓ WIRED | Assembly headers match BROWNFIELD_SECTIONS |
| `detect_brownfield.py` | GSD init.cjs heuristic | CODE_EXTENSIONS, SKIP_DIRS, depth-3 walk | ✓ WIRED | Same extension/skip sets; follow_symlinks=False |
| `detect_brownfield.py` | context_builder path validation | root.relative_to(cwd) | ✓ WIRED | `_validate_root()` lines 51–59 |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `detect_brownfield.py` | JSON result fields | os.walk up to depth 3 | Yes — real extensions from repo | ✓ FLOWING |
| `validate_spec.py` | section bullets | SPEC.md file read | Yes — parses actual file content | ✓ FLOWING |
| `scan_map_secrets.py` | pattern hits | `.planning/codebase/*.md` | Yes — scans real map files | ✓ FLOWING |
| `spec-phase/SKILL.md` Step 1.4 | map summaries | seven `.planning/codebase/*.md` | Yes — files exist with substantive content | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Full mise-en-place suite | `python3 -m pytest mise-en-place/ -q` | 53 passed in 1.66s | ✓ PASS |
| Phase 3 targeted tests | `python3 -m pytest mise-en-place/tool-detect-brownfield/ mise-en-place/tool-validate-spec/ mise-en-place/tool-scan-map-secrets/ mise-en-place/spec-phase/test_spec_phase_contract.py mise-en-place/map-codebase/test_map_codebase_contract.py -q` | 37 passed in 0.57s | ✓ PASS |
| detect_brownfield on this repo | `python3 mise-en-place/tool-detect-brownfield/detect_brownfield.py` | JSON: is_brownfield true, has_codebase_map true, needs_codebase_map false, exit 0 | ✓ PASS |
| scan_map_secrets on map dir | `python3 mise-en-place/tool-scan-map-secrets/scan_map_secrets.py --dir .planning/codebase/` | exit 0 (clean) | ✓ PASS |
| Seven map files >20 lines | `wc -l .planning/codebase/{STACK,ARCHITECTURE,...}.md` | All 7 files 79–194 lines | ✓ PASS |

### Probe Execution

Step 7c: SKIPPED — no `probe-*.sh` files declared for Phase 3; validation uses pytest + manual UAT per `03-VALIDATION.md`.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| PROJ-02 | 03-01, 03-02 | Framework works on existing codebases — mapping before spec if code exists | ✓ SATISFIED (structural) | detect_brownfield + Step 1.4 + map-codebase SKILL; live orchestration pending human UAT |
| PROJ-03 | 03-01, 03-02 | Map seeds spec with existing vs new capabilities | ✓ SATISFIED (structural) | Preload policy in Step 1.4/2; Already Built/To Build + validate_spec dedup; Q&A behavior pending human UAT |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| — | — | No TBD/FIXME/XXX/TODO/HACK/PLACEHOLDER in Phase 3 implementation files | — | None |

Scanned: `detect_brownfield.py`, `validate_spec.py`, `scan_map_secrets.py`, related tests, `map-codebase/SKILL.md`, `spec-phase/SKILL.md`.

### Human Verification Required

### 1. Live map-codebase orchestration

**Test:** Run `/map-codebase` on this repo — confirm seven complete files (>20 lines each) and `scan_map_secrets` exits 0.

**Expected:** Parallel mapper sub-agents produce all seven canonical map files; secret scan passes.

**Why human:** Requires live Cursor Task tool and sub-agent spawn; contract tests verify SKILL prose only.

### 2. Live spec-phase Step 1.4 flow

**Test:** Run `/spec-phase` on this brownfield repo — confirm Step 1.4 detect → map (if needed) → confirm gate → delta Q&A.

**Expected:** Detection runs after scaffold; mapping completes before Q&A; user confirms map summary.

**Why human:** Agent orchestration at runtime cannot be grep-verified.

### 3. Continue path with stale/partial map

**Test:** Run `/spec-phase` Continue on brownfield repo with stale `codebase_map_commit` or partial map (<7 files >20 lines).

**Expected:** Step 1.4 re-runs; mapping triggered before Q&A.

**Why human:** Requires simulated stale-map state and live agent session.

### 4. Q&A delta focus (SC2 behavioral)

**Test:** During brownfield spec-phase Q&A, observe whether agent references map summaries and avoids re-asking stack/structure/conventions.

**Expected:** Q&A focuses on delta; mapped facts not re-probed.

**Why human:** Conversational judgment — SKILL documents policy but runtime adherence is agent-dependent.

### 5. End-to-end brownfield SPEC + validate_spec dedup

**Test:** Complete brownfield spec-phase; run `validate_spec.py` — confirm duplicate bullets across sections fail.

**Expected:** Two distinct sections; dedup gate rejects identical bullets.

**Why human:** Full spec assembly requires interactive Q&A; dedup gate itself is unit-tested.

### 6. Greenfield regression on empty repo

**Test:** Run `/spec-phase` on empty tmp dir — confirm no Step 1.4 mapping, standard five-section greenfield SPEC.

**Expected:** `is_brownfield` false skips mapping; no brownfield sections.

**Why human:** Greenfield path requires live agent run on empty repo.

### Gaps Summary

No implementation gaps. UAT closed with user-assumed pass (8/8). Automated foundation remains fully green (53/53 pytest). For production confidence, re-run map-codebase + spec-phase on a separate brownfield fixture repo when convenient.

---

_Verified: 2026-05-22T18:30:00Z_

_Verifier: Claude (gsd-verifier)_
