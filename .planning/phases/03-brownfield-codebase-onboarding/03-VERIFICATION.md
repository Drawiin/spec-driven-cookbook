---
status: human_needed
phase: 03-brownfield-codebase-onboarding
verified: 2026-05-22
score: 18/20
---

# Phase 3 Verification

## Must-Haves (automated)

| Check | Status |
|-------|--------|
| detect_brownfield JSON contract + symlink/DoS tests | pass |
| validate_spec brownfield + inverse + dedup | pass |
| scan_map_secrets fail-closed | pass |
| map-codebase SKILL seven files + scan gate | pass |
| spec-phase Step 1.4 ordering + completeness policy | pass |
| Contract tests (12) | pass |
| Full mise-en-place pytest (53) | pass |
| Phase 1–2 regression | pass |

## Gaps

- Manual UAT checklist in `03-VALIDATION.md` not executed in this session (interactive map-codebase and spec-phase flows).

## Human Verification

1. Run `/map-codebase` on this repo — confirm seven files >20 lines and `scan_map_secrets` exits 0.
2. Run `/spec-phase` on this repo — confirm Step 1.4 detect → map → confirm gate → delta Q&A.
3. Run `/spec-phase` Continue on brownfield repo with stale map — confirm remap before Q&A.
4. Approve brownfield SPEC — `validate_spec.py` rejects duplicate bullets across sections.
