---
phase: 1
reviewers: [cursor]
reviewed_at: 2026-05-21T18:35:00Z
plans_reviewed: [01-01-PLAN.md, 01-02-PLAN.md, 01-03-PLAN.md]
---

# Cross-AI Plan Review — Phase 1: Tooling Foundation

## Cursor Review

# Cross-AI Plan Review — Phase 1: Tooling Foundation (01-01, 01-02, 01-03)

## Executive Summary

The three plans form a coherent **walking skeleton → parallel vertical slices** layout: Wave 1 establishes `mise-en-place/`, pytest, and `tool-env-check`; Wave 2 delivers `tool-context-builder` and `tool-planning-scaffold` with no file overlap. Locked decisions (D-01–D-09) are traced into tasks, must-haves, and threat models more thoroughly than typical MVP plans. The main gaps are **Python 3.9.6 typing in 01-01**, **weak automated proof of SC-2 ("paste-ready")**, **gitignore/tree edge cases in 01-02**, **`write-artifact` CLI ergonomics in 01-03**, and **no explicit "copy to `.cursor/skills/`" story for TOOL-05** beyond co-location under `mise-en-place/`. Overall the plans are **executable and likely to meet phase goals** with minor fixes during implementation.

---

## PLAN 01-01: Walking Skeleton + tool-env-check

### 1. Summary

Strong first slice: SKILL contract, script, tests, security grep gates, and SC-1 timing are specified clearly. Wave-1 pytest install is correctly scoped as dev-only. The plan aligns with TOOL-04/TOOL-05 and sets the pattern for 01-02/01-03. Fix **3.10+ type hints** before execution on Python 3.9.6, and tighten **cursor detection** and **CI-flaky timing tests**.

### 2. Strengths

- **Vertical slice discipline** — SKILL.md → `env_check.py` → tests → verification commands in one plan.
- **Security baked in** — explicit ban on `shell=True` and `capture_output`; `timeout=3` on subprocess; threat model matches implementation.
- **Exit-code contract** — 0/1 semantics documented in SKILL.md and tested (with mocks).
- **D-01 honored at runtime** — stdlib-only script; pytest isolated to dev install in Task 1.
- **Dependency ordering** — Wave 1 correctly blocks 01-02/01-03; README previews all three tools.
- **PATTERNS.md integration** — `read_first` points to `gsd-fast/SKILL.md` adapter block; reduces executor drift.

### 3. Concerns

| Severity | Concern |
|----------|---------|
| **HIGH** | Plan specifies `run_check(name: str, cmd: list) -> tuple[str, str]` and module-level `(name_str, cmd_list)` tuples — **`tuple[str, str]` requires Python 3.10+**; on 3.9.6 use `Tuple[str, str]` from `typing` or drop hints. |
| **MEDIUM** | **Cursor check ambiguity** — CHECKS includes `["cursor", "--version"]` but special-case uses `CURSOR_TRACE_ID` only; fallback to `cursor --version` may fail outside Cursor IDE while still being a "phase prerequisite." Behavior should be explicit in SKILL.md and tests. |
| **MEDIUM** | **`test_completes_in_under_five_seconds`** runs the real script against the host PATH — **flaky in CI/sandbox** (missing git/bun/cursor) and couples unit tests to environment. |
| **LOW** | Task 1 runs `pip install pytest` without **pinning, `requirements-dev.txt`, or README note** — reproducibility across machines is unspecified. |
| **LOW** | Comment says "Python 3.6 portability" for `stdout=PIPE`; target is **3.9.6** — harmless but may confuse executors. |
| **LOW** | **Bun/node tests** — only git-missing exit-1 test; bun/node fallback and `CURSOR_TRACE_ID` fast-path lack dedicated unit tests. |

### 4. Suggestions

- Replace all `X | Y` and builtin generics (`tuple[str, str]`, `list[str]`) with **`typing` imports** or omit hints; add a one-line note in PATTERNS: "target interpreter: Python 3.9.6."
- Document cursor rule in SKILL.md: **pass if `CURSOR_TRACE_ID` set OR `cursor --version` succeeds**; add a mocked test for the env-var path.
- Split timing: keep **mocked fast unit tests**; move wall-clock `<5s` to **01-VALIDATION.md manual/smoke** (already listed there) or mark `@pytest.mark.skipif` outside dev machines.
- Record pytest as dev dependency in `mise-en-place/README.md` (e.g. `python3 -m pip install pytest`).
- Extend `test_exits_one_when_git_missing` pattern to **bun/node neither in PATH** (mock `shutil.which`).

### 5. Risk Assessment

