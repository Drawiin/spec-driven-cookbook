# Review — Role of Developer Skills (Fowler memo #13) vs. Research Dossier

> Compared: research/external-sources/summaries/04-role-of-developer-skills.md ↔ research/SUMMARY.md (+ relevant topic files)
> Reviewer date: 2026-05-24

## 1. Alignment Snapshot (1-5 + one paragraph)

**Score: 3 / 5 (moderately aligned, with several genuinely new framings).**

The memo and the dossier converge on the load-bearing claim that AI coding assistants need structured guardrails, deterministic verification, and stop conditions — not just better prompts. Specific mechanisms in the dossier (TLC's safety-valve table with max-3 diagnostic iterations, GSD's diagnose-into-PLAN self-healing, GSD's `node_repair_budget`, the asymmetric decision-coverage gate) are direct engineering analogs to memo concepts like "artisanal fallback," "diagnose-before-fix," and "rules are necessary but insufficient." However, the memo is written from a developer-skills lens rather than a framework-mechanics lens, and several of its framings have no analog in the dossier: the **three impact radiuses** taxonomy (commit / iteration / maintainability) for routing defects to gates, **steering as the unit of work**, the **"go-wrong" log** as a team-level institutional-learning ritual, the **reuse-awareness pre-check**, and **DX guardrails** (one-command run, hot reload). These are NEW and should be incorporated. Confidence is MEDIUM — three relevant topic files were read in full; context-engineering, local-storage, and others were not.

## 2. Findings Table

| # | Memo concept | Classification | Closest dossier analog | Notes |
|---|---|---|---|---|
| 1 | Three impact radiuses (commit / iteration / maintainability) for AI defects | **NEW** | Asymmetric-cost framing in Pattern 10 (block where cheap, warn where expensive) | Adjacent in spirit but the radius taxonomy and routing model are not in the dossier. |
| 2 | Steering as the unit of work — micro-corrections are the value-add | **NEW** | TLC's sub-agent contract (Pattern 6) standardizes the *boundary*, not the steering itself | Dossier treats steering as residual; memo elevates it to a primitive. |
| 3 | Prompt fidelity decay over long sessions ("LLMs frequently don't listen to the letter of the prompt; longer = more hit-and-miss") | **EXTENDS** | Per-file token budgets + health zones (Pattern 3); fresh subagent contexts (GSD 200K) | Dossier addresses *retrieval* degradation; memo adds *instruction-adherence* degradation as a distinct decay axis. |
| 4 | Custom rules are necessary but insufficient; need deterministic verification on top | **ALIGNS** | Pattern 16 (Constitution as governance) + GSD verifier + TLC test-as-spec | Dossier already separates rules-as-governance from gates-as-enforcement. |
| 5 | Vertical-slice constraint — force one end-to-end slice before broad sweeps | **EXTENDS** | Pattern 5 escape valve ("Execute always lists steps inline; if >5 STOP") | Pattern 5 *catches* over-broad work; memo *positively constructs* the first slice as a deliverable shape. |
| 6 | Diagnose-before-fix — explicit root-cause hypothesis required before any fix | **ALIGNS** | Pattern 8 (Diagnose-into-PLAN); GSD `gsd-debugger` writes new `PLAN.md` from root cause | Memo extends scope of this gate to *all* non-trivial errors, not just verify-time UAT failures. |
| 7 | Test-quality gates beyond coverage (flag duplicated assertions, redundant new tests) | **EXTENDS** | Pattern 11 (Test-as-Spec, SPEC_DEVIATION); TLC Test Integrity Check on count delta | Pattern 11 prevents *weakening*; memo adds a *redundancy / over-generation* dimension orthogonal to it. |
| 8 | Reuse-awareness pre-check — search codebase for existing components before generating new ones | **NEW** | Graphify's `query_graph` / `get_neighbors` could implement it, but it is not framed as a pre-generation gate anywhere in the dossier | Real plug-in point for Graphify-style codebase navigation. |
| 9 | DX guardrails — preserve one-command run, hot reload, single build flow | **NEW** | None. Dossier covers correctness gates, not developer-ergonomic gates. | Genuinely new gate category. |
| 10 | Artisanal fallback / stop conditions / step-token-iteration budgets that auto-pause | **ALIGNS** | TLC safety-valve table (7 stop conditions, max 3 diagnostic iterations); GSD `node_repair_budget: 2`; `/gsd-plan-review-convergence` stall detection | Strong direct analog. Memo adds the framing that sometimes the right move is *manual* completion of the slice. |
| 11 | "Go-wrong" log — team ritual of structured AI-induced friction telemetry | **NEW** | TLC `L-NNN` lessons (Pattern 4) capture per-project lessons; no team-level/cross-project telemetry equivalent | Useful extension target for Pattern 4. |
| 12 | Shift-left review — bake review at the IDE/pre-commit step, not at PR time | **EXTENDS** | Plan-checker loop (up to 3×) and `gsd-plan-checker`; GSD pre-commit hook validation | Dossier reviews *plans* early; memo adds reviewing *generated code* before commit, IDE-integrated. |
| 13 | Quality monitoring tuned for AI risks (duplication-sensitive CI gates) | **EXTENDS** | TLC Test Integrity Check (count delta only); no duplication-weighted code metric in dossier | Specific CI gate (e.g., higher Sonarqube/Codescene duplication weight) is new tooling guidance. |
| 14 | Custom rules as a versioned product with provenance back to "go-wrong" log | **EXTENDS** | Pattern 16 (Constitution as governance artifact) | Pattern 16 establishes the artifact; memo adds the *update loop* tied to telemetry. |
| 15 | Culture / environment / psychological safety shapes tool effectiveness (Hicks credit) | **OUT-OF-SCOPE** | None. Dossier is engineering-systems-only. | Out of scope for this dossier; would belong in a separate adoption-guidance file if one is created. |

## 3. NEW Items — Incorporation Proposals

**N1 — Three impact radiuses for defect routing**

- *Why:* Provides a defensible taxonomy for *why* gates should be asymmetric (Pattern 10 currently justifies asymmetry on cost-of-fix only). Maintainability-tier defects are systematically under-detected because they are invisible to less experienced reviewers — this is a strong design implication.
- *Proposed home:* `topics/self-healing-and-verification.md`, new subsection in §8 "Implications for Our Framework" (or as a new §1.1 "Defect Taxonomy"). Optionally promote to a new pattern in `topics/patterns-worth-stealing.md`.
- *Proposed text (insert into self-healing-and-verification.md §8):*
  > **Classify defects by impact radius before routing them to gates.** Böckeler's Memo #13 distinguishes three radiuses: (a) time-to-commit (caught by linters and unit tests in seconds), (b) team flow in the iteration (caught by reviewers in hours-to-days), and (c) long-term maintainability (caught by experienced engineers in weeks-to-years, if at all). Bigger radius = longer feedback loop = more dangerous. Asymmetric gates (Pattern 10) are an instance of this principle, but the dossier currently justifies asymmetry only on cost-of-fix. Routing a "redundant DI parameter" or "duplicated test" check at maintainability-radius requires a different gate and reviewer pool than a "commit fails to lint" check. Source: <https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html>.

**N2 — Steering as the unit of work**

- *Why:* The dossier optimizes the orchestrator/sub-agent boundary as if a clean handoff is the goal. The memo argues the *micro-corrections* between handoffs are the actual value-add and should be capturable. This reframes the design target.
- *Proposed home:* `topics/workflow-and-orchestration.md` §8 "Implications," new bullet. Possibly also a callout in `SUMMARY.md` §4 introducing the framing alongside the top patterns.
- *Proposed text (insert as new §8 bullet in workflow-and-orchestration.md):*
  > **Treat steering — not handoff — as the unit of work.** Böckeler's observation is that "even in successful sessions, I intervened, corrected and steered all the time, and often decided not to commit the changes" (<https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html>). A framework whose only first-class artifacts are PLAN/SUMMARY/VERIFICATION optimizes for the handoff but loses the steering signal that produced the handoff. A capturable steering-event log (what was redirected, why, which prompt edit was applied) is a candidate first-class artifact, distinct from the existing decision-coverage and SPEC_DEVIATION channels.

**N3 — Reuse-awareness pre-check**

- *Why:* AI re-implements existing components silently; the memo cites a concrete example of a duplicated UI component. A pre-generation "have we already built this?" gate has no analog in the dossier despite Graphify being the obvious mechanism.
- *Proposed home:* `topics/patterns-worth-stealing.md`, new pattern in Group C (Verification and Quality), or as an extension under Pattern 13 (Confidence Tagging) since both rely on grounded codebase analysis.
- *Proposed text (new pattern entry):*
  > ### Pattern 20: Reuse-Awareness Pre-Check
  > - **Origin:** Inferred from Böckeler Memo #13 examples; Graphify's `query_graph` / `get_neighbors` is the natural mechanism.
  > - **Problem it solves:** Generative agents re-implement existing components instead of importing them, producing duplication that pollutes the codebase and degrades modularity over time. The defect surfaces only at code review or never.
  > - **How it works:** Before a `gsd-executor`-equivalent generates a new component, a pre-step queries a codebase index (Graphify graph, ripgrep, ast-grep) for symbols semantically close to the requested API surface. Hits surface as a "candidate-for-reuse" list that the executor must address (use, extend, or explicitly justify ignoring) before generation proceeds.
  > - **Transferability:** HIGH for any framework that uses brownfield codebase mapping. Pairs naturally with Pattern 13 (Confidence Tagging) — `EXTRACTED` matches are higher-priority candidates than `INFERRED` ones.
  > - **What to adapt:** A pre-generation step in the executor's prompt template that runs the index query and injects results; a "must address each candidate" output contract field. Source: <https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html>.

**N4 — DX guardrails**

- *Why:* The dossier's gates concentrate on correctness; the memo identifies a separate failure class — agents breaking developer ergonomics (two start commands, broken hot reload, multi-step builds). This is gate-able but no gate exists.
- *Proposed home:* `topics/self-healing-and-verification.md`, new subsection (e.g., §2.4 "DX Gates" or a new §9 "Beyond Correctness: Ergonomic Gates"). Could also be added to the framework's eventual rules registry as a standing principle.
- *Proposed text (new subsection in self-healing-and-verification.md):*
  > ### 9. Ergonomic Gates: Beyond Correctness
  > Correctness gates (does the test pass?) miss a category of regressions that Böckeler highlights: AI agents that break the developer experience even when the code works. Concrete examples from Memo #13 — introducing a second start command instead of unifying with the existing one, breaking hot reload, over-complicating the build pipeline. These regressions degrade team flow (radius b) and maintainability (radius c) without being caught by any test. A complementary gate set — "the project must still start with one command," "hot reload must still trigger on save," "the build pipeline gains no new mandatory steps without explicit approval" — would catch them at commit time. Source: <https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html>.

**N5 — "Go-wrong" log as team ritual**

- *Why:* TLC's `L-NNN` lessons capture per-project learnings, but the memo's "go-wrong" log is a team-level, structured-telemetry-style ritual that feeds back into the rule registry. This is an extension of Pattern 4 with a different scope (team, not project) and a specific feedback loop.
- *Proposed home:* `topics/patterns-worth-stealing.md` as an addendum to Pattern 4, or `topics/self-healing-and-verification.md` §8 as a new bullet.
- *Proposed text (addendum to Pattern 4):*
  > **Extension — team-level "go-wrong" log.** Per-project `L-NNN` lessons capture knowledge inside one project's `STATE.md`, but they do not aggregate across projects or feed back into the rule registry. Böckeler describes a team ritual of weekly review of AI-induced friction (<https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html>) — every cataloged friction case becomes a candidate update to the custom-rules artifact (Pattern 16). Closing the loop requires (a) a cross-project log location, (b) a review cadence, (c) a provenance link from each rule to the friction case that motivated it.

## 4. EXTENDS Items — Augmentation Proposals

**E1 — Prompt fidelity decay (in addition to context bloat)**

- *Augment:* `topics/context-engineering.md` (not read this round) and/or `topics/self-healing-and-verification.md` §8.
- *Proposal:* Add an explicit acknowledgment that long sessions degrade *instruction adherence* in addition to retrieval quality. The memo's quote — "the longer a coding session gets, the more hit-and-miss it becomes" (<https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html>) — supports a checkpoint-and-re-anchor recommendation that is currently implicit in the per-file token budgets pattern.

**E2 — Vertical-slice as constructive constraint (not just escalation trigger)**

- *Augment:* Pattern 5 (Auto-Sized Pipeline with Hard Escape Valves) in `topics/patterns-worth-stealing.md`.
- *Proposal:* Add a positive corollary: "First slice must be end-to-end working before any breadth-pass is allowed." Memo example: AI tried to convert all components at once during a frontend migration instead of one component end-to-end. Pattern 5 already catches >5-step plans; this addition forces the *shape* of the first deliverable (one slice through the stack), not just its size.

**E3 — Diagnose-before-fix as a universal step, not just UAT-time**

- *Augment:* Pattern 8 (Diagnose-into-PLAN) in `topics/patterns-worth-stealing.md`.
- *Proposal:* Add: "The same diagnose-into-PLAN principle should apply at execute-time, not only at verify-time. When a within-wave failure occurs, `node_repair` should require an explicit root-cause statement before retry, mirroring the `gsd-debugger` artifact." Memo cites AI raising Docker memory limits instead of asking why memory was high — a brute-force fix path that node_repair currently allows.

**E4 — Test-quality gates: redundancy axis**

- *Augment:* Pattern 11 (Test-as-Spec and SPEC_DEVIATION) in `topics/patterns-worth-stealing.md`.
- *Proposal:* Add a redundancy/over-generation axis to the existing immutability axis. Concrete: a lint or reviewer-agent gate that flags new tests with assertions duplicating existing tests, or with no assertion that fails when the new behavior is broken. Memo: "More tests are not necessarily better."

**E5 — Shift-left review at the IDE / pre-commit boundary**

- *Augment:* `topics/self-healing-and-verification.md` §2 (GSD Plan-Time Gates) — or a new "Code-Time Gates" subsection.
- *Proposal:* The dossier reviews *plans* early (`gsd-plan-checker` 3×) but reviews *generated code* primarily at PR time. Add a pre-commit, IDE-integrated reviewer-agent step that examines diff-level concerns (DI redundancy, inline CSS instead of variables, over-engineering) before the commit lands.

**E6 — Quality monitoring with AI-tuned weights**

- *Augment:* `topics/auxiliary-tooling.md` (not read) or Pattern 11 in `patterns-worth-stealing.md`.
- *Proposal:* CI templates should ship with duplication-sensitivity raised relative to typical defaults — Memo argues AI-induced duplication is structurally more common than human-authored duplication.

**E7 — Custom rules as a versioned product with provenance**

- *Augment:* Pattern 16 (Constitution as Governance Artifact) in `patterns-worth-stealing.md`.
- *Proposal:* Pattern 16 establishes that the constitution is a first-class file. Add: it should be versioned, and each rule should carry provenance back to the friction case that motivated it (link to N5's "go-wrong" log entry).

## 5. Contradictions

None identified. The memo's claim that "rules are necessary but insufficient — LLMs may ignore them" is consistent with the dossier's emphasis on layering deterministic gates (lint, tests, hooks, verifier) on top of governance artifacts (TLC's `coding-principles.md`, GSD's `STATE.md`, Spec Kit's constitution). The memo does not push back on any specific dossier mechanism.

## 6. Items Rejected

- **"AI will not write 90% of code autonomously in a year"** — Out of scope. Industry forecast, not a framework-design implication.
- **The personal-skill list itself** (critical review, pattern recognition, architectural awareness, DI-chain awareness, requirements discipline) — Out of scope as patterns; these are *human* skills, not framework mechanisms. They inform the *content* of a rule registry but are not patterns to extract directly.
- **Culture / psychological safety / org pressure (Hicks credit)** — Out of scope for an engineering-systems dossier. Belongs in a separate adoption-guidance document if one is created. Noted explicitly so it is not lost.
- **Specific anecdotes** (Docker arch issue, two start commands, JSON-display web component) — Useful as illustrative quotes but not directly portable as patterns; the *pattern abstractions* above (DX guardrails, root-cause-first, restraint-against-over-engineering) cover the ground.

## 7. Reviewer Confidence

**MEDIUM.**

Topic files read in full this review:
- `research/SUMMARY.md`
- `research/topics/patterns-worth-stealing.md`
- `research/topics/self-healing-and-verification.md`
- `research/topics/workflow-and-orchestration.md`

Topic files not read (per scoping instructions): `context-engineering.md`, `local-storage-and-artifacts.md`, `auxiliary-tooling.md`, `multi-runtime-support.md`, and the four framework deep-dives. Confidence is reduced because:
- E1 (prompt fidelity decay) likely overlaps with `context-engineering.md` content I did not verify.
- E6 (CI quality monitoring) likely overlaps with `auxiliary-tooling.md` content I did not verify.
- The specific reuse-awareness pre-check (N3) may already be discussed in `frameworks/graphify.md`; I assumed not based on dossier-level mentions of `query_graph` as a query primitive rather than a pre-generation gate.

If those files are read in a follow-up pass, expect 1–2 EXTENDS rows to migrate to ALIGNS, but no NEW rows to be eliminated — the impact-radius taxonomy, steering-as-unit-of-work, "go-wrong" log ritual, and DX guardrails have no plausible home in the unread files.
