---
phase: 3
reviewers: [reviewer-a-general, reviewer-b-security, reviewer-c-requirements]
reviewed_at: 2026-05-22T12:00:00Z
plans_reviewed: [03-01-PLAN.md, 03-02-PLAN.md]
cli_availability:
  gemini: missing
  claude: missing
  codex: missing
  coderabbit: missing
  opencode: missing
  qwen: missing
  cursor: available
  ollama: missing
  lm_studio: missing
  llama_cpp: missing
note: "No external AI CLIs available except cursor (skipped for independence). Three independent subagent reviewers conducted this review. Plans reflect post-review revisions — prior HIGH items (inverse rule, Step 1.4 naming, detection tests, all-seven preload, scan_for_secrets, Continue path, blocking UAT) appear addressed."
---

# Cross-AI Plan Review — Phase 3

## Reviewer A (General) Review

### Plan 03-01 — Wave 1

**Summary:** Wave 1 delivers a testable foundation: stdlib `detect_brownfield.py` with JSON contract aligned to GSD `init.cjs`, and `validate_spec.py` extensions for brownfield sections plus explicit inverse rule. TDD RED→GREEN, threat model, and wave ordering are well specified. Covers the deterministic half of PROJ-02/PROJ-03; end-to-end onboarding depends on Wave 2 and manual UAT.

**Strengths:**
- Clear TDD sequence with named tests mapped in 03-VALIDATION.md
- Scaffold-then-detect gap closed: `has_codebase_map` requires `STACK.md` as a file
- Inverse validate_spec rule is first-class with dedicated test
- Detection edge cases in scope: empty scaffold, STACK present, package-only, path outside cwd
- Greenfield regression preserved; security patterns match Phase 1–2

**Concerns:**

| Severity | Concern |
|----------|---------|
| MEDIUM | `has_codebase_map` vs workflow completeness mismatch — any `STACK.md` file satisfies detection; stub can set `needs_codebase_map: false` at tool layer |
| MEDIUM | Header substring matching for brownfield sections remains spoofable |
| LOW | `project_type` typo fail-open when no brownfield headers present |
| LOW | `code_extensions_found` unused in Wave 2 |
| LOW | Depth-3 walk can miss deeply nested code |

**Risk Assessment:** **LOW** — Familiar tool patterns, strong pytest coverage.

---

### Plan 03-02 — Wave 2

**Summary:** Wave 2 delivers the user-visible slice with Step 1.4 after scaffold on every Step 1 branch, mandatory map confirmation, all-seven preload, delta Q&A, and brownfield SPEC assembly. PROJ-02/PROJ-03 achievable if agents follow SKILL instructions; automated proof remains grep + blocking manual UAT.

**Strengths:**
- Step 1.4 placement and naming explicit; Step 0 forbidden in acceptance criteria
- Continue path coverage for greenfield-format SPEC on brownfield repo
- All-seven map preload; partial/stub map policy with completeness gate
- `scan_for_secrets` ported with deny-list and context_builder redaction
- Invalid JSON handling documented; embedded template outlines; blocking manual UAT

**Concerns:**

| Severity | Concern |
|----------|---------|
| HIGH | PROJ-03 "no mixing" is honor-system only — no validator dedup |
| MEDIUM | Wave 2 verification is grep-based — cannot prove agent behavior |
| MEDIUM | Detection vs map completeness split can confuse execution |
| MEDIUM | Continue with existing brownfield SPEC may skip remapping without explicit policy |
| MEDIUM | Invalid JSON UAT is document-only, not runnable negative test |
| LOW | `--fast` single-agent mode discretionary |

**Risk Assessment:** **MEDIUM** — Correct architecture; residual risk is agent adherence and PROJ-03 semantic quality.

---

## Reviewer B (Security) Review

**Summary:** Materially improved security posture: Wave 1 encodes deterministic controls with pytest coverage; Wave 2 adds defense-in-depth for mapping. Remaining risk concentrates in prompt-only enforcement for mapper secret handling and map integrity, untested symlink escape, and detection/completeness split where stub `STACK.md` satisfies `has_codebase_map`.

