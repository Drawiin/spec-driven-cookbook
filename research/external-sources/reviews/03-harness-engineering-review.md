# Review — Harness Engineering vs. Research Dossier

> Compared: research/external-sources/summaries/03-harness-engineering.md ↔ research/SUMMARY.md (+ relevant topic files)
> Reviewer date: 2026-05-24

## 1. Alignment Snapshot (1–5 + one paragraph)

**Score: 4 / 5 — high alignment with substantive additions.**

The Harness Engineering article and the dossier are studying the same object (the structured-control system around an AI coding agent) from complementary angles. The dossier inventories *concrete mechanisms* observed in seven frameworks (plan-checker loops, decision-coverage gates, slopcheck, Nyquist auditor, SPEC_DEVIATION markers, lockfiles) and groups them by *timing* (pre-code / execute-time / post-execute) and by *transferability rank*. The article supplies a unifying *vocabulary and conceptual axes* the dossier currently lacks: feedforward-vs-feedback (Guides/Sensors), deterministic-vs-LLM (Computational/Inferential), and a regulation-category split (Maintainability/Architecture/Behaviour). Most dossier patterns map cleanly onto the article's taxonomy without contradiction. The genuinely *new* ideas the dossier should absorb are: (1) the Guides/Sensors pairing rule, (2) the Approved Scenarios pattern as a primitive for AI-generated behaviour tests, (3) the steering loop as a meta-pattern that turns recurring failures into harness updates rather than retries, and (4) "harnessability" as a tech-stack evaluation input. One small but high-value addition is the article's prescription that sensor output should embed agent-actionable remediation prompts — the dossier mentions verifier output but does not standardise this.

---

## 2. Findings Table (8–15 rows)

