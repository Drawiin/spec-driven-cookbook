# Research Dossier — Summary

> Entry point for the spec-driven AI coding framework research.
> Produced: 2026-05-19. All detail files treat the post-validation framework files as the source of truth.

---

## 1. About This Dossier

This dossier documents a research sweep of seven spec-driven AI coding frameworks conducted in May 2026 to inform the design of a new framework being built by this team. It contains four framework deep dives (GSD, TLC Spec-Driven, Graphify, and four adjacent frameworks in one file), seven cross-cutting topic analyses, and this hub. To get design inputs fast, start with [`topics/patterns-worth-stealing.md`](topics/patterns-worth-stealing.md), which ranks thirty-two transferable patterns by transferability (the original nineteen plus thirteen added on 2026-05-24 from external sources — see §9 Incorporation Log). For depth on any framework, follow the links in Section 5. One source — a Cursor login/OAuth challenge URL — was auth-gated and could not be fetched; its contents are excluded from the dossier.

A useful framing introduced by the 2026-05-24 incorporation pass: the dossier's verification mechanisms can be read collectively as an *outer harness* around the agent. The Harness Engineering article ([https://martinfowler.com/articles/harness-engineering.html](https://martinfowler.com/articles/harness-engineering.html)) describes this harness cybernetically as a "governor" subject to **Ashby's Law of Requisite Variety** — the harness must have at least as much regulatory variety as the agent has behavioural variety. A practical diagnostic: when a phase fails repeatedly despite added controls, the harness probably lacks variety; narrow the scope or add a control of a different *kind* (a new sensor type, not another instance of the same).

---

## 2. Frameworks Studied

| Framework | Maintained by | What it is | Deep dive |
|---|---|---|---|
| GSD (get-shit-done) | TÂCHES / gsd-build | Meta-prompting + context engineering system for 15+ AI runtimes | [frameworks/gsd.md](frameworks/gsd.md) |
| TLC Spec-Driven | Felipe Rodrigues / tech-leads-club | 4-phase adaptive spec skill (Specify→Design→Tasks→Execute) | [frameworks/tlc-spec-driven.md](frameworks/tlc-spec-driven.md) |
| Graphify | Safi Shamsi | Knowledge graph builder for AI coding assistants | [frameworks/graphify.md](frameworks/graphify.md) |
| GitHub Spec Kit | GitHub | SDD toolkit with constitution, specify, clarify, plan, tasks, implement | [frameworks/adjacent-frameworks.md](frameworks/adjacent-frameworks.md) |
| OpenSpec | Fission-AI | Brownfield-first spec framework with current-vs-proposed model | [frameworks/adjacent-frameworks.md](frameworks/adjacent-frameworks.md) |
| Task Master | Eyal Toledano | MCP-server-based PRD-driven task management | [frameworks/adjacent-frameworks.md](frameworks/adjacent-frameworks.md) |
| BMAD-METHOD | bmad-code-org | Multi-agent agile framework with 12+ specialized agent personas | [frameworks/adjacent-frameworks.md](frameworks/adjacent-frameworks.md) |

---

## 3. At-a-Glance Comparison Table

| Dimension | GSD | TLC Spec-Driven | Graphify | GitHub Spec Kit | OpenSpec | Task Master | BMAD-METHOD |
|---|---|---|---|---|---|---|---|
| **Core abstraction** | Meta-prompting + wave-based agents | 4-phase adaptive pipeline | Knowledge graph (nodes + communities) | Specs + phases + constitution | Spec deltas (current vs proposed) | Tasks + subtasks + tags | Specialized personas + agile workflows |
| **Primary artifact** | `.planning/STATE.md` + per-phase `PLAN.md` | `spec.md` + `tasks.md` per feature | `graph.json` + `GRAPH_REPORT.md` | `specs/NNN/spec.md`, `plan.md`, `tasks.md` | `openspec/specs/` + `openspec/changes/` | `.taskmaster/tasks/` (PRD-derived) | PRDs, architecture docs, stories |
| **Greenfield / brownfield** | Both (`/gsd-new-project` + `/gsd-map-codebase`) | Both (brownfield-mapping ref) | Both (excels brownfield) | Both | Brownfield-first | Both (PRD-driven) | Both (scale-adaptive) |
| **Context-bloat strategy** | Fresh 200K subagent contexts; compound init; 2-stage namespace routing | ~15k base load; <40k Healthy-zone target; per-file limits; 16 lazy-loaded refs | Scoped graph queries; `--budget N` caps [unverified] | Phase-scoped artifacts; `[P]` markers | Minimal vs expanded profiles | Tiered tool loading (~5k–21k) | Persona separation; pre-baked story context |
| **Sub-agent model** | 33 agents in 11 categories; wave-based parallel execution | On-demand delegation; fixed input/output contracts; `[P]` 3-condition gate | N/A | `[P]` task markers in `tasks.md` | `/opsx:bulk-archive`; expanded profile | `expand_task`; tags as workstreams | 12+ personas; Party Mode; planning vs execution split |
| **Self-healing approach** | Debugger writes new PLAN.md; same execute loop; plan-checker 3×; asymmetric decision gates | Escape valve (>5 steps → stop); SPEC_DEVIATION markers; max 3 diagnostic iterations | Confidence tags (EXTRACTED/INFERRED/AMBIGUOUS) | `/speckit.clarify`, `/speckit.analyze`, `/speckit.checklist` | `/opsx:verify`; archive auto-merges spec deltas | `complexity-report`; fallback model role | Multi-agent reviews; TEA module; retro phase |
| **Local artifact layout** | `.planning/` | `.specs/` | `graphify-out/` | `.specify/` | `openspec/` | `.taskmaster/` | IDE config dirs (module-installed) |
| **Multi-runtime support** | 15 runtimes; install-time transform | Stack-agnostic; single SKILL.md | 17+ assistants [unverified]; per-platform subcommands | 30+ agents; slash commands or skills mode | 25+ tools; slash commands | MCP server (Cursor, Windsurf, VS Code, Claude Code, Q CLI) | Claude Code, Cursor via `npx` |
| **License** | Not found in docs reviewed | CC-BY-4.0 | MIT | MIT | MIT | MIT + Commons Clause | MIT |

