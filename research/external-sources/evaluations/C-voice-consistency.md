# Evaluator C — Voice and Consistency Report

## 1. Scope checked

- `research/topics/patterns-worth-stealing.md` — full file (Patterns 1–32 + extensions + ranking table).
- `research/topics/self-healing-and-verification.md` — §2, §3, §8, §9, §10 (additions made on 2026-05-24).
- `research/topics/workflow-and-orchestration.md` — §8 (two new bullets).
- `research/SUMMARY.md` — §1, §4 (intro, outer-harness paragraph, Patterns Added subsection), §5, §6, §7, §9.
- `research/external-sources/INCORPORATION-REPORT.md` — read once for cross-reference; not modified.
- Voice/style baseline: Patterns 1–19 in `patterns-worth-stealing.md`.

Checked dimensions: bullet structure conformity, tone (empirical / source-cited / no hype), extension framing as observations vs replacements, duplication between new §4 list and existing "Additional Patterns" list, Pattern 11 ↔ Pattern 31 scoping explicitness, cross-reference reciprocity, Böckeler `[inference]` tag accuracy, URL spelling for Harness Engineering, ArchUnit, OpenRewrite, Lex Lerumph.

## 2. Auto-fixes applied

| # | File | Issue | Fix |
|---|---|---|---|
| 1 | `research/topics/patterns-worth-stealing.md` (Pattern 11 `See also`, ~line 184) | Pattern 11's extensions discuss AI-test redundancy but never back-reference Pattern 31; reader on Pattern 11 cannot find the scoping resolution without flipping forward. | Appended `; Pattern 31 (Approved Scenarios) for AI-generated fixture tests, which scope this pattern's immutability rule to hand-authored contract tests.` to the existing `See also` line. Preserves the original sentence structure (single-phrase addition; same bullet). |
| 2 | `research/SUMMARY.md` §9 Incorporation Log (second copy, ~line 336) | Markdown link text `[Fowler/Böckeler]` for the Harness Engineering article was missing the `[inference]` tag, which appears everywhere else the attribution is used. | Appended `[inference]` outside the link target: `[Fowler/Böckeler](URL) [inference]`. (Outside the link to avoid nested-bracket parsing issues.) |

No other auto-fixes were eligible. No hype-word substitutions were needed: a grep of `powerful`, `revolutionary`, `game-changing`, `cutting-edge`, `groundbreaking`, `seamless`, `robust`, `world-class`, `next-gen`, `unparalleled`, `unprecedented`, `state-of-the-art`, `paradigm shift` (case-insensitive) found zero hits in modified dossier files. ("Robust" appears only in the verbatim title of a sibling memo cited in an immutable summary file.)

URL spelling spot-checks: `https://martinfowler.com/articles/harness-engineering.html`, `https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html`, `https://docs.openrewrite.org/...`, `https://www.archunit.org/...`, `https://lexler.github.io/augmented-coding-patterns/patterns/approved-scenarios/` all spelled consistently across modified files. No typos.

## 3. FOR HUMAN — Issues not auto-fixed