**Strengths:**
- Inverse validate_spec rule explicit and tested (03-01-06 through 03-01-08)
- `follow_symlinks=False` and `relative_to(cwd)` in Plan 03-01
- DoS bounds documented (max_depth=3, SKIP_DIRS)
- Secret controls ported: deny-read list, scan_for_secrets, context_builder redaction
- Stale/partial map mitigations and mandatory confirm gate
- Manual UAT blocking for `/gsd-verify-work`

**Concerns:**

| Severity | Concern |
|----------|---------|
| HIGH | Secret disclosure remains prompt-only — no automated fail-closed gate if agent reads `.env` |
| HIGH | Map integrity controls not enforceable — completeness, stale warning, confirm gate are SKILL-only |
| MEDIUM | Symlink escape not tested despite `follow_symlinks=False` mitigation claim |
| MEDIUM | `has_codebase_map` vs completeness gate mismatch |
| MEDIUM | validate_spec bypass edge cases under-tested (case normalization, single section) |
| MEDIUM | T-03-02 DoS has zero validation mapping |
| LOW | Header substring matching spoofable; Continue-path migration manual-only |

**Suggestions:**
- Add `test_symlink_outside_root_not_followed`
- Require both `relative_to` AND `follow_symlinks=False` in acceptance (remove OR grep)
- Map T-03-02 to unit tests (max_depth, skip_dirs)
- Consider stdlib `scan_map_secrets.py` with exit 1 on API-key regex matches
- Align detection with completeness or document stub STACK behavior explicitly

**Risk Assessment:** **MEDIUM** — Wave 1 sound and test-backed; residual HIGH items are agent non-compliance, not missing threat identification.

---

## Reviewer C (Requirements Traceability) Review

**Summary:** Plans trace partially to all three ROADMAP success criteria and PROJ-02/PROJ-03. Wave 1 is well-covered by pytest. Wave 2 is design-complete but verification-thin: agent orchestration, Q&A behavior, and "no mixing" are prose + grep + manual UAT.

| Target | Traced? | Automated proof? |
|--------|---------|------------------|
| SC1 — detect → map before Q&A | Yes | Partial (detection tests only) |
| SC2 — map loaded; Q&A skips mapped facts | Yes | No (manual UAT only) |
| SC3 — Already Built vs To Build, no mixing | Partial | Headers only; content overlap unenforced |
| PROJ-02 | Yes | Wave 1 strong; Wave 2 weak |
| PROJ-03 | Yes | Structural gates only |

**Strengths:**
- Sensible two-wave split with explicit dependency chain
- Wave 1 TDD discipline aligned to validation map
- Scaffold-then-detect gap addressed
- Defense-in-depth for partial maps
- Continue-path and honest validation contract (UAT blocking, autonomous: false)

**Concerns:**

| Severity | Concern |
|----------|---------|
| HIGH | "No mixing" (SC3) not validator-enforced — duplicate items can pass validate_spec |
| HIGH | Wave 2 automated verification is grep-only |
| HIGH | SC2 has no falsifiable automated check |
| HIGH | `has_codebase_map` vs seven-file completeness mismatch |
| MEDIUM | Invalid JSON error path not exercised |
| MEDIUM | Success Criteria mixing only at SKILL level |
| MEDIUM | Confidence tags discretionary, not validated |
| MEDIUM | No ROADMAP SC ↔ task ID traceability matrix |

**Suggestions:**
- Add ROADMAP SC1–SC3 column to 03-VALIDATION per-task table
- Extend validate_spec for minimal content-level SC3 (reject identical bullets in both sections)
- Replace grep-only Wave 2 gates with contract tests (step ordering schema, seven-filename assertion)
- Formalize Manual UAT with saved transcript artifacts
- Consider `has_complete_codebase_map` flag separate from `has_codebase_map`

**Risk Assessment:** **Medium–High** for requirements traceability at phase-verify time. Wave 1 low risk; Wave 2 high residual risk because SC1–SC3 behavioral criteria depend on manual UAT.

---

## Consensus Summary

### Agreed Strengths

- **Two-wave architecture is correct** — All reviewers agree Wave 1 (deterministic tools) must precede Wave 2 (agent workflows).
- **Prior review fixes incorporated** — Inverse validate_spec rule, Step 1.4 naming (not Step 0), detection test gaps filled, all-seven preload, scan_for_secrets, Continue path coverage, and blocking manual UAT all appear in current plans.
- **STACK.md canonical marker** — Unanimous praise for fixing the empty-scaffold gap.
- **TDD on Wave 1** — Strong automated verification for detection and validation contracts.
- **Greenfield preservation** — Conditional brownfield gates and explicit regression paths.

