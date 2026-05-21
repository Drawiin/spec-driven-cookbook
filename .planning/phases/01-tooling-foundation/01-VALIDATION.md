---
phase: 1
slug: tooling-foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-21
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (Wave 0 installs) |
| **Config file** | none — Wave 0 creates `pytest.ini` |
| **Quick run command** | `python3 -m pytest tests/ -x -q` |
| **Full suite command** | `python3 -m pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest tests/ -x -q`
- **After every plan wave:** Run `python3 -m pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-env-check | TBD | 1 | TOOL-04 | — | N/A | unit | `python3 -m pytest tests/test_env_check.py -x -q` | ❌ W0 | ⬜ pending |
| 01-context-builder | TBD | 1 | TOOL-02 | — | N/A | unit | `python3 -m pytest tests/test_context_builder.py -x -q` | ❌ W0 | ⬜ pending |
| 01-planning-scaffold | TBD | 1 | TOOL-01 | — | N/A | unit | `python3 -m pytest tests/test_planning_scaffold.py -x -q` | ❌ W0 | ⬜ pending |
| 01-skill-bundling | TBD | 1 | TOOL-05 | — | N/A | smoke | `python3 -c "import pathlib; assert pathlib.Path('mise-en-place/tool-env-check/SKILL.md').exists()"` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_env_check.py` — stubs for TOOL-04 (env check outputs pass/fail for git, python3, cursor)
- [ ] `tests/test_context_builder.py` — stubs for TOOL-02 (context builder produces valid markdown with required sections)
- [ ] `tests/test_planning_scaffold.py` — stubs for TOOL-01 (scaffold creates .planning/ idempotently)
- [ ] `tests/conftest.py` — shared fixtures (temp directories, mock project roots)
- [ ] `pip install pytest` — test framework not yet installed

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| context-builder output is pasteable into agent prompt without editing | TOOL-02 | Requires human judgment on prompt quality | Run `python3 mise-en-place/tool-context-builder/context_builder.py` in a real project and verify sections are well-formatted |
| environment-check completes in under 5 seconds | TOOL-04 | Wall-clock timing, not unit-testable | Run `time python3 mise-en-place/tool-env-check/env_check.py` and verify elapsed < 5s |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
