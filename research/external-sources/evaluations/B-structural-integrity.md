# Evaluator B — Structural Integrity Report

## 1. Scope checked

- 4 files checked: `research/topics/patterns-worth-stealing.md`, `research/topics/self-healing-and-verification.md`, `research/topics/workflow-and-orchestration.md`, `research/SUMMARY.md`.
- 32 unique patterns enumerated in `patterns-worth-stealing.md` (file order: 1–9, 21, 10–14, 20, 22, 23, 25, 29, 30, 31, 32, 15–19, 24, 26–28).
- Pattern Ranking Summary Table verified for completeness (1–32) and column shape (5 columns).
- Markdown well-formedness: heading nesting (no jumps from `##` to `####`), code-fence balance, table column counts, list indentation.
- Cross-link verification: every relative `[text](path)` link resolves; every `Pattern N` reference resolves to an existing pattern; every `§N` reference resolves to an existing section.
- Cross-checked against `external-sources/INCORPORATION-REPORT.md` — every row in the "EXTENDS applied" table and every "NEW patterns added" row verified against the target file.
- Verified all original 19 patterns and original `SUMMARY.md` §§1–8 content are intact.

## 2. Auto-fixes applied

| # | File | Issue | Fix |
|---|---|---|---|
| 1 | `topics/patterns-worth-stealing.md` | Pattern Ranking Summary Table contained two consecutive sets of rows for Patterns 20–32 (lines 446–458 duplicated by lines 459–471) — 13 duplicated rows with slightly different titles/origins/transferability strings. | Removed the first set (lines 446–458). Kept the second set because its titles, origin attributions, and transferability qualifiers (e.g., `HIGH (where IR investment is justified)`, `Lex Lerumph (via Harness Engineering)`, `Böckeler Memo #13 (mechanism: Graphify)`) match the pattern entries themselves and the `INCORPORATION-REPORT.md` "NEW patterns added" table more accurately than the first set's flattened versions. |
| 2 | `SUMMARY.md` | File contained two consecutive `## 9. Incorporation Log — 2026-05-24` sections (lines 313–324 and lines 328–356) with overlapping but non-identical content. | Removed the first (concise table only). Kept the second (comprehensive — includes per-source table, Items skipped, Contradictions logged, Risks). The second matches `INCORPORATION-REPORT.md`'s description of §9 ("Per-source table of patterns/extends/skipped/risks") and the file's own forward-reference at SUMMARY §1 line 10 (`see §9 Incorporation Log`). |

After fixes:

- `patterns-worth-stealing.md` ranking table = 32 rows (Patterns 1–32), no duplicates, consistent 5-column shape.
- `SUMMARY.md` headings = `## 1` through `## 9`, one of each.

## 3. FOR HUMAN — Issues not auto-fixed

| # | File | Issue | Why not auto-fixed |
|---|---|---|---|
| 1 | `topics/patterns-worth-stealing.md` | Patterns 24, 26, 27, 28 are physically located in **Group D: Extensibility and Adaptability** in the file body, but `INCORPORATION-REPORT.md`'s "NEW patterns added" table lists their "Anchor section in patterns file" as **Group C**. The report itself acknowledges the inconsistency in a footnote: "A future restructuring may want to rebalance — Patterns 26, 27, 28 are arguably better fits for Group D … and Pattern 24 could move there too. Left as-is per the 'do not restructure' constraint." The note's "Left as-is" wording is internally inconsistent with the EXTENDS table. | Resolving this requires either restructuring (forbidden by user constraints) or editing `external-sources/INCORPORATION-REPORT.md` (also forbidden — immutable input). Editorial judgment needed on whether the file-body placement (Group D) or the report's table claim (Group C) is correct. |
| 2 | `topics/self-healing-and-verification.md` | Duplicate content: the OpenRewrite ScanningRecipe accumulator paragraph appears in both §2 (line 45, "ScanningRecipe accumulator (OpenRewrite extension)") and §8 (line 223, "Survey-then-edit with a typed accumulator"). Similarly, the Developer Skills Memo #13 shift-left review appears in both §2 (line 49, "Shift-left code review") and §8 (line 225, "Shift-left review at the IDE / pre-commit boundary"). | `INCORPORATION-REPORT.md` explicitly notes this duplication and chose to retain both placements per the "no-removal rule" ("Either is sufficient; the §2 placement matches the reviewer's instruction more closely"). Removing either would be deletion of content, which the user-supplied auto-fix rules forbid. Editorial decision needed on which placement to canonicalize. |
| 3 | `topics/patterns-worth-stealing.md` | Pattern 11 (Test-as-Spec + SPEC_DEVIATION) does not reciprocate Pattern 31's "complements Pattern 11" cross-reference. The `INCORPORATION-REPORT.md` "Contradictions logged but not auto-applied" section flags this: a reader following only Pattern 11 may not see the AI-fixture-test qualification that Pattern 31 introduces. | Adding the reciprocal cross-link would be a content addition (extending Pattern 11's body), not a structural fix. The user-supplied rules forbid adding patterns or extensions not in the incorporation report; this falls in a gray area between "cross-link integrity" (allowed to fix) and "rewrite a pattern body" (forbidden). Surfacing for explicit editorial decision. |
| 4 | `topics/patterns-worth-stealing.md` | Pattern 8 (Diagnose-into-PLAN) entry could optionally cross-reference `workflow-and-orchestration.md` §8's new bullet "Repair-the-instance vs update-the-harness are two different loops." `INCORPORATION-REPORT.md` flags this as an optional reciprocation, not a required one. | Same reasoning as Issue 3 — content addition rather than structural fix. |

