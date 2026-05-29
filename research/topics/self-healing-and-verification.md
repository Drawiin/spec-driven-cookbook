# Self-Healing and Verification

> Topic: Cross-cutting verification loops, gate systems, and self-repair mechanisms across spec-driven AI frameworks.
> Related: [../frameworks/gsd.md](../frameworks/gsd.md) · [../frameworks/tlc-spec-driven.md](../frameworks/tlc-spec-driven.md) · [../frameworks/graphify.md](../frameworks/graphify.md) · [../frameworks/adjacent-frameworks.md](../frameworks/adjacent-frameworks.md)

---

## 1. Overview: Why Self-Healing Matters

AI-generated code is evaluated at runtime, not at write time: the model has no feedback signal until the code runs against a test, a schema validator, or a human reviewer. Without structured verification loops baked into the workflow, each generation step drifts silently — passing syntax checks while violating requirements, missing decisions reached in earlier discussions, or relying on packages that do not exist. GSD's README states the problem directly: "Code that 'runs' isn't code that 'works.'" Self-healing frameworks close that gap by making verification a first-class primitive — not an afterthought — and by feeding failure signals back into the same generation loop that produced the failure, rather than requiring a separate recovery mode.

The frameworks surveyed take three distinct approaches: layered pre-code and post-code gates with automatic repair loops (GSD), inline stop-the-line safety valves with test-as-contract immutability (TLC), and structural epistemic tagging that prevents fabricated claims from entering the data model in the first place (Graphify). These approaches are complementary and together define the design space any new framework must navigate.

---

## 2. GSD: Layered Gate System

GSD's verification is organized into three distinct layers. Each layer either passes cleanly or produces a diagnosed artifact that the next loop iteration consumes. The result is a pipeline where failure is never silent — it always produces a structured artifact describing what failed and what to do next.

See also: [./workflow-and-orchestration.md](./workflow-and-orchestration.md) for how waves and orchestrators interact with these gates.

### Plan-Time Gates (Before Any Code Is Written)

**Plan-checker loop.** After the `gsd-planner` agent produces a `PLAN.md`, the `gsd-plan-checker` agent reviews it against an 8-dimension check. If any dimension fails, the planner is re-invoked. The loop runs up to 3 times before the plan is accepted. The 8 dimensions are not enumerated in the publicly available docs but the loop-exit condition is explicit: all dimensions must pass.

**Research gate.** Planning is blocked if the phase's `RESEARCH.md` file contains unresolved open questions. The gate ensures that the planner never works from incomplete research — it forces resolution of ambiguity before any code structure is committed to.

**Package Legitimacy Gate.** During the research phase, `gsd-phase-researcher` runs `slopcheck install --json` on every package recommended by any research agent (including those discovered through web search, which GSD treats as `[ASSUMED]` by default). The results are written as a `## Package Legitimacy Audit` table into `RESEARCH.md` with five columns: Registry, Age, Downloads, Source Repo, and Verdict. Verdicts have four values:

- `[SLOP]` — package stripped entirely from the plan; no install task is generated.
- `[SUS]` — package flagged as suspicious; planner injects a `checkpoint:human-verify` task before any install task.
- `[ASSUMED]` — package not verified; same treatment as `[SUS]` (human checkpoint injected).
- `[OK]` — package passes; install proceeds normally.

This gate addresses slopsquatting and hallucinated package names before a single line of code is written. See also: [./auxiliary-tooling.md](./auxiliary-tooling.md) for `slopcheck` details.

**Requirements coverage gate.** Every `REQ-ID` defined in `REQUIREMENTS.md` must map to at least one plan before planning is considered complete. Unmapped requirements block phase progression.

