# Context Engineering

> Cross-cutting analysis of how GSD, TLC, Task Master, BMAD, and Graphify manage
> context windows, token budgets, persistent state, and shared artifact conflicts.

---

## 1. The Problem: Context Rot

"Context rot" is the term GSD's README uses to describe quality degradation as an AI
fills its context window during a long coding session. It is not simply a token-limit
problem; it is a reliability problem. As the context window fills, earlier decisions
and constraints are de-weighted or lost, the model loses track of what has already
been verified, and outputs become inconsistent with the project's accumulated intent.

GSD's README names three concrete failure modes that together constitute context rot:

1. **Context bloat** — the main session accumulates tool-call outputs, partial file
   reads, intermediate reasoning, and raw command output until earlier context is
   effectively unreachable. The session that started the feature is not the same
   session that finishes it.

2. **No shared memory** — sessions forget. Each `/clear` or new terminal window
   starts with no knowledge of prior decisions, blockers, or what was already built
   and verified. Tribal knowledge lives in the human's head, not in an artifact the
   next agent can read.

3. **No verification** — "Code that 'runs' isn't code that 'works.'" Without a
   dedicated verification step anchored to explicit acceptance criteria, passing
   tests are interpreted as completion even when the feature diverges from
   requirements established earlier in the session.

These three failures are not independent. Bloat accelerates the forgetting, and the
forgetting makes verification impossible because the criteria for "done" are no
longer in context.

The frameworks surveyed below address at least one of these failures, and the most
mature ones address all three.

---

## 2. Solution Category 1: Fresh Sub-Agent Contexts

The sharpest tool against context bloat is to never let a single context window
accumulate work that another context could handle in isolation. Every framework in
this survey has a version of this idea, though implementation depth varies
significantly.

### GSD

GSD's architecture document states the principle directly: "Every agent spawned by an
orchestrator gets a clean context window (up to 200K tokens). This eliminates context
rot." Orchestrators are explicitly thin — workflows "never do heavy lifting
themselves." Researchers, planners, executors, and verifiers are always invoked
through the runtime's `Task` / `SubAgent` primitive, never inline in the orchestrator
turn.

When `config.context_window >= 500000`, GSD enables an adaptive enrichment path:
executor and verifier prompts are enriched with prior wave `SUMMARY.md` files and
phase context. Below that threshold, prompts use truncated, cache-friendly versions.
The 1M-context path is opt-in at the model capability level, not a default that
degrades smaller deployments.

See `../frameworks/gsd.md` for the full agent roster and spawn taxonomy.

### TLC

TLC's sub-agent delegation is governed by an explicit decision table (`SKILL.md`):

| Activity | Delegate? | Reason |
|---|---|---|
| Research (design phase, brownfield mapping) | Yes | "Research output is large; only the summary matters to the main context" |
| Implementing a task | Yes | "File reads, edits, test output consume context; only the result matters" |
| Parallel `[P]` tasks | Yes (one per task) | "The only way to actually run tasks in parallel" |
| Sequential tasks with no `[P]` | Yes | "Keeps implementation artifacts out of the main context" |
| Planning, task creation, validation reports | **No** | "These require the full accumulated context to be coherent" |
| Quick mode tasks | **No** | "Too small to justify the overhead" |

The planning prohibition is the most distinctive entry. TLC treats planning as
inherently context-dependent — the decisions made during Specify are the fuel for
Design and Tasks, so splitting them across contexts would lose coherence. Research and
implementation, by contrast, produce outputs that only need to be summarized back;
the intermediate file reads, AST traversals, and test runs are noise from the main
context's point of view.

Each sub-agent receives a narrow input contract: the specific task definition, relevant
coding principles and conventions, the testing guide for gate commands, and any spec
or design sections the task references. Sub-agents must NOT receive other tasks'
definitions, accumulated chat history, validation reports from other tasks, or
`STATE.md` unless the task explicitly references a decision or blocker.

See `../frameworks/tlc-spec-driven.md` for the full sub-agent input and output
contracts.

### BMAD

