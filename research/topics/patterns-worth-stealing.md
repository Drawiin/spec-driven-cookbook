# Patterns Worth Stealing

This file ranks and describes transferable design patterns extracted from the research into GSD, TLC spec-driven, and five adjacent frameworks (Graphify, Spec Kit, OpenSpec, Task Master, BMAD-METHOD). "Transferability" means a pattern is general enough to apply to any spec-driven AI coding framework, is not tied to a specific runtime or technology stack, and solves a real, recurring problem that shows up across more than one system. These are observations drawn from the research cache — they are not prescriptions, and no pattern should be adopted without evaluating fit against your own constraints and conventions.

Cross-links to framework profiles: [GSD](../frameworks/gsd.md) · [TLC spec-driven](../frameworks/tlc-spec-driven.md) · [Adjacent frameworks](../frameworks/adjacent-frameworks.md) · [Graphify](../frameworks/graphify.md)

---

## Group A: Context and Memory Management

Patterns that prevent context rot, manage token budgets, and persist state across sessions.

---

### Pattern 1: Compound Init Handlers

- **Origin:** GSD (`gsd-sdk query init.<workflow>`)
- **Problem it solves:** Each workflow entry point had to re-discover project state by reading multiple files independently, wasting tokens on repeated I/O and creating divergence risk when file reads returned stale data.
- **How it works:** One CLI call (`node gsd-tools.cjs init execute-phase 1`) returns everything that workflow needs as a single JSON blob — project info, config, phase details, and state. When the payload exceeds ~50 KB it spills to a tempfile and returns `@file:/tmp/gsd-init-XXXXX.json`, which the workflow expands. One loader call per workflow, deduplicated, ready to inject. No per-workflow re-discovery.
- **Transferability:** HIGH. Any framework with multiple workflow entry points benefits from a single compound-load primitive. The tempfile spill threshold is a clean release valve for unexpectedly large payloads.
- **What to adapt:** The "context payload" object model — define a standard shape that all workflow entrypoints consume, and centralize the logic for assembling it. The tempfile spill pattern is elegant and worth copying verbatim.
- **See also:** [./context-engineering.md](./context-engineering.md)

---

### Pattern 2: Two-Stage Namespace Routing Meta-Skills

- **Origin:** GSD (v1.40 consolidation)
- **Problem it solves:** Eager-listing 86 flat skills costs ~2,150 tokens per session. The AI agent pays this overhead before doing any work, regardless of which skills are needed.
- **How it works:** Six namespace routers (`/gsd-workflow`, `/gsd-project`, `/gsd-quality`, `/gsd-context`, `/gsd-manage`, `/gsd-ideate`) replace the flat listing. Each router is ~20 tokens. The agent picks a router, then routes to the specific skill. Router descriptions use "pipe-separated keyword tags (≤ 60 chars)" — the GSD docs cite "Tool Attention research showing keyword-dense tags outperform prose for routing at ~40% the token cost." Net result: ~120 tokens for 6 routers vs ~2,150 tokens for 86 flat skills.
- **Transferability:** HIGH. Any framework with a large skill or command surface should consider two-stage routing. The reduction in eager-listing cost is proportional to the surface size.
- **What to adapt:** The router-as-skill pattern; the keyword-tag format for router descriptions rather than prose descriptions. The cluster grouping (workflow / project / quality / context / manage / ideate) is a reasonable starting taxonomy for most frameworks.
- **See also:** [./context-engineering.md](./context-engineering.md)

---

### Pattern 3: Per-File Token Budgets with Health Zones

- **Origin:** TLC spec-driven (`context-limits.md`)
- **Problem it solves:** Persistent state files grow unboundedly. Without size governance, `STATE.md` becomes a liability — too large to load affordably, too important to skip.
- **How it works:** Each file has a maximum token limit and a warning threshold (e.g., `STATE.md`: max 10,000 tokens, warn at 7,000). Three health zones drive distinct agent behaviors:
  - **Healthy** (<40k total context): silent
  - **Moderate** (40–60k): discrete footer note
  - **Critical** (>60k): active warning with optimization suggestion
  
  Per-file limits are concrete: `PROJECT.md` max 2,000 / warn at 1,600; `design.md` max 8,000 / warn at 6,400; `tasks.md` max 10,000 / warn at 8,000. Graduated cleanup zone for `STATE.md`: <7k no action, 7–10k footer note, >10k active prompt.
- **Transferability:** HIGH. Directly applicable to any framework that accumulates persistent state in markdown files. The three-zone model gives the agent a clear, non-binary response: it doesn't have to choose between ignoring the problem and hard-failing.
- **What to adapt:** The three-zone model; the 60-day archive policy for aged entries; the graduated cleanup prompt rather than a hard limit that breaks loading.
- **See also:** [./context-engineering.md](./context-engineering.md) · [./local-storage-and-artifacts.md](./local-storage-and-artifacts.md)

---

### Pattern 4: ID-Based, Ageable Persistent Memory

