---
phase: 02-spec-phase-greenfield
verified: 2026-05-22T16:00:00Z
status: human_needed
score: 5/5 roadmap success criteria verified (automated)
overrides_applied: 0
human_verification:
  - test: "On an empty repo, invoke spec-phase (mention 'spec-phase' or read mise-en-place/spec-phase/SKILL.md). Confirm five Q&A categories appear in order: Problem → Who it's for → Constraints → Success Criteria → Out-of-scope."
    expected: "Agent opens structured Q&A without requiring prior session history; startup scaffolds .planning/ and creates .planning/research/."
    why_human: "Conversational Q&A flow is agent-native; SKILL.md contract verified but end-to-end behavior requires live agent execution."
  - test: "During Q&A, trigger a research sub-task (say 'research X' or accept an agent-suggested topic)."
    expected: "Sub-agent writes .planning/research/RESEARCH-<topic-slug>.md; findings are incorporated before SPEC.md is finalized."
    why_human: "Requires live Cursor Task tool and sub-agent spawn; file path contract verified in SKILL.md Step 3."
  - test: "Complete Q&A, reach approval prompt ('Approve this spec? yes / edit / abort'), reply 'yes'."
    expected: "SPEC.md front-matter status changes from draft to approved; python3 mise-en-place/tool-validate-spec/validate_spec.py exits 0."
    why_human: "StrReplace approval gate requires live agent + user confirmation; validate_spec.py gate verified independently via pytest and spot-checks."
  - test: "Run spec-phase a second time on a repo that already has SPEC.md."
    expected: "Agent detects existing spec, presents status, and offers continue / start fresh / abort — does not silently overwrite."
    why_human: "Resume/restart UX is agent-conversational; Step 1 contract verified in SKILL.md but behavior needs live run."
---

# Phase 2: Spec Phase — Greenfield — Verification Report

**Phase Goal:** Developer can spec any new project from scratch by running one command, working through a structured deep-questioning flow, optionally triggering research sub-tasks, and landing an explicitly approved spec file — the entire flow running on a clean context with only local files.

**Verified:** 2026-05-22T16:00:00Z  
**Status:** HUMAN_NEEDED  
**Re-verification:** No — fresh adversarial pass (prior report had no `gaps:` frontmatter; prior `passed` not trusted)

**MVP mode note:** Phase is marked `mode: mvp` in ROADMAP.md but the goal is not in user-story format (`As a …, I want …, so that ….`). User Flow Coverage below is derived from the goal intent. Consider running `/gsd mvp-phase 2` to reformat the goal for future MVP-mode UAT scripts.

---

## User Flow Coverage

**Derived flow from phase goal** (not a formal user story):

| Step | Expected | Evidence | Status |
|------|----------|----------|--------|
| Invoke spec-phase on empty repo | Structured Q&A begins; no prior session required | `spec-phase/SKILL.md` Step 1 (scaffold + mkdir research) + Step 2 (five-category spine) | ✓ contract |
| Answer Q&A across five categories | Problem, Who it's for, Constraints, Success Criteria, Out-of-scope covered in order | Step 2 lines 67–78 | ✓ contract |
| Optional research | User or agent triggers research; output to `.planning/research/RESEARCH-<slug>.md` | Step 3 lines 82–107; portable path (no `phases/02-*` refs) | ✓ contract |
| Spec assembly | `.planning/SPEC.md` written with YAML front-matter + five canonical sections | Step 4 lines 109–141; headers match `validate_spec.py` `REQUIRED_SECTIONS` | ✓ contract |
| Approval gate | User approves; status patched draft → approved | Step 5 lines 143–151; StrReplace on `status: draft` | ✓ contract |
| Planning gate | Unapproved spec blocks planning via exit code 1 | `validate_spec.py` + 6 pytest functions; spot-checks confirm exit 0/1 | ✓ verified |
| Outcome | Developer lands approved SPEC.md from clean context | Automated tooling + SKILL contract complete; **live agent walk-through pending** | ? human |

---

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| SC-1 | `/spec-phase` on empty repo delivers structured Q&A (what, why, constraints, success criteria) | ✓ VERIFIED | `spec-phase/SKILL.md` Step 2: five categories in order; Problem probes what/why; 153-line substantive workflow skill |
| SC-2 | Q&A produces persisted `SPEC.md` in durable format | ✓ VERIFIED | Step 4 template: YAML front-matter (`status`, `version`, `date`) + five `##` sections; Write tool to `.planning/SPEC.md` |
| SC-3 | Research sub-tasks gather domain knowledge; spec not finalized until incorporated | ✓ VERIFIED | Step 3: inline + end-of-Q&A triggers; Task tool spawns `generalPurpose` sub-agent; "All are read before the spec is finalized" (line 107); Step 4 merges findings |
| SC-4 | Explicit approval gate — planning blocked until spec approved | ✓ VERIFIED | Step 5 approval gate with yes/edit/abort; `validate_spec.py` exits 1 on draft/missing/malformed/missing-section (6/6 pytest pass); `tool-validate-spec/SKILL.md` documents gate before `/plan-phase` |
| SC-5 | Invocable with no prior session history; reads/writes local files only | ✓ VERIFIED | Step 1: "no session history is assumed"; scaffold + local file reads only; `grep` confirms 0 hardcoded `phases/02-spec-phase-greenfield` paths in spec-phase SKILL |

