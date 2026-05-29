# Workflow and Orchestration

> Cross-cutting topic file — synthesized from raw research cache.
> Primary sources: [`../frameworks/gsd.md`](../frameworks/gsd.md),
> [`../frameworks/tlc-spec-driven.md`](../frameworks/tlc-spec-driven.md),
> [`../frameworks/adjacent-frameworks.md`](../frameworks/adjacent-frameworks.md).
> Related topics: [`./context-engineering.md`](./context-engineering.md),
> [`./self-healing-and-verification.md`](./self-healing-and-verification.md),
> [`./patterns-worth-stealing.md`](./patterns-worth-stealing.md).

---

## 1. Phase Models Compared

| Framework | Phases / Commands | Rigid or Adaptive? |
|---|---|---|
| GSD | 6-command loop: `new-project` → `discuss-phase` → `plan-phase` → `execute-phase` → `verify-work` → `ship` | Adaptive (auto-advance via `/gsd-progress --next`) |
| TLC spec-driven | 4 phases: Specify → Design → Tasks → Execute | Adaptive (auto-sizing matrix; Design and Tasks are optional) |
| GitHub Spec Kit | 7 commands: `constitution` → `specify` → `clarify` → `plan` → `tasks` → `analyze` → `implement` | Semi-rigid (sequential gates; `clarify` recommended before `plan`) |
| OpenSpec | `propose` → `apply` → `archive` triplet | Fluid (no phase gates; any artifact editable at any time) |
| Task Master | `parse-prd` → `expand` → `next` → `implement` loop | PRD-driven, continuous (no fixed phase count) |
| BMAD-METHOD | Analyst/PM/Architect planning → Scrum Master stories → Developer execution | Scale-adaptive (depth adjusts to detected project complexity) |