### Agreed Concerns (highest priority)

1. **PROJ-03 "no mixing" not validator-enforced (HIGH)** — All three reviewers flag that structural header separation is proven but semantic dedup across Already Built / To Build / Success Criteria remains honor-system only. SC3 third clause not reliably met by automation.

2. **Wave 2 verification is grep-only (HIGH)** — Phase goals #2–#3 are behavioral. Plan completion does not prove agents spawn mappers, run Step 1.4, or skip mapped facts. Blocking manual UAT compensates but is human-dependent.

3. **`has_codebase_map` vs completeness mismatch (MEDIUM–HIGH)** — Detection treats any `STACK.md` file as mapped; workflow requires seven files >20 lines. Defense-in-depth in Step 1.4 mitigates but is not tested.

4. **Secret/map controls are prompt-only (HIGH — security)** — scan_for_secrets and deny rules live in SKILL prose; non-compliant agent can leak secrets with no fail-closed gate.

5. **Symlink/DoS mitigations under-verified (MEDIUM)** — `follow_symlinks=False` and `max_depth=3` documented but no dedicated pytest tasks in validation map.

6. **Continue with existing brownfield SPEC policy unclear (MEDIUM)** — Re-run mandated for greenfield-format SPEC only; stale brownfield SPEC may skip remapping.

### Divergent Views

- **Overall phase risk** — General reviewer: MEDIUM; Security reviewer: MEDIUM; Requirements reviewer: MEDIUM–HIGH (due to SC traceability gaps).
- **Dedup enforcement strictness** — Requirements reviewer rates as blocking for SC3 sign-off; General reviewer accepts as intentional MVP scope with post-MVP validate_spec extension.
- **Detection alignment** — Security/Requirements suggest aligning `has_codebase_map` with completeness threshold; General reviewer accepts two-layer model (detection + workflow gate) if documented in SKILL.md.

### Prior Review Fix Status

| Prior concern | Status |
|---------------|--------|
| Inverse validate_spec rule | ✅ Addressed in 03-01 |
| Step 0 vs Step 1.4 naming | ✅ Addressed in 03-02 + validation |
| Detection test gaps | ✅ Addressed in 03-01 |
| All-seven map preload | ✅ Addressed in 03-02 |
| scan_for_secrets | ✅ Addressed in 03-02 |
| Continue path bypass | ✅ Addressed in 03-02 + UAT |
| Blocking manual UAT | ✅ Addressed in 03-VALIDATION |
| Partial map / stub STACK | ⚠️ Mostly addressed — workflow gate exists; detection layer still file-only |
| PROJ-03 dedup / no mixing | ❌ Not addressed — still SKILL-level only |
| Grep-only Wave 2 verify | ❌ Inherent — mitigated by blocking UAT only |

### Recommended Pre-Execute Actions

| Priority | Action | Plans Affected |
|----------|--------|----------------|
| 1 | Execute blocking Manual UAT honestly before `/gsd-verify-work` | 03-VALIDATION |
| 2 | Document in Step 1.4: stub STACK + `has_codebase_map: true` still triggers remap if <7 complete files | 03-02 |
| 3 | Add Continue policy for existing brownfield SPEC with stale/partial map | 03-02 |
| 4 | Add symlink + max_depth pytest tasks to validation map | 03-01, 03-VALIDATION |
| 5 | Consider minimal validate_spec dedup (identical bullets in both sections) for SC3 | 03-01 |
| 6 | Add ROADMAP SC1–SC3 column to per-task validation table | 03-VALIDATION |
| 7 | Document `has_codebase_map` ≠ complete map in detect_brownfield SKILL.md | 03-01 |

### Overall Phase Risk

**MEDIUM** — Wave 1 is execution-ready (LOW implementation risk). Wave 2 has correct architecture and incorporates most prior review fixes. Residual risk is agent adherence, PROJ-03 semantic quality without validator dedup, and grep-only Wave 2 proof. With blocking manual UAT and stub-STACK documentation, confidence moves toward **LOW–MEDIUM**.
