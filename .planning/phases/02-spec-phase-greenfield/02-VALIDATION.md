---
phase: 2
slug: spec-phase-greenfield
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-05-21
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (established in Phase 1) |
| **Config file** | none — pytest auto-discovers `test_*.py` |
| **Quick run command** | `python3 -m pytest mise-en-place/tool-validate-spec/ -x -q` |
| **Full suite command** | `python3 -m pytest mise-en-place/ -q` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest mise-en-place/tool-validate-spec/ -x -q`
- **After every plan wave:** Run `python3 -m pytest mise-en-place/ -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | SPEC-04 | — | validate_spec exits 1 on draft, 0 on approved | unit | `pytest mise-en-place/tool-validate-spec/test_validate_spec.py::test_approved_spec_exits_zero -x` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | SPEC-04 | — | validate_spec exits 1 on draft SPEC.md | unit | `pytest mise-en-place/tool-validate-spec/test_validate_spec.py::test_draft_spec_exits_one -x` | ❌ W0 | ⬜ pending |
| 02-01-03 | 01 | 1 | SPEC-04 | — | validate_spec exits 1 when SPEC.md missing | unit | `pytest mise-en-place/tool-validate-spec/test_validate_spec.py::test_missing_spec_exits_one -x` | ❌ W0 | ⬜ pending |
| 02-01-04 | 01 | 1 | SPEC-04 | — | validate_spec exits 1 on malformed front-matter | unit | `pytest mise-en-place/tool-validate-spec/test_validate_spec.py::test_malformed_frontmatter_exits_one -x` | ❌ W0 | ⬜ pending |
| 02-01-05 | 01 | 1 | SPEC-02 | — | SPEC.md template contains all five required sections | integration | `pytest mise-en-place/tool-validate-spec/test_validate_spec.py::test_approved_spec_has_required_sections -x` | ❌ W0 | ⬜ pending |
| 02-01-06 | 01 | 1 | SPEC-02 | — | validate_spec exits 1 when approved spec missing a required section header | unit | `pytest mise-en-place/tool-validate-spec/test_validate_spec.py::test_approved_spec_missing_section_exits_one -x` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 2 | SPEC-01/05 | — | SKILL.md has category spine + clean-context instructions | manual | Reviewer confirms Q&A category spine (Problem→Who→Constraints→Success Criteria→Out-of-scope) and no session-state references present | N/A | ⬜ pending |
| 02-02-02 | 02 | 2 | SPEC-03 | — | SKILL.md defines both research trigger modes (agent-suggested + user-requested) | manual | Reviewer confirms D-03a and D-03b trigger patterns present in SKILL.md | N/A | ⬜ pending |
| 02-02-03 | 02 | 2 | SPEC-04 | — | SKILL.md references tool-validate-spec for belt-and-suspenders check | manual | Reviewer confirms D-09 enforcement wording present in SKILL.md | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `mise-en-place/tool-validate-spec/test_validate_spec.py` — stubs/full tests for SPEC-04 (4 unit cases + 2 section-validation cases)
- [ ] `mise-en-place/tool-validate-spec/validate_spec.py` — implementation under test

*Existing pytest infrastructure from Phase 1 covers the framework setup — no additional install needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| spec-phase SKILL.md drives structured Q&A with category spine | SPEC-01, SPEC-05 | Conversational flow is agent-native; cannot be exercised by a unit test | Open `/spec-phase` on an empty repo, verify five categories appear in order (Problem → Who → Constraints → Success Criteria → Out-of-scope) and that no session history is required to start |
| Research sub-tasks spawn and write RESEARCH-<topic>.md | SPEC-03 | Requires live Cursor Task tool and agent context | Trigger a research sub-task (agent-suggested or user-requested), verify `.planning/research/RESEARCH-<topic>.md` is created |
| Approval gate flips status: draft → approved in SPEC.md | SPEC-04 | Requires live agent to run StrReplace after user confirms | Complete Q&A, reach approval prompt, answer "yes", verify SPEC.md status field changes to `approved` |
| Spec-phase detects existing SPEC.md and offers resume/restart/abort | PROJ-01 | Startup path requires agent context | Run `/spec-phase` twice; verify second invocation detects existing spec and prompts for action instead of silently overwriting |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify (Wave 1 tasks are all automated; Wave 2 tasks are manual + documented)
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 5s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