The frameworks split into two camps on the question of whether phase gates are load-bearing. GSD, Spec Kit, and TLC use gates to enforce an ordering guarantee: no execution begins before a plan exists, no plan begins before a spec is locked. Gates make it impossible to accidentally skip verification or commit to implementation before decisions are documented. The cost is ceremony — a two-line bug fix still has to enter the loop somewhere, which is why all three of these frameworks also provide a fast-path escape (GSD's `/gsd-quick`, TLC's quick mode, Spec Kit's profile system). Gate-based frameworks also tend to accumulate richer artifacts per phase precisely because the gate forces a pause: GSD's `discuss-phase` produces numbered decision IDs (`D-01`, `D-02`) that downstream gates then verify by ID match, creating a traceable chain from decision to plan to implementation.

OpenSpec and Task Master take the opposite position. OpenSpec's `propose → apply → archive` triplet is deliberately minimal: any artifact can be edited after the fact, and the `archive` step handles reconciliation. Task Master is even more continuous — the PRD is the only front-loaded gate, and every subsequent operation (`expand`, `next`, `set-status`) is available at any time. This produces a lower floor on ceremony but also a lower ceiling on traceability: there is no mechanism equivalent to GSD's decision coverage gate or TLC's requirement traceability table unless the team adds one manually. BMAD sits between the two camps: it inherits an agile workflow metaphor (planning → stories → execution) but adds "scale-adaptive intelligence" that auto-adjusts how much ceremony each phase receives based on project complexity. The key asymmetry is that BMAD's adaptation is persona-driven rather than metric-driven — the Architect and Scrum Master agents exercise judgment about depth rather than evaluating a file-count or step-count threshold.

---

## 2. Auto-Sizing vs Fixed Pipelines

### TLC auto-sizing

TLC's auto-sizing matrix is the most explicit formalization of adaptive depth in this landscape. Four tiers (from `SKILL.md`):

| Scope | Trigger | Phases active |
|---|---|---|
| Small | ≤3 files, one-sentence change | Quick mode — skip entire pipeline |
| Medium | Clear feature, fewer than 10 tasks | Specify (brief) + Execute; Design and Tasks implicit |
| Large | Multi-component feature | Full Specify + Design + Tasks + Execute |
| Complex | Ambiguity, new domain | Full pipeline + Discuss sub-step + interactive UAT |

Quick mode carries hard guardrails: maximum 3 files, maximum 1 hour, no design decisions, no new dependencies. If the pre-implementation check reveals any of those thresholds exceeded, the skill escalates to the full pipeline rather than proceeding in quick mode.

The safety valve is the mechanism that holds the whole system together. Even when Tasks is skipped (Medium scope), Execute always starts by listing atomic steps inline. If that listing reveals more than five steps or complex dependencies, the agent must stop and create a formal `tasks.md`. This catches the common failure mode where a task was optimistically classified as Medium but unfolds into Large during implementation.

### OpenSpec's no-gates philosophy

OpenSpec positions its fluid model as a deliberate correction to what it calls "rigid phase gates" in Spec Kit. Any artifact — `proposal.md`, `design.md`, `tasks.md` — can be edited at any point in the lifecycle. The `archive` command handles the reconciliation work that gate-based systems handle via ordering: after implementation, spec deltas in `openspec/changes/<name>/` are merged back into the source-of-truth `openspec/specs/`. The discipline is moved from "you must do steps in order" to "the artifact stays current because the tooling reconciles it." This works well for brownfield projects where the idea of starting from a clean spec is unrealistic. OpenSpec also introduces a conceptual model absent from the other frameworks: the explicit separation of current truth (`openspec/specs/`) from proposed truth (`openspec/changes/<name>/`), which maps naturally to how engineers already think about branches. Each `changes/` folder is effectively a mini branch inside the spec layer, with `archive` playing the role of merge.

### BMAD's scale-adaptive intelligence

BMAD describes its equivalent of auto-sizing as "scale-adaptive intelligence" that automatically adjusts planning depth based on project complexity [unverified — this phrase appears in the README but the exact detection mechanism is not documented in public sources reviewed]. In practice, this is expressed through the Scrum Master agent's output: for more complex features, the Scrum Master produces hyper-detailed stories with embedded context; for simpler ones, the stories are leaner. The Developer agent consumes whatever it receives without needing to re-fetch architecture documents. BMAD's v6 Story Automator adds a complexity assessment step before each story is dispatched, which maps more closely to TLC's explicit auto-sizing decision — but the assessment is agent-driven rather than rule-driven, making the outcome less predictable and less auditable than TLC's deterministic tier selection.

### GSD's fixed core loop and artifact topology

GSD's six commands are always available, but each can function as a near-no-op in minimal setups. The `workflow.*` flags in `config.json` let individual phases be disabled (`research: false`, `plan_check: false`, `verifier: false`). The "absent = enabled" design principle means all gates are on by default, and the user explicitly opts out rather than opts in. The result is a fixed-shape loop that shrinks through configuration rather than auto-detection. This is the inverse of TLC's design: TLC's pipeline expands from a minimal baseline (Specify + Execute) when the scope warrants it, while GSD's pipeline contracts from a maximal baseline when the configuration disables features.

The `config.json` `granularity` flag also modulates the loop without changing its shape: `coarse` targets 3–5 phases, `standard` 5–8, and `fine` 8–12. Granularity controls the planner's output (how many `PLAN.md` files it generates per phase) rather than which commands exist. The practical effect is that a coarse project has fewer execution waves and faster turnaround at the cost of less precise dependency isolation.

The per-phase artifact topology is fixed and predictable — every phase produces the same set of files regardless of content:

| Phase artifact | Produced by | Consumed by |
|---|---|---|
| `XX-CONTEXT.md` | `discuss-phase` | `plan-phase`, verifier |
| `XX-RESEARCH.md` | `plan-phase` researchers | planner |
| `XX-NN-PLAN.md` | planner | executor, verifier |
| `XX-NN-SUMMARY.md` | executor | verifier, ship |
| `XX-VERIFICATION.md` | verifier | ship, UAT |
| `XX-VALIDATION.md` | Nyquist auditor | verifier |
| `XX-UI-SPEC.md` | `ui-phase` | executor |
| `XX-UAT.md` | `verify-work` | human, optional re-execute |

This predictable topology is what makes the compound init handler possible: `gsd-sdk query init.execute-phase 1` knows exactly which files to collect for phase 1 without inspecting the filesystem dynamically.

---

## 3. Sub-Agent Dispatch Patterns

Three distinct patterns emerge from the frameworks surveyed.

### Pattern A: Wave-based dependency parallelism (GSD)

GSD's `execute-phase` analyzes dependency declarations on each `PLAN.md` and groups plans into dependency waves before dispatching any executors:

```
Wave Analysis:
  Plan 01 (no deps)        ─┐
  Plan 02 (no deps)        ─┤── Wave 1 (parallel)
  Plan 03 (depends: 01)    ─┤── Wave 2 (waits for Wave 1)
  Plan 04 (depends: 02)    ─┘
  Plan 05 (depends: 03,04) ─── Wave 3 (waits for Wave 2)
```

Within a wave, each plan is dispatched to a fresh `gsd-executor` agent in a separate 200K-token context. On runtimes or models with context windows at or above 500K tokens, the executor and verifier prompts are enriched with prior-wave `SUMMARY.md` files and phase context; below that threshold, truncated cache-friendly versions are used instead. This adaptive enrichment means that the orchestration pattern is the same regardless of model capability, but the information density of each agent call scales with available context. Key mechanics that make safe parallel commits possible:

- Parallel executors commit with `--no-verify` to avoid build lock contention (e.g., cargo lock conflicts in Rust projects) from concurrent hook runs. (GSD ARCHITECTURE.md)
- The orchestrator runs `git hook run pre-commit` exactly once after each wave completes.
- All `writeStateMd()` calls go through lockfile-based mutual exclusion (`STATE.md.lock` with `O_EXCL` atomic creation, 10-second stale-lock timeout, jittered spin-wait).
- Checkpoint heartbeats (`[checkpoint] phase N wave W/M`) are emitted at every wave and plan boundary to prevent streaming timeouts on long-running parallel dispatches.

### Pattern B: Test-parallelism-gated `[P]` markers (TLC, Spec Kit)

TLC uses `[P]` markers on tasks in `tasks.md` to signal that a task can be executed concurrently. A `tasks.md` file also carries an explicit Parallel Execution Map section — a diagram showing which tasks run in which phase and which are parallel:

```
Phase 1 (sequential foundation):
  Task 1.1 ──► Task 1.2 ──► Task 1.3

Phase 2 (parallel where safe):
  Task 2.1 [P] ─┐
  Task 2.2 [P] ─┤── all complete ──► Task 2.4
  Task 2.3 [P] ─┘

Phase 3 (integration):
  Task 3.1 ──► Task 3.2
```

However, `[P]` is gated by three conditions, all of which must hold simultaneously:

1. No unfinished dependencies.
2. The required test type is parallel-safe, as determined by the `TESTING.md` Parallelism Assessment section.
3. No shared mutable state with other `[P]` tasks in the same phase.

The critical insight is that parallel-safety is a property of the test suite, not just the implementation code:

> "If a task's tests are NOT parallel-safe, it MUST run sequentially even if its implementation code has no dependencies. The test execution is the bottleneck." (TLC `tasks.md` reference)

Spec Kit uses the same `[P]` marker convention in its `tasks.md` files but without the same three-condition rigor documented in TLC. Spec Kit's `[P]` markers appear alongside TDD ordering constraints (`/speckit.tasks` produces tasks with TDD ordering), but the parallelism assessment is not anchored to a separate `TESTING.md` Parallelism Assessment section.

### Pattern C: PRD decomposition tree (Task Master)

Task Master's approach has no explicit wave model. Instead, it starts from a single `parse-prd` invocation that generates a flat-ish task list, and then uses `expand_task` as the primary decomposition primitive — any task can be recursively broken into subtasks on demand. Tags function as workstream isolation: tasks belong to tags, and cross-tag movement is supported without creating parallel git branches (`--from-tag=backlog --to-tag=in-progress --with-dependencies`). Before committing to the full plan, `complexity-report` / `analyze-project-complexity` surfaces a complexity signal that can trigger additional decomposition. Task Master has no built-in parallel-execution orchestration analogous to GSD waves; parallelism is left to the IDE agent consuming the MCP tools. The closest analogue to wave-based dispatch is the `loop` command, a named automation primitive for autonomous sequential task execution, but it does not implement dependency-wave analysis.

What distinguishes Pattern C architecturally is that the decomposition tree is a runtime artifact, not a pre-planned one. In GSD, dependency waves are computed from a fully specified set of `PLAN.md` files before any executor is dispatched. In Task Master, the tree grows incrementally: a developer runs `next`, observes the next task, runs `expand` if it looks too coarse, and then executes. The planning horizon is intentionally short. This matches the mental model of developers who want to stay in flow rather than front-load a full breakdown, but it means the framework provides fewer guarantees about inter-task dependency correctness at the time execution begins.

---

## 4. Model Profile Routing

### GSD: 5-layer precedence

GSD defines five named global profiles (`quality`, `balanced`, `budget`, `adaptive`, `inherit`) and resolves the model for each agent call through a five-layer precedence stack, highest to lowest:

```
1. model_overrides[<agent>]            ← per-agent override
2. dynamic_routing.tier_models[<tier>] ← auto-escalate on soft failure
3. models[<phase_type>]                ← phase-level (planning, research, execution, etc.)
4. model_profile (per-agent column)    ← global tier strategy
5. Runtime default                     ← fallback
```

Built-in tier maps for the `claude` runtime: `opus` = `claude-opus-4-7`, `sonnet` = `claude-sonnet-4-6`, `haiku` = `claude-haiku-4-5`. The `model_profile: "inherit"` setting defers entirely to whatever model the user's IDE session is running — making GSD usable with no model configuration at all. Dynamic routing (layer 2) enables automatic escalation: if a soft failure occurs (e.g., a plan-checker iteration fails), the router can promote the next attempt to a heavier tier without manual intervention.

### Task Master: three-role config

Task Master defines three named model slots: `main` (implementation), `research` (live web lookup via Perplexity or similar), and `fallback`. Different models for different job types within the same workflow. The research model is explicitly separated because it runs against live web content and benefits from models optimized for synthesis over generation. The fallback model activates when the primary model is rate-limited or unavailable. A zero-API-key path is supported via Claude Code CLI or Codex CLI OAuth, so the three-role config can be wired without any new API key management. Task Master is also the only framework surveyed that natively integrates Perplexity as a first-class research backend, treating live web search as a named component of the workflow rather than an optional add-on.

### Model routing comparison

| Framework | Routing granularity | Key differentiator |
|---|---|---|
| GSD | 5-layer precedence per agent | Dynamic escalation on soft failure; `inherit` defers to IDE session |
| TLC | Implicit (no routing config documented) | Relies on runtime's default model throughout |
| Spec Kit | Implicit | No per-phase model config documented |
| OpenSpec | Explicit model quality recommendation | "Recommend Opus 4.5 and GPT 5.2 for high-reasoning tasks" [unverified — version numbers may have drifted] |
| Task Master | 3-role: main / research / fallback | Only framework with a dedicated research-model slot |
| BMAD | Persona-based (implicit) | Planning personas vs. execution personas; Scrum Master pre-bakes context to reduce Developer model load |

The table highlights that model routing is a first-class design concern only in GSD and Task Master. TLC, Spec Kit, and OpenSpec leave model selection to the user's IDE session, which is a valid choice for frameworks targeting simpler setups but means the framework cannot enforce cost or quality guarantees per phase.

### BMAD: persona-based model separation

BMAD's model routing is implicit in its persona architecture. Planning agents (Analyst, PM, Architect) may be configured to use a heavier model; execution agents (Developer) may use a faster one [unverified — BMAD README describes persona separation but does not publish a configuration reference for per-persona model assignment]. The key architectural contribution is the Scrum Master agent, whose job is to pre-bake architecture context into stories at handoff time so the Developer agent does not need to load the full planning corpus. This is a form of model-cost optimization through context pre-processing rather than model-profile routing.

---

## 5. Atomic Commits and Git Integration

**GSD** uses a `feat(NN-MM):` commit format per task inside `execute-phase`, where `NN` is the phase number and `MM` is the plan number. Parallel executors commit with `--no-verify` for wave-level efficiency; the orchestrator runs the pre-commit hook once per wave. `/gsd-ship N` generates a GitHub PR via the `gh` CLI with a structured body assembled from `PLAN.md`, `SUMMARY.md`, and `VERIFICATION.md` sections. The `gsd-validate-commit.sh` hook enforces Conventional Commit format on every commit outside the parallel-execution path.

**TLC** treats "one task = one commit" as a hard rule rather than a convention (stated in `implement.md`). The reference is Conventional Commits 1.0.0. The atomic-per-task discipline is stated in `implement.md` as an invariant, not a recommendation. Any deviation from the spec discovered during implementation is marked with a `SPEC_DEVIATION` inline comment rather than silently diverging, and the deviation surfaces in the sub-agent's return payload so the orchestrator can decide whether to accept it.

**Spec Kit** ties its git model to numbered feature branches: each spec folder (`001-create-taskify`) corresponds to a branch (`001-create-taskify`), making the branch name a human-readable pointer to the spec artifacts. `/speckit.taskstoissues` pushes the task list to GitHub Issues, bridging the spec layer into standard project management tooling.

**OpenSpec's** `archive` step is the git-adjacent operation: when a change is complete, `openspec/changes/<name>/` is moved to `openspec/changes/archive/YYYY-MM-DD-<name>/` and the spec deltas are merged back into `openspec/specs/`. This automated reconciliation keeps the source-of-truth spec current without manual hygiene, which is the OpenSpec equivalent of a merge-back workflow. No commit convention is prescribed — OpenSpec defers git workflow to team preference and focuses its discipline on the spec artifact lifecycle rather than the commit graph.

A practical note on the `--no-verify` pattern in GSD: skipping hooks per-executor and running them once per wave at the orchestrator level is a deliberate performance optimization for parallel execution. However, it assumes the pre-commit hook is idempotent and that a single post-wave run is sufficient to catch issues that would have been caught by per-commit runs. If a project's pre-commit hooks are not idempotent — for example, if they write to a shared file — the wave-level hook consolidation can produce incorrect results.

The most significant structural difference across the five approaches is where commit authority lives. In GSD, commits are produced by executor sub-agents and consolidated by the orchestrator's wave-level hook run — commit authorship is distributed across agents. In TLC, the single "one task = one commit" rule means commit authorship stays with whichever agent is executing that task. In Spec Kit, the numbered branch creates an external coordination mechanism (branch name = spec number) that makes commit provenance visible at the git-log level without requiring per-commit format enforcement.

---

## 6. Orchestration Layer Design

### GSD: thin orchestrators with SDK seams

GSD's design principle states explicitly that "workflows never do the heavy work themselves" (`ARCHITECTURE.md`). Every orchestrator (a workflow `.md` file) follows the same dispatch pattern — load context via SDK, resolve model, spawn agent, collect result, update state — with no exceptions for any of the 33+ agents in the roster:

```
Orchestrator (workflow .md)
   ├── Load context: gsd-sdk query init.<workflow> <phase>
   ├── Resolve model: gsd-sdk query resolve-model <agent-name>
   │   Returns: opus | sonnet | haiku | inherit
   ├── Spawn Agent (Task/SubAgent call)
   ├── Collect result
   └── Update state: gsd-sdk query state.update / state.patch / state.advance-plan
```

The `gsd-sdk query init.*` call is a compound init handler: it returns project info, config, current state, and phase details as a single JSON blob. When the blob exceeds roughly 50 KB, it spills to a tempfile and the workflow receives an `@file:/tmp/gsd-init-XXXXX.json` reference instead. One loader call per workflow, deduplicated, ready to inject into the agent prompt. This design eliminates per-workflow re-discovery cost and ensures cache-friendly ordering is deterministic regardless of which files happened to be read in a prior session. State transitions are routed through the SDK (`state.advance-plan`, `state.update`, `state.patch`) rather than written directly to `STATE.md`, which is what allows the lockfile-based mutual exclusion to function correctly during parallel execution. The `shouldPreserveExistingProgress` invariant enforced inside `state-document.cjs` prevents state regressions: a completed plan cannot be marked pending again by a concurrent write.

The uniformity of the dispatch pattern is also what makes the 5-layer model resolution predictable: every agent call goes through `gsd-sdk query resolve-model <agent-name>`, which means model assignment is never ad-hoc and always observable. A developer debugging an unexpected model selection can add a single log call to `resolve-model` and see the resolution trace for every agent in the workflow. This observability property is absent from all other frameworks surveyed, which either defer model selection to the IDE or assign it through config files with no runtime inspection path.

### TLC: orchestrator holds planning context, sub-agents hold task slices

TLC's orchestrator does not spawn sub-agents for planning or validation — those phases require "the full accumulated context to be coherent" (TLC `SKILL.md`). Sub-agents are dispatched only for implementation tasks (both sequential and parallel). The orchestrator holds `spec.md`, `design.md`, and `tasks.md` in its context while each sub-agent receives only its task definition plus the relevant coding principles, conventions, and testing guide. This split minimizes main-context pollution: file reads, edits, and test output generated during implementation stay in the sub-agent's context and are not returned to the orchestrator. The explicit include list (task definition, `coding-principles.md`, `CONVENTIONS.md`, `TESTING.md`, referenced spec/design context) and explicit exclude list (other tasks' definitions, accumulated chat history, validation reports from other tasks, `STATE.md` unless the task explicitly references a decision) are stated as a contract in the skill, not left to agent judgment. The sub-agent returns a fixed-shape payload (status, files changed, gate check result, `SPEC_DEVIATION` markers, issues) rather than a raw transcript. This makes the orchestrator's post-dispatch logic simple and deterministic: it reads one structured record per task rather than parsing a variable-length conversation.

### BMAD: multi-persona Party Mode and pre-baked story context

BMAD's orchestration model is structured around persona handoffs rather than a central workflow file. The Scrum Master agent occupies a unique position: it converts planning outputs (PRDs, architecture docs) into hyper-detailed stories with embedded context, explicitly so that the Developer agent can execute without re-fetching the planning corpus. This is a form of context pre-processing at handoff time. The Scrum Master's output is engineered for the Developer agent's consumption: architecture context that would require the Developer to load and reason across multiple documents is synthesized into each story's preamble, making each story independently actionable. This pattern — pre-baking cross-cutting context into the unit of work at handoff time — is distinct from GSD's approach of loading context dynamically through the SDK at dispatch time, and from TLC's approach of specifying exactly which documents each sub-agent should receive.

Party Mode is BMAD's mechanism for multi-agent design review within a single session: multiple agent personas (e.g., Architect + PM + Security Analyst) can participate in a discussion before the Scrum Master synthesizes the result into stories. Party Mode enables the kind of structured disagreement between roles that a single-agent session cannot replicate [unverified — described in BMAD README but the implementation mechanism in v6 is not publicly detailed]. BMAD's v6 Story Automator extends the orchestration further: it automates spec creation → implementation → test automation → code review → retrospective across multiple stories, with a complexity assessment driving agent selection for each story. This makes BMAD's v6 orchestrator the most autonomous of the frameworks surveyed, at the cost of the least human checkpointing per story.

---

## 7. Session Continuity and Workflow Resumability

A cross-cutting concern that the phase models do not fully capture is how each framework handles the end of a session — and the beginning of the next one. This matters because AI coding sessions have hard context limits, and a framework that does not encode a resumption contract forces users to reconstruct state manually.

**GSD** provides two resumption mechanisms. `/gsd-pause-work` writes a `continue-here.md` under `.planning/` as a session checkpoint, capturing stopped-at position, uncommitted changes, and the next recommended command. `/gsd-progress --next` auto-detects the current state from `STATE.md` and runs the appropriate next command, making resumption a single-command operation even without a `continue-here.md` file. The `STATE.md` schema includes explicit `stopped-at` and `resume-file` fields in its YAML frontmatter, so state detection is deterministic.

**TLC** uses `HANDOFF.md` at `.specs/HANDOFF.md` as the session checkpoint. It is capped at approximately 500 tokens and overwrites the previous handoff on each pause, keeping it lean. Contents are fixed-format: Completed, In Progress, Pending, Blockers, and Context (branch name, uncommitted files). The small size cap is intentional — the handoff is designed to be injected into the next session's opening prompt without consuming significant context budget.

**Spec Kit** has no dedicated session-resumption artifact documented in the sources reviewed. The numbered branch and numbered spec folder provide implicit resumption hints (the branch name tells you where you are), but no equivalent of `HANDOFF.md` or `continue-here.md` was identified [unverified].

**OpenSpec's** `/opsx:continue` command is part of its expanded profile, suggesting resumption was added after the initial minimal design. The `changes/<name>/tasks.md` checklist format, with checkboxes, gives the agent a visual progress indicator to resume from without requiring a separate checkpoint artifact.

**BMAD's** `bmad-help` skill, invokable at any time, is the closest to a resumption aid: it can answer "what should I do next?" as a self-discovery primitive. The Scrum Master agent's pre-baked story context also reduces the cost of resumption for the Developer agent — the story is already self-contained, so a new session can pick up mid-story without reloading architecture documents.

| Framework | Checkpoint artifact | Size constraint | Resumption mechanism |
|---|---|---|---|
| GSD | `continue-here.md` | Not specified | `/gsd-progress --next` auto-detects state |
| TLC | `HANDOFF.md` | ~500 tokens (hard cap) | Inject into next session opening prompt |
| Spec Kit | None identified [unverified] | — | Numbered branch provides implicit hint |
| OpenSpec | Checklist in `tasks.md` | Not specified | `/opsx:continue` command |
| BMAD | `bmad-help` skill (dynamic) | Not applicable | Self-discovery via `bmad-help` |

The pattern across all five frameworks is that resumability is addressed at the artifact level (structured files that survive session end) rather than at the runtime level (no framework relies on persistent agent memory). This is the correct architectural choice given current model limitations, but it places the burden of checkpoint discipline on the framework's tooling rather than on the user. TLC's HANDOFF.md size cap is the only explicit recognition that the checkpoint artifact itself can become a context problem if unconstrained.

---

## 8. Implications for Our Framework

- **Phase gates and fast paths are not mutually exclusive.** Every gate-based framework surveyed ships a complementary fast path (GSD's `/gsd-quick`, TLC's quick mode, Spec Kit's profiles). Designing the gate first and the fast path second appears to be the safer order — the safety valve that escalates a quick task to the full pipeline is only meaningful if the full pipeline is well-defined. TLC's safety valve (inline step listing that triggers formal `tasks.md` creation when more than five steps are revealed) is the tightest implementation of this principle: it catches miscategorized scope dynamically rather than requiring the user to reclassify before starting.

- **Parallel-safety is a test-suite property, not a code-dependency property.** TLC's three-condition `[P]` rule — specifically the requirement that `TESTING.md` Parallelism Assessment must confirm parallel-safety before `[P]` is allowed — suggests that most frameworks underspecify parallelism by focusing only on code dependencies. A framework that wants reliable parallel execution needs a test-parallelism classification mechanism as a first-class artifact. GSD's wave model handles this differently by running hooks once per wave rather than per executor, which moves the test-safety question to the post-wave integration level rather than the per-task level.

- **Sub-agent context contracts reduce orchestration coupling.** Both GSD (compound init handlers + fixed dispatch pattern) and TLC (explicit include/exclude lists for sub-agent input and a fixed return shape) invest in making the sub-agent boundary explicit. The recurring failure mode across frameworks that lack this is main-context pollution — implementation artifacts accumulate in the orchestrator context and degrade subsequent planning decisions. The TLC contract is particularly instructive: `STATE.md` is explicitly excluded from sub-agent input unless the task explicitly references a decision or blocker, which prevents the sub-agent from loading the entire project history when it only needs one decision.

- **State mutation routing through a single choke point prevents concurrent corruption.** GSD's lockfile-based `STATE.md.lock` and its `state-document.cjs` routing layer exist because parallel wave execution creates genuine concurrent write contention. Any framework that supports parallel sub-agents needs a write-serialization strategy before it needs parallelism, not after. The jittered spin-wait pattern (rather than a fixed-interval retry) in GSD's lock implementation is worth noting: fixed-interval retries create thundering-herd contention when many executors complete simultaneously at the end of a wave. The `shouldPreserveExistingProgress` invariant prevents a second class of corruption: a successfully completed plan cannot be overwritten as pending by a stale state write from a slower executor.

- **Model routing complexity scales with framework complexity.** GSD's 5-layer precedence stack is appropriate for a framework that ships 33 agents across 15 runtimes. A simpler framework probably needs only two tiers (planning vs. execution) and a global inherit fallback. The interesting design question is not which models to assign but whether the routing is observable — GSD's `resolve-model` SDK call makes the assignment inspectable at runtime, which aids debugging. Task Master's three-role config (main / research / fallback) is the simplest formalization that still captures the important distinction between models used for generation and models used for live information retrieval.

- **The `archive` / reconciliation step is an underexplored primitive.** OpenSpec's `archive` command — which merges spec deltas back into source-of-truth specs after implementation — solves a problem that gate-based frameworks sidestep by keeping specs immutable during execution. In practice, implementation almost always reveals at least minor spec corrections. A framework that does not have a reconciliation step accumulates spec drift silently. Whether the reconciliation is automated (OpenSpec) or surfaced as a `SPEC_DEVIATION` marker for human review (TLC) is a design choice with tradeoffs, but the absence of any reconciliation mechanism is the failure mode to avoid.

- **Session resumability should be a first-class artifact, not an afterthought.** All five frameworks encode resumability at the file level (GSD's `continue-here.md`, TLC's `HANDOFF.md`, OpenSpec's checklist-based `tasks.md`). The highest-leverage design here is TLC's 500-token size cap on `HANDOFF.md`: it is small enough to inject directly into an opening prompt without consuming context budget, which means resumption does not require a separate loading step. Any framework that wants reliable multi-session continuity should define both the checkpoint artifact format and its maximum size at design time.

- **Treat steering — not handoff — as the unit of work.** Böckeler's observation is that "even in successful sessions, I intervened, corrected and steered all the time, and often decided not to commit the changes" ([https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html](https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html)). A framework whose only first-class artifacts are `PLAN`/`SUMMARY`/`VERIFICATION` optimizes for the *handoff* but loses the steering signal that produced the handoff. A capturable steering-event log (what was redirected, why, which prompt edit was applied) is a candidate first-class artifact, distinct from the existing decision-coverage and `SPEC_DEVIATION` channels. The steering log doubles as raw material for the "go-wrong" log ritual (see Pattern 4 extension) and as evidence behind constitution updates (Pattern 16 extension).

- **Repair-the-instance vs update-the-harness are two different loops.** The dossier's diagnose-into-PLAN pattern (Pattern 8) handles individual verification failures, but the Harness Engineering article ([https://martinfowler.com/articles/harness-engineering.html](https://martinfowler.com/articles/harness-engineering.html)) names a second loop: when the *same kind* of failure recurs N times, the human (or an agent under human supervision) should add a guide or sensor so it stops recurring. Add a `harness-update` task type that triggers automatically when the failure classifier records the same root-cause class above a threshold within a milestone. Agents themselves can be used to draft the new control (a new lint rule, a new judge prompt, an AGENTS.md addition). This pairs naturally with Pattern 29 (Guides + Sensors taxonomy): a recurring failure either signals a missing guide (the agent did not know better) or a missing sensor (the failure was detectable only post-hoc).

- **Authored composition of typed transformations belongs in the workflow layer.** The dossier's primitives are phases, plans, tasks, and stories. OpenRewrite's Recipe + `recipeList` model (Pattern 21 — [https://docs.openrewrite.org/concepts-and-explanations/recipes](https://docs.openrewrite.org/concepts-and-explanations/recipes)) lets fine-grained transformations be composed declaratively in YAML. Translated to a spec-driven AI framework: define a `skill` contract such that deterministic skills (regex/AST refactors, code-mod recipes) and LLM skills expose the same options and validation surface; high-level specs are then a YAML DAG of skills. The planner does tool-selection over the DAG, not over chat prompts. The wave dependency analysis already present in GSD is the runtime; Recipe-DAG is the authored composition that the planner consumes.