**Score:** 5/5 roadmap success criteria verified at artifact/tooling level

### Plan Must-Haves Detail

#### Plan 02-01 — tool-validate-spec (6/6 truths)

| Truth | Status | Evidence |
|-------|--------|----------|
| Approved spec exits 0 | ✓ VERIFIED | `test_approved_spec_exits_zero` + spot-check on temp approved SPEC.md |
| Draft spec exits 1 with stderr | ✓ VERIFIED | `test_draft_spec_exits_one` + spot-check: "must be 'approved'" |
| Missing spec exits 1 | ✓ VERIFIED | `test_missing_spec_exits_one` + spot-check: "not found" |
| Malformed front-matter exits 1 | ✓ VERIFIED | `test_malformed_frontmatter_exits_one` |
| Missing section exits 1 | ✓ VERIFIED | `test_approved_spec_missing_section_exits_one` |
| pytest 6/6 pass | ✓ VERIFIED | `python3 -m pytest mise-en-place/tool-validate-spec/ -x -q` → 6 passed |

#### Plan 02-02 — SKILL contracts + README (8/8 truths)

| Truth | Status | Evidence |
|-------|--------|----------|
| Five Q&A categories in order | ✓ VERIFIED | spec-phase/SKILL.md Step 2 |
| SPEC.md with front-matter + canonical sections | ✓ VERIFIED | Step 4 template; headers match `REQUIRED_SECTIONS` exactly |
| Research inline or end-of-Q&A → RESEARCH file | ✓ VERIFIED | Step 3; `.planning/research/RESEARCH-<topic-slug>.md` |
| Approval gate yes → StrReplace draft→approved | ✓ VERIFIED | Step 5 line 149 |
| validate_spec exits 0 only after approval + sections | ✓ VERIFIED | pytest + spot-checks |
| Zero prior session history | ✓ VERIFIED | Step 1 line 38 |
| Works when `.planning/` absent — scaffolds + research/ | ✓ VERIFIED | Step 1 scaffold command + `mkdir -p .planning/research`; scaffold spot-check on empty tmp dir |
| README documents both tools | ✓ VERIFIED | `### tool-validate-spec`, `### spec-phase` with invocation one-liners |

---

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | ----------- | ------ | ------- |
| `mise-en-place/tool-validate-spec/validate_spec.py` | Stdlib approval + section validator | ✓ VERIFIED | 108 lines; `REQUIRED_SECTIONS`, `SPEC_CANDIDATES`, `parse_frontmatter` |
| `mise-en-place/tool-validate-spec/test_validate_spec.py` | 6 pytest exit-code tests | ✓ VERIFIED | 118 lines; all 6 functions present and passing |
| `mise-en-place/tool-validate-spec/SKILL.md` | Agent invocation contract | ✓ VERIFIED | 72 lines; documents exit codes, headers, validate_spec.py command |
| `mise-en-place/spec-phase/SKILL.md` | Full five-step workflow | ✓ VERIFIED | 153 lines; Steps 1–5 complete with cursor_skill_adapter |
| `mise-en-place/README.md` | Tool catalog with Phase 2 entries | ✓ VERIFIED | Documents tool-validate-spec + spec-phase |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| spec-phase/SKILL.md Step 1 | planning_scaffold.py | `python3 … planning_scaffold.py scaffold` | ✓ WIRED | Pattern found line 43 |
| spec-phase/SKILL.md Step 1 | .planning/research/ | `mkdir -p .planning/research` | ✓ WIRED | Lines 50–51; scaffold confirmed does NOT create research/ |
| spec-phase/SKILL.md Step 4 | validate_spec.py REQUIRED_SECTIONS | Exact `## Who It's For` etc. | ✓ WIRED | Lines 128–136 match validator lines 23–28 |
| spec-phase/SKILL.md Step 5 | .planning/SPEC.md | StrReplace status draft→approved | ✓ WIRED | Line 149 |
| spec-phase/SKILL.md Step 3 | RESEARCH-<slug>.md | Task tool generalPurpose | ✓ WIRED | Lines 91–97 |
| tool-validate-spec/SKILL.md | validate_spec.py | Shell invocation | ✓ WIRED | Line 38 |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| validate_spec.py | `status` from front-matter | Reads `.planning/SPEC.md` from disk | Yes — parses YAML block, checks `approved` | ✓ FLOWING |
| validate_spec.py | Section headers | Full file text scan | Yes — substring match against REQUIRED_SECTIONS | ✓ FLOWING |
| spec-phase/SKILL.md | Q&A answers → SPEC.md | Agent Write tool (documented) | N/A — agent workflow; not programmatically executable | ? human |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Approved spec exits 0 | Temp dir with approved SPEC.md → validate_spec.py | `✓ SPEC.md approved …` exit=0 | ✓ PASS |
| Missing spec exits 1 | Empty temp dir → validate_spec.py | `ERROR: SPEC.md not found…` exit=1 | ✓ PASS |
| Draft spec exits 1 | Temp dir with draft SPEC.md → validate_spec.py | `must be 'approved'` exit=1 | ✓ PASS |
| Scaffold on empty repo | `planning_scaffold.py scaffold` in tmp dir | Creates `.planning/`, phases/, codebase/ | ✓ PASS |
| Full test suite | `python3 -m pytest mise-en-place/ -q` | 22 passed in 0.37s | ✓ PASS |