| # | Article concept | Dossier counterpart (if any) | Classification | Notes |
|---|---|---|---|---|
| 1 | Outer harness as a first-class, specified, versioned artifact | Implicit across `gsd.md`, `tlc-spec-driven.md`; no unifying term | EXTENDS | Dossier treats verifiers/checkers as first-class but has no umbrella concept tying them to guides (skills/AGENTS.md/constitution). |
| 2 | Guides (feedforward) vs Sensors (feedback) taxonomy; every control is one or both | Dossier groups gates by *timing* (pre/during/post) only | NEW | Crosscuts existing GSD/TLC/Spec-Kit gate inventories. Strong fit for patterns file. |
| 3 | Computational vs Inferential controls (deterministic vs LLM-based) | Implicit: slopcheck/lint = deterministic; gsd-verifier/plan-checker = inferential, but never labelled | NEW | Useful cost-tier label; supports decisions about what to run pre-commit vs at phase gates. |
| 4 | "Quality-left" lifecycle distribution (pre-commit / in-agent / pipeline / drift) | `self-healing-and-verification.md` §8: "Verify at the cheapest moment" | ALIGNS | Article supplies a richer four-slot vocabulary; dossier's framing is the same idea phrased differently. |
| 5 | Custom sensor messages embed remediation instructions for the agent ("positive prompt injection") | GSD `gsd-debugger` produces a fix `PLAN.md`; no standard for lint/judge outputs to embed remediation | EXTENDS | Worth standardising as a verifier-output field. |
| 6 | Three regulation categories: Maintainability, Architecture fitness, Behaviour — with distinct maturity | Dossier categorises gates by stage and dimension (decision coverage, requirements coverage, schema drift), not by regulation target | NEW | Important honesty signal: behaviour harness is the unsolved one — guards against "verified" claims that are really just "tests pass". |
| 7 | Fitness Functions (Thoughtworks Radar) as architecture-fitness controls | Not present | NEW | Architecture-level continuous tests (e.g., ArchUnit, dependency-cruiser) are absent from the dossier. |
| 8 | Approved Scenarios pattern (Lex Lerumph's *Augmented Coding Patterns*): input+expected fixtures, runner regenerates, reviewer diffs | TLC has "tests are the spec / RED tests immutable" — different primitive | NEW | Specifically addresses AI-generated tests, where TLC's immutability rule is awkward. Complements Pattern 11, doesn't replace it. |
| 9 | Harnessability: typed langs / clear module boundaries / opinionated frameworks help; legacy hurts | Not present as an evaluation lens; OpenAI Codex layered architecture mentioned only in passing in OpenAI link | NEW | Architectural choice should be partly evaluated on harness-supportiveness. |
| 10 | Harness templates bundled per service topology | Pattern 15 (Install-Time Profile + Surface Toggle) is adjacent — install-time/runtime composition of skill clusters | EXTENDS | Article's "templates per service topology" is a different cut (vertical bundle per service archetype, not horizontal feature toggle). |
| 11 | Steering loop: human iteratively updates the harness when same failure recurs; agents help build new controls | Pattern 8 (Diagnose-into-PLAN) fixes the *instance*; no mechanism for "the same failure mode recurred N times, update the rules/sensors" | EXTENDS | Genuine gap. A new task type ("harness-update") fits the dossier's spec-driven model. |
| 12 | Cybernetic framing: governor, Ashby's Law (requisite variety), ambient affordances | Not present | NEW | Useful diagnostic frame: "does the harness have enough variety to regulate the agent's variety on this task?" |
| 13 | "Harness coverage" — open: no code-coverage-equivalent metric for harness quality | Not present | NEW | Belongs in SUMMARY §7 Open Questions; a candidate for framework innovation. |
| 14 | Behaviour harness is honestly unsolved | Implied by dossier's gap (no behavioural-coverage primitive beyond test counts) | ALIGNS | Article's honesty about this should be reflected explicitly. |
| 15 | OpenAI Codex write-up cited: "designing environments, feedback loops, and control systems" | Not in dossier | OUT-OF-SCOPE | Useful citation but vendor-specific; belongs as a source reference rather than a dossier section. |

---

## 3. NEW Items — Incorporation Proposals

### N1. Guides/Sensors Taxonomy as a Pattern

- **Why:** Crosscuts every gate already inventoried; tagging each rule/skill/verifier as `guide`, `sensor`, or both forces designers to notice when a spec is unverifiable (a guide with no paired sensor) or when a sensor exists for behaviour no spec actually requires.
- **Proposed home:** `research/topics/patterns-worth-stealing.md` — add as a new Group C entry (Verification and Quality), and reference from `research/topics/self-healing-and-verification.md` §1.
- **Proposed text:**
  > **Pattern 20: Guides + Sensors Taxonomy**
  > *Origin: Harness Engineering (Martin Fowler / Birgitta Böckeler [inference], 2026-04-02 — https://martinfowler.com/articles/harness-engineering.html)*
  > Every control in an agent harness is either a **guide** (feedforward — anticipates misbehaviour and steers before action, e.g., AGENTS.md, skills, code-mod recipes, LSP access) or a **sensor** (feedback — observes after the act and surfaces signals optimised for LLM consumption, e.g., lints, type checks, LLM-as-judge, fitness functions). Either alone is insufficient: guides without sensors cannot be verified; sensors without guides surface failures the agent has no instruction to avoid. **Adapt:** require every load-bearing rule to declare which axis it serves; for any "spec" item, require a paired sensor that proves the spec held — otherwise mark the spec unverifiable.

### N2. Computational vs Inferential Control Axis

- **Why:** Lets the framework cost-tier verifications (cheap deterministic checks every step; expensive LLM judgments only at gates). Maps directly onto the dossier's pre-commit / phase-verify / milestone-audit timing tiers.
- **Proposed home:** `research/topics/patterns-worth-stealing.md` (companion to N1) and a one-line addition to `research/topics/self-healing-and-verification.md` §7 comparison table.
- **Proposed text:**
  > **Pattern 21: Computational vs Inferential Control Labelling**
  > *Origin: Harness Engineering — https://martinfowler.com/articles/harness-engineering.html*
  > Each control carries a second axis label: **computational** (deterministic — linters, type checkers, fitness functions, structural/architectural tests, mutation tests) or **inferential** (LLM-based — AI review, LLM-as-judge, semantic diff). The label is a cost and reliability hint that drives lifecycle placement: cheap deterministic checks belong on the hot path (pre-commit, in-agent), expensive inferential checks belong at phase or milestone gates. **Adapt:** every dossier-inventoried gate should carry a `{guide|sensor}` + `{computational|inferential}` pair (e.g., `slopcheck` = sensor/computational; `gsd-verifier` = sensor/inferential; AGENTS.md = guide/computational; LLM-judge plan review = sensor/inferential).

### N3. Approved Scenarios as a Behaviour-Test Primitive

- **Why:** The dossier has no answer for AI-generated tests except TLC's immutability rule, which is awkward when the tests themselves were AI-generated. Approved Scenarios make the *fixture* (input + expected output) reviewable by diff and regenerable, which is a better fit for noisy AI-authored tests than the RED-test-immutability stance.
- **Proposed home:** `research/topics/patterns-worth-stealing.md` Group C (next to Pattern 11 Test-as-Spec, explicitly noted as complementary).
- **Proposed text:**
  > **Pattern 22: Approved Scenarios for AI-Generated Behaviour Tests**
  > *Origin: Lex Lerumph, *Augmented Coding Patterns* — Approved Scenarios (https://lexler.github.io/augmented-coding-patterns/patterns/approved-scenarios/), surfaced via Harness Engineering.*
  > Behaviour tests are stored as domain-friendly fixture files combining an input and its expected output. The runner regenerates the expected-output side on demand; the reviewer's job is a diff review, not assertion authorship. This separates "is this the right behaviour?" (human judgment, by diff) from "does the code still produce this output?" (mechanical check). Complements Pattern 11: RED-phase contract tests remain immutable, but AI-generated *fixture* tests use the approved-scenarios protocol. **Adapt:** offer it as a first-class behaviour-harness primitive for phases that ship workflows, prompts, or agent loops — domains where assertion-style tests are noisy and review-by-diff is more honest.

### N4. Three Regulation Categories (Maintainability / Architecture / Behaviour)

- **Why:** Dossier verification dimensions today (decision coverage, requirements coverage, schema drift) describe *what is checked*; the article's three categories describe *what the check regulates*. The Behaviour category being honestly labelled "unsolved" is itself valuable — it stops "tests pass + manual QA" from being claimed as a behaviour harness.
- **Proposed home:** `research/topics/self-healing-and-verification.md` §8 (Implications) — add as a new bullet; and one row in the §7 cross-framework table headed "Regulation category coverage".
- **Proposed text:**
  > **Regulate by category, not just by stage.** The Harness Engineering article (https://martinfowler.com/articles/harness-engineering.html) splits controls into three regulation targets: *maintainability* (linters, type checkers, code-mod recipes), *architecture fitness* (Fitness Functions, dependency rules, layered-architecture checks), and *behaviour* (functional correctness — the unsolved one). A new framework should make verification phases category-aware and refuse to claim "verified" when only the maintainability harness is in place. The behaviour harness should be explicitly the weakest link until a behaviour primitive (e.g., Approved Scenarios — see Pattern 22) is wired in.

### N5. Steering Loop as a Harness-Update Task Type

- **Why:** Pattern 8 (Diagnose-into-PLAN) repairs the *instance*; it does not encode "this kind of failure has now recurred, update the rules so it stops". Without a steering loop, every recurrence is paid for at full cost.
- **Proposed home:** `research/topics/workflow-and-orchestration.md` §8 (Implications) — new bullet; cross-link from `self-healing-and-verification.md` §3 (Diagnose-into-PLAN) as a complementary loop.
- **Proposed text:**
  > **Repair-the-instance vs update-the-harness are two different loops.** The dossier's diagnose-into-PLAN pattern handles individual verification failures, but the Harness Engineering article (https://martinfowler.com/articles/harness-engineering.html) names a second loop: when the *same kind* of failure recurs N times, the human (or an agent under human supervision) should add a guide or sensor so it stops recurring. Add a `harness-update` task type that triggers automatically when the failure classifier records the same root-cause class above a threshold within a milestone. Agents themselves can be used to draft the new control (a new lint rule, a new judge prompt, an AGENTS.md addition).

### N6. Harnessability as an Architectural-Decision Input

- **Why:** The dossier's framework-comparison axes do not include "how harness-supportive is the underlying tech stack?" Yet the article's claim — "the harness is most needed where it is hardest to build" — flips this into a first-class design concern.
- **Proposed home:** `research/SUMMARY.md` §7 Open Questions (new bullet); optionally a paragraph in `research/topics/patterns-worth-stealing.md` Group D.
- **Proposed text:**
  > **Open question: harnessability as a stack-evaluation criterion.** The Harness Engineering article (https://martinfowler.com/articles/harness-engineering.html) argues that typed languages, clear module boundaries, and opinionated frameworks materially improve how well an outer harness can exist on top of them. The dossier does not currently evaluate frameworks (or their target codebases) on this axis. For a new framework, an explicit harnessability heuristic — "does this stack admit cheap, deterministic guides and sensors at the boundaries that matter?" — belongs alongside cost and DX in tech-selection guidance. Cited example: OpenAI Codex layered architecture (https://openai.com/index/harness-engineering/).

### N7. Cybernetic Framing / Ashby's Law as a Diagnostic

- **Why:** Lightweight conceptual frame. The "requisite variety" question — does the harness have enough variety to regulate the agent's variety on this task? — is a usable diagnostic when a phase is repeatedly failing despite tooling investment.
- **Proposed home:** `research/SUMMARY.md` §1 (About This Dossier) — one-sentence framing addition; not a standalone pattern.
- **Proposed text (optional sidebar):**
  > Cited framing: the Harness Engineering article (https://martinfowler.com/articles/harness-engineering.html) describes the harness cybernetically as a "governor" subject to **Ashby's Law of Requisite Variety** — the harness must have at least as much regulatory variety as the agent has behavioural variety. A practical diagnostic: when a phase fails repeatedly despite added controls, the harness probably lacks variety; narrow the scope or add a control of a different *kind* (a new sensor type, not another instance of the same).

### N8. Harness Coverage as an Emerging Metric

- **Why:** Honest open question worth flagging alongside the dossier's existing "Open Questions and Unverified Items".
- **Proposed home:** `research/SUMMARY.md` §7 Open Questions — new bullet.
- **Proposed text:**
  > - **Open question: no "code-coverage equivalent" for harness quality.** The Harness Engineering article (https://martinfowler.com/articles/harness-engineering.html) flags this as an unresolved problem. Possible directions for a new framework: percentage of REQ-IDs with paired sensors; percentage of D-IDs with paired remediation prompts; ratio of guides-without-sensors to total guides.

---

## 4. EXTENDS Items — Augmentation Proposals

### E1. Outer Harness as a Unifying Frame for Existing Dossier Patterns

- **Existing:** SUMMARY §4 lists 10 patterns ranging across context, workflow, and verification; no unifying narrative ties them as parts of an "outer harness".
- **Proposed augmentation:** Add a single framing paragraph to SUMMARY §4 introducing "outer harness" as the umbrella for Patterns 8, 10, 11, 14 (the verification/quality patterns) — explicitly Guides (constitution, AGENTS.md, sub-agent context contract = Pattern 6 / 16) and Sensors (decision coverage gate = Pattern 10, package legitimacy gate = Pattern 14, test-as-spec markers = Pattern 11, plan-checker, gsd-verifier). Citation: https://martinfowler.com/articles/harness-engineering.html.
- **Why:** Improves the dossier's readability for designers without changing any pattern content; gives newcomers a single mental model the inventory then fills in.

### E2. Standardise Remediation-Embedded Verifier Output

- **Existing:** `self-healing-and-verification.md` §2–3 describe `gsd-verifier` output and the debugger's diagnosis line, but there is no general rule that lint/judge/verifier outputs should embed an agent-actionable remediation prompt.
- **Proposed augmentation:** Add to `self-healing-and-verification.md` §8 (Implications):
  > **Sensor output should embed remediation, not just diagnose.** The Harness Engineering article (https://martinfowler.com/articles/harness-engineering.html) describes custom-linter messages that include self-correction instructions as a "positive kind of prompt injection". Standardise verifier output as a triple: `{finding, evidence, agent_remediation_prompt}`. The third field is what lets the next loop iteration act, not just re-read the failure.
- **Why:** Cheap addition; turns existing GSD/TLC verifier outputs from "what's wrong" into "what's wrong and what to do" without restructuring the gate system.

### E3. Quality-Left Lifecycle Distribution

- **Existing:** `self-healing-and-verification.md` §8 already says "Verify at the cheapest moment" — same intuition.
- **Proposed augmentation:** Cite the article and replace the single bullet with a four-slot distribution: **pre-commit** (computational guides/sensors only) / **in-agent** (computational sensors + lightweight inferential guides) / **pipeline** (heavier inferential sensors at phase gates) / **continuous drift** (out-of-lifecycle sensors — dead-code, coverage quality, dependency scans, runtime SLO monitoring). Forbid expensive inferential checks on the hot path.
- **Why:** Adds operational precision to the existing implication without contradicting it.

### E4. Harness Templates per Service Topology

- **Existing:** Pattern 15 (Install-Time Profile + Surface Toggle) handles horizontal cluster toggles; per-phase-type starter packs are not present.
- **Proposed augmentation:** Add a one-paragraph note under Pattern 15 in `patterns-worth-stealing.md`:
  > A complementary axis (Harness Engineering — https://martinfowler.com/articles/harness-engineering.html, §Harness templates): bundle vertical "harness templates" per phase type or service topology (API service, data pipeline, AI integration, frontend SPA). Each template ships an AGENTS.md skeleton, lint config, judge prompts, and a starter VALIDATION.md. Templates share the same drift problem as service templates — they need a refresh story.
- **Why:** Cleanly extends an existing pattern without inventing a new one.

---

## 5. Contradictions

**None directly contradictory.** Two tensions worth noting:

- **TLC test immutability vs Approved Scenarios.** TLC's RED-test immutability rule (Pattern 11) assumes hand-authored contract tests. Approved Scenarios are designed to be regenerable with diff review. These are not contradictory if applied to different test types — RED contract tests remain immutable; AI-generated *fixture* tests use approved scenarios — but the dossier should be explicit about this scoping if it adopts Pattern 22, otherwise a future reader will see the two rules as competing.
- **GSD's diagnose-into-PLAN repair loop vs the steering loop.** Not a contradiction; they operate at different cadences (instance vs class). The dossier should make this distinction explicit if both are described, to avoid readers conflating "rerun the same plan with a fix" (instance repair) with "add a new rule so this class of failure stops happening" (harness update).

---

## 6. Items Rejected (with rationale)

| Item | Rationale for rejection / deferral |
|---|---|
| Verbatim citation of the OpenAI Codex "harness engineering" write-up as a dossier section | Useful citation, but vendor-specific anecdote rather than transferable pattern. Add as a source reference under N6 (Harnessability) — do not promote to its own dossier section. |
| Importing all of Birgitta Böckeler's *Exploring Gen AI* failure-mode catalogue (degree-1 link `13-role-of-developer-skills.html`) | Out of scope for this review — it would double the dossier's surface and is one author's view. If absorbed later, it belongs in a separate review pass, not this one. |
| Full cybernetic governor diagram / Ashby's Law deep dive as a standalone topic file | Too abstract for the dossier's empirical bias. Capture as the one-paragraph framing in SUMMARY §1 (N7) and stop there. |
| "Behaviour harness as an entirely new topic file" | Premature. The article itself admits behaviour is unsolved; the right move is to flag it in §8 implications (N4) and in §7 open questions (N8), not to spin up a topic file with thin content. |
| Replacing dossier's pre/during/post-code timing axis with the article's Guides/Sensors axis | Both axes are useful and orthogonal. Layer them; do not replace. |

---

## 7. Reviewer Confidence (HIGH/MEDIUM/LOW + which topic files read)

**Confidence: MEDIUM-HIGH.**

- **HIGH** on the classification (ALIGNS/EXTENDS/NEW) of each article concept: the source summary is structured and explicit, and the dossier files relevant to the article's themes were read in full.
- **MEDIUM** on the proposed homes for NEW items: the dossier's authors may prefer a different placement (e.g., a new short topic file `harness-engineering.md` rather than scattered additions across `patterns-worth-stealing.md` and `self-healing-and-verification.md`). The proposals are defensible but not the only sensible choice.
- **MEDIUM** on the Approved Scenarios proposal: the underlying source (Lex Lerumph) was *not* re-fetched in this review pass — only the article's summary of it. Anyone implementing it should follow the canonical URL (https://lexler.github.io/augmented-coding-patterns/patterns/approved-scenarios/) before authoring framework support.
- **LOW** on whether the steering-loop "harness-update task type" (N5) is sized correctly without prototyping; the proposal is conceptually sound but operational details (when to trigger, who reviews) need a sketch before committing.

**Topic files read in full for this review:**

- `research/SUMMARY.md`
- `research/topics/self-healing-and-verification.md`
- `research/topics/patterns-worth-stealing.md`
- `research/topics/workflow-and-orchestration.md`
- `research/topics/auxiliary-tooling.md`

**Files deliberately NOT read** (judged off-theme for Harness Engineering): `topics/context-engineering.md`, `topics/local-storage-and-artifacts.md`, `topics/multi-runtime-support.md`, and the four `frameworks/*.md` deep dives (SUMMARY.md and the four read topic files supplied enough framework-specific anchors for this review).