**Overall: MEDIUM** — Implementation risk is low; **compatibility and CI stability** are the main blockers if 3.10+ hints slip through or timing tests run in minimal environments.

---

## PLAN 01-02: tool-context-builder

### 1. Summary

Best-aligned plan for D-05–D-07: four sections, depth 3, `.planning/` exclusion, git `--no-pager`, path guards, and four focused tests. Delivers TOOL-02 structurally. **SC-2 ("no manual editing")** is asserted but not objectively tested; **150-line cap** may conflict with full tree + git + previews; **gitignore matching** is intentionally shallow (name-only) — acceptable for MVP if documented.

### 2. Strengths

- **Requirement traceability** — Maps directly to TOOL-02, D-05, D-06, D-07; `ALWAYS_EXCLUDE` includes `.planning`.
- **Graceful degradation** — missing `.gitignore`, non-git repo, unreadable previews; always `sys.exit(0)` except bad `--root`.
- **Security parity with 01-01** — no `shell=True`, `--no-pager`, path traversal guard on `--root`, threat model T-02-01–T-02-03.
- **Test coverage matches risks** — four tests for sections, `.planning` exclusion, gitignore, missing gitignore.
- **Parallel-safe** — no shared files with 01-03; depends only on 01-01 for pytest/SKILL pattern reference.

### 3. Concerns

| Severity | Concern |
|----------|---------|
| **MEDIUM** | **SC-2 not verifiable by current tests** — grep for four headers does not prove markdown quality (fences, ordering, paste size, no broken paths). Human UAT in 01-VALIDATION.md is the real gate; plan should say so explicitly. |
| **MEDIUM** | **Gitignore pitfall (RESEARCH Pitfall 1)** — `fnmatch` on **entry name only** misses `src/build/`, negation rules, and directory-only patterns; tests only cover top-level `node_modules/`. |
| **MEDIUM** | **`--root` path guard** allows `--root` **above cwd** when `root in cwd.parents` — can read parent trees (monorepo ok; **broader read scope** than "project root only"). |
| **LOW** | **150-line budget** vs tree connectors + git + previews — likely tight; risk of under-tested shortcuts or overrun. |
| **LOW** | **Dependencies section** dumps first manifest file raw — D-07 says "dependency list"; may not satisfy agents expecting parsed package names. |
| **LOW** | **No test for path traversal rejection** on `--root` despite threat model T-02-01. |
| **LOW** | **`build_tree` with empty patterns** still excludes via `ALWAYS_EXCLUDE` — test (b) passes `[]` patterns; good, but doesn't prove gitignore + ALWAYS_EXCLUDE together in one integration run. |

### 4. Suggestions

- Add **`test_root_outside_cwd_rejected`** (subprocess or direct `main()` with `pytest.raises(SystemExit)`).
- Add one **golden-output fixture** (small tmp tree) asserting section order and `---` separators — minimal SC-2 signal.
- Document in SKILL.md: **gitignore support is basename/pattern-level MVP**, not full git spec.
- Clarify D-07 dependencies: **"first manifest found, verbatim excerpt"** vs parsed list — avoids executor inventing parsers.
- Consider **`--max-preview-files`** in argparse if output size blows token budgets (optional, not required for phase).

### 5. Risk Assessment

**Overall: LOW–MEDIUM** — Core behavior is well specified; **output quality and gitignore completeness** are product risks, not execution blockers.

---

## PLAN 01-03: tool-planning-scaffold

### 1. Summary

Solid TOOL-01 delivery: idempotent `scaffold`, no-clobber defaults, `write_artifact` traversal guard with test, `format-file` normalization. Six tests cover the critical guarantees. Main risks are **`write-artifact` CLI design** (content as positional arg), **`format-file` without scope limit**, and **unused `json` import**; parallel execution with 01-02 is sound.

### 2. Strengths

- **Idempotency spelled out** — `mkdir(exist_ok=True)` + `if not target.exists()` before defaults; Pitfall 4 from RESEARCH applied.
- **Security test** — `test_write_artifact_path_traversal_blocked` verifies exit 1 and no escape file.
- **TOOL-01 subcommands complete** — scaffold, read, write, format; matches phase SC-3.
- **Six behavioral tests** — idempotent scaffold, no-clobber, read, format, traversal — good coverage.
- **Threat model** — T-03-01/T-03-02 with test linkage for write path.

### 3. Concerns