---

## 4. Top 10 Patterns Worth Stealing

Patterns are drawn from [`topics/patterns-worth-stealing.md`](topics/patterns-worth-stealing.md). Each is rated HIGH transferability in that file. The entry for each pattern here gives the problem solved and what to adapt; for full mechanism detail, origin, and adaptation guidance, follow the link. The full file contains thirty-two patterns ranked across four groups (nineteen from the original 2026-05-19 sweep plus thirteen added on 2026-05-24 from external sources — see §9 Incorporation Log); only the top ten by transferability are featured here.

The 2026-05-24 incorporation pass also introduces an *outer harness* framing for these patterns: many of them can be read as either **guides** (feedforward — constitutions, AGENTS.md, the sub-agent context contract = Patterns 6 and 16) or **sensors** (feedback — decision coverage gate = Pattern 10, package legitimacy gate = Pattern 14, test-as-spec markers = Pattern 11, plan-checker, gsd-verifier). The unifying mental model is from Martin Fowler's *Harness Engineering* ([https://martinfowler.com/articles/harness-engineering.html](https://martinfowler.com/articles/harness-engineering.html)). See Patterns 29 and 30 for the explicit taxonomy.

### Group A: Context and Memory Management

Patterns that prevent context rot, manage token budgets, and persist institutional memory across sessions. These are foundational — the other groups depend on having stable context to work with.

---

**1. Compound Init Handlers**
*Origin: GSD (`gsd-sdk query init.<workflow>`)*

Each workflow entry point re-discovers state by reading scattered files independently, wasting tokens on repeated I/O and creating divergence risk when reads return stale data. GSD solves this with a single CLI call (`node gsd-tools.cjs init execute-phase 1`) that returns all context needed for that specific workflow as one JSON blob — project info, config, phase details, and state in cache-friendly order; when the payload exceeds approximately 50 KB it spills to a tempfile and the workflow expands `@file:/tmp/gsd-init-XXXXX.json`. This removes per-workflow file re-discovery cost, ensures deterministic cache-friendly context ordering, and makes cache invalidation predictable. Adapt the compound-load primitive: define a standard payload shape that all workflow entrypoints consume, centralize the assembly logic, and copy the tempfile spill threshold as a clean release valve for unexpectedly large payloads.

[Full detail](topics/patterns-worth-stealing.md)

### Group B: Context Management, Workflow, and Orchestration

Patterns that govern the flow of context into agents, the pipeline structure, and how agents are dispatched and coordinated. Note: Patterns 5–7 below (Per-File Token Budgets, ID-Based Memory, Two-Stage Namespace Routing) belong to the Context and Memory Management group in the full [patterns-worth-stealing.md](topics/patterns-worth-stealing.md) analysis; they are grouped here with workflow patterns for editorial conciseness in this top-10 summary.

---

**2. Auto-Sized Pipeline with Hard Escape Valves**
*Origin: TLC Spec-Driven (`SKILL.md`, `quick-mode.md`)*

Rigid phase pipelines do not scale from a typo fix to a greenfield epic, but soft phase-skipping allows complexity to accumulate silently until it is expensive to surface. TLC resolves this with four deterministic size tiers — Small (quick mode, ≤3 files), Medium (spec brief, <10 tasks), Large (full spec + design + tasks), Complex (with discussion and interactive UAT) — and a hard escape valve: "Even when Tasks is skipped, Execute ALWAYS starts by listing atomic steps inline. If that listing reveals >5 steps or complex dependencies, STOP and create a formal `tasks.md`." Quick mode has its own self-ejecting gate: if the pre-implementation check reveals more than 3 files, unclear dependencies, or design decisions, the agent escalates to the full pipeline rather than proceeding. Adapt the tiers and, above all, the escape valve — it is the mechanism that prevents silent complexity accumulation; the four tiers are less important than the rule that Execute always lists steps first and checks against a threshold.

[Full detail](topics/patterns-worth-stealing.md)

---

**3. Sub-Agent Context Contract**
*Origin: TLC Spec-Driven (`SKILL.md`, `tasks.md`, `implement.md`)*

