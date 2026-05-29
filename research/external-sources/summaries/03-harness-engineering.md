# Source Summary — Harness Engineering (Martin Fowler)

> URL: https://martinfowler.com/articles/harness-engineering.html
> Fetched: 2026-05-24

## 1. Thesis

"Harness engineering" is the practice of building an **outer harness** around a coding agent — a coordinated system of feed-forward "guides" and feedback "sensors", each either computational (deterministic) or inferential (LLM-based) — that raises the probability the agent gets a change right the first time and lets it self-correct before output reaches a human. The harness is framed cybernetically as a "governor" regulating the codebase toward a desired state; it externalises (imperfectly) the implicit experience of human developers, with the goal of *directing* — not eliminating — human attention.

## 2. Author & date / status

- Author: not explicitly named in the fetched body; published on Martin Fowler's site under the *Exploring Gen AI* series, primarily authored by Birgitta Böckeler at Thoughtworks [inference].
- Status: **published full article**, **02 April 2026**; supersedes the 17 February 2026 memo at `exploring-gen-ai/harness-engineering-memo.html` (now redirected).
- Explicitly framed as "a starting point — and open questions" mental model, not a prescriptive playbook.

## 3. Core ideas

- Borrows `Agent = Model + Harness` (LangChain) and narrows it: the **outer harness** is what users build on top of the agent's built-in harness (system prompt, retrieval, orchestration).
- Two goals: raise correct-first-attempt rate; provide a self-correcting loop *before* humans review.
- Two control directions: **Guides (feedforward)** and **Sensors (feedback)**. Either alone is insufficient.
- Two execution modes: **Computational** (linters, type checkers, structural/architectural tests, mutation tests — cheap, deterministic) and **Inferential** (LLM-as-judge, AI review — expensive, probabilistic).
- Custom sensor messages should embed remediation instructions for the agent — a "positive kind of prompt injection".
- "Keep quality left": distribute controls across the lifecycle (pre-commit, in-agent, pipeline, continuous drift) by cost and criticality.
- Three regulation categories: **Maintainability**, **Architecture fitness** (Fitness Functions), **Behaviour** — varying maturity; behaviour is the unsolved one.
- **Harnessability** varies: typed languages, clear module boundaries, opinionated frameworks help; legacy code needs harnessing most but supports it least.
- Speculative future: **harness templates** bundled per service topology, like service templates, with similar drift problems.
- Human's job is the **steering loop**: when an issue recurs, update the harness so it stops recurring. Agents themselves can help build new controls.

## 4. Practices / patterns named explicitly in the article