## 4. Cross-link verification table

| Link | Target exists? | Notes |
|---|---|---|
| `../frameworks/gsd.md` (from topics/*.md) | YES | File present at `research/frameworks/gsd.md`. |
| `../frameworks/tlc-spec-driven.md` | YES | Present. |
| `../frameworks/graphify.md` | YES | Present. |
| `../frameworks/adjacent-frameworks.md` | YES | Present. |
| `./context-engineering.md` | YES | Present in `research/topics/`. |
| `./workflow-and-orchestration.md` | YES | Present. |
| `./self-healing-and-verification.md` | YES | Present. |
| `./local-storage-and-artifacts.md` | YES | Present. |
| `./auxiliary-tooling.md` | YES | Present. |
| `./multi-runtime-support.md` | YES | Present. |
| `topics/patterns-worth-stealing.md` (from SUMMARY.md) | YES | Present. |
| `topics/*.md` (all six referenced from SUMMARY.md) | YES | All six topic files present. |
| `frameworks/*.md` (all four referenced from SUMMARY.md) | YES | All four framework files present. |
| External URLs (OpenRewrite, ArchUnit, Harness Engineering, Memo #13) | N/A | Not verified live; preserved verbatim from source summaries. |
| `Pattern 1` … `Pattern 32` references across all four files | YES | All 32 numbered pattern headings exist in `patterns-worth-stealing.md`. Numbers are unique; no duplicate "Pattern N" anywhere. |
| `§2`, `§3`, `§8`, `§9`, `§10` references in self-healing-and-verification.md | YES | All target sections exist (§1–§10 present). |
| `§8` reference in workflow-and-orchestration.md | YES | §8 present (file has §1–§8). |
| `SUMMARY.md` `§1`, `§4`, `§6`, `§7`, `§9` references | YES | All target sections exist (§1–§9 present after dedup fix). |
| `Pattern 4 extension`, `Pattern 16 extension`, etc. | YES | Extension sub-bullets verified present in the named pattern entries. |
| `INCORPORATION-REPORT.md` "EXTENDS applied" table — every row | YES | Each named extension verified present in its target file: Pattern 4 (line 60), Pattern 5 (line 78), Pattern 6 (line 90), Pattern 8 (line 120), Pattern 11 (lines 180–183), Pattern 13 (line 210), Pattern 15 (line 329), Pattern 16 (line 341); §8 implications bullets (self-healing lines 215–225, workflow lines 268–272); §9 and §10 sections present in self-healing-and-verification.md. |

## 5. Pattern ranking table coverage

- **All patterns 1–32 present in the table? YES** (after auto-fix #1).
- Any patterns in the body but missing from the table? **None.** Verified: 32 numbered headings in the body, 32 unique rows in the table.
- Any rows in the table but missing from the body? **None.** Verified by Grep cross-check of pattern numbers.
- Column shape: consistent 5 columns (`#`, `Pattern`, `Origin`, `Transferability`, `Primary problem solved`) across all 32 rows.

## 6. Overall structural verdict

**HIGH.**

After two auto-fixes (duplicate ranking-table rows removed; duplicate `SUMMARY.md` §9 section removed), the dossier's structural integrity is sound. All 32 patterns are present and uniquely numbered; the original 19 patterns are intact; original SUMMARY.md §§1–8 content is unchanged. Every cross-link verified (`Pattern N`, `§N`, relative file paths) resolves to an existing target. The Pattern Ranking Summary Table now covers Patterns 1–32 with consistent column shape and no duplicates. Code fences are balanced (0 in SUMMARY.md, 2 pairs in patterns, 2 pairs in self-healing, 4 pairs in workflow). Heading nesting is correct everywhere (no `##` → `####` jumps).

The four FOR HUMAN issues are editorial/judgment matters rather than structural defects — three of them (Group C vs Group D placement, the §2/§8 duplicate paragraphs, the reciprocal cross-links between Patterns 11/31 and Pattern 8 / workflow §8) are explicitly flagged in `INCORPORATION-REPORT.md` itself as known issues the report deferred to the evaluator pass. None of them prevent the dossier from being navigable or internally consistent; resolving them would require either restructuring (forbidden by constraints) or content additions/deletions outside the auto-fix scope.
