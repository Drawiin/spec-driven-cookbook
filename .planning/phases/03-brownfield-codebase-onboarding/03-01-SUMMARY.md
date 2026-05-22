---
phase: 03-brownfield-codebase-onboarding
plan: 01
subsystem: testing
tags: [python, pytest, brownfield, stdlib]

requires:
  - phase: 02-spec-phase-greenfield
    provides: validate_spec.py base and pytest patterns
provides:
  - detect_brownfield.py JSON detection contract
  - validate_spec brownfield gates + dedup
  - scan_map_secrets fail-closed gate
affects: [spec-phase, map-codebase, tool-validate-spec]

tech-stack:
  added: []
  patterns:
    - "relative_to(cwd) + follow_symlinks=False for safe walks"
    - "STACK.md file existence vs seven-file completeness (documented in SKILL)"

key-files:
  created:
    - mise-en-place/tool-detect-brownfield/detect_brownfield.py
    - mise-en-place/tool-detect-brownfield/test_detect_brownfield.py
    - mise-en-place/tool-detect-brownfield/SKILL.md
    - mise-en-place/tool-scan-map-secrets/scan_map_secrets.py
    - mise-en-place/tool-scan-map-secrets/test_scan_map_secrets.py
  modified:
    - mise-en-place/tool-validate-spec/validate_spec.py
    - mise-en-place/tool-validate-spec/test_validate_spec.py
    - mise-en-place/README.md

key-decisions:
  - "has_codebase_map uses STACK.md file only; completeness enforced in workflows"
  - "Bullet dedup normalizes case and list markers before intersection"

patterns-established:
  - "Subprocess pytest fixtures for new stdlib CLI tools"

requirements-completed: [PROJ-02, PROJ-03]

duration: 25min
completed: 2026-05-22
---

# Phase 3 Plan 01 Summary

**Brownfield detection JSON, validate_spec section gates with dedup, and fail-closed secret scan for codebase maps**

## Performance

- **Duration:** ~25 min
- **Tasks:** 3 (RED, GREEN, docs)
- **Files modified:** 8

## Accomplishments

- `detect_brownfield.py` ports GSD init depth-3 walk with symlink/DoS bounds
- `validate_spec.py` enforces brownfield sections, inverse rule, and SC3 bullet dedup
- `scan_map_secrets.py` fail-closed regex gate for `.planning/codebase/*.md`
- 25 new pytest cases; full `mise-en-place/` suite 41 tests green at plan end

## Self-Check: PASSED

- `python3 -m pytest mise-en-place/tool-detect-brownfield/ mise-en-place/tool-validate-spec/ mise-en-place/tool-scan-map-secrets/ -x -q` → pass
- `python3 mise-en-place/tool-detect-brownfield/detect_brownfield.py` → JSON with `is_brownfield: true` on this repo