BMAD takes the freshness principle further by making it a persona boundary rather than
a spawning decision. Planning agents (Analyst, PM, Architect) produce PRDs and
architecture documents. A separate Scrum Master agent converts those documents into
hyper-detailed stories with embedded context — specifically engineered so that the
developer agent does not need to re-fetch the architecture. The context required for
design never loads into the implementation agent; it is pre-baked at the story
handoff boundary.

The consequence is that implementation agents run with much smaller, task-scoped
context — the story artifact itself carries everything needed. See
`../frameworks/adjacent-frameworks.md` for BMAD's Story Automator detail.

### Task Master

Task Master is not sub-agent based in the same sense. It is an MCP server that tools
inside the IDE call. The equivalent of the "fresh context" benefit comes from the
tool-tier model system: different model roles (main, research, fallback) handle
different parts of the workflow. Research queries go to a research-grade model with
live web access (Perplexity or similar) rather than polluting the implementation
model's context with search output. The implementation model only sees task
definitions and immediate context, not the full task history.

---

## 3. Solution Category 2: Per-File and Per-Workflow Token Budgets

Freshness prevents accumulation in the main orchestrator; budgets enforce a ceiling on
what any individual file or workflow prompt may contribute. Several frameworks define
these explicitly.

### TLC

TLC defines hard per-file limits in `references/context-limits.md`:

| File | Max tokens | Warning at |
|---|---|---|
| PROJECT.md | 2,000 | 1,600 (80%) |
| ROADMAP.md | 3,000 | 2,400 (80%) |
| STATE.md | 10,000 | 7,000 (70%) |
| spec.md | 5,000 | 4,000 (80%) |
| design.md | 8,000 | 6,400 (80%) |
| tasks.md | 10,000 | 8,000 (80%) |
| STACK.md | 2,000 | 1,600 (80%) |
| ARCHITECTURE.md | 4,000 | 3,200 (80%) |
| CONVENTIONS.md | 3,000 | 2,400 (80%) |
| STRUCTURE.md | 2,000 | 1,600 (80%) |
| TESTING.md | 4,000 | 3,200 (80%) |
| INTEGRATIONS.md | 5,000 | 4,000 (80%) |

These limits are not advisory in the sense of "try to stay under this." They drive
active agent behavior: when a file approaches its warning threshold, the agent is
expected to trim before continuing. Files that exceed the hard limit cannot be loaded
as part of the base context.

TLC also defines three context health zones at the aggregate session level:

- **Healthy** (below 40k total): no action, no mention.
- **Moderate** (40k–60k): discrete footer note surfaced to the user.
- **Critical** (above 60k): active warning with an optimization suggestion.

The 40k target is explicit: "Reserve 160k+ tokens for work, reasoning, outputs."

STATE.md has a graduated cleanup policy layered on top of the per-file budget. Below
7k tokens: no action. At 7k–10k: footer note, "Cleanup recommended." Above 10k: "STATE.md
critical. Cleanup now?" The cleanup action moves decisions older than 60 days to
`STATE-ARCHIVE.md`, retains only active blockers, and preserves lessons learned that
are under 60 days old.

### GSD

GSD enforces per-workflow line caps validated in CI:

- `XL` workflows (top-level orchestrators): 1,700 lines maximum.
- `LARGE` workflows: 1,500 lines.
- `DEFAULT` workflows: 1,000 lines.

Per-agent file caps apply to agent definition files: approximately 45,000 characters
soft limit, 50,000 characters hard invariant. Content that would overflow is extracted
to `references/*.md` files and loaded lazily.

Two real-time monitoring mechanisms are active at runtime. The `gsd-context-monitor.js`
hook (`PostToolUse` / `AfterTool` events) injects warnings into the next turn when the
remaining context drops to specific thresholds: at 35% remaining, "avoid starting new
complex work"; at 25% remaining, "inform user." A five-tool-use debounce prevents
warning spam. A separate `validate context` CLI verb emits `{utilization, status,
suggestion}` with its own warn/critical levels at 60% and 70% utilization.

For local model deployments (Ollama, llama.cpp, LM Studio), `review.max_prompt_tokens`
and per-reviewer overrides allow token-budget trimming on models with smaller effective
context.