**Decision coverage gate (BLOCKING).** After planning, GSD refuses to mark the phase as planned until every decision ID (`D-01`, `D-02`, …) from the `<decisions>` block in the phase's `CONTEXT.md` appears in at least one plan's `must_haves`, `truths`, or body. The gate names each missed decision ID explicitly in the error output — the agent is not told "some decisions are missing," it is told exactly which ones. This gate is blocking at plan-time. The same check runs at verify-time but is non-blocking there (see post-execute gates below). The reasoning is stated in the docs: "The blocking gate is cheap at plan time but hostile at verify time."

Decisions support two match modes: strict ID match (`D-01` substring) or a 6+-word verbatim phrase match for decisions that were recorded without a short ID tag. Explicit opt-out tags (`[informational]`, `[folded]`, `[deferred]`) suppress the gate for individual decisions.

**Nyquist validation.** Before any code is written, `gsd-nyquist-auditor` maps each phase requirement to a specific test command. The output is written to `XX-VALIDATION.md`. The name invokes the Nyquist sampling theorem: you must know how you will verify a requirement at the frequency it can fail before generating code that implements it. This artifact is written before execution begins and becomes the reference the post-execute `gsd-verifier` agent uses to confirm coverage. A requirement that has no mapped test command at this stage cannot be verified after execution — the gate forces the team to confront that gap before any code is generated, not after.

**ScanningRecipe accumulator (OpenRewrite extension).** OpenRewrite's `ScanningRecipe` formalizes the survey-then-edit pattern with a typed accumulator: scanners populate a structured object that the edit phase reads, never re-reading source files ([https://docs.openrewrite.org/concepts-and-explanations/recipes](https://docs.openrewrite.org/concepts-and-explanations/recipes)). Translated to AI workflows, the scan pass produces a typed project memo (deps used, patterns found, files matching predicates), and the edit pass consumes only that memo — not the whole repo and not the freeform research markdown. This is a sharper, typed alternative to the freeform `RESEARCH.md` → planner handoff used by GSD.

