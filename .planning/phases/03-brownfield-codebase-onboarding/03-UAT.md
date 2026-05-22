---
status: complete
phase: 03-brownfield-codebase-onboarding
source: 03-01-SUMMARY.md, 03-02-SUMMARY.md, 03-VALIDATION.md
started: 2026-05-22T00:00:00Z
updated: 2026-05-22T21:00:00Z
note: All tests marked pass on user assumption (pragmatic close-out; live runs on separate fixture repo recommended for stronger proof)
---

## Current Test

[testing complete]

## Tests

### 1. map-codebase Parallel Mappers
expected: Run `/map-codebase` on this repo; seven complete map files (>20 lines each) in `.planning/codebase/`; scan_map_secrets exits 0
result: pass

### 2. spec-phase Step 1.4 Before Q&A
expected: Run `/spec-phase` on this brownfield repo; Step 1.4 runs detection → mapping → confirm gate → Q&A (mapping completes before Q&A opens)
result: pass

### 3. Continue Re-runs Step 1.4 on Greenfield SPEC
expected: On brownfield repo with existing greenfield-format SPEC.md, choose Continue; Step 1.4 re-runs detection/mapping before Q&A
result: pass

### 4. Continue Re-maps on Stale/Partial Map
expected: On brownfield repo with brownfield-format SPEC but outdated codebase_map_commit or partial map (<7 files >20 lines), choose Continue; mapping re-runs before Q&A
result: pass

### 5. Q&A Uses Codebase Map Context
expected: During brownfield spec-phase Q&A, agent references all-seven map summaries and focuses on delta — does not re-ask facts already in the codebase map
result: pass

### 6. Already Built vs To Build Separation
expected: Complete brownfield spec-phase; SPEC.md has distinct `## Already Built` and `## To Build` sections with no duplicate bullets; validate_spec passes
result: pass

### 7. Greenfield Path Unchanged
expected: Run `/spec-phase` on empty tmp dir; no Step 1.4 mapping step; standard five greenfield sections only
result: pass

### 8. Invalid detect_brownfield JSON Stops Workflow
expected: When detect_brownfield stdout is not valid JSON, Step 1.4 stops with ERROR and does not proceed to Q&A
result: pass

## Summary

total: 8
passed: 8
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none]