### Task Master

Task Master's most distinctive budget mechanism is the `TASK_MASTER_TOOLS` environment
variable, which controls how many MCP tools are registered at startup:

| Mode | Tools loaded | Approximate token cost |
|---|---|---|
| `all` (default) | 36 | ~21,000 |
| `standard` | 15 | ~10,000 |
| `core` / `lean` | 7 | ~5,000 |
| `custom` | comma-separated list | variable |

The core 7 are: `get_tasks`, `next_task`, `get_task`, `set_task_status`,
`update_subtask`, `parse_prd`, `expand_task`. Every registered MCP tool consumes
tokens in the context whether or not it is called; this is the most thoroughly
documented "tool budget" knob in the frameworks surveyed.

---

## 4. Solution Category 3: Lazy Loading and Compound Init

Loading everything up front conflicts with the per-file budgets described above.
Several frameworks have engineered explicit lazy-loading mechanisms to avoid the
contradiction.

### GSD

GSD's compound init handlers are the most architecturally distinctive mechanism in
this survey. Workflows never read individual files piecemeal. Instead, they call a
single CLI/SDK seam:

```
node gsd-tools.cjs init execute-phase 1
node gsd-tools.cjs init plan-phase 1
node gsd-tools.cjs init new-project
```

Each call returns all context needed for that specific workflow as a single JSON blob,
deduplicated, and in a cache-friendly order. When the JSON exceeds approximately 50 KB,
it spills to a tempfile and the workflow receives `@file:/tmp/gsd-init-XXXXX.json`
instead of an inline payload. This approach removes per-workflow re-discovery cost and
ensures that every agent receives exactly the context it needs, no more.

Two-stage namespace routing compounds the savings. Before v1.40, GSD listed skills
flat: 86 skills at approximately 2,150 tokens. After v1.40, six namespace
meta-skills ("routers") act as an intermediate dispatch layer. Each router describes
a cluster of skills using pipe-separated keyword tags of up to 60 characters each —
approximately 20 tokens per router, 120 tokens total. The tool attention research
cited in GSD's architecture documentation found that "keyword-dense tags outperform
prose for routing at ~40% the token cost."

The six routers:

| Router | Covers |
|---|---|
| `/gsd-workflow` | discuss / plan / execute / verify / phase / progress |
| `/gsd-project` | milestones, audits, summary |
| `/gsd-quality` | code review, debug, audit, security, eval, ui |
| `/gsd-context` | map, graphify, docs, learnings |
| `/gsd-manage` | config, workspace, workstreams, thread, update, ship, inbox |
| `/gsd-ideate` | explore, sketch, spike, spec, capture |

The full skill loads only when the router determines it is needed for the current
query.

### TLC

TLC's loading strategy is structural rather than programmatic. `SKILL.md` is a thin
index — approximately 15,000 tokens for the base load — and serves as a dispatch
table. The 16 reference files are loaded on-demand by trigger-phrase matching:

| Trigger Pattern | Reference loaded |
|---|---|
| "specify feature", "define requirements" | `references/specify.md` |
| "design feature", "architecture" | `references/design.md` |
| "implement task", "build", "execute" | `references/implement.md` |
| "validate", "verify", "test", "UAT" | `references/validate.md` |
| "quick fix", "quick task", "bug fix" | `references/quick-mode.md` |
| ... | ... (16 total) |

Hard constraints reinforce the lazy pattern: the skill never loads multiple feature
specs simultaneously, never loads multiple architecture documents at the same time,
and never loads archived documents. These are explicit prohibitions in
`references/context-limits.md`, not implicit conventions.

### Graphify

Graphify's query interface provides lazy access to codebase structure without loading
source files. Rather than reading raw source to understand relationships, a
`graphify query "…"` returns only the relevant subgraph nodes. The `--budget N`
flag caps the token cost of a graph query explicitly. The net effect is that an
agent asking "what calls this function?" receives a compact, structured answer — a
subgraph — rather than the full transitive closure of the codebase.

---

## 5. Solution Category 4: Persistent Memory Artifacts

Lazy loading solves the per-session accumulation problem. Persistent memory artifacts
solve the cross-session forgetting problem.