Sub-agents receive too much context (degrading output quality) or too little (producing incoherent output) when the orchestrator makes ad-hoc decisions about what to pass each time. TLC defines a fixed input contract (the orchestrator MUST pass: the specific task definition from `tasks.md`, relevant `coding-principles.md` and `CONVENTIONS.md`, `TESTING.md`, and any spec or design context the task references) and an equally important "must NOT receive" list (other tasks' definitions, accumulated chat history, validation reports from other tasks, and `STATE.md` unless the task explicitly references a specific decision or blocker ID). The fixed five-field output shape — Status (Complete / Blocked / Partial), Files changed, Gate check result, SPEC_DEVIATION markers, Issues encountered — makes orchestration predictable and parallelism cheap. Adapt the output contract verbatim; the "must NOT receive" list requires active maintenance as the framework grows; it is as important as the input list.

[Full detail](topics/patterns-worth-stealing.md)

---

**4. Diagnose-into-PLAN Self-Healing**
*Origin: GSD (`gsd-debugger`, `ARCHITECTURE.md`)*

When verification fails, the natural instinct is to create a "fix mode" — a separate command path, a different context, special-case repair logic — which fragments the workflow surface and grows its own complexity surface. GSD collapses this: when `/gsd-verify-work N` finds a failure, it spawns `gsd-debugger` (the largest agent in the roster at approximately 47 KB), which writes a new `PLAN.md` into the same phase directory. The user re-runs `/gsd-execute-phase N` — the same command, the same executor agents, the same commit loop. Fix plans are first-class tasks in the normal workflow, not special-case repairs, which keeps the system's behavior surface minimal and every repair auditable by the same tooling. Adapt the principle that failures produce tasks, not exceptions; the concrete mechanism (writing a new PLAN.md) ports directly to any artifact-based framework.

[Full detail](topics/patterns-worth-stealing.md)

---

**5. Per-File Token Budgets with Health Zones**
*Origin: TLC Spec-Driven (`context-limits.md`)*

Persistent state files grow unboundedly; without size governance, `STATE.md` becomes too expensive to load affordably but too important to skip. TLC defines hard per-file limits with warning thresholds — `STATE.md`: max 10,000 tokens, warn at 7,000; `design.md`: max 8,000, warn at 6,400; `tasks.md`: max 10,000, warn at 8,000 — and three aggregate context health zones (Healthy <40k: silent; Moderate 40–60k: discrete footer note; Critical >60k: active warning with optimization suggestion). `STATE.md` additionally uses a graduated four-tier cleanup policy: <7k no action, 7–10k "Cleanup recommended" footer, >10k active "Cleanup now?" prompt, then move decisions older than 60 days to `STATE-ARCHIVE.md`. Adapt the three-zone model as the cheapest starting point (requires no tooling); graduate to per-file limits as artifacts grow and the zones prove insufficient.

[Full detail](topics/patterns-worth-stealing.md)

---

**6. ID-Based Ageable Persistent Memory**
*Origin: TLC Spec-Driven (`state-management.md`)*

State files accumulate silently — without identifiers there is no discipline around what to keep, what to age out, or how to cross-reference an entry from another artifact. TLC tags decisions (`AD-NNN`), blockers (`B-NNN`), and lessons (`L-NNN`) with sequential IDs, making every state entry queryable and referenceable by stable ID from specs, tasks, and commit messages. A dedicated Deferred Ideas section absorbs scope-creep impulses without losing them or acting on them immediately — giving scope creep a landing zone that is neither the trash nor the active backlog. The 60-day archive rule gives the cleanup policy a concrete, automatable threshold. Adapt the ID scheme (minimal and clean) plus the deferred-ideas section as a first-class slot; the 60-day rule is a concrete starting value that can be tuned.

[Full detail](topics/patterns-worth-stealing.md)

---

**7. Two-Stage Namespace Routing Meta-Skills**
*Origin: GSD (v1.40 consolidation, ADR-0011)*

Eager-listing a large skill surface costs thousands of tokens per session before any work begins, regardless of which skills are actually needed. GSD's v1.40 redesign replaced 86 flat skills (approximately 2,150 tokens) with six namespace meta-skill routers (approximately 120 tokens total): `/gsd-workflow`, `/gsd-project`, `/gsd-quality`, `/gsd-context`, `/gsd-manage`, `/gsd-ideate`. Each router description uses pipe-separated keyword tags of up to 60 characters rather than prose, following evidence that "keyword-dense tags outperform prose for routing at ~40% the token cost." The full skill loads only when the router determines it is needed for the current query. Adapt the router-as-skill pattern and the keyword-tag description format; the six-cluster taxonomy (workflow / project / quality / context / manage / ideate) is a reasonable starting taxonomy for most frameworks.

[Full detail](topics/patterns-worth-stealing.md)

**9. Three-Role Model Config (main / research / fallback)**
*Origin: Task Master (`TASK_MASTER_TOOLS`, three-role model config) — Group B in [patterns-worth-stealing.md](topics/patterns-worth-stealing.md)*

Using one model for all operations in a workflow wastes capability on simple task management and is too slow or expensive where depth is required; it also cannot satisfy the live-web-access requirement for external research. Task Master defines three named roles: `main` (implementation and task execution), `research` (live-web-grounded queries via Perplexity or equivalent — treated as a distinct capability class with different provider requirements, not a cheaper tier), and `fallback` (recovery when the primary model is unavailable or rate-limited). All three roles are independently configurable in the MCP config without touching workflow code. Adapt the three-role taxonomy; the critical design insight is that `research` is a separate capability class, not a cost-optimization variant of `main` — it requires live web access that most implementation models do not have.

[Full detail](topics/patterns-worth-stealing.md)

---

### Group C: Verification and Quality

Patterns that validate correctness before, during, and after execution — ensuring that decisions made early in the pipeline survive to the shipped artifact and that deviations are explicit rather than silent.

---

**8. Asymmetric Decision Coverage Gates**
*Origin: GSD (`gsd-discuss-phase`, `gsd-plan-checker`, `gsd-verifier`)*

Tracking user decisions from a discussion phase through planning and into shipped code requires blocking somewhere — but blocking at the wrong moment creates friction without preventing drift. GSD's Discuss phase produces numbered decision IDs (`D-01`, `D-02`, …) in `{phase}-CONTEXT.md`. A BLOCKING gate at plan-time refuses to mark the phase planned until every trackable D-id appears in at least one plan's `must_haves`, `truths`, or body — cheap to fix here, before code is written. A NON-BLOCKING gate at verify-time searches plans, SUMMARY files, modified files, and recent commit messages for each D-id and logs misses as a warning section in `VERIFICATION.md` — expensive to fix here, so it warns rather than halts. Two match modes (strict ID and 6+-word verbatim phrase) handle decisions referenced differently in plan prose; opt-out tags (`[informational]`, `[folded]`, `[deferred]`) prevent false-positive blocking on decisions that genuinely do not require coverage. Adapt the asymmetric blocking/non-blocking pair; the specific match modes and opt-out tags are also worth copying verbatim.

[Full detail](topics/patterns-worth-stealing.md)

---

**10. Test-as-Spec and SPEC_DEVIATION Markers**
*Origin: TLC Spec-Driven (`coding-principles.md`, `implement.md`)*

Implementation drifts from spec silently: tests get weakened to pass, specs get retroactively updated to match code, and eventually the test suite describes what the code happens to do rather than what it should do. TLC's response is two-part: RED-phase tests (written before implementation) are immutable during the GREEN phase — five hard rules: never weaken assertions, never delete a test to reduce failure count, never use skip/disable/pending to bypass failures, never modify RED-phase tests during GREEN, and "Tests are the spec — implementation conforms to tests, not the other way around." When a genuine deviation is necessary, the agent marks it inline with `// SPEC_DEVIATION: [what diverged] / Reason: [why]` rather than silently updating spec or test; these markers surface in sub-agent output reports so the orchestrator makes an explicit acceptance decision per deviation. Adapt the immutability rule plus the marker format; the output contract from Pattern 3 already includes a SPEC_DEVIATION field, making these two patterns composable.

[Full detail](topics/patterns-worth-stealing.md)

---

### Additional Patterns in the Full File

Nine patterns not featured above are covered in [`topics/patterns-worth-stealing.md`](topics/patterns-worth-stealing.md) with the same format (origin, mechanism, transferability, what to adapt):

- **Wave-Based Parallelism with State Lockfile** (MEDIUM-HIGH) — dependency-wave grouping with O_EXCL lockfile mutual exclusion for concurrent state writes; from GSD.
- **Parallel-Safety as a Property of Tests, Not Code** (HIGH) — the `[P]` marker requires `TESTING.md` Parallelism Assessment as the gate, not just code dependency absence; from TLC.
- **Confidence Tagging on Inferred Data** (MEDIUM) — EXTRACTED / INFERRED / AMBIGUOUS tags on every relation in an analysis artifact, built into the data model rather than added as post-hoc prose hedging; from Graphify.
- **Package Legitimacy Gate / Slopsquatting Defense** (MEDIUM) — two-level provenance-then-audit verdict taxonomy with slopcheck, human-verify checkpoints for suspicious packages, and hard stop on failed installs; from GSD.
- **Install-Time Profile + Runtime Surface Toggle** (HIGH) — `--profile=core/standard/full` at install time, `/gsd:surface` cluster toggle at runtime, `requires:` frontmatter for transitive install; from GSD.
- **Constitution as Governance Artifact** (MEDIUM-HIGH) — a separate persistent principles document consulted during every phase, distinct from spec (what to build) and plan (how to build it); from GitHub Spec Kit.
- **Current-vs-Proposed Spec Separation** (MEDIUM-HIGH) — `specs/` holds current truth, `changes/<name>/` holds proposed deltas, `archive` auto-merges on completion; from OpenSpec.
- **Conditional Skill Delegation with One-Shot Nudges** (HIGH) — probe-or-fallback for optional peer skills with a hard "recommend install at most once per session" rule; from TLC.
- **Post-Commit Rebuild Hook for Shared Artifacts** (MEDIUM) — a post-commit hook automatically rebuilds the canonical artifact file after every commit; from Graphify. `[note: the cache described this as a union-merge driver but the live README describes a post-commit rebuild hook — see graphify.md for correction]`

### Patterns Added 2026-05-24 from External Sources

Thirteen patterns were added from OpenRewrite, ArchUnit, Martin Fowler's "Harness Engineering," and Birgitta Böckeler's "Role of Developer Skills" memo. Full entries in [`topics/patterns-worth-stealing.md`](topics/patterns-worth-stealing.md); brief tag lines below.

- **Pattern 20: Lossless Semantic Tree (LST) Substrate** (HIGH where IR investment is justified) — propose AI edits against a typed, format-preserving IR rather than text; type info gives grounding, whitespace is tree-resident; from OpenRewrite.
- **Pattern 21: Authored Composition of Typed Transformations (Recipe DAG)** (HIGH) — `recipeList` lets deterministic and LLM skills compose uniformly in a YAML DAG; planner does tool-selection over the DAG; from OpenRewrite.
- **Pattern 22: Precondition Scope Filter** (HIGH) — every AI skill ships a deterministic precondition (glob/AST query/type predicate) that gates which files it may touch *before* the LLM is invoked; from OpenRewrite.
- **Pattern 23: Isomorphic vs Non-Isomorphic Edits (Tiered Review Gating)** (HIGH) — classify edits as safe (rename/retype/format) vs structural (replace function/change interface) and apply different review gates per class; from OpenRewrite.
- **Pattern 24: Self-Describing Skill Manifest with Estimated Effort** (HIGH) — every skill publishes parameters, tags, and an `estimatedEffortPerOccurrence` field that the planner selects on; from OpenRewrite.
- **Pattern 25: Frozen Baseline with Ratchet Semantics** (HIGH) — snapshot existing violations into a VCS-committed store; CI fails only on *new* violations, auto-shrinks when fixed; from ArchUnit.
- **Pattern 26: Diagram-as-Executable-Spec** (MEDIUM-HIGH) — a PlantUML/Mermaid component diagram is both human-readable architecture and an executable rule; any code edge not in the diagram fails the build; from ArchUnit.
- **Pattern 27: Importable Spec Packs** (MEDIUM-HIGH; companion to Pattern 15) — org-wide constraint packs become installable dependencies on top of the framework; from ArchUnit.
- **Pattern 28: Named Architectural Primitives Vocabulary** (MEDIUM-HIGH) — ship a curated catalog of named architectures (layered/onion/hexagonal/slices) as parameterized spec primitives instead of free-form architectural prose; from ArchUnit.
- **Pattern 29: Guides + Sensors Taxonomy** (HIGH) — every control is a guide (feedforward), a sensor (feedback), or both; spec items without paired sensors are unverifiable by construction; from Harness Engineering.
- **Pattern 30: Computational vs Inferential Control Labelling** (HIGH) — each control carries a second axis label (deterministic vs LLM-based) that drives lifecycle placement (pre-commit vs phase gate); from Harness Engineering.
- **Pattern 31: Approved Scenarios for AI-Generated Behaviour Tests** (HIGH for workflow/prompt phases) — fixtures combine input + expected output; runner regenerates expected, reviewer does diff review; complements Pattern 11; from Lex Lerumph via Harness Engineering.
- **Pattern 32: Reuse-Awareness Pre-Check** (HIGH for brownfield) — before generating new components, query a codebase index for semantically close existing symbols and surface a "candidate-for-reuse" list the executor must address; from Böckeler Memo #13 (mechanism via Graphify).

Several existing patterns received Extension sub-bullets (visible inline in [`topics/patterns-worth-stealing.md`](topics/patterns-worth-stealing.md)): Pattern 4 (team-level "go-wrong" log), Pattern 5 (vertical-slice constraint), Pattern 6 (per-hunk attribution from `Result.recipesThatMadeChanges`), Pattern 8 (universal diagnose-before-fix + OpenRewrite `causesAnotherCycle` cycles), Pattern 11 (architecture-rule tests + self-describing rules + AI-test redundancy axis + per-hunk attribution), Pattern 13 (OpenRewrite Markers + ArchUnit bytecode substrate), Pattern 15 (versioned packaged distribution + harness templates per service topology), Pattern 16 (versioned with provenance back to friction telemetry).

---

## 5. Dossier Index (Backlinks)

### Framework Deep Dives

- [frameworks/gsd.md](frameworks/gsd.md) — Full analysis of GSD: six-command core workflow (`/gsd-new-project` → `/gsd-discuss-phase` → `/gsd-plan-phase` → `/gsd-execute-phase` → `/gsd-verify-work` → `/gsd-ship`), compound init handlers, 33-agent roster across 11 categories, wave-based parallel execution with lockfile-protected state writes, hooks architecture (13 hook files), layered self-healing gates (plan-time, execute-time, post-execute, UAT), 15-runtime install-time transform system authored in Claude Code's native format, TypeScript SDK with sync runtime bridge, and auxiliary tooling (slopcheck, fallow, gh CLI, intel, graphify). GSD is the most architecturally complete framework in the dossier; it is also the most opinionated about tooling.

- [frameworks/tlc-spec-driven.md](frameworks/tlc-spec-driven.md) — Full analysis of TLC Spec-Driven v2.0.0: auto-sizing matrix and five hard phase-skip rules, quick-mode guardrails, three-zone aggregate context loading policy, per-file token limits with warning thresholds for 12 files, sub-agent delegation decision table, fixed input/output contracts, `[P]` parallel-safety conditions (3-condition gate), `.specs/` artifact layout with traceability IDs, 14-trigger lazy-loading system, five-step knowledge verification chain, and stop-condition table. TLC ships as a single SKILL.md plus 16 lazy-loaded reference files with no scripts or binaries.

- [frameworks/graphify.md](frameworks/graphify.md) — Full analysis of Graphify: 7-stage pipeline (detect→extract→build→cluster→analyze→report→export), Tree-sitter AST extraction without LLM involvement on source code, confidence tagging on every relation (EXTRACTED/INFERRED/AMBIGUOUS) built into the data model, local `graphify-out/` layout with gitignore recommendations, per-platform AI assistant integration via skill manifests and PreToolUse hooks, MCP server tool roster (`query_graph`, `get_node`, `get_neighbors`, `shortest_path`, PR triage tools), incremental rebuild tiers (`--update`, `--cluster-only`), and god-node/surprising-connection report sections. Graphify is a companion tool rather than a full spec framework, but its patterns for context-efficient codebase navigation are directly applicable.

- [frameworks/adjacent-frameworks.md](frameworks/adjacent-frameworks.md) — Survey of GitHub Spec Kit (constitution artifact as persistent governance doc, `/speckit.clarify` coverage-based questioning gate, four-level template priority cascade, `[P]` parallel markers, `/speckit.analyze` cross-artifact consistency check), OpenSpec (current-vs-proposed spec separation, archive auto-merge, no hard phase gates), Task Master (tiered tool loading with measured token costs, three-role model config, first-class `research` command with live-web access, `expand_task` decomposition primitive), and BMAD-METHOD (12+ specialized agent personas, planning vs execution agent split, hyper-detailed story pre-baking, Party Mode, module ecosystem); includes a cross-framework comparison table across eight dimensions.

### Cross-Cutting Topic Analyses

- [topics/context-engineering.md](topics/context-engineering.md) — How all five frameworks combat context rot across five solution categories: fresh subagent contexts (GSD's 200K per agent, TLC's delegation decision table, BMAD's persona boundaries), per-file and per-workflow token budgets (TLC's 12-file limit table, GSD's CI line caps), lazy loading and compound init (GSD's single-call JSON blob, TLC's trigger-phrase index, Graphify's scoped queries), persistent memory artifact design (comparing GSD's operational log, TLC's ID-based knowledge store, Spec Kit's governance document), and shared-artifact conflict resolution (GSD's O_EXCL lockfile, Graphify's git merge driver). Includes a cross-framework comparison table and design implications for a new framework.

- [topics/workflow-and-orchestration.md](topics/workflow-and-orchestration.md) — Phase sequencing models, auto-sizing rules and escape valves, wave-based dependency analysis and parallel execution, thin-orchestrator dispatch patterns (pseudocode from GSD ARCHITECTURE.md), state management and progress tracking (STATE.md YAML frontmatter schema, lockfile mechanics), checkpoint heartbeats, quick-mode self-ejection, and milestone lifecycle management across GSD, TLC, Spec Kit, OpenSpec, Task Master, and BMAD.

- [topics/self-healing-and-verification.md](topics/self-healing-and-verification.md) — Plan-time gates (plan-checker loop up to 3×, research gate blocking on unresolved questions, package legitimacy gate with slopcheck verdicts, requirements coverage gate, decision coverage gate with D-id tracking, Nyquist test coverage mapping), execute-time gates (atomic commits, STATE.md O_EXCL lockfile, checkpoint heartbeats, executor failure classifier with runtime-specific sentinel strings, node_repair budget), post-execute gates (verifier agent, schema drift, codebase drift), UAT self-healing via plan generation, SPEC_DEVIATION markers, and test integrity guardrails across frameworks.

- [topics/local-storage-and-artifacts.md](topics/local-storage-and-artifacts.md) — Artifact directory layouts and naming conventions for all seven frameworks (`.planning/`, `.specs/`, `graphify-out/`, `.specify/`, `openspec/`, `.taskmaster/`, IDE config dirs), token limits and graduated cleanup policies, cross-session handoff file designs (`continue-here.md` written by `/gsd-pause-work` vs TLC's single-slot `HANDOFF.md` at approximately 500 tokens), gitignore recommendations, traceability ID schemes, STATE.md YAML frontmatter schema for GSD, and git-committing conventions for shared artifacts.

- [topics/auxiliary-tooling.md](topics/auxiliary-tooling.md) — CLI toolchains and SDK layers (gsd-tools.cjs with 20+ domain modules, TypeScript SDK with sync runtime bridge using `synckit`/Atomics.wait, gsd-sdk shim), hooks architectures (13 GSD hook files and their event types), MCP server integrations, external tool integrations (slopcheck for package legitimacy, fallow v2.70+ for structural code review, Context7 MCP two-call sequence, codenavi for code navigation, mermaid-studio for diagrams, gh CLI for PR creation, intel for codebase intelligence), installer mechanics (469 KB / 10,700-line `bin/install.js`), and the probe-or-fallback pattern for optional integrations with one-shot install nudges.

- [topics/multi-runtime-support.md](topics/multi-runtime-support.md) — How GSD handles 15-runtime install-time content transformation (tool name mapping for Bash/Read/etc., hook event renaming PostToolUse↔AfterTool, agent frontmatter conversion per runtime, hyphen-to-colon command spelling rewrite for Gemini, Installer Migration Module ADR-0008 for version upgrades); how Graphify handles per-platform installation with layered PreToolUse hooks and instruction-file fallback strategies for 17+ assistants [unverified]; and how Spec Kit (30+ agents, slash commands or skills mode toggle), OpenSpec (25+ tools), and Task Master (MCP server across five IDE environments) achieve broad agent support.

- [topics/patterns-worth-stealing.md](topics/patterns-worth-stealing.md) — Thirty-two transferable design patterns ranked by transferability (HIGH / MEDIUM-HIGH / MEDIUM), grouped into four categories: Context and Memory Management (Patterns 1–4: compound init, two-stage namespace routing, per-file token budgets, ID-based persistent memory), Workflow and Orchestration (Patterns 5–9 plus Pattern 21: auto-sized pipeline, sub-agent context contract, wave-based parallelism, diagnose-into-plan self-healing, three-role model config, authored composition of typed transformations), Verification and Quality (Patterns 10–14 plus 20, 22, 23, 25, 29, 30, 31, 32: asymmetric decision gates, test-as-spec, parallel-safety as test property, confidence tagging, package legitimacy gate, LST substrate, precondition scope filter, isomorphic/non-isomorphic edit gating, frozen baseline with ratchet semantics, guides+sensors taxonomy, computational/inferential labelling, approved scenarios, reuse-awareness pre-check), and Extensibility and Adaptability (Patterns 15–19 plus 24, 26, 27, 28: install-time profile + surface toggle, constitution as governance artifact, current-vs-proposed spec separation, conditional delegation with one-shot nudge, git merge driver for shared artifacts, self-describing skill manifest, diagram-as-executable-spec, importable spec packs, named architectural primitives). Each entry includes origin framework, mechanism, transferability rating, what to adapt, and cross-links to supporting topic files.

---

## 6. Sources Cited

Sources are grouped by framework and limited to URLs that were actually fetched (HTTP 200) during the research runs on 2026-05-19. URLs not fetched are excluded.

**GSD (gsd-build/get-shit-done)**

- `https://raw.githubusercontent.com/gsd-build/get-shit-done/main/README.md` (project README)
- `https://raw.githubusercontent.com/gsd-build/get-shit-done/main/AGENTS.md` (agent registry overview)
- `https://raw.githubusercontent.com/gsd-build/get-shit-done/main/CONTEXT.md` (65 KB; context engineering reference)
- `https://raw.githubusercontent.com/gsd-build/get-shit-done/main/docs/ARCHITECTURE.md` (43 KB; design principles, agent roster, orchestration patterns)
- `https://raw.githubusercontent.com/gsd-build/get-shit-done/main/docs/COMMANDS.md` (55 KB; full command reference)
- `https://raw.githubusercontent.com/gsd-build/get-shit-done/main/docs/CONFIGURATION.md` (67 KB; config.json schema and model profiles)
- `https://raw.githubusercontent.com/gsd-build/get-shit-done/main/docs/CLI-TOOLS.md` (CLI and SDK tool reference)
- `https://raw.githubusercontent.com/gsd-build/get-shit-done/main/docs/FEATURES.md` (142 KB; full feature documentation)
- `https://raw.githubusercontent.com/gsd-build/get-shit-done/main/docs/USER-GUIDE.md` (60 KB; user guide)
- `https://api.github.com/repos/gsd-build/get-shit-done/contents/agents` (directory listing — 33 agent files confirmed)
- `https://api.github.com/repos/gsd-build/get-shit-done/contents/bin` (directory listing — installer + SDK shim)
- `https://api.github.com/repos/gsd-build/get-shit-done/contents/commands/gsd` (directory listing — 60+ command files)
- `https://api.github.com/repos/gsd-build/get-shit-done/contents/hooks` (directory listing — 12 hook files + lib/)
- `https://api.github.com/repos/gsd-build/get-shit-done/contents/scripts` (directory listing — 23+ CI and engineering scripts)
- `https://api.github.com/repos/gsd-build/get-shit-done/contents/sdk` (directory listing — TypeScript SDK)

**TLC Spec-Driven (tech-leads-club/agent-skills)**

- `https://raw.githubusercontent.com/tech-leads-club/agent-skills/main/packages/skills-catalog/skills/(development)/tlc-spec-driven/SKILL.md` (base skill file, v2.0.0)
- All 16 reference files at the same base URL under `references/`: `discuss.md`, `design.md`, `specify.md`, `tasks.md`, `implement.md`, `validate.md`, `quick-mode.md`, `project-init.md`, `roadmap.md`, `brownfield-mapping.md`, `concerns.md`, `state-management.md`, `session-handoff.md`, `context-limits.md`, `code-analysis.md`, `coding-principles.md`
- `https://api.github.com/repos/tech-leads-club/agent-skills/contents/packages/skills-catalog/skills/(development)/tlc-spec-driven/references` (directory listing — confirmed 16 files)

**Graphify (safishamsi/graphify)**

- `https://graphify.net/` (Graphify landing page; star count 3.7k+)
- `https://github.com/safishamsi/graphify` (GitHub repo — README, pipeline documentation)

**GitHub Spec Kit (github/spec-kit)**

- `https://raw.githubusercontent.com/github/spec-kit/main/README.md` (project README)

**OpenSpec (Fission-AI/OpenSpec)**

- `https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/README.md` (project README)

**Task Master (eyaltoledano/claude-task-master)**

- `https://raw.githubusercontent.com/eyaltoledano/claude-task-master/main/README.md` (project README)

**BMAD-METHOD (bmad-code-org/BMAD-METHOD)**

- `https://github.com/bmad-code-org/BMAD-METHOD` (repo metadata)
- `https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/README.md` (project README)

**External Sources (added 2026-05-24 — see §9 Incorporation Log)**

- `https://docs.openrewrite.org/` (OpenRewrite docs hub; fetched recipes, visitors, LSTs, preconditions, YAML format reference, getting-started) — source for Patterns 20, 21, 22, 23, 24 and Extensions to Patterns 6, 8, 11, 13, 15.
- `https://www.archunit.org/` (ArchUnit landing + user guide §7, §8.1–8.6) — source for Patterns 25, 26, 27, 28 and Extensions to Patterns 11, 13.
- `https://martinfowler.com/articles/harness-engineering.html` (Martin Fowler / Birgitta Böckeler [inference], 2026-04 — "Harness Engineering") — source for Patterns 29, 30, 31 and implications added to `topics/self-healing-and-verification.md` §8 and `topics/workflow-and-orchestration.md` §8, plus the cybernetic/Ashby framing in §1 above.
- `https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html` (Birgitta Böckeler memo #13 in *Exploring Gen AI*) — source for Pattern 32 and Extensions to Patterns 4, 5, 8, 11, 16, plus the impact-radius and DX-guardrails sections in `topics/self-healing-and-verification.md` §8 and §9.

Detail per source lives in `research/external-sources/summaries/` (one summary per URL) and `research/external-sources/reviews/` (one alignment review per source vs the dossier).

---

## 7. Open Questions and Unverified Items

- GSD's exact agent behavior details: agent roles were paraphrased from the `ARCHITECTURE.md` taxonomy table, not from each agent's frontmatter directly; `docs/INVENTORY-MANIFEST.json` was not fetched.
- Whether `/gsd-ultraplan-phase` is general-purpose or Claude-only; the docs label it `[BETA]` without clarifying runtime scope.
- GSD's exact model tier mappings for non-Claude, non-Codex runtimes: referenced in the GSD issue tracker as Issue #2612; only the Claude tier map (`opus` = `claude-opus-4-7`, `sonnet` = `claude-sonnet-4-6`, `haiku` = `claude-haiku-4-5`) was confirmed in documents reviewed.
- GSD's plan-checker `8-dimension check`: the plan-checker loop and its "up to 3×" retry behavior are documented in `ARCHITECTURE.md`, but the specific eight dimensions it evaluates are stated as not enumerated in public docs reviewed.
- GSD's license: the project README, ARCHITECTURE.md, and CONFIGURATION.md do not explicitly state the license; the license was not confirmed from documents reviewed in this research run.
- Graphify's git hook: the live README describes a post-commit rebuild hook; the research cache described it as a union-merge git merge driver. The live README was consulted and the merge-driver claim is not supported there — the detail files flag this claim as unverified.
- Graphify's star count: the research cache reported approximately 49k GitHub stars; `graphify.net` shows 3.7k+. The cache figure is likely inaccurate; `graphify.net` is the more recently verified source.
- Graphify's 17+ assistant support, MCP tool names (`query_graph`, `get_node`, `get_neighbors`, `shortest_path`, `list_prs`, `get_pr_impact`, `triage_prs`), and `--cluster-only` and `--budget` flags: sourced from the cache and landing page only; not confirmed in the live GitHub README.
- BMAD Story Automator v6.6+: referenced in the research cache but not found on the live BMAD README landing page; sourced from cache only.
- BMAD-METHOD's star count (~47k) and Task Master's star count (~26k): both sourced from the research cache and not independently verified against live GitHub metadata.
- OpenSpec's documented model recommendations ("Opus 4.5 and GPT 5.2"): the adjacent frameworks detail file flags these model version strings as potentially aspirational; the exact versions may not exist under those names.
- GitHub Spec Kit install command: `uv tool install specify-cli` requires a `--from git+https://github.com/github/spec-kit.git@vX.Y.Z` clause for installation from source; the exact current release tag was not confirmed.
- `gsd-check-update-worker.js` is counted separately from `gsd-check-update.js`, producing 13 files in `hooks/`; `ARCHITECTURE.md` references 12 functional hook entry points. The discrepancy is noted and not resolved in public documentation.
- The `continue-here.md` artifact is described as the single context handoff file written by `/gsd-pause-work`; whether it overwrites or appends to a prior session's handoff is not confirmed in public documentation.
- Graphify's claim of approximately 71.5× token reduction versus naive RAG: this figure appears in Graphify's marketing materials and is listed as unverified in the detail file; no independent validation of the measurement methodology was performed.

- **Open question (added 2026-05-24): harnessability as a stack-evaluation criterion.** The Harness Engineering article ([https://martinfowler.com/articles/harness-engineering.html](https://martinfowler.com/articles/harness-engineering.html)) argues that typed languages, clear module boundaries, and opinionated frameworks materially improve how well an outer harness can exist on top of them. The dossier does not currently evaluate frameworks (or their target codebases) on this axis. For a new framework, an explicit harnessability heuristic — "does this stack admit cheap, deterministic guides and sensors at the boundaries that matter?" — belongs alongside cost and DX in tech-selection guidance. Cited example: OpenAI Codex layered architecture (referenced in the Harness Engineering article).

- **Open question (added 2026-05-24): no "code-coverage equivalent" for harness quality.** The Harness Engineering article flags this as an unresolved problem. Possible directions for a new framework: percentage of REQ-IDs with paired sensors; percentage of D-IDs with paired remediation prompts; ratio of guides-without-sensors to total guides (see Pattern 29).

---

## 8. Note on Excluded Source

The URL `cursor.com/loginDeepControl?…` provided as a research source was a Cursor OAuth challenge URL requiring an active authenticated browser session; it was not accessible and its contents are excluded from this dossier.

---

## 9. Incorporation Log — 2026-05-24

On 2026-05-24 the dossier was extended with material from `SOURCES.md` (four external URLs unrelated to the seven frameworks originally surveyed). The extension was produced by a four-stage subagent pipeline: (1) one fetcher per URL produced a structured summary in `research/external-sources/summaries/`; (2) one reviewer per summary classified each finding as ALIGNS / EXTENDS / NEW / CONTRADICTS / OUT-OF-SCOPE against the existing dossier, with ready-to-paste text for NEW and EXTENDS items, in `research/external-sources/reviews/`; (3) an incorporator agent and a follow-up direct pass applied the proposals to dossier files; (4) evaluator agents review the result and auto-fix issues.

| Source | New patterns added | EXTENDS applied (existing patterns + sections) | Files touched |
|---|---|---|---|
| OpenRewrite ([docs.openrewrite.org](https://docs.openrewrite.org/)) | Pattern 20 (LST substrate), Pattern 21 (Recipe DAG), Pattern 22 (precondition scope filter), Pattern 23 (isomorphic vs non-isomorphic edits), Pattern 24 (self-describing skill manifest) | Pattern 6 (per-hunk attribution), Pattern 8 (`causesAnotherCycle` cycles), Pattern 11 (per-hunk attribution), Pattern 13 (Markers on AST nodes), Pattern 15 (versioned packaged distribution); plus survey-then-edit typed-accumulator implication in `self-healing-and-verification.md` §8 | `topics/patterns-worth-stealing.md`, `topics/self-healing-and-verification.md`, `SUMMARY.md` |
| ArchUnit ([archunit.org](https://www.archunit.org/)) | Pattern 25 (frozen baseline with ratchet semantics), Pattern 26 (diagram-as-executable-spec), Pattern 27 (importable spec packs), Pattern 28 (named architectural primitives vocabulary) | Pattern 11 (generalizes to architecture-rule tests + self-describing rules), Pattern 13 (bytecode as deterministic substrate); plus frozen-baselines section in `self-healing-and-verification.md` §10 | `topics/patterns-worth-stealing.md`, `topics/self-healing-and-verification.md`, `SUMMARY.md` |
| Harness Engineering ([Fowler/Böckeler](https://martinfowler.com/articles/harness-engineering.html) [inference]) | Pattern 29 (guides + sensors taxonomy), Pattern 30 (computational vs inferential), Pattern 31 (approved scenarios) | Pattern 15 (harness templates per service topology); plus regulation-categories, sensor-remediation, quality-left-distribution, and steering-loop/harness-update implications in `self-healing-and-verification.md` §8 and `workflow-and-orchestration.md` §8; plus cybernetic/Ashby framing in `SUMMARY.md` §1 and two open questions in §7 (harnessability, harness coverage) | `topics/patterns-worth-stealing.md`, `topics/self-healing-and-verification.md`, `topics/workflow-and-orchestration.md`, `SUMMARY.md` |
| Role of Developer Skills ([Böckeler memo #13](https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html)) | Pattern 32 (reuse-awareness pre-check) | Pattern 4 (team-level "go-wrong" log), Pattern 5 (vertical-slice as constructive constraint), Pattern 8 (universal diagnose-before-fix), Pattern 11 (test redundancy axis + AI-tuned duplication weight), Pattern 16 (constitution versioned with friction-case provenance); plus impact-radius classification, shift-left review, prompt-fidelity-decay note in `self-healing-and-verification.md` §8 and new §9 Ergonomic Gates; plus steering-as-unit-of-work implication in `workflow-and-orchestration.md` §8 | `topics/patterns-worth-stealing.md`, `topics/self-healing-and-verification.md`, `topics/workflow-and-orchestration.md`, `SUMMARY.md` |

**Items skipped (with rationale)** — see per-source review files for full lists:

- OpenRewrite: Styles (derivative of LST; no transfer without IR), recipe immutability + visitor-local mutable state (Java visitor authoring discipline), Maven/Gradle plugin shape (already covered by Pattern 1), `mvn rewrite:discover` (already covered by `/gsd-help` analogs), Moderne (too lightly sourced).
- ArchUnit: `@AppModule` JPMS-like modularization, `GeneralCodingRules` catalog (Java-specific lint), `ImportOption` filters, `ClassFileImporter` API surface (implementation detail).
- Harness Engineering: verbatim OpenAI Codex anecdote (cited under N6 only), full cybernetic governor deep dive (kept as single-paragraph framing in §1), behaviour-harness standalone topic file (premature — flagged in §8 and §7 only), replacement of pre/during/post-code timing axis with guides/sensors axis (kept as orthogonal layer).
- Role of Developer Skills: "AI will not write 90% of code autonomously in a year" (industry forecast), personal-skill list itself (out of scope as patterns), culture / psychological safety (out of scope for engineering-systems dossier), specific anecdotes (Docker arch, JSON-display web component — pattern abstractions cover the ground).

**Contradictions logged but not auto-applied:** None across the four sources.

**Risks / known issues with the incorporation:**

- Pattern numbering: the original dossier ended at Pattern 19. New patterns are 20–32, sequentially in file order. The Pattern Ranking Summary Table was extended to cover all 32.
- Two reviews (OpenRewrite, Developer Skills) flagged MEDIUM reviewer confidence because the framework deep-dive files (`frameworks/*.md`) were not re-read during review; a small number of EXTENDS items may already be covered there at a depth not surfaced in the topic files. Recommended: a follow-up audit cross-checks the new EXTENDS entries against the framework deep-dives.
- TLC RED-test immutability (Pattern 11) and Approved Scenarios (Pattern 31) are not contradictory but apply to different test types (hand-authored contract tests vs AI-generated fixture tests). The dossier should be explicit about this scoping; the current Pattern 31 entry notes "complements Pattern 11" but a reader following only Pattern 11 may not see the qualification. Flagged for evaluator pass.
- The Harness Engineering article is attributed in the dossier text as "Martin Fowler / Birgitta Böckeler [inference]" — author attribution was inferred from the *Exploring Gen AI* series authorship, not stated verbatim on the article page. The `[inference]` tag is preserved everywhere the attribution appears.
- `cursor.com/loginDeepControl?…` from the original research and the four new external URLs from `SOURCES.md` are independent corpora; no cross-references were attempted between them.

See `research/external-sources/summaries/` and `research/external-sources/reviews/` for the per-source material and rationale, and `research/external-sources/INCORPORATION-REPORT.md` for the operational record of which edits were applied directly vs by subagent.