### Probe Execution

Step 7c: SKIPPED — no `scripts/*/tests/probe-*.sh` files exist; phase does not declare probe scripts.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| SPEC-01 | 02-02 | Structured deep-questioning flow | ✓ SATISFIED | spec-phase Step 2 five-category spine |
| SPEC-02 | 02-01, 02-02 | Persisted spec file with required sections | ✓ SATISFIED | Step 4 template + validate_spec section enforcement |
| SPEC-03 | 02-02 | Research sub-tasks before locking requirements | ✓ SATISFIED | Step 3 dual triggers + incorporation before finalize |
| SPEC-04 | 02-01, 02-02 | Explicit user approval before planning | ✓ SATISFIED | Step 5 gate + validate_spec.py exit-code contract |
| SPEC-05 | 02-02 | Clean context, local files only | ✓ SATISFIED | Step 1 startup contract |
| PROJ-01 | 02-02 | Works on empty repos | ✓ SATISFIED | Step 1 scaffold + research mkdir on absent `.planning/` |

No orphaned requirements — all six Phase 2 requirements appear in plan frontmatter.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| test_validate_spec.py | 23 | "Placeholder content." | ℹ️ Info | Test fixture only — not user-visible stub |
| mise-en-place/README.md | 41 | "details printed to stdout" | ℹ️ Info | Minor doc inaccuracy — validate_spec prints errors to stderr; not blocking |

No TBD/FIXME/XXX debt markers in phase-modified files.

### Human Verification Required

### 1. Structured Q&A on empty repo

**Test:** Invoke spec-phase on an empty repo; confirm five categories in order without prior session history.  
**Expected:** Agent scaffolds `.planning/` + `.planning/research/` and opens Q&A spine.  
**Why human:** Conversational flow cannot be exercised by unit tests.

### 2. Research sub-task spawn and incorporation

**Test:** Trigger research during Q&A; verify RESEARCH file created and merged into final SPEC.md.  
**Expected:** `.planning/research/RESEARCH-<topic-slug>.md` exists; spec reflects findings.  
**Why human:** Requires live Task tool sub-agent spawn.

### 3. Approval gate flips status

**Test:** Complete Q&A, reply "yes" at approval prompt.  
**Expected:** SPEC.md `status: approved`; validate_spec.py exits 0.  
**Why human:** StrReplace requires live agent after user confirmation (validator gate verified separately).

### 4. Existing spec resume/restart/abort

**Test:** Run spec-phase twice on repo with existing SPEC.md.  
**Expected:** Agent offers continue / start fresh / abort — no silent overwrite.  
**Why human:** Startup UX is agent-conversational.

### Deferred Items (informational)

| Item | Addressed In | Evidence |
|------|-------------|----------|
| plan-phase skill calls validate_spec.py before proceeding | Phase 4 | Phase 4 SC-1: "Developer can run `/plan-phase` against an approved spec"; D-09 belt-and-suspenders enforcement deferred to plan-phase implementation |

Phase 2 delivers the gate tool and documents the contract; plan-phase wiring is explicitly Phase 4 scope.

---

## Gaps Summary

No automated gaps found. All roadmap success criteria, plan must-haves, artifacts, and key links verified in the codebase. Status is `human_needed` because the primary deliverable is an agent workflow skill — four end-to-end conversational behaviors documented in `02-VALIDATION.md` require live human/agent verification before the phase can be considered fully validated in production use.

---

_Verified: 2026-05-22T16:00:00Z_  
_Verifier: Claude (gsd-verifier)_