### GSD

GSD maintains a committed directory structure at `.planning/`. The core cross-session
files are:

- `PROJECT.md` — vision, constraints, decisions, evolution rules. Read by all agents.
- `REQUIREMENTS.md` — requirement IDs scoped to v1 / v2 / out-of-scope. Read by
  planner, verifier, and auditor.
- `ROADMAP.md` — phase breakdown with status table. Read by orchestrators.
- `STATE.md` — "living memory" with `## Current Position`, decisions, blockers,
  metrics, progress bar, and session continuity fields (`stopped-at`, `resume-file`,
  `waiting`, `resume`). All mutations route through `state-document.cjs` with a
  `shouldPreserveExistingProgress` invariant.
- `config.json` — all dials: mode, model profile, workflow toggles, parallelization,
  code quality, ship sections.
- `continue-here.md` — context handoff written by `/gsd-pause-work`, read at
  session resume.

Per-phase artifacts under `.planning/phases/XX-name/` carry phase-scoped memory:
`XX-CONTEXT.md` (numbered `D-01`, `D-02` decisions), `XX-RESEARCH.md`,
`XX-YY-PLAN.md`, `XX-VERIFICATION.md`, and `XX-UAT.md`.

### TLC

TLC's persistent memory lives at `.specs/project/STATE.md`. It uses an ID-based
schema: decisions are tagged `AD-NNN`, blockers `B-NNN`, lessons learned `L-NNN`.
The graduated cleanup policy (7k / 10k thresholds, 60-day archive to
`STATE-ARCHIVE.md`) is described in Section 3 above.

`HANDOFF.md` (at `.specs/HANDOFF.md`) is a session checkpoint file of approximately
500 tokens that overwrites its previous version on each session end. It carries:
Completed tasks, In Progress tasks, Pending tasks, Blockers, and Context (branch,
uncommitted files). Unlike GSD's `continue-here.md` (a single handoff file written by `/gsd-pause-work`), the
`HANDOFF.md` is a single-slot snapshot — only the most recent session handoff
survives.

### Spec Kit

Spec Kit uses `.specify/memory/constitution.md` as a persistent governance document.
Unlike GSD's STATE.md (a living operational log) or TLC's STATE.md (ID-based memory),
the constitution is a principles document — governing invariants consulted during every
phase, not a record of what has happened. It is closer to a durable architectural
decision record than to a session checkpoint.

---

## 6. Solution Category 5: Shared Artifact Conflict Resolution

When multiple agents write to the same artifact concurrently — or when multiple
developers on the same codebase produce commits that touch the same spec files — the
artifacts can conflict. Two frameworks have explicit mechanisms for this.

### Graphify

Graphify installs a git merge driver via `graphify hook install`. The driver intercepts
merge conflicts on `graph.json` and resolves them by union-merging the two versions
automatically. Concurrent commits that add different nodes and edges to the knowledge
graph never produce conflict markers. The canonical artifact stays valid across
parallel contributions.

### GSD

GSD's parallel executor architecture creates a more acute version of the same problem:
multiple `gsd-executor` agents run concurrently within a wave and all write to
`STATE.md`. GSD uses a `STATE.md.lock` file with `O_EXCL` atomic creation for mutual
exclusion. Key properties:

- `O_EXCL` creation is atomic at the OS level — no two processes can create the
  file simultaneously.
- Stale locks (older than 10 seconds) are automatically cleared, preventing a crashed
  executor from blocking the wave indefinitely.
- Waiting processes use a jittered spin-wait to reduce contention.

All `writeStateMd()` calls in the SDK route through this lockfile mechanism.

TLC does not address concurrent writes in its documentation — a gap consistent with
its single-agent orientation. Task Master's `.taskmaster/tasks/` directory is
written by the MCP server sequentially; concurrent access is not a documented concern.

---

## 7. Cross-Framework Comparison Table