| # | File | Issue | Why not auto-fixed |
|---|---|---|---|
| 1 | `research/SUMMARY.md` lines 313–324 and 328–356 | Two `## 9. Incorporation Log — 2026-05-24` sections exist back-to-back. The earlier (~12-line) table is a compact version; the later (~28-line) table is the verbose version with skipped-items and risks. They are not literal duplicates — the second is a superset — but the file ships with two `## 9` headings and two tables that describe the same incorporation pass. | Editorial merge required (deletions + structural choice between compact and verbose versions). Task rules forbid deletion and forbid rewriting prose to merge two sections. |
| 2 | `research/topics/patterns-worth-stealing.md` lines 446–458 vs 459–471 (Pattern Ranking Summary Table) | Rows for patterns 20–32 appear **twice** in the ranking table. The first block uses the compact column shape used for patterns 1–19; the second block uses an expanded transferability column ("HIGH (where IR investment is justified)", "HIGH (workflow/prompt phases)", etc.). Both refer to the same patterns. | Editorial deletion required. Task rules forbid deleting content. The compact block matches the table's voice/format used for patterns 1–19; the expanded block is informationally richer but stylistically inconsistent with the rest of the table. Recommend keeping the compact block and folding the parenthetical qualifiers into the "Primary problem solved" column, or vice versa. |
| 3 | `research/topics/patterns-worth-stealing.md` Pattern 13 (line 210, `What to adapt`) | The OpenRewrite Markers and ArchUnit bytecode-graph extensions were folded **into** Pattern 13's `What to adapt` paragraph rather than appended as separate `**Extension — …**` sub-bullets the way every other 2026-05-24 extension is formatted (Patterns 4, 5, 6, 8, 11, 15, 16). The content reads fine, but the structural inconsistency is the most visible style drift between new material and the dossier's existing extension convention. | Restructuring required (split the paragraph into a base `What to adapt` clause plus two `**Extension — …**` bullets). Task rules forbid restructuring pattern bodies. |
| 4 | `research/topics/self-healing-and-verification.md` §8 (lines 215, 217, 219, 221, 223, 225) — paired with §2 `ScanningRecipe accumulator` and `Shift-left code review` paragraphs | `Survey-then-edit with a typed accumulator` (§8) and `ScanningRecipe accumulator` (§2) describe the same OpenRewrite mechanism in two locations; similarly the Developer Skills `Shift-left code review` appears in both §2 and §8. The `INCORPORATION-REPORT.md` Risks section already flags this and explains that the no-removal rule prevented consolidation. Listed here for evaluator completeness. | Already documented as a known risk by the incorporator. Resolution requires editorial deletion; not an auto-fix candidate. |
| 5 | `research/topics/patterns-worth-stealing.md` Patterns 6 (line 90) and 11 (line 183) | Both carry an identical `per-hunk attribution from Result.recipesThatMadeChanges` extension. This is the duplicate per-hunk-attribution issue flagged in `INCORPORATION-REPORT.md` under Risks. Pattern 6 is the home the OpenRewrite review proposed; Pattern 11's copy is pre-existing. | Already documented. Consolidation requires deletion; not an auto-fix candidate. |

No genuine semantic contradictions were detected during this voice/consistency pass. The tensions flagged by the incorporation (TLC RED-test immutability vs Approved Scenarios; diagnose-into-PLAN vs steering loop) are addressed explicitly in the dossier text (see §6 below).

## 4. Voice spot-check

Random sample of three new patterns rated against the Patterns 1–19 voice baseline:

- **Pattern 22 (Precondition Scope Filter):** HIGH. Structure matches (`Origin` / `Problem it solves` / `How it works` / `Transferability` / `What to adapt` / `See also`). Tone is empirical and cites the OpenRewrite YAML format reference inline. "Slashes token cost, scopes blast radius" is brisk but within the dossier's existing register (compare Pattern 7's "thundering herd" and Pattern 14's "worst possible recovery behavior"). No hype.
- **Pattern 29 (Guides + Sensors Taxonomy):** HIGH. Standard six-bullet structure. Empirical claim ("Crosscuts existing GSD/TLC/Spec-Kit gate inventories along an axis…") with appropriate hedging. Citations on both author-attribution line (`[inference]` present) and origin URL. Reads as observation, not as advocacy.
- **Pattern 32 (Reuse-Awareness Pre-Check):** HIGH. Bullet structure conforms. Origin is honestly flagged as "Inferred from Böckeler Memo #13 examples; Graphify's `query_graph` / `get_neighbors` is the natural mechanism" — the dossier's standing convention is to surface mechanism vs source separation explicitly, which this entry does. Cross-references Pattern 13 with a concrete pairing rationale (`EXTRACTED` matches outrank `INFERRED` ones), matching Pattern 27's "Companion to Pattern 15" style.

Overall: all three sampled patterns indistinguishable from Patterns 1–19 in tone, citation discipline, and bullet structure.

## 5. Duplication check results

Within `patterns-worth-stealing.md` (new vs old patterns):