- **Guides (feedforward controls)** — anticipate misbehaviour and steer before action; e.g. AGENTS.md, Skills, code-mod recipes, LSP/code-intelligence access. *§Feedforward and Feedback.*
- **Sensors (feedback controls)** — observe after the act and surface signals optimised for LLM consumption. *§Feedforward and Feedback.*
- **Computational vs Inferential controls** — deterministic vs LLM/GPU-based judgment. *§Computational vs Inferential.*
- **Fitness Functions** — Thoughtworks Radar pattern used for the architecture-fitness harness. *§Architecture fitness harness.*
- **Approved fixtures pattern** (Lex Lerumph's *Augmented Coding Patterns*; cookbook redirects to "Approved Scenarios") — domain-specific approval files combining input + expected output to make AI-generated tests reviewable by diff. *§Behaviour harness.*
- **Steering loop** — human iteratively improves the harness on recurring issues. *§The steering loop.*
- **Quality-left / drift sensors** — out-of-lifecycle continuous sensors (dead-code, coverage quality, dependency scans, runtime SLO monitoring). *§Timing.*
- **Harness templates** — bundled, reusable harnesses tied to a service topology. *§Harness templates.*
- **Cybernetic framing**: governor, **Ashby's Law**, ambient affordances. *§Sidebars.*

## 5. Concepts directly relevant to spec-driven AI coding frameworks

- **Outer harness as a first-class artifact.** Treat the harness (rules, skills, sensors, evaluators) as something specified, versioned, verified — not ad-hoc prompts.
- **Feed-forward + feedback symmetry.** Every spec/convention encoded as a guide should have a paired sensor proving it held; otherwise the spec is unverifiable.
- **Computational vs inferential split.** Lets a framework cost-tier its checks: cheap deterministic checks every step; LLM judgments only at gates. Maps onto pre-commit / phase-verify / milestone-audit tiers.
- **Custom-linter messages as remediation prompts.** Verifier output should instruct the agent how to fix, not just flag — directly applicable to plan-/phase-checker findings.
- **Three regulation categories.** Specs should distinguish maintainability, architecture-fitness, and behaviour, and not pretend behaviour is solved by "more AI tests".
- **Approved scenarios as a primitive.** A concrete answer to noisy AI-generated tests; a strong candidate for behaviour harnesses inside spec-driven flows.
- **Harnessability as architectural input.** Tech-stack and module-boundary choices should be evaluated partly on how well they let an outer harness exist (cf. OpenAI Codex layered architecture).
- **Harness coverage as an emerging metric.** Open question: no "code coverage equivalent" for harness coverage/quality — a natural place for a spec-driven framework to innovate.
- **Steering loop = retro discipline.** Recurring failures should update the spec/rule/sensor — matches "pause / reflect / encode" steps in spec-driven workflows.

## 6. Mechanisms worth stealing

| Mechanism | Description | Adaptation suggestion |
| --- | --- | --- |
| Guides + Sensors taxonomy | Every control is feed-forward or feedback (or both). | Tag each rule/skill/verifier as `guide`, `sensor`, or both; require pairing for load-bearing rules. |
| Computational/Inferential matrix | Each control is also deterministic or LLM-based. | 2-axis label so reviewers see deterministic vs LLM cost of any phase verification. |
| Remediation-embedded sensor output | Lints/judges emit fix instructions, not just diagnostics. | Standardise verifier output: `finding`, `evidence`, `agent_remediation_prompt`. |
| Quality-left distribution | Cheap checks pre-commit; expensive checks pipeline-side; drift sensors continuous. | Map framework verifications to lifecycle slots; forbid expensive inferential checks on hot path. |
| Steering loop | Recurring agent mistakes drive harness updates, not retries. | Add a "harness-update" task type triggered when the same failure recurs N times in a milestone. |
| Approved scenarios pattern | Fixtures combine input + expected output in a domain-friendly format; runner regenerates, reviewer diffs. | Offer it as a first-class testing primitive for behaviour-heavy phases (workflows, prompts, agent loops). |
| Harness templates | Per-topology bundles of guides+sensors. | Provide starter packs per phase type (API service, data pipeline, AI integration) — AGENTS.md skeleton, lints, judge prompts. |
| Cybernetic framing | Harness as governor with requisite variety (Ashby). | Diagnostic question: "Does our harness have enough variety to regulate the agent's variety on this task?" If not, narrow scope or add controls. |
| Maintainability/Architecture/Behaviour split | Distinct dimensions with distinct maturity. | Make verification phases category-aware; don't claim "verified" if behaviour harness is just "tests pass + manual QA". |

## 7. Notable quotes

- "The term *harness* has emerged as a shorthand to mean everything in an AI agent except the model itself." — definitional (URL §intro).
- "A well-built outer harness serves two goals: it increases the probability that the agent gets it right in the first place, and it provides a feedback loop that self-corrects as many issues as possible before they even reach human eyes." (URL §intro).
- "Custom linter messages that include instructions for the self-correction — a positive kind of prompt injection." (URL §Feedforward and Feedback).
- "The agent harness acts like a cybernetic governor, combining feed-forward and feedback to regulate the codebase towards its desired state." (URL §Regulation categories).
- "The harness is most needed where it is hardest to build." (URL §Harnessability).
- "A good harness should not necessarily aim to fully eliminate human input, but to direct it to where our input is most important." (URL §The role of the human).
- Cited from the OpenAI Codex write-up: "Our most difficult challenges now center on designing environments, feedback loops, and control systems." (https://openai.com/index/harness-engineering/).

## 8. Pages fetched (degree 0/1/2)

- Degree 0: https://martinfowler.com/articles/harness-engineering.html
- Degree 1: https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html (failure-mode catalogue mapped against the Maintainability harness).
- Degree 1: https://openai.com/index/harness-engineering/ (real-world example — Codex, layered architecture, doc-gardening, golden principles).
- Degree 1: https://lexler.github.io/augmented-coding-patterns/patterns/approved-scenarios/ ("approved fixtures" referenced for the Behaviour harness; URL redirects from `approved-fixtures/`).
- Degree 2: none followed — no second-degree link was uniquely load-bearing given degree-1 coverage.

## 9. Pages attempted but failed

- https://martinfowler.com/articles/exploring-gen-ai/harness-engineering-memo.html — fetch timed out. Per the main article this is the superseded earlier memo with canonical content now in the degree-0 page; not reattempted to stay within token budget.

## 10. Confidence

**MEDIUM-HIGH.**

- HIGH on structure, taxonomy, named patterns, and direct quotes — full body was fetched cleanly and (unlike many short *Exploring Gen AI* memos) this is a full article with explicit categories and cited examples.
- MEDIUM on authorship: the series is primarily Birgitta Böckeler's, and voice/acknowledgements match, but the fetched HTML did not surface a byline, so attribution is marked [inference].
- MEDIUM on the Behaviour-harness section: the article itself is honest that this is unsolved; the summary preserves that. Anyone implementing a behaviour harness from this source alone should expect more research — the approved-scenarios pattern is the most concrete primitive offered.
- The superseded memo was not re-fetched after a timeout; risk of missing a load-bearing idea is low because the main article explicitly supersedes it.