**Scope precondition gate (OpenRewrite extension).** Require every AI editing skill to ship with a deterministic precondition (glob, AST query, type predicate, or short search recipe). Preconditions, as defined in OpenRewrite ([https://docs.openrewrite.org/reference/yaml-format-reference](https://docs.openrewrite.org/reference/yaml-format-reference)), gate which files a skill may touch *before* the LLM is invoked. For LLM workflows this is the difference between "the model reads the whole repo" and "the model only sees the slice that matched a glob/AST query/type predicate". See Pattern 22 in `patterns-worth-stealing.md`.

**Shift-left code review (Developer Skills Memo #13 extension).** The dossier reviews *plans* early (`gsd-plan-checker` 3×) but reviews *generated code* primarily at PR time. Memo #13 ([https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html](https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html)) recommends a pre-commit, IDE-integrated reviewer-agent step that examines diff-level concerns (DI redundancy, inline CSS instead of variables, over-engineering) before the commit lands.

### Execute-Time Gates (During Code Generation)

**STATE.md file locking.** Parallel executor agents all write progress to `STATE.md`. To prevent read-modify-write races, GSD uses `STATE.md.lock` with `O_EXCL` atomic creation (a POSIX primitive that fails if the file already exists, making the lock creation itself atomic). Stale locks expire after 10 seconds. Waiting agents use a jittered spin-wait to avoid thundering-herd retries. All `writeStateMd()` calls route through this mechanism.

**Checkpoint heartbeats.** At every wave and plan boundary, the orchestrator emits a `[checkpoint] phase N wave W/M` log line. These serve as liveness signals for streaming runtimes that kill sessions on idle timeout. Without them, a long-running wave could be silently terminated mid-execution.

**Executor failure classifier.** The SDK module `sdk/src/query/agent-failure-classifier.ts` classifies executor failures into three categories — `quota-exceeded`, `classify-handoff-bug`, or `unknown-failure` — and selects a class-distinct recovery prompt for each. The classifier uses cross-runtime sentinel sets to detect quota signals regardless of which AI provider is running:

- Anthropic: `usage limit` / `rate limit` / `quota` / `429` / `retry-after`
- Copilot: `rate_limit`
- Codex: `429` / `usage_limit_reached` / `too many requests`
- Gemini: `RESOURCE_EXHAUSTED` / `exceeded your`

Class-distinct responses: `quota-exceeded` → wait for reset; `classify-handoff-bug` → spot check the handoff; `unknown-failure` → continue or stop based on user mode.

**Node repair.** `workflow.node_repair: true` (the default) combined with `workflow.node_repair_budget: 2` enables autonomous task repair on verification failure within a single execute pass. When a plan's verification step fails, the executor retries up to the budget limit before propagating the failure upward. This is distinct from the full `gsd-debugger` loop (which runs at UAT time) — node repair is a lightweight, same-executor retry for transient or single-step failures.

### Post-Execute Gates (After Code Generation)

**`gsd-verifier` agent.** After all executors for a phase complete, `gsd-verifier` reads the full artifact set — `PLAN.md`, `SUMMARY.md`, `REQUIREMENTS.md`, `CONTEXT.md`, `RESEARCH.md` (on 1M-context models, RESEARCH is also included for smaller models) — checks the output against the phase goal and the Nyquist validation map, and writes `VERIFICATION.md` with a PASS or FAIL verdict. The verifier operates in a fresh subagent context, so it cannot rationalize away failures by inheriting the executor's assumptions.

**Decision coverage gate (NON-BLOCKING).** The same D-id check that blocked at plan-time runs again at verify-time, but now it is non-blocking. It searches plans, `SUMMARY.md`, modified files, and recent commit messages for each tracked decision ID. Missed decisions are logged as a warning section in `VERIFICATION.md`, not as a gate failure. The rationale: blocking at verify-time would be hostile to the user after all the implementation work has been done, while warning preserves visibility.

**Schema drift gate.** After execution, GSD checks for ORM schema drift using Prisma and Drizzle patterns. If the codebase's schema has diverged from what the plan specified, this gate surfaces the discrepancy.

**Codebase drift gate.** After the last wave's commits, GSD compares `last_mapped_commit..HEAD` against `.planning/codebase/STRUCTURE.md` (the map produced by `/gsd-map-codebase`). When the number of structurally significant changes exceeds `workflow.drift_threshold` (default: 3), the behavior depends on `workflow.drift_action`: the default is a warning; setting it to `auto-remap` triggers an automatic re-run of `gsd-codebase-mapper` to refresh the structure map. This prevents the planning artifacts from becoming stale relative to the actual codebase state.

---

## 3. GSD: The Diagnose-into-PLAN Self-Healing Loop

The most architecturally significant design choice in GSD's self-healing system is what happens when `/gsd-verify-work N` finds a failure during UAT. Rather than entering a special "fix mode" with its own primitives and state, GSD invokes `gsd-debugger` — a ~47 KB agent, the largest in the system — which analyzes the failure, identifies a root cause, and writes the fix as a *new* `PLAN.md` file into the same phase directory. The user then re-runs `/gsd-execute-phase N`. Same command. Same loop. No new primitives.

This is architecturally clean for two reasons. First, the executor pipeline is already proven to correctly consume a `PLAN.md` and produce verified output — reusing it for fix plans means the fix path has exactly the same correctness guarantees as the original path. Second, the fix plan goes through the same plan-checker loop and pre-code gates described above, so a badly diagnosed fix is caught before it generates more broken code.

The USER-GUIDE.md provides a concrete example of the debugger's output format:

```
[3/3] Does a request with an invalid signature return 401 with { error: "invalid_signature" }?
> no — I'm getting a 500 instead
[Diagnosing...]
Root cause: middleware catches crypto.timingSafeEqual TypeError when buffers are
  different lengths. Fix: normalize to same length before compare.
Fix plan created: .planning/phases/01-core-middleware/01-03-PLAN.md
Run /gsd-execute-phase 1 to apply.
```

The user sees a root cause, not a generic "something failed." The fix plan is a first-class artifact with a path, not an ephemeral instruction set. And the recovery instruction is the same command they already know.

**Plan convergence loop.** For cases where multiple review cycles are needed, GSD provides `/gsd-plan-review-convergence`: a `plan-phase → review → replan → re-review` loop that runs up to 3 cycles by default (configurable via `--max-cycles`). The orchestrator tracks a HIGH-concern count across cycles. If the count is not decreasing between cycles — stall detection — it escalates rather than continuing to loop. When `--max-cycles` is reached without convergence, an escalation gate fires, surfacing the remaining concerns to the user rather than silently accepting a plan that never converged.

OpenRewrite extends this idea inside a single invocation: the recipe pipeline re-runs until no recipe changes anything, capped at 3 cycles by default, with each recipe self-declaring `causesAnotherCycle` when it knows its output may unblock another recipe ([https://docs.openrewrite.org/concepts-and-explanations/recipes](https://docs.openrewrite.org/concepts-and-explanations/recipes)). Adopting a per-skill 'may-need-another-cycle' flag lets agentic edits converge typecheck/format/test passes without bespoke control loops or fresh user-initiated runs.

---

## 4. TLC: Safety Valves and Test Integrity

TLC's approach to self-healing is lighter-weight and more distributed. Instead of a central verification agent, it places stop conditions at multiple points in the workflow and makes test immutability a hard behavioral rule.

### Safety Valve Table

The following table lists all seven stop-the-line conditions documented in the TLC skill:

| Where | Stop Trigger | Action |
|---|---|---|
| Execute (`implement.md`) | Inline-step listing reveals >5 steps | Stop; create formal `tasks.md` |
| Quick mode | Pre-impl check reveals >3 files, unclear dependencies, or design decisions needed | Recommend full pipeline |
| Execute Step 4b (GREEN phase) | A test seems "wrong" | Stop; ask user; never silently change a test |
| Execute Step 5 (Gate) | Non-zero exit code | Stop. Fix. Re-run. Do not proceed until green. |
| Validate Step 4 | Build-level gate fails | Stop; do not proceed to Code Quality Check |
| Validate Step 7 | Issue diagnosis | Max 3 diagnostic iterations per issue, then flag for human |
| Tasks (pre-approval) | Granularity, Diagram-Definition, or Test Co-location validation fails | Restructure; do not show failing tasks to user |

The "max 3 diagnostic iterations" rule at Validate Step 7 is an explicit anti-loop guardrail. Frameworks without this guard tend to spiral: the agent applies a fix, the test still fails, the agent applies a variation, and so on indefinitely. Capping iterations at 3 forces escalation to human judgment before the agent has burned significant context on a path it cannot complete autonomously. TLC's `validate.md` also defines a deterministic severity-inference table so the agent never needs to ask the user how serious a failure is — "crash" or "broken" maps to Blocker, "doesn't work" or "missing" maps to Major, "slow" or "weird" maps to Minor, and "color" or "font" maps to Cosmetic. Unclear reports default to Major. This removes a friction point that would otherwise slow the diagnostic loop.

### SPEC_DEVIATION Marker

When implementation reality forces a divergence from the specification, TLC requires the developer (or implementing sub-agent) to annotate the divergence inline:

```
// SPEC_DEVIATION: [what diverged]
// Reason: [why the deviation was necessary]
```

This marker is surfaced in the sub-agent's return report so the orchestrating agent can make a deliberate decision about whether the deviation is acceptable, rather than discovering the drift at review time. The marker preserves the spec as the authoritative document while acknowledging that implementation sometimes cannot match specification exactly. It also creates a searchable audit trail of every place where code and spec disagree.

### Test Integrity Guardrails

TLC's `coding-principles.md` and `implement.md` establish five hard rules about test behavior during implementation:

1. Never weaken assertions to make a test pass.
2. Never delete a test to reduce a failure count.
3. Never use `skip`, `disable`, or `pending` to bypass failures.
4. Never modify RED-phase tests during the GREEN phase.
5. "Tests are the spec — implementation conforms to tests, not the other way around."

The fifth rule is the load-bearing one. In TLC's RED→GREEN model, tests written during the RED phase are treated as immutable contracts. If the implementation cannot satisfy a RED test, the correct response is to surface the conflict (via `SPEC_DEVIATION` marker or direct escalation), not to mutate the test.

A Test Integrity Check runs at validation time: the current test count is compared against the pre-feature baseline count. Any decrease triggers an investigation. The check is intentionally blunt — even a single test deletion is treated as a signal worth examining.

### Scope Guardrails

TLC's scope controls are behavioral rules rather than file-based gates. During the Discuss phase, the agent is constrained to clarify *how* to implement existing capabilities, never to propose *whether* to add new ones. `discuss.md` makes the distinction explicit: "'How should posts be displayed?' (allowed — clarifying ambiguity) vs 'Should we also add comments?' (not allowed — new capability)."

During Execute, the test is simpler: "Is this in my task definition? If no, don't touch it." Any improvement noticed during implementation that falls outside the current task definition is routed to `STATE.md` as a Deferred Idea — captured for later, not acted upon in the current task. This prevents scope creep from accumulating silently inside what appears to be a focused implementation pass.

---

## 5. GitHub Spec Kit: Pre-Code Verification

Spec Kit's verification model is entirely pre-code. Rather than verifying after generation, it front-loads three structured verification steps that must complete before any implementation begins. This reflects a different philosophy: prevention over repair.

**`/speckit.clarify` — Coverage-based questioning.** Before `/speckit.plan` can run, `/speckit.clarify` must complete. The command runs a structured, sequential loop: one focused question at a time, recorded in a Clarifications section of the spec. The sequential (not all-at-once) design matters — each answer can inform subsequent questions, and the questioner avoids overwhelming the user with a long form that they fill out without context.

**`/speckit.analyze` — Cross-artifact consistency check.** Run after `/speckit.tasks` and before `/speckit.implement`. The command checks alignment across three artifacts: spec ↔ plan ↔ tasks. It is not a runtime check — it is a static consistency analysis that catches cases where the task list has drifted from the plan, or the plan has drifted from the spec, before a single line of code is generated.

**`/speckit.checklist` — "Unit tests for English."** Generates checklists that validate the spec itself, not the code. The framing is precise: a checklist item is to a spec what a unit test is to code. It forces the spec author (human or AI) to express the spec in terms that can be mechanically checked for completeness, unambiguity, and internal consistency. Failing a checklist item is a signal that the spec needs revision before planning begins.

Spec Kit does not provide post-code verification or self-repair mechanisms. Its contribution to this design space is entirely pre-code, which makes it complementary to GSD and TLC rather than competitive. A framework that combines Spec Kit's pre-code coverage questioning with GSD's post-code verifier and TLC's test-immutability rules would have verification gates at every major transition point: before planning, before implementation, during implementation, and after implementation.

---

## 6. Graphify: Confidence Tagging as Anti-Fabrication

Graphify takes a different approach to the verification problem: rather than verifying generated code, it addresses the epistemic reliability of the *analysis* that the AI assistant uses to reason about the codebase. Every relation in the knowledge graph carries a mandatory confidence tag:

- `EXTRACTED` — derived directly from source code via Tree-sitter AST parsing; no LLM inference involved.
- `INFERRED` — produced by LLM-driven semantic extraction from prose, diagrams, or non-code assets.
- `AMBIGUOUS` — the system could not determine the relation's basis with confidence.

This is anti-fabrication built into the data model. In prose-based frameworks, an AI assistant's analysis of a codebase arrives as natural language with no signal about whether a given claim is grounded in the actual source or generated from pattern-matching. A statement like "this module depends on the auth service" could be accurate or hallucinated, and the reader has no way to distinguish them from the text alone.

Graphify's confidence tags make epistemic status explicit at the data-model level. An `INFERRED` relation is still useful — it represents the LLM's semantic understanding — but it is labeled as such, and a downstream agent or developer can choose to treat `INFERRED` claims with more skepticism than `EXTRACTED` ones. `AMBIGUOUS` claims signal that human review is warranted before the relation is acted upon.

This pattern is particularly relevant for frameworks that use codebase maps as planning inputs (GSD's `gsd-codebase-mapper`, TLC's brownfield mapping). If the map contains untagged inferences, planning gates that check "does this plan align with the codebase structure?" are checking against a mix of facts and guesses without knowing which is which. GSD's codebase drift gate exacerbates this risk: when the gate auto-remaps via `gsd-codebase-mapper`, the new map may contain LLM-inferred structure claims that are treated with the same authority as AST-extracted facts. Graphify's tagging model offers a direct remedy — but only if the planning layer is built to consume and respect the confidence signal rather than flatten it to plain text.

---

## 7. Cross-Framework Comparison Table

| Dimension | GSD | TLC | Spec Kit | Graphify |
|---|---|---|---|---|
| Pre-code verification | Plan-checker loop (up to 3×), decision coverage gate (blocking), Nyquist validation, research gate, requirements coverage gate | Pre-approval validation tables in `tasks.md` (Granularity, Diagram-Definition, Test Co-location) | `/speckit.clarify`, `/speckit.analyze`, `/speckit.checklist` | N/A |
| During-execution gates | `STATE.md.lock` (atomic `O_EXCL`), executor failure classifier (cross-runtime sentinels), checkpoint heartbeats, `node_repair` (budget: 2) | Stop-the-line on non-zero exit code; max 3 diagnostic iterations; scope guardrail ("is this in my task definition?") | N/A | N/A |
| Post-execution verification | `gsd-verifier` agent writes `VERIFICATION.md` (PASS/FAIL); schema drift gate; codebase drift gate; decision coverage gate (non-blocking warning) | Validation phase: build gate → code quality → UAT; test integrity check (compare test counts) | N/A | Confidence tags on all relations (`EXTRACTED` / `INFERRED` / `AMBIGUOUS`) |
| Self-healing mechanism | `gsd-debugger` writes new `PLAN.md` → user re-runs `/gsd-execute-phase N` (same loop, no special fix mode); `/gsd-plan-review-convergence` (max 3 cycles, stall detection, escalation gate) | `SPEC_DEVIATION` markers; scope guardrail (deferred ideas, not inline fixes); max 3 diagnostic iterations then escalate | N/A | N/A |
| Supply-chain defense | `slopcheck` per package; `[SLOP]` stripped; `[SUS]` / `[ASSUMED]` inject `checkpoint:human-verify`; `[OK]` proceeds | Knowledge Verification Chain Steps 1–4 (codebase → project docs → Context7 MCP → web search) before any technical claim | N/A | N/A |

---

## 8. Implications for Our Framework

The survey of GSD, TLC, Spec Kit, and Graphify suggests five design implications for a new spec-driven framework's self-healing and verification strategy:

- **Verify at the cheapest moment.** GSD's blocking decision-coverage gate is cheap at plan time but hostile at verify time — the docs say this explicitly. Detecting a missed requirement or decision before code is written costs one loop iteration; detecting it after costs an entire execution pass. A new framework should front-load the cheapest structural checks (coverage, consistency, decision traceability) and reserve expensive behavioral checks (running tests, schema validation) for post-execution.

- **Self-repair should reuse the same primitive as initial generation.** GSD's diagnose-into-PLAN pattern is elegant precisely because it produces the same artifact type (`PLAN.md`) that the execute loop already knows how to consume. A "fix mode" that uses different commands, different artifacts, or different agent prompts doubles the surface area that must be kept correct. Design repair to be indistinguishable from initial generation at the executor level.

- **Cap diagnostic loops with hard budgets.** TLC's max-3-iterations rule and GSD's `node_repair_budget: 2` both recognize that an agent looping without convergence is a liability, not a virtue. Any framework that allows unbounded retry loops will eventually spiral. Escalation to human judgment is not a failure mode — it is a designed outcome for cases the agent cannot resolve autonomously.

- **Confidence tagging belongs in the data model, not in prose.** Graphify's `EXTRACTED` / `INFERRED` / `AMBIGUOUS` tags demonstrate that epistemic status can be a first-class property of a structured artifact. For a framework that uses codebase maps as planning inputs, untagged inferences in those maps corrupt the reliability of downstream gates that compare plans against the map. At minimum, any AI-generated analysis document should distinguish grounded observations from inferred ones.

- **Supply-chain verification is a pre-code concern.** GSD's Package Legitimacy Gate runs before planning is finalized, not at install time. Waiting until the executor runs `npm install` to discover that a package does not exist (or is a typosquat) means the entire execution pass was wasted. A new framework should treat package legitimacy as a plan-time gate, not a runtime surprise.

- **Classify defects by impact radius before routing them to gates.** Böckeler's Memo #13 ([https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html](https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html)) distinguishes three radiuses: (a) time-to-commit (caught by linters and unit tests in seconds), (b) team flow in the iteration (caught by reviewers in hours-to-days), and (c) long-term maintainability (caught by experienced engineers in weeks-to-years, if at all). Bigger radius = longer feedback loop = more dangerous. Asymmetric gates (Pattern 10) are an instance of this principle, but the dossier currently justifies asymmetry only on cost-of-fix. Routing a "redundant DI parameter" or "duplicated test" check at maintainability-radius requires a different gate and reviewer pool than a "commit fails to lint" check. The maintainability tier is precisely where 20+ years of experience matters most and where less-experienced reviewers cannot reliably substitute.

- **Regulate by category, not just by stage.** The Harness Engineering article ([https://martinfowler.com/articles/harness-engineering.html](https://martinfowler.com/articles/harness-engineering.html)) splits controls into three regulation targets: *maintainability* (linters, type checkers, code-mod recipes), *architecture fitness* (Fitness Functions, dependency rules, layered-architecture checks — see Pattern 28 and tools like ArchUnit), and *behaviour* (functional correctness — the unsolved one). A new framework should make verification phases category-aware and refuse to claim "verified" when only the maintainability harness is in place. The behaviour harness should be explicitly the weakest link until a behaviour primitive (e.g., Approved Scenarios — see Pattern 31) is wired in.

- **Sensor output should embed remediation, not just diagnose.** The Harness Engineering article describes custom-linter messages that include self-correction instructions as a "positive kind of prompt injection" ([https://martinfowler.com/articles/harness-engineering.html](https://martinfowler.com/articles/harness-engineering.html)). Standardise verifier output as a triple: `{finding, evidence, agent_remediation_prompt}`. The third field is what lets the next loop iteration *act*, not just re-read the failure. ArchUnit's `DescribedPredicate` mechanism (see Pattern 11 extension) is a concrete example: the rule's own prose statement is embedded in the failure message alongside the violating file:line.

- **Quality-left lifecycle distribution.** Refine "verify at the cheapest moment" (first bullet) into a four-slot distribution: **pre-commit** (computational guides/sensors only — lint, type check, format, ArchUnit-style architecture rules), **in-agent** (computational sensors + lightweight inferential guides — local tests, fast judges), **pipeline** (heavier inferential sensors at phase gates — `gsd-verifier`, full LLM review, full test suite), and **continuous drift** (out-of-lifecycle sensors — dead-code detection, coverage quality, dependency scans, runtime SLO monitoring). Forbid expensive inferential checks on the hot path. (Source: [https://martinfowler.com/articles/harness-engineering.html](https://martinfowler.com/articles/harness-engineering.html).)

- **Survey-then-edit with a typed accumulator.** OpenRewrite's `ScanningRecipe` formalizes the research-then-plan pattern with a typed object that the edit phase reads, never re-reading source files ([https://docs.openrewrite.org/concepts-and-explanations/recipes](https://docs.openrewrite.org/concepts-and-explanations/recipes)). Translated to AI workflows, the scan pass produces a typed project memo (deps used, patterns found, files matching predicates), and the edit pass consumes only that memo — not the whole repo and not the freeform research markdown. This is a structural answer to the existing research-phase-passes-markdown-to-planner pattern in GSD (`gsd-phase-researcher` → `RESEARCH.md` → planner).

- **Shift-left review at the IDE / pre-commit boundary.** The dossier reviews *plans* early (`gsd-plan-checker` 3×) but reviews *generated code* primarily at PR time. Add a pre-commit, IDE-integrated reviewer-agent step that examines diff-level concerns (DI redundancy, inline CSS instead of variables, over-engineering) before the commit lands. This addresses Böckeler's observation that "the longer a coding session gets, the more hit-and-miss it becomes" ([https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html](https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html)) — long sessions degrade not only retrieval but also *instruction adherence*, so checkpoint-and-re-anchor at the commit boundary is more valuable than at PR time.

---

## 9. Ergonomic Gates: Beyond Correctness

Correctness gates (does the test pass?) miss a category of regressions that Böckeler's Memo #13 highlights: AI agents that break the developer experience even when the code works. Concrete examples from the memo ([https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html](https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html)):

- Introducing a second start command instead of unifying with the existing one.
- Breaking hot reload.
- Over-complicating the build pipeline (gratuitous Docker layers, extra mandatory steps).

These regressions degrade team flow (radius b) and maintainability (radius c) without being caught by any test. A complementary gate set — "the project must still start with one command," "hot reload must still trigger on save," "the build pipeline gains no new mandatory steps without explicit approval" — would catch them at commit time. The framework's eventual rules registry should include a standing principle that DX guardrails are non-negotiable defaults; any plan that proposes adding a developer-facing step must mark it as a `D-id` decision so the asymmetric decision-coverage gate (Pattern 10) surfaces it for explicit acceptance.

---

## 10. Frozen Baselines for Legacy-Codebase Adoption

When a new framework introduces a verification rule (a lint, an architectural constraint, a coverage threshold) into a brownfield codebase, two failure modes are common:

- Uniform blocking: the rule produces thousands of pre-existing violations, the team disables the rule, the gate is dead on arrival.
- Uniform warning: the rule logs everything, no one acts, new violations slip in indistinguishably from inherited debt.

ArchUnit's `FreezingArchRule` ([https://www.archunit.org/userguide/html/000_Index.html](https://www.archunit.org/userguide/html/000_Index.html) §8.6) demonstrates a third option: snapshot every existing violation into a VCS-committed `ViolationStore` text file; CI fails only on *new* violations and the store auto-shrinks when violations are fixed. Two CI-side safety flags (`freeze.store.default.allowStoreCreation=false`, `allowStoreUpdate=false`) prevent silent baseline growth. Pattern 25 formalizes this as "Frozen Baseline with Ratchet Semantics." Adapt by adding a `freeze-on-adoption` mode to any rule introduced after the first 100 commits: the AI agent ships under the new rule today, with strict enforcement on its diff and ratchet-down semantics on the inherited debt. This generalizes Pattern 10's per-decision opt-out tags (`[informational]`, `[folded]`, `[deferred]`) from individual decisions to whole-violation-set baselining.