| Dimension | GSD | TLC | Task Master | BMAD | Graphify |
|---|---|---|---|---|---|
| Main context budget | 200K per subagent; 1M enrichment path at >=500K config | <40k target; 160k+ reserved for work | Tool-tier (5k–21k via `TASK_MASTER_TOOLS`) | Persona-separated; story pre-bakes context | `--budget N` on graph queries |
| Per-file limits | CI line caps (XL ≤1700, LARGE ≤1500, DEFAULT ≤1000); 50K agent hard cap | 2k–10k per file (table in `context-limits.md`) | N/A | N/A | N/A |
| Lazy loading | Compound init + two-stage namespace routing (6 routers / ~120 tokens vs 86 flat / ~2,150) | Thin SKILL.md (~15k) + 16 on-demand ref files via trigger-phrase matching | `TASK_MASTER_TOOLS` env var at startup | N/A | Scoped `graphify query` + `--budget N` |
| Persistent memory | `.planning/` (PROJECT, STATE, ROADMAP, REQUIREMENTS, per-phase artifacts, continue-here.md) | `.specs/project/STATE.md` (ID-based, 60d archive); `HANDOFF.md` (~500 tokens, single-slot) | `.taskmaster/tasks/` (PRD-derived task files) | PRDs + architecture docs + stories | `graphify-out/graph.json` (committed) |
| Conflict resolution | `STATE.md.lock` (O_EXCL atomic creation, 10s stale timeout, jittered spin-wait) | Not addressed | Not addressed | Not addressed | Git merge driver (union-merge `graph.json`) |
| Context monitoring | `gsd-context-monitor.js` (warn at ≤35% remaining, critical at ≤25%); `validate context` CLI | Aggregate zone warnings (40k / 60k); per-file warning thresholds | None documented | None documented | None documented |
| Cross-session handoff | `continue-here.md` (from `/gsd-pause-work`) + STATE.md `stopped-at` / `resume-file` fields | `HANDOFF.md` (~500 tokens, overwrites; single-slot) | PRD + task status in `.taskmaster/tasks/` | Story artifacts carry embedded context | `graph.json` committed to repo |

---

## 8. Implications for Our Framework

The following observations are drawn from the comparative analysis above. They are
stated as observations rather than design decisions; the appropriate trade-offs depend
on the team's tooling, scale, and tolerance for ceremony.

- **The orchestrator-as-thin-dispatcher pattern is consistent across the two most
  mature frameworks (GSD and TLC), and it is consistently motivated by the same
  reason: planning requires accumulated context, implementation does not.** Any
  framework that conflates these two modes in a single context will eventually
  reproduce the context rot problem it is trying to solve.

- **Per-file token budgets and aggregate health zones serve different purposes.**
  Per-file limits prevent individual artifacts from becoming load-bearing monoliths.
  Aggregate health zones give the agent behavioral cues before limits are reached.
  GSD and TLC both implement both, but at different levels of precision. A framework
  can start with health zones (cheapest to implement) and graduate to per-file limits
  as artifacts grow.

- **The compound init pattern (one loader call returns everything a workflow needs)
  is a significant architectural investment that pays off in two ways: it removes
  per-workflow re-discovery cost, and it makes cache-friendly context ordering
  deterministic.** The naive alternative — each workflow reads files ad hoc —
  produces non-deterministic context ordering that degrades caching.

- **Persistent memory artifacts design matters as much as their content.** GSD's
  `STATE.md` is an operational log with YAML frontmatter for machine consumption. TLC's
  `STATE.md` is an ID-based knowledge store with an aging policy. Spec Kit's
  `constitution.md` is a governance document. Each reflects a different theory of what
  needs to survive across sessions. A framework that conflates these purposes into a
  single file will find the file growing without bound or becoming incoherent.

- **Conflict resolution is only a problem if parallel writes are possible.** TLC's
  single-agent orientation means it never needs a lockfile. GSD's wave-based parallel
  execution makes the lockfile non-optional. The choice of concurrency model at the
  architecture level determines whether this category of complexity exists at all.

---

## Related Files

- `../frameworks/gsd.md`
- `../frameworks/tlc-spec-driven.md`
- `../frameworks/graphify.md`
- `../frameworks/adjacent-frameworks.md`
- `./workflow-and-orchestration.md`
- `./patterns-worth-stealing.md`