- **Origin:** TLC spec-driven (`state-management.md`)
- **Problem it solves:** State files accumulate silently. Without IDs, there is no discipline around what to keep, what to age out, and no way to cross-reference a state entry from another artifact.
- **How it works:** Decisions (`AD-NNN`), blockers (`B-NNN`), and lessons (`L-NNN`) get sequential IDs. A dedicated "Deferred Ideas" section absorbs scope-creep impulses without losing them or acting on them immediately. Graduated cleanup zone (see Pattern 3) prevents unbounded growth. Entries older than 60 days move to `STATE-ARCHIVE.md`.
- **Transferability:** HIGH. The ID scheme makes state queryable and referenceable from specs, tasks, and commits. The deferred-ideas absorber is particularly valuable — it gives scope creep a landing zone that is neither the trash nor the active backlog.
- **What to adapt:** The ID scheme (`AD-NNN`/`B-NNN`/`L-NNN` is clean and minimal); the deferred-ideas section as a first-class slot in the state file; the 60-day archive policy as a concrete, automatable rule.
- **Extension — team-level "go-wrong" log (Developer Skills Memo #13):** Per-project `L-NNN` lessons capture knowledge inside one project's `STATE.md`, but they do not aggregate across projects or feed back into the rule registry. Böckeler describes a team ritual of weekly review of AI-induced friction ([https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html](https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html)) — every cataloged friction case becomes a candidate update to the custom-rules artifact (Pattern 16). Closing the loop requires (a) a cross-project log location, (b) a review cadence, (c) a provenance link from each rule to the friction case that motivated it.
- **See also:** [./local-storage-and-artifacts.md](./local-storage-and-artifacts.md)

---

## Group B: Workflow and Orchestration

Patterns that structure how work gets planned, executed, and coordinated across agents.

---

### Pattern 5: Auto-Sized Pipeline with Hard Escape Valves

- **Origin:** TLC spec-driven (`SKILL.md`, `quick-mode.md`)
- **Problem it solves:** Rigid phase pipelines don't scale to both "fix a typo" and "build a new auth system." But skipping phases too aggressively hides complexity until it's expensive to surface.
- **How it works:** Four deterministic size tiers — Small (≤3 files, quick mode), Medium (clear feature, <10 tasks), Large (multi-component), Complex (ambiguity, new domain) — each with specific phase skip rules. Design and Tasks are auto-skipped when scope doesn't justify them. The key escape valve: "Even when Tasks is skipped, Execute ALWAYS starts by listing atomic steps inline. If that listing reveals >5 steps or complex dependencies, STOP and create a formal `tasks.md`." Quick mode has its own hard guardrails: max 3 files, max 1 hour, no design decisions, no new dependencies. If the pre-implementation check reveals >3 files or unclear dependencies, escalate to the full pipeline.
- **Transferability:** HIGH. The escape valve is the load-bearing mechanism — it prevents silent complexity accumulation. The tiered model itself is less important than the rule that Execute always lists steps first and checks against a threshold.
- **What to adapt:** The deterministic size tiers; the "Execute always lists inline first" rule; the pre-implementation check as an explicit escalation gate in quick mode.
- **Extension — vertical slice as constructive constraint (Developer Skills Memo #13):** First slice must be end-to-end working before any breadth-pass is allowed. Pattern 5 already catches >5-step plans; this addition forces the *shape* of the first deliverable (one slice through the stack), not just its size. Example: AI tried to convert all components at once during a frontend migration instead of one component end-to-end. (Source: [https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html](https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html).)
- **See also:** [./workflow-and-orchestration.md](./workflow-and-orchestration.md)

---

### Pattern 6: Sub-Agent Context Contract

- **Origin:** TLC spec-driven (`SKILL.md`, `tasks.md`, `implement.md`)
- **Problem it solves:** Sub-agents receive too much context (degrading output quality) or too little (producing incoherent output). Without a contract, the orchestrator makes ad-hoc decisions about what to pass.
- **How it works:** Fixed input contract — orchestrator MUST pass: the specific task definition from `tasks.md`, relevant `coding-principles.md` and `CONVENTIONS.md`, `TESTING.md` if it exists, and any spec/design context the task explicitly references. Fixed output contract — each sub-agent returns: Status (Complete | Blocked | Partial), Files changed, Gate check result (pass/fail + test counts), `SPEC_DEVIATION` markers if any, Issues encountered if any. Explicit "must NOT receive" list: other tasks' definitions, accumulated chat history, validation reports from other tasks, `STATE.md` (unless the task explicitly references a decision/blocker).
- **Transferability:** HIGH. The fixed contracts make parallelism cheap and main-context pollution minimal. The "must NOT receive" list is as important as the "must receive" list — it codifies the discipline of not passing everything.
- **What to adapt:** The output contract shape (Status/Files/Gate/Deviations/Issues) is reusable verbatim. The "must NOT receive" list should be maintained actively as the framework grows.
- **Extension — per-hunk attribution (OpenRewrite `Result.recipesThatMadeChanges`):** Add a per-hunk attribution layer modeled on OpenRewrite's `Result` with `recipesThatMadeChanges` ([https://docs.openrewrite.org/concepts-and-explanations/recipes](https://docs.openrewrite.org/concepts-and-explanations/recipes)): persist, alongside each diff hunk, the skill ID, prompt hash, model version, and originating spec/decision ID. Every line in a PR can then be traced back to a spec, which makes audit and selective rollback feasible without re-running the workflow.
- **See also:** [./workflow-and-orchestration.md](./workflow-and-orchestration.md)

---

### Pattern 7: Wave-Based Parallelism with State Lockfile

- **Origin:** GSD (`ARCHITECTURE.md`)
- **Problem it solves:** Parallel agent execution creates race conditions on shared state files and git hooks. Naive parallelism produces corrupted `STATE.md` entries and double-fired hooks.
- **How it works:** Dependency analysis groups plans into waves. Tasks within a wave are dependency-free relative to each other and execute in parallel. Parallel executors commit with `--no-verify`; the orchestrator runs `git hook run pre-commit` once after each wave (not once per task). State mutations go through `STATE.md.lock` with `O_EXCL` atomic creation (standard POSIX atomic), 10-second stale-lock timeout, and jittered spin-wait to prevent thundering herd.

  ```
  Wave 1: Plan 01 (no deps), Plan 02 (no deps)          — parallel
  Wave 2: Plan 03 (depends: 01), Plan 04 (depends: 02)  — parallel within wave, waits for Wave 1
  Wave 3: Plan 05 (depends: 03, 04)                     — waits for Wave 2
  ```

- **Transferability:** MEDIUM-HIGH. Directly applicable when parallelism is a goal. The `O_EXCL` lockfile is the right primitive on Unix; a cross-platform fallback is needed for Windows (GSD handles this via `EPERM`/`EBUSY` retry logic).
- **What to adapt:** The `O_EXCL` lockfile pattern; the "hooks once per wave, not once per task" rule; the jittered spin-wait (prevents lock convoy).
- **See also:** [./workflow-and-orchestration.md](./workflow-and-orchestration.md)

---

### Pattern 8: Diagnose-into-PLAN Self-Healing

- **Origin:** GSD (`gsd-debugger`, `ARCHITECTURE.md`)
- **Problem it solves:** When verification fails, the natural instinct is to create a "fix mode" branch — a separate command path, a different context, a different loop. This fragments the workflow and gives the agent special-case repair logic that diverges from the normal path.
- **How it works:** When `/gsd-verify-work N` finds a failure, it spawns `gsd-debugger`, which writes a *new* `PLAN.md` into the same phase directory. The user then re-runs `/gsd-execute-phase N` — the same command, the same loop. No "fix mode," no context switch, no new primitive. Fix plans are first-class tasks in the normal workflow, not special-case repairs.
- **Transferability:** HIGH. The "failures produce tasks, not exceptions" principle is broadly applicable. It collapses the repair path into the execution path, reducing the surface of the system.
- **What to adapt:** The principle that fix plans are tasks. The concrete mechanism (writing a new PLAN.md) can be adapted to any artifact-based framework.
- **Extension — universal diagnose-before-fix (Developer Skills Memo #13):** The same diagnose-into-PLAN principle should apply at execute-time, not only at verify-time. When a within-wave failure occurs, `node_repair` should require an explicit root-cause statement before retry, mirroring the `gsd-debugger` artifact. Example: AI raising Docker memory limits instead of asking why memory was high — a brute-force fix path that `node_repair` currently allows. (Source: [https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html](https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html).)
- **See also:** [./self-healing-and-verification.md](./self-healing-and-verification.md)

---

### Pattern 9: Three-Role Model Config

- **Origin:** Task Master (main / research / fallback)
- **Problem it solves:** Using one model for all jobs wastes capability where it's not needed (simple task management) and is too slow or expensive where depth is required (architecture research). One model also can't satisfy the live-web-access requirement for external research.
- **How it works:** Three named roles in the model config: `main` (handles implementation and task execution), `research` (handles live web lookups — often a dedicated web-search model like Perplexity), `fallback` (handles recovery when primary fails or is rate-limited). The research role is treated as a distinct capability with live-web access, not just a cheaper version of main.
- **Transferability:** HIGH. Model routing by job type is universally applicable. The key insight is that `research` is a separate capability class, not a tier in a cost/quality ladder.
- **What to adapt:** The three-role taxonomy (main / research / fallback); the explicit separation of live-web research from implementation reasoning as distinct model responsibilities.
- **See also:** [./auxiliary-tooling.md](./auxiliary-tooling.md)

---

### Pattern 21: Authored Composition of Typed Transformations (Recipe DAG)

- **Origin:** OpenRewrite (`Recipe`, `recipeList`)
- **Problem it solves:** The dossier's primitives are phases, plans, tasks, and stories — all coarse-grained. There is no fine-grained, parameterized, validated, composable unit that lets a high-level spec decompose into ordered, traceable, testable sub-operations. Closest analog is GSD wave dependency analysis, which is per-execution computation rather than authored composition.
- **How it works:** OpenRewrite formalizes a transformation as a Recipe: a named, parameterized, validated unit with two flavors — imperative (code) and declarative YAML that composes other recipes via `recipeList` ([https://docs.openrewrite.org/concepts-and-explanations/recipes](https://docs.openrewrite.org/concepts-and-explanations/recipes), [https://docs.openrewrite.org/reference/yaml-format-reference](https://docs.openrewrite.org/reference/yaml-format-reference)). Translated to a spec-driven AI framework: define a 'skill' contract such that deterministic skills (regex/AST refactors) and LLM skills expose the same options and validation surface, then let high-level specs be authored as a YAML DAG of skills. The composition surface is the unit of reuse; the planner does tool-selection over the DAG, not over chat prompts.
- **Transferability:** HIGH. Elevates per-execution wave dependency computation to a first-class authored composition surface.
- **What to adapt:** A typed `skill` contract that both deterministic and LLM-powered skills implement; a YAML-DAG composition surface; planner tool-selection over the DAG instead of over chat prompts.
- **See also:** [./workflow-and-orchestration.md](./workflow-and-orchestration.md)

---

## Group C: Verification and Quality

Patterns that validate correctness before, during, and after execution.

---

### Pattern 10: Asymmetric Decision Coverage Gates

- **Origin:** GSD (`gsd-discuss-phase`, `gsd-plan-checker`, `gsd-verifier`)
- **Problem it solves:** Tracking user decisions from the discussion phase through planning and into shipped code is hard. Blocking everywhere creates friction; blocking nowhere creates drift.
- **How it works:** The Discuss phase produces numbered decision IDs (`D-01`, `D-02`, …) stored in `{phase}-CONTEXT.md`. Two gates with different blocking behavior:
  - **Plan-time gate — BLOCKING:** every trackable D-id must appear in at least one plan's `must_haves`, `truths`, or body before the phase is marked planned. Cheap to fix at this stage.
  - **Verify-time gate — NON-BLOCKING:** after execution, GSD searches plans, `SUMMARY.md`, modified files, and recent commit messages for each D-id. Misses are logged as warnings, not failures. Expensive to fix here, so it warns rather than blocks.
  
  Two match modes: strict ID (`D-01`) or a 6+-word verbatim phrase from the decision text. Explicit opt-out tags (`[informational]`, `[folded]`, `[deferred]`) exclude decisions that don't need coverage.
- **Transferability:** HIGH. The asymmetric blocking/non-blocking pair is the key insight — block where the cost of fixing is low, warn where the cost of fixing is high. This is more useful than uniform blocking.
- **What to adapt:** The D-id numbering scheme; the opt-out tags as a safety valve; the two-match-mode approach (strict ID + phrase fallback).
- **See also:** [./self-healing-and-verification.md](./self-healing-and-verification.md)

---

### Pattern 11: Test-as-Spec and SPEC_DEVIATION Markers

- **Origin:** TLC spec-driven (`coding-principles.md`, `implement.md`)
- **Problem it solves:** Implementation drifts from spec silently. Tests get weakened to pass. Specs get retroactively updated to match code. The test suite stops being a contract and becomes a post-hoc description of what the code happens to do.
- **How it works:** RED-phase tests (written before implementation) are immutable during the GREEN phase. Hard rules: never weaken assertions, never delete a test to reduce failure count, never use skip/disable/pending to bypass failures, never modify RED-phase tests during GREEN. "Tests are the spec — implementation conforms to tests, not the other way around." When a deviation is genuinely necessary, it must be marked inline:
  ```
  // SPEC_DEVIATION: [what diverged]
  // Reason: [why the deviation was necessary]
  ```
  `SPEC_DEVIATION` markers are surfaced in sub-agent output reports so the orchestrator can decide whether to accept or escalate.
- **Transferability:** HIGH. The immutability principle combined with the explicit marker is a clean alternative to silent drift. The marker externalizes the deviation decision instead of embedding it invisibly in the code.
- **What to adapt:** The `SPEC_DEVIATION` annotation format (could be a comment, a YAML front-matter field, or a separate tracking file). The sub-agent output contract (Pattern 6) already includes a "SPEC_DEVIATION markers" field, making this composable.
- **Extension — generalizes to architecture-rule tests.** Architecture-level invariants (layer access, dependency direction, naming, annotation presence) are testable with the same assertion-failure-as-feedback model. Tools like ArchUnit ([https://www.archunit.org/](https://www.archunit.org/)) demonstrate the pattern in Java; the abstraction transfers to any AST/IR layer (e.g., dependency-cruiser for JavaScript, ts-arch for TypeScript).
- **Extension — rules should be self-describing.** ArchUnit's `DescribedPredicate`/`ArchCondition` carry their own English description, which the test runner embeds in the failure message alongside the violating `Class.java:line`. The spec sentence appears in the feedback the agent receives. This is the inverse of the `SPEC_DEVIATION` marker (which annotates code with the deviation prose); both close the spec↔code↔feedback loop in opposite directions, and they compose.
- **Extension — redundancy / over-generation axis for AI-authored tests.** Pattern 11's immutability rule prevents *weakening* of RED-phase tests, but AI agents also over-generate: duplicate assertions, redundant new tests, tests whose assertions mirror the code. Böckeler's Memo #13 calls this out ("more tests are not necessarily better" — [https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html](https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html)). Add a lint or reviewer-agent gate that flags assertions duplicating those in existing tests, and CI templates that ship with raised duplication weight by default since AI-induced duplication is structurally more common than human-authored duplication.
- **Extension — per-hunk attribution layer.** OpenRewrite's `Result.recipesThatMadeChanges` ([https://docs.openrewrite.org/concepts-and-explanations/recipes](https://docs.openrewrite.org/concepts-and-explanations/recipes)) records, for every changed file, exactly which recipes contributed. Adopt the same idea for AI edits: persist alongside each diff hunk the skill ID, prompt hash, model version, and originating spec/decision ID. Every line in a PR can then be traced back to a spec, making audit and selective rollback feasible without re-running the workflow.
- **See also:** [./self-healing-and-verification.md](./self-healing-and-verification.md); Pattern 31 (Approved Scenarios) for AI-generated fixture tests, which scope this pattern's immutability rule to hand-authored contract tests.

---

### Pattern 12: Parallel-Safety as a Property of Tests, Not Code

- **Origin:** TLC spec-driven (`tasks.md`, `TESTING.md`)
- **Problem it solves:** Tasks get marked parallel-safe because their code has no implementation dependencies — but their tests share a database, a port, or a temp directory, causing flaky failures in parallel runs.
- **How it works:** A task earns `[P]` (parallel-safe) only if THREE conditions are met:
  1. No unfinished code dependencies.
  2. The required test type is parallel-safe per the `TESTING.md` Parallelism Assessment.
  3. No shared mutable state with other `[P]` tasks in the same phase.

  The rule: "If a task's tests are NOT parallel-safe, it MUST run sequentially even if its implementation code has no dependencies. The test execution is the bottleneck." The `TESTING.md` Parallelism Assessment is the source of truth for condition 2 — it's maintained as part of codebase mapping, not inferred at task-creation time.
- **Transferability:** HIGH. The insight that test execution is the bottleneck for parallelism (not code dependencies) is non-obvious and valuable. Most frameworks check only code deps.
- **What to adapt:** A `TESTING.md` Parallelism Assessment section as part of brownfield codebase mapping; treating it as the authoritative input to parallel-safety decisions.
- **See also:** [./workflow-and-orchestration.md](./workflow-and-orchestration.md) · [./self-healing-and-verification.md](./self-healing-and-verification.md)

---

### Pattern 13: Confidence Tagging on Inferred Data

- **Origin:** Graphify (`EXTRACTED` / `INFERRED` / `AMBIGUOUS` relation tags)
- **Problem it solves:** AI-generated analysis of codebases arrives as confident prose, even when the underlying claim was derived by inference rather than direct source extraction. Consumers cannot distinguish source-grounded facts from model-derived guesses.
- **How it works:** Every relation in Graphify's knowledge graph is tagged with its epistemic status: `EXTRACTED` (sourced directly from the codebase — inferred from the pipeline's Tree-sitter AST extraction stage, which uses no LLM on source code), `INFERRED` (the LLM derived it from context), or `AMBIGUOUS` (the source was unclear). The explicit definition of `EXTRACTED` is not in the live README; this interpretation is based on the pipeline design. Tagging is built into the data model, not added as a post-hoc annotation.
- **Transferability:** MEDIUM. Directly applicable to any framework that generates analysis artifacts — architecture docs, codebase maps, risk assessments, brownfield findings. Less relevant for purely greenfield or implementation-only frameworks.
- **What to adapt:** A convention for tagging inferred sections in brownfield analysis docs. At minimum: distinguish "observed in code" from "inferred from patterns" from "uncertain." Even a simple `[unverified]` marker on individual claims (as used in this dossier) is a lightweight version of this pattern. OpenRewrite's Markers ([https://docs.openrewrite.org/concepts-and-explanations/visitors](https://docs.openrewrite.org/concepts-and-explanations/visitors)) extend this pattern from analysis artifacts to source IR: a `Markers` bag on every AST node lets agents annotate code with rationale, confidence, source-of-truth links, and review status as structurally co-located metadata that survives transformations and is invisible at runtime. ArchUnit reinforces the same principle at the *verifier* layer — rules evaluated against bytecode (post-compile, deterministic) are a second example of the wider design principle that spec verifiers for AI-generated code should anchor on a post-compile/post-build artifact (AST, IR, bundle graph, bytecode) wherever possible, because AI agents are prone to "looks-right" source output that fails the moment a deterministic substrate is consulted.
- **See also:** [./local-storage-and-artifacts.md](./local-storage-and-artifacts.md)

---

### Pattern 14: Package Legitimacy Gate (Slopsquatting Defense)

- **Origin:** GSD (v1.42.1 release, `gsd-phase-researcher`, `slopcheck`)
- **Problem it solves:** AI agents hallucinate package names. Some hallucinated names have been pre-registered with malicious post-install scripts — a supply-chain attack pattern called "slopsquatting." Silently substituting an alternative package when the first fails to install is the worst possible recovery behavior.
- **How it works:** Every package discovered via web search is pre-tagged `[ASSUMED]` (a provenance tag, not a slopcheck verdict). The `slopcheck` tool (MIT-licensed, pip-installable) then audits each package: checks registry presence, age, download count, source repo. The slopcheck audit produces its own verdict (`[SLOP]`, `[SUS]`, `[OK]`). Both `[SUS]` (from slopcheck) and `[ASSUMED]` (unaudited packages) trigger `checkpoint:human-verify` before the install task. `[SLOP]` is stripped from the plan entirely. Failed installs stop — no silent substitution.
- **Transferability:** MEDIUM. Critical for frameworks where agents autonomously recommend or install dependencies. Less relevant for analysis-only frameworks that don't touch package management.
- **What to adapt:** The two-level taxonomy (provenance tags like `[ASSUMED]` upstream, audit verdicts like `[SLOP]`/`[SUS]`/`[OK]` from the tool); the "never silently substitute" rule; the audit table as a first-class artifact in the research output.
- **See also:** [./self-healing-and-verification.md](./self-healing-and-verification.md) · [./auxiliary-tooling.md](./auxiliary-tooling.md)

---

### Pattern 20: Lossless Semantic Tree (LST) Substrate for AI Edits

- **Origin:** OpenRewrite (Lossless Semantic Trees)
- **Problem it solves:** Every framework surveyed has an LLM produce text and then verifies after the fact. There is no structured IR substrate for AI edits — all editing is text-level, so hallucinated APIs and incidental reformatting only surface post-hoc.
- **How it works:** An alternative to text-level editing is to have the model propose changes against a typed, format-preserving intermediate representation (Lossless Semantic Tree, [https://docs.openrewrite.org/concepts-and-explanations/lossless-semantic-trees](https://docs.openrewrite.org/concepts-and-explanations/lossless-semantic-trees)) and let the framework print the IR back to source. Type information travels with each node, so the model has grounding against fabricated APIs; whitespace and local style are tree-resident, so unrelated lines are never reformatted.
- **Transferability:** Adoption cost is high (per-language IR), but the correctness ceiling is meaningfully higher than after-the-fact text verification. Marked HIGH where the correctness ceiling justifies the per-language IR investment.
- **What to adapt:** Treat a typed IR substrate as a first-class alternative to the text-level editing assumption shared by every dossier framework — a structural answer to "code that runs vs code that works" and to the hallucinated-API problem.
- **See also:** [./self-healing-and-verification.md](./self-healing-and-verification.md)

---

### Pattern 22: Precondition Scope Filter

- **Origin:** OpenRewrite (`Preconditions`)
- **Problem it solves:** Dossier gates are about coverage and decisions, not scope. LLM workflows that "let the model read the whole repo" pay full token cost on every invocation; ineligible files are not filtered out before the heavy LLM call.
- **How it works:** Require every AI editing skill to ship with a deterministic precondition (glob, AST query, type predicate, or short search recipe). Preconditions, as defined in OpenRewrite ([https://docs.openrewrite.org/reference/yaml-format-reference](https://docs.openrewrite.org/reference/yaml-format-reference)), gate which files a skill may touch *before* the LLM is invoked. For LLM workflows this is the difference between "the model reads the whole repo" and "the model only sees the slice that matched a glob/AST query/type predicate".
- **Transferability:** HIGH. Slashes token cost, scopes blast radius, and keeps the model's attention on a verified subset rather than the whole repo.
- **What to adapt:** Make a deterministic precondition (glob / AST query / type predicate / short search recipe) a required field on every AI skill manifest, paired with the skill's invocation as a plan-time scope gate.
- **See also:** [./self-healing-and-verification.md](./self-healing-and-verification.md)

---

### Pattern 23: Isomorphic vs Non-Isomorphic Edits (Tiered Review Gating)

- **Origin:** OpenRewrite (isomorphic vs non-isomorphic visitors)
- **Problem it solves:** TLC's RED→GREEN immutability and GSD's plan-checker treat all edits with the same review intensity. Rename/retype/reformat shares a gate with replace-function-with-class, which forces uniformly heavy or uniformly light review.
- **How it works:** Adopt OpenRewrite's distinction between isomorphic (provably structure-preserving) and non-isomorphic (allows node-type replacement) edits ([https://docs.openrewrite.org/concepts-and-explanations/visitors](https://docs.openrewrite.org/concepts-and-explanations/visitors)). Map it to AI edits: classify each skill's output as 'safe' (rename, retype, format, comment) or 'structural' (replace function, change interface, alter control flow). Apply different review gates per class — safe edits can auto-merge after gate checks; structural edits require explicit human or higher-tier-model approval.
- **Transferability:** HIGH for any framework with both deterministic and LLM-driven skills.
- **What to adapt:** A two-class taxonomy on every skill's output (`safe` / `structural`); per-class review gates; auto-merge eligibility tied to the safe class only.
- **See also:** [./self-healing-and-verification.md](./self-healing-and-verification.md)

---

### Pattern 25: Frozen Baseline with Ratchet Semantics

- **Origin:** ArchUnit (`FreezingArchRule`, `ViolationStore`)
- **Problem it solves:** A new rule introduced into a grown codebase can produce thousands of violations, none of which the AI agent caused — uniform blocking is hostile, uniform warning lets new violations slip in. Asymmetric Decision Coverage Gates (Pattern 10) cover individual decisions but do not scale to whole-violation-set baselining.
- **How it works:** ArchUnit's `FreezingArchRule.freeze(rule)` snapshots every existing violation into a VCS-committed `ViolationStore` text file; CI fails only on *new* violations and the store auto-shrinks when violations are fixed. Two CI-side safety flags (`freeze.store.default.allowStoreCreation=false`, `allowStoreUpdate=false`) prevent silent baseline growth. The two configuration flags govern who may *write* to the violation store: `freeze.store.default.allowStoreCreation` (gates first-time creation) and `allowStoreUpdate` (gates baseline modification). In CI both are set to `false` — CI may only *read* the baseline. Local developers may set them `true` to refreeze after intentionally accepting new debt. This separates "CI enforces the ratchet" from "humans may explicitly grow the baseline," and prevents a misconfigured pipeline from silently re-baselining failures away.
- **Transferability:** HIGH for any framework whose verifiers run against legacy code.
- **What to adapt:** A "freeze on adoption" mode where new constraints snapshot the current violation set; the AI agent ships under the new rule today, with strict enforcement on its diff and ratchet-down semantics on the inherited debt. Mirror ArchUnit's `allowStoreCreation` / `allowStoreUpdate` safety flags so CI is a read-only consumer of the baseline. (Source: [https://www.archunit.org/userguide/html/000_Index.html](https://www.archunit.org/userguide/html/000_Index.html) §8.6.)
- **See also:** [./self-healing-and-verification.md](./self-healing-and-verification.md)

---

### Pattern 29: Guides + Sensors Taxonomy

- **Origin:** Harness Engineering (Martin Fowler / Birgitta Böckeler [inference], 2026-04-02 — [https://martinfowler.com/articles/harness-engineering.html](https://martinfowler.com/articles/harness-engineering.html))
- **Problem it solves:** Crosscuts every gate already inventoried; tagging each rule/skill/verifier as `guide`, `sensor`, or both forces designers to notice when a spec is unverifiable (a guide with no paired sensor) or when a sensor exists for behaviour no spec actually requires.
- **How it works:** Every control in an agent harness is either a **guide** (feedforward — anticipates misbehaviour and steers before action, e.g., AGENTS.md, skills, code-mod recipes, LSP access) or a **sensor** (feedback — observes after the act and surfaces signals optimised for LLM consumption, e.g., lints, type checks, LLM-as-judge, fitness functions). Either alone is insufficient: guides without sensors cannot be verified; sensors without guides surface failures the agent has no instruction to avoid.
- **Transferability:** HIGH. Crosscuts existing GSD/TLC/Spec-Kit gate inventories along an axis (feedforward/feedback) orthogonal to timing.
- **What to adapt:** Require every load-bearing rule to declare which axis it serves; for any "spec" item, require a paired sensor that proves the spec held — otherwise mark the spec unverifiable.
- **See also:** [./self-healing-and-verification.md](./self-healing-and-verification.md)

---

### Pattern 30: Computational vs Inferential Control Labelling

- **Origin:** Harness Engineering — [https://martinfowler.com/articles/harness-engineering.html](https://martinfowler.com/articles/harness-engineering.html)
- **Problem it solves:** Lets the framework cost-tier verifications (cheap deterministic checks every step; expensive LLM judgments only at gates). Maps directly onto the dossier's pre-commit / phase-verify / milestone-audit timing tiers.
- **How it works:** Each control carries a second axis label: **computational** (deterministic — linters, type checkers, fitness functions, structural/architectural tests, mutation tests) or **inferential** (LLM-based — AI review, LLM-as-judge, semantic diff). The label is a cost and reliability hint that drives lifecycle placement: cheap deterministic checks belong on the hot path (pre-commit, in-agent), expensive inferential checks belong at phase or milestone gates.
- **Transferability:** HIGH. Pairs with Pattern 29 as a `{guide|sensor}` + `{computational|inferential}` two-axis tag on every harness item.
- **What to adapt:** Every dossier-inventoried gate should carry a `{guide|sensor}` + `{computational|inferential}` pair (e.g., `slopcheck` = sensor/computational; `gsd-verifier` = sensor/inferential; AGENTS.md = guide/computational; LLM-judge plan review = sensor/inferential).
- **See also:** [./self-healing-and-verification.md](./self-healing-and-verification.md)

---

### Pattern 31: Approved Scenarios for AI-Generated Behaviour Tests

- **Origin:** Lex Lerumph, *Augmented Coding Patterns* — Approved Scenarios ([https://lexler.github.io/augmented-coding-patterns/patterns/approved-scenarios/](https://lexler.github.io/augmented-coding-patterns/patterns/approved-scenarios/)), surfaced via Harness Engineering ([https://martinfowler.com/articles/harness-engineering.html](https://martinfowler.com/articles/harness-engineering.html)).
- **Problem it solves:** The dossier has no answer for AI-generated tests except TLC's immutability rule (Pattern 11), which is awkward when the tests themselves were AI-generated. Approved Scenarios make the *fixture* reviewable by diff and regenerable, which is a better fit for noisy AI-authored tests than the RED-test-immutability stance.
- **How it works:** Behaviour tests are stored as domain-friendly fixture files combining an input and its expected output. The runner regenerates the expected-output side on demand; the reviewer's job is a diff review, not assertion authorship. This separates "is this the right behaviour?" (human judgment, by diff) from "does the code still produce this output?" (mechanical check). Complements Pattern 11: RED-phase contract tests remain immutable, but AI-generated *fixture* tests use the approved-scenarios protocol.
- **Transferability:** HIGH for phases that ship workflows, prompts, or agent loops — domains where assertion-style tests are noisy and review-by-diff is more honest.
- **What to adapt:** Offer it as a first-class behaviour-harness primitive; pair with Pattern 11 by scoping RED-phase contract tests to assertion-style and AI-generated fixture tests to approved-scenarios.
- **See also:** [./self-healing-and-verification.md](./self-healing-and-verification.md)

---

### Pattern 32: Reuse-Awareness Pre-Check

- **Origin:** Inferred from Böckeler Memo #13 examples ([https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html](https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html)); Graphify's `query_graph` / `get_neighbors` is the natural mechanism.
- **Problem it solves:** Generative agents re-implement existing components instead of importing them, producing duplication that pollutes the codebase and degrades modularity over time. The defect surfaces only at code review or never.
- **How it works:** Before a `gsd-executor`-equivalent generates a new component, a pre-step queries a codebase index (Graphify graph, ripgrep, ast-grep) for symbols semantically close to the requested API surface. Hits surface as a "candidate-for-reuse" list that the executor must address (use, extend, or explicitly justify ignoring) before generation proceeds.
- **Transferability:** HIGH for any framework that uses brownfield codebase mapping. Pairs naturally with Pattern 13 (Confidence Tagging) — `EXTRACTED` matches are higher-priority candidates than `INFERRED` ones.
- **What to adapt:** A pre-generation step in the executor's prompt template that runs the index query and injects results; a "must address each candidate" output contract field.
- **See also:** [./self-healing-and-verification.md](./self-healing-and-verification.md)

---

## Group D: Extensibility and Adaptability

Patterns that enable the framework itself to grow and adapt.

---

### Pattern 15: Install-Time Profile + Runtime Surface Toggle

- **Origin:** GSD (Skill Surface Budget Module, ADR-0011)
- **Problem it solves:** A framework with 86+ skills is too heavy for "just fix a bug" usage. But stripping features for a minimal install shouldn't require reinstalling when the user needs something heavier. And reinstalling shouldn't blow away user customizations.
- **How it works:** Two separate mechanisms:
  - **Install-time profiles:** `--profile=core` (six core-loop skills), `--profile=standard` (core + phase management), full default. Profiles compose: `--profile=core,audit`. `--minimal` aliases `--profile=core`. Closure over `requires:` frontmatter in each skill ensures transitive install (if skill A requires skill B, installing A installs B automatically).
  - **Runtime cluster toggle:** `/gsd:surface` enables or disables cluster-level skill groups without reinstall. Cluster definitions in `bin/lib/clusters.cjs`; state persisted in `<config>/.gsd-surface.json`.
- **Transferability:** HIGH. The split between "what's installed" and "what's active" is a clean separation that applies to any framework with a large surface. The `requires:` frontmatter dependency declaration is a reusable pattern for managing transitive install.
- **What to adapt:** The `requires:` frontmatter dependency declaration; the cluster-toggle as a lightweight runtime knob that doesn't require reinstall; the profile composition syntax (`core,audit`). Also: treat AI specs and skills as versioned, packaged artifacts (npm/OCI/PyPI) with semver and a BOM-style coordinator — the model OpenRewrite uses to ship recipes as JARs scanned for `META-INF/rewrite/*.yml` and aligned via `rewrite-recipe-bom` ([https://docs.openrewrite.org/running-recipes/getting-started](https://docs.openrewrite.org/running-recipes/getting-started)). This unlocks a shared catalog where third-party skill modules can be pulled in, pinned, and discovered (`mvn rewrite:discover` analog) instead of being copy-pasted into every repo.
- **Extension — Harness templates per service topology.** A complementary axis (Harness Engineering — [https://martinfowler.com/articles/harness-engineering.html](https://martinfowler.com/articles/harness-engineering.html), §Harness templates): bundle vertical "harness templates" per phase type or service topology (API service, data pipeline, AI integration, frontend SPA). Each template ships an AGENTS.md skeleton, lint config, judge prompts, and a starter VALIDATION.md. Templates share the same drift problem as service templates — they need a refresh story.
- **See also:** [./multi-runtime-support.md](./multi-runtime-support.md)

---

### Pattern 16: Constitution as Governance Artifact

- **Origin:** GitHub Spec Kit (`/speckit.constitution`, `.specify/memory/constitution.md`)
- **Problem it solves:** Project-wide decisions — "always use async/await," "never add new dependencies without discussion," "prefer server-side rendering for all pages" — drift silently as the project evolves. They exist in meeting notes, Slack threads, or people's memories, but not in any artifact the AI agent consults.
- **How it works:** `/speckit.constitution` establishes governing principles and writes them to `.specify/memory/constitution.md`. This file is consulted during every phase. It is separate from the spec (which describes WHAT to build) and the plan (which describes HOW to build it) — the constitution governs HOW decisions are made, not what is built.
- **Transferability:** MEDIUM-HIGH. Any long-running project benefits from a durable governance artifact. The separation from spec and plan is important — mixing them creates a document that is too large and too volatile to be authoritative.
- **What to adapt:** The idea that governance is a first-class artifact with its own file, its own command to populate it, and an explicit "consult during every phase" rule. The constitution doesn't have to be large — even a dozen principles is enough.
- **Extension — versioned with provenance back to friction telemetry.** Pattern 16 establishes the constitution as a first-class file. Böckeler's Memo #13 ([https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html](https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html)) adds: each rule should carry provenance back to the friction case that motivated it. Link each principle to the "go-wrong" log entry (see Pattern 4 extension) that introduced it. This turns the constitution from a static document into a living artifact whose growth is justified by observed failure cases.
- **See also:** [./local-storage-and-artifacts.md](./local-storage-and-artifacts.md)

---

### Pattern 17: Current-vs-Proposed Spec Separation

- **Origin:** OpenSpec (Fission-AI/OpenSpec, `openspec/specs/` vs `openspec/changes/`)
- **Problem it solves:** Editing the main spec while implementing a change means the spec is simultaneously a description of current reality and a description of a proposed future. The two are conflated. Any agent that reads the spec can't tell whether a given section describes what exists or what's planned.
- **How it works:** `openspec/specs/` holds current source-of-truth specs. `openspec/changes/<name>/` holds proposed deltas — a proposal, spec deltas, design, and tasks. On archive (after implementation), deltas are automatically merged back into `openspec/specs/`. Specs stay current without manual hygiene. This is a mini PR/branch model inside the spec folder.
- **Transferability:** MEDIUM-HIGH. Directly applicable to brownfield projects where "what exists" and "what's planned" need to be kept separate. The `archive` step that auto-merges spec deltas is the key — it eliminates the common failure mode where specs are updated before implementation but never re-reconciled after.
- **What to adapt:** The `changes/<name>/` folder model for proposed work; the `archive` command that auto-merges deltas back into source-of-truth specs.
- **See also:** [./local-storage-and-artifacts.md](./local-storage-and-artifacts.md)

---

### Pattern 18: Conditional Skill Delegation with One-Shot Nudges

- **Origin:** TLC spec-driven (`mermaid-studio` and `codenavi` integrations, `SKILL.md`)
- **Problem it solves:** A framework can't know which complementary skills or tools the user has installed. Mandatory dependencies break in many environments. Repeated install recommendations become noise that the user learns to ignore.
- **How it works:** A standard probe-or-fallback pattern: check if the optional skill is available → delegate to it if present → fall back to built-in behavior gracefully → recommend install at most ONCE per session, never again. For `mermaid-studio`: if unavailable, fall back to inline mermaid code blocks. For `codenavi`: if unavailable, fall back to `code-analysis.md` (ast-grep → ripgrep → grep). The "one-shot nudge" constraint prevents the recommendation from becoming noise.
- **Transferability:** HIGH. The "recommend once" rule is the key. Most frameworks either make optional integrations mandatory (breaking many environments) or never recommend them (leaving capability on the table).
- **What to adapt:** The probe-or-fallback pattern as a standard template for optional integrations; the "display this recommendation at most once per session" constraint as an explicit rule, not an aspiration.
- **See also:** [./auxiliary-tooling.md](./auxiliary-tooling.md)

---

### Pattern 19: Git Merge Driver for Shared Artifacts

- **Origin:** Graphify (`graphify hook install`, `graph.json`)
- **Problem it solves:** When multiple agents or developers commit changes to the same shared artifact (a graph file, a spec file, a state file), standard git merge produces conflict markers that corrupt the structure of the file and require manual resolution.
- **How it works:** A custom git merge driver performs union-merge on `graph.json`. Concurrent commits are merged without conflict markers — both sets of additions are preserved. Installed via `graphify hook install`, which writes the merge driver configuration into `.git/config` and `.gitattributes`. The mechanism is transparent to agents that don't know about it.
- **Transferability:** MEDIUM. Directly applicable to any framework artifact that multiple agents write to concurrently — `STATE.md` (if parallel agents update it), knowledge graphs, shared task lists, or any append-heavy artifact where union-merge semantics are correct.
- **What to adapt:** The concept of a custom merge driver for framework-managed files. The union-merge strategy is correct for append-heavy artifacts; it is not correct for artifacts where ordering or uniqueness matters.
- **See also:** [./workflow-and-orchestration.md](./workflow-and-orchestration.md) · [./local-storage-and-artifacts.md](./local-storage-and-artifacts.md)

---

### Pattern 24: Self-Describing Skill Manifest with Estimated Effort

- **Origin:** OpenRewrite (recipe descriptors: `@Option`, `displayName`, `estimatedEffortPerOccurrence`, tags)
- **Problem it solves:** A planner LLM doing tool-selection over an opaque skill catalog is a known weakness. GSD's `requires:` frontmatter handles dependencies but not capability description.
- **How it works:** Require every AI skill to publish a typed manifest including parameters, display name, description, tags, and an `estimatedEffortPerOccurrence` field — modeled on OpenRewrite's recipe descriptors ([https://docs.openrewrite.org/concepts-and-explanations/recipes](https://docs.openrewrite.org/concepts-and-explanations/recipes)). The manifest is the input the planner LLM does tool-selection over (no prompt-time prose), and `estimatedEffortPerOccurrence` lets product owners prioritize a backlog of automated migrations the way OpenRewrite users already do.
- **Transferability:** HIGH. Sibling to Pattern 15 (install-time profile + surface toggle) — addresses what a skill exposes for planner tool-selection rather than how it is installed.
- **What to adapt:** A typed manifest schema (parameters, displayName, description, tags, `estimatedEffortPerOccurrence`); planner tool-selection on manifest metadata only; effort sorting for prioritization.
- **See also:** [./multi-runtime-support.md](./multi-runtime-support.md)

---

### Pattern 26: Diagram-as-Executable-Spec

- **Origin:** ArchUnit (`adhereToPlantUmlDiagram(url, consideringAllDependencies())`)
- **Problem it solves:** Architecture diagrams drift silently from the code they purport to describe; an AI agent reading a diagram has no signal whether it still matches reality. The dossier covers governance prose (Constitution, Pattern 16) and structured deltas (OpenSpec current-vs-proposed, Pattern 17) but no mechanism where a *diagram itself* is the contract.
- **How it works:** ArchUnit lets a PlantUML component diagram with stereotyped components (`<<..pkg..>>`) be both the human-readable architecture and an executable `ArchRule`: components map to package identifiers, arrows are the only allowed dependencies, and any code-level edge not present in the diagram fails the build.
- **Transferability:** MEDIUM-HIGH — applicable wherever a structured diagram format (PlantUML, Mermaid component graphs, C4 model exports) can be parsed into a dependency contract.
- **What to adapt:** Pick one diagram format as canonical, give the AI agent a tool that derives rules from it, and run those rules on every commit. The diagram is the contract; the agent cannot drift without the diff failing. Cross-reference Pattern 16 (Constitution). (Source: [https://www.archunit.org/userguide/html/000_Index.html](https://www.archunit.org/userguide/html/000_Index.html) §8.5.)
- **See also:** [./local-storage-and-artifacts.md](./local-storage-and-artifacts.md)

---

### Pattern 27: Importable Spec Packs (Companion to Pattern 15)

- **Origin:** ArchUnit (`ArchTests.in(...)`, `@AnalyzeClasses`)
- **Problem it solves:** Pattern 15 governs the framework's own skill surface, but says nothing about how a project consumes *external* constraint packs (org-wide architecture standards, client-specific conventions, regulatory rule sets).
- **How it works:** ArchUnit's `ArchTests.in(SharedRules.class)` plus `@AnalyzeClasses(packages=...)` lets an organization publish a rule library (a JAR of `ArchRule` static fields) that downstream projects import like any other test dependency.
- **Transferability:** MEDIUM-HIGH. Spec packs become installable dependencies on top of the framework.
- **What to adapt:** A project declares which packs are active (via `requires:` frontmatter or a `spec-packs.yaml`), and the AI agent treats them as hard constraints. Analog to ESLint shared configs or shared lint rule sets, but with semantic, cross-file architectural scope. (Source: [https://www.archunit.org/userguide/html/000_Index.html](https://www.archunit.org/userguide/html/000_Index.html) §7.4, §9.)
- **See also:** [./multi-runtime-support.md](./multi-runtime-support.md)

---

### Pattern 28: Named Architectural Primitives Vocabulary

- **Origin:** ArchUnit Library API (`layeredArchitecture()`, `onionArchitecture()`, `slices().matching()`)
- **Problem it solves:** The dossier's vocabulary is process-shaped (phases, gates, agents). A small named-primitive vocabulary for *architecture* (layered, onion, hexagonal, slices) gives the AI agent a high-signal target to comply with.
- **How it works:** ArchUnit's Library API encodes a handful of well-known architectures as parameterized DSL methods: `layeredArchitecture().layer(..).definedBy(..).whereLayer(..).mayOnlyBeAccessedByLayers(..)`, `onionArchitecture().domainModels(..).domainServices(..).applicationServices(..).adapter(..)`, `slices().matching(..).should().beFreeOfCycles()`.
- **Transferability:** MEDIUM-HIGH for frameworks targeting brownfield projects with established architectural patterns.
- **What to adapt:** Ship a curated catalog of named architectural patterns as first-class spec primitives ("this project is layered: controller → service → persistence"; "this project is onion: domain ← application ← adapters"). The AI agent then writes against a small, well-known parameter-driven vocabulary instead of free-form architectural prose, which is much higher signal at a tiny token cost. (Source: [https://www.archunit.org/userguide/html/000_Index.html](https://www.archunit.org/userguide/html/000_Index.html) §8.1, §8.2, §8.4.)
- **See also:** [./self-healing-and-verification.md](./self-healing-and-verification.md)

---

## Pattern Ranking Summary Table

| # | Pattern | Origin | Transferability | Primary problem solved |
|---|---|---|---|---|
| 1 | Compound init handlers | GSD | HIGH | Context re-discovery cost |
| 2 | Two-stage namespace routing | GSD | HIGH | Eager skill listing token cost |
| 3 | Per-file token budgets + health zones | TLC | HIGH | Unbounded state file growth |
| 4 | ID-based ageable persistent memory | TLC | HIGH | Silent state accumulation |
| 5 | Auto-sized pipeline with escape valves | TLC | HIGH | Rigid vs overcomplicated workflow |
| 6 | Sub-agent context contract | TLC | HIGH | Context pollution between tasks |
| 7 | Wave-based parallelism + state lockfile | GSD | MEDIUM-HIGH | Race conditions in parallel execution |
| 8 | Diagnose-into-PLAN self-healing | GSD | HIGH | Fragmented fix-mode workflows |
| 9 | Three-role model config | Task Master | HIGH | One model doing all jobs |
| 10 | Asymmetric decision coverage gates | GSD | HIGH | Silent decision drift |
| 11 | Test-as-spec + SPEC_DEVIATION | TLC | HIGH | Silent spec drift |
| 12 | Parallel-safety as test property | TLC | HIGH | Flaky parallel tests |
| 13 | Confidence tagging | Graphify | MEDIUM | Undifferentiated AI analysis |
| 14 | Package legitimacy gate | GSD | MEDIUM | Slopsquatting / supply-chain |
| 15 | Install-time profile + surface toggle | GSD | HIGH | Too-heavy default install |
| 16 | Constitution as governance artifact | Spec Kit | MEDIUM-HIGH | Governance drift |
| 17 | Current-vs-proposed spec separation | OpenSpec | MEDIUM-HIGH | Spec/reality conflation |
| 18 | Conditional delegation + one-shot nudge | TLC | HIGH | Broken optional dependencies |
| 19 | Git merge driver for shared artifacts | Graphify | MEDIUM | Concurrent write conflicts |
| 20 | Lossless Semantic Tree (LST) substrate | OpenRewrite | HIGH (where IR investment is justified) | Text-level edits hide hallucinated APIs |
| 21 | Authored composition of typed transformations (Recipe DAG) | OpenRewrite | HIGH | Coarse-grained workflow primitives |
| 22 | Precondition scope filter | OpenRewrite | HIGH | Unbounded LLM-on-whole-repo cost |
| 23 | Isomorphic vs non-isomorphic edits (tiered review gating) | OpenRewrite | HIGH | Uniform review intensity on heterogeneous edits |
| 24 | Self-describing skill manifest with estimated effort | OpenRewrite | HIGH | Opaque skill catalog for planner tool-selection |
| 25 | Frozen baseline with ratchet semantics | ArchUnit | HIGH | New rule on legacy codebase = uniform fail/warn dilemma |
| 26 | Diagram-as-executable-spec | ArchUnit | MEDIUM-HIGH | Architecture diagrams drift silently from code |
| 27 | Importable spec packs (companion to Pattern 15) | ArchUnit | MEDIUM-HIGH | No mechanism for external constraint packs |
| 28 | Named architectural primitives vocabulary | ArchUnit | MEDIUM-HIGH | Free-form architectural prose is low-signal |
| 29 | Guides + sensors taxonomy | Harness Engineering | HIGH | Gates lack feedforward/feedback distinction |
| 30 | Computational vs inferential control labelling | Harness Engineering | HIGH | No cost-tier label on verifications |
| 31 | Approved scenarios for AI-generated behaviour tests | Lex Lerumph (via Harness Engineering) | HIGH (workflow/prompt phases) | RED-test immutability awkward for AI-authored fixtures |
| 32 | Reuse-awareness pre-check | Böckeler Memo #13 (mechanism: Graphify) | HIGH (brownfield) | AI re-implements existing components silently |