- Pattern 21 (Recipe DAG) vs Pattern 7 (Wave-Based Parallelism): different axes — Pattern 7 is per-execution dependency computation, Pattern 21 is authored composition. Pattern 21's body calls this distinction out explicitly. No duplication.
- Pattern 22 (Precondition Scope Filter) vs Pattern 14 (Package Legitimacy Gate): both are pre-LLM gates but address different objects (files in scope vs package installability). No duplication.
- Pattern 27 (Importable Spec Packs) vs Pattern 15 (Install-Time Profile): Pattern 27 calls itself "Companion to Pattern 15" and addresses a distinct axis (consuming external rule packs vs governing the framework's own surface). No duplication.
- Pattern 30 (Computational vs Inferential) vs Pattern 10 (Asymmetric Decision Coverage Gates): both are labeling axes for verifications, but Pattern 10's axis is blocking/non-blocking by cost-of-fix and Pattern 30's is deterministic/LLM by cost-of-run. No duplication.
- Pattern 31 (Approved Scenarios) vs Pattern 11 (Test-as-Spec): explicit scoping resolves the apparent overlap (see §6).
- Pattern 32 (Reuse-Awareness Pre-Check) vs Pattern 13 (Confidence Tagging): Pattern 32 pairs with Pattern 13 rather than restating it.

Between SUMMARY.md §4 "Patterns Added 2026-05-24 from External Sources" (Patterns 20–32) and the pre-existing "Additional Patterns in the Full File" list (Patterns 7, 12, 13, 14, 15, 16, 17, 18, 19): zero pattern overlap, no near-duplicate prose.

Note: the duplications that **do** exist are within identical sections (§9 in SUMMARY.md; ranking table block in patterns-worth-stealing.md) and across §2/§8 of `self-healing-and-verification.md` — see FOR HUMAN rows 1, 2, 4, 5 above. None are duplications between new patterns and existing patterns.

## 6. Pattern 11 ↔ Pattern 31 scoping check

**Verdict:** The scoping is explicit, but only in **Pattern 31**, not in Pattern 11. After the auto-fix above (§2 row 1), Pattern 11's `See also` line now also points to Pattern 31 with the scoping rationale.

Specific locations of the scoping language:

- `patterns-worth-stealing.md` line 296 (Pattern 31, `How it works`): "Complements Pattern 11: RED-phase contract tests remain immutable, but AI-generated *fixture* tests use the approved-scenarios protocol."
- `patterns-worth-stealing.md` line 298 (Pattern 31, `What to adapt`): "pair with Pattern 11 by scoping RED-phase contract tests to assertion-style and AI-generated fixture tests to approved-scenarios."
- `INCORPORATION-REPORT.md` line 63 (Contradictions logged but not auto-applied): documents the tension and its resolution.
- `SUMMARY.md` line 352 (second §9 Risks section): explicitly notes that a reader following only Pattern 11 may not see the qualification — this evaluator pass acted on that flag.
- `patterns-worth-stealing.md` line 184 (Pattern 11 `See also`, **after this evaluator's auto-fix**): now back-references Pattern 31 with the scoping rationale in a single phrase.

The scoping is now navigable from either direction.

## 7. Overall voice/consistency verdict

**HIGH.**

Patterns 20–32 are stylistically indistinguishable from Patterns 1–19: the six-bullet structure is preserved without exception, citations are inline and source-grounded, tone is empirical with appropriate hedging (`[inference]` on Harness Engineering authorship, "Inferred from … examples" on Pattern 32), and no hype language appears anywhere in the modified content. Extension sub-bullets uniformly read as observations augmenting an existing pattern, not as standalone replacements. The 2026-05-24 incorporation reads as a continuation of the original dossier voice, not as a pasted-in addendum. The remaining issues are structural duplications (second §9 in SUMMARY.md; double row block in the ranking table; §2/§8 paragraph echoes) that the incorporation report itself already flagged and which require editorial deletion outside the auto-fix mandate; none affect voice or surface a semantic contradiction.