| Severity | Concern |
|----------|---------|
| **MEDIUM** | **`write-artifact <artifact> <content>` as positional** — multiline/special characters break shell invocation; agents may need stdin/file flag not specified. High friction for real use. |
| **MEDIUM** | **`format-file <file>` has no `.planning/` boundary** — can rewrite any path the user passes; threat model "mitigate" is weak vs read/write under planning root. |
| **LOW** | **`import json` in action block** — unused; minor scope noise. |
| **LOW** | **`read_artifact` / `write_artifact` artifact strings** not validated for `..` segments before resolve — reliance on `.resolve()` + parent check; worth a test for `foo/../../outside`. |
| **LOW** | **No CLI integration test** for subcommands via `subprocess` — only direct function imports; argparse wiring could drift. |
| **LOW** | **PLANNING_DEFAULTS minimal headers** — may not match existing `.planning/` in this repo if scaffold run at root; no-clobber protects, but greenfield vs brownfield not documented in SKILL.md. |

### 4. Suggestions

- Prefer **`write-artifact` content via stdin** (`-` or `--content-file`) in SKILL.md and argparse; keep positional for tiny smoke tests only.
- Restrict **`format-file`** to paths under `--root` / `.planning/` (same Shared Pattern 4) or document "formats arbitrary path — developer responsibility."
- Remove unused **`json`** import from the plan action.
- Add **`test_write_artifact_nested_path_allowed`** (`phases/01/STATE.md`) to confirm valid subpaths work.
- Add one **subprocess smoke test** per subcommand mirroring 01-02's pattern.

### 5. Risk Assessment

**Overall: LOW** — Idempotency and traversal block are the hard parts and are planned well; **CLI ergonomics** is the main post-MVP friction.

---

## Cross-Cutting Analysis

### Phase goal coverage

| Success criterion | Plans coverage | Gap |
|-------------------|----------------|-----|
| SC-1 env-check <5s | 01-01 + timing test | CI flakiness; prefer validation doc for wall-clock |
| SC-2 paste-ready context | 01-02 structure | No quality rubric in automated tests |
| SC-3 scaffold + format idempotent | 01-03 | Strong |
| SC-4 tools in skill folder | All three under `mise-en-place/tool-*` | No copy/install step to `.cursor/skills/`; D-02 "co-located with skill" vs `mise-en-place/` staging needs one sentence in README |

### Python 3.9.6 / D-01

| Item | Verdict |
|------|---------|
| Stdlib-only runtime scripts | Plans comply |
| `capture_output=False`, explicit PIPE | Good for 3.9 |
| `tuple[str, str]` in 01-01 | **Must fix** |
| pytest via pip | Acceptable per constraint; document it |

### Security (cross-plan)

Consistent: no `shell=True`, subprocess timeouts, path resolve checks. Residual gaps: **01-02 permissive `--root`**, **01-03 format-file arbitrary path**, **01-03 write content via argv**.

### Performance

- **01-01**: 4×3s subprocess caps → worst case ~12s if all run serially; plan expects <5s total — fine if cursor short-circuits via env var.
- **01-02**: git timeout 10s; tree walk depth 3 — should be fast on typical repos.
- **01-03**: filesystem only — negligible.

### Missing edge cases (rollup)

- Non-UTF-8 entry files (01-02 handles via `UnicodeDecodeError` — good).
- Shallow git clone / empty log (01-02 git_summary — partial handling).
- Windows paths (not in constraints; acceptable omission for v1).

---

## Consensus Summary

*(Single reviewer — no consensus divergence to report)*

### Agreed Strengths

- Vertical slice discipline with correct Wave 1 → Wave 2 gating
- Security-first approach: no `shell=True`, explicit timeouts, path traversal guards
- Decision traceability: D-01 through D-09 visible in task actions
- Graceful degradation on missing env (no .gitignore, non-git repo, missing binaries)

### Top Concerns (priority order)

1. **[HIGH] Python 3.9.6 type hints** — `tuple[str, str]` in 01-01 will fail at runtime. Fix before execution.
2. **[MEDIUM] SC-2 not testable by automation** — "paste-ready" quality requires human UAT; plan should state this explicitly.
3. **[MEDIUM] write-artifact positional content arg** — multiline content will break shell invocation; add stdin/file option or document workaround.
4. **[MEDIUM] Cursor detection ambiguity** — document pass rule (env var OR binary) and add mocked test.
5. **[MEDIUM] Timing test environment coupling** — `test_completes_in_under_five_seconds` is flaky without host binaries; mark skipif or move to smoke.

### Recommended Pre-Execution Fixes

1. Fix `tuple[str, str]` → `Tuple[str, str]` from `typing` in 01-01 (or drop hints)
2. Document gitignore MVP scope in 01-02 SKILL.md
3. Add stdin option for `write-artifact` or document argv workaround in 01-03 SKILL.md
4. Record pytest dev install in README

**Verdict: Approve with comments** — plans are executable after the Python 3.9.6 typing fix. Other concerns are implementation guidance, not blockers.
