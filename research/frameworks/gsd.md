# GSD — Get Shit Done

> Source: [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done)
> Cached findings: `../.research-cache/01-gsd-findings.md`
> All source URLs fetched successfully on 2026-05-19.

---

## 1. Overview

GSD ("Get Shit Done") is a "light-weight meta-prompting, context engineering, and spec-driven development system" distributed as a Node.js installer (`npx get-shit-done-cc@latest`) that lays down skills, slash commands, agents, references, hooks, and a CLI/SDK toolchain into the directories of 15 AI coding runtimes (Claude Code, OpenCode, Gemini CLI, Kilo, Codex, Copilot, Cursor, Windsurf, Antigravity, Augment, Trae, Qwen Code, Hermes, CodeBuddy, Cline). The headline problem it claims to solve is "context rot — the quality degradation that happens as your AI fills its context window" (GSD README.md), targeting three specific failure modes: context bloat as the main session grows, the inability of sessions to share memory across restarts, and the lack of automated verification that running code actually satisfies requirements. GSD is explicitly framed for solo developers and small teams who do not want sprint ceremonies: "Other spec-driven tools exist, but they're all built for 50-person engineering orgs… The complexity is in the system, not in your workflow" (GSD README.md). Comparable tools called out directly in the README include SpecKit, OpenSpec, and Taskmaster. The system is built around six guiding design principles extracted from `ARCHITECTURE.md`: (1) fresh context per agent — each subagent receives up to 200K tokens, or up to 1M on big-context models; (2) thin orchestrators — workflows never do heavy work themselves, only coordinate; (3) file-based state — no database or server, all artifacts live in `.planning/`; (4) "absent = enabled" — feature flags default to true when the key is missing from config; (5) defense in depth — plans are verified before execution, and execution output is verified before a phase is marked done; and (6) multi-runtime portability — everything is authored in Claude Code's native format and transformed at install time for each target runtime.

---

## 2. Core Workflow

The main loop is six commands. Each command is a one-line orchestrator that bootstraps a workflow file under `get-shit-done/workflows/*.md`. Each phase accumulates a known set of artifacts under `.planning/phases/XX-name/`.

| Step | Command | What it does | Artifacts produced |
|---|---|---|---|
| 1. Initialize | `/gsd-new-project` | Asks questions, spawns 4 parallel research agents (stack, features, architecture, pitfalls), extracts requirements, drafts roadmap, awaits approval | `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`, `config.json`, `research/{SUMMARY,STACK,FEATURES,ARCHITECTURE,PITFALLS}.md`, `CLAUDE.md` |
| 1b. Brownfield prep | `/gsd-map-codebase` | Spawns 4 parallel `gsd-codebase-mapper` agents (tech, arch, quality, concerns) so a brownfield project is analyzed before new-project planning begins | `.planning/codebase/{STACK,ARCHITECTURE,CONVENTIONS,CONCERNS,STRUCTURE,TESTING,INTEGRATIONS}.md` with `last_mapped_commit` YAML frontmatter |
| 2. Discuss | `/gsd-discuss-phase N` | Phase-scoped interactive Q&A to lock implementation decisions before any planning; modes: `--all`, `--auto`, `--batch`, `--analyze`, `--power`, `--assumptions` | `{phase}-CONTEXT.md` with numbered `<decisions>` (`D-01`, `D-02`…), `{phase}-DISCUSSION-LOG.md` audit trail |
| 2b. UI design | `/gsd-ui-phase N` | Optional design contract for frontend phases — 6-pillar contract: copywriting, visuals, color, typography, spacing, registry safety | `{phase}-UI-SPEC.md` |
| 3. Plan | `/gsd-plan-phase N` | Research → plan → verify loop: 4 parallel researchers, then a planner, then a `plan-checker` that loops up to 3 times | `{phase}-RESEARCH.md`, `{phase}-{NN}-PLAN.md` files, `{phase}-VALIDATION.md` |
| 4. Execute | `/gsd-execute-phase N` | Plans grouped into dependency waves; each plan dispatched to a `gsd-executor` agent in a fresh 200K context; atomic git commit per task | `{phase}-{NN}-SUMMARY.md` per plan, atomic git commits (`feat(NN-MM):`), `{phase}-VERIFICATION.md` |
| 5. Verify | `/gsd-verify-work N` | Walks the user through phase goal acceptance criteria; on failure invokes a debug/diagnosis agent that writes a fix plan | `{phase}-UAT.md`, optional new fix `PLAN.md` |
| 6. Ship | `/gsd-ship N` | Generates a GitHub PR via `gh` with body assembled from PLAN, SUMMARY, and VERIFICATION artifacts | GitHub PR, updated `STATE.md` |
| Auto-advance | `/gsd-progress --next` | Auto-detects the current project state and runs the correct next command | — |
| Close milestone | `/gsd-complete-milestone` → `/gsd-new-milestone` | Archives milestone to `MILESTONES.md`, tags release in git, starts fresh requirements and roadmap | `MILESTONES.md` entry, git tag |

After v1.40 consolidation, GSD ships 59 sub-skills plus 6 namespace meta-skills, covering a wide range of auxiliary operations beyond the core loop.

The phases compose sequentially by design, but with deliberate parallelism inside each phase. Discuss must precede Plan because the decision IDs it produces (`D-01`, `D-02`…) are inputs to the plan-time decision coverage gate. Plan must precede Execute because executors consume `PLAN.md` files as their primary instruction set. The auto-advance command `/gsd-progress --next` allows a project to move through all phases with a single repeated invocation, reading `STATE.md` to determine where it left off. See also [`../topics/workflow-and-orchestration.md`](../topics/workflow-and-orchestration.md).

---

## 3. Context Engineering

GSD's approach to context management is its most distinctive technical feature. Each mechanism targets a specific failure mode of long-running AI sessions. See also [`../topics/context-engineering.md`](../topics/context-engineering.md).

### Compound init handlers

Workflows never read individual files piecemeal. Instead, they call one CLI or SDK seam that returns everything needed for that workflow as a single JSON blob:

```
node gsd-tools.cjs init execute-phase 1
node gsd-tools.cjs init plan-phase 1
node gsd-tools.cjs init new-project
```

When the returned JSON exceeds approximately 50 KB it spills to a tempfile and the CLI returns `@file:/tmp/gsd-init-XXXXX.json`, which workflows expand. This design removes per-workflow file re-discovery cost and keeps cache-friendly ordering deterministic. One loader call per workflow, deduplicated, ready to inject.

### Fresh subagent context per task

"Every agent spawned by an orchestrator gets a clean context window (up to 200K tokens). This eliminates context rot." (GSD ARCHITECTURE.md). Researchers, planners, and executors are always invoked through the runtime's native subagent or Task primitive, never inline within the orchestrator's own context window.

### Adaptive enrichment on 1M-context models

When `config.context_window` is greater than or equal to 500,000, executor and verifier prompts are enriched with prior-wave `SUMMARY.md` files and full phase context. Below that threshold, prompts use truncated, cache-friendly versions. This allows GSD to take advantage of extended context hardware without requiring it.

### Two-stage namespace routing

The v1.40 skill surface redesign introduced six namespace meta-skill routers. The stated trade-off: eager listing of 86 flat skills costs approximately 2,150 tokens; the six-router layer costs approximately 120 tokens. Routing is triggered by keyword matching against pipe-separated tag strings on each router — a design informed by "Tool Attention research showing keyword-dense tags outperform prose for routing at ~40% the token cost" (GSD ARCHITECTURE.md).

### Status-line context bridge

The `gsd-statusline.js` hook runs on every tool use and writes session-level context utilization to `/tmp/claude-ctx-{session}.json`. This bridge file is read by `gsd-context-monitor.js` to make context budget visible to subsequent agents and hooks without an additional API call.

### `gsd-context-monitor.js` hook

This `PostToolUse`/`AfterTool` hook monitors remaining context budget. It emits a WARNING hint ("avoid starting new complex work") when remaining context drops to 35% or below, and a CRITICAL hint ("inform user") at 25% or below. A 5-tool-use debounce prevents alert fatigue. Stale metrics older than 60 seconds are ignored.

### Per-workflow CI line caps

Workflow file sizes are capped in CI to keep orchestrator prompts from growing unbounded:

- `XL` workflows (top-level orchestrators): 1,700 lines maximum
- `LARGE` workflows: 1,500 lines maximum
- `DEFAULT` workflows: 1,000 lines maximum

### Per-agent file caps

Agent `.md` files must stay under approximately 45,000 characters, with a hard invariant at 50,000 characters. Content that would exceed this is extracted to `references/*.md` files and loaded only when needed.

### `review.max_prompt_tokens`

Per-reviewer token budget overrides are available for small-context local models such as Ollama, llama.cpp, and LM Studio, allowing the review workflow to function on hardware with constrained context windows.

---

## 4. Sub-Agent Roster and Orchestration

`ARCHITECTURE.md` advertises 31–33 agents (minor documentation drift between files). The GitHub API listing of `/agents` confirms 33 agent `.md` files. [unverified: exact roles paraphrased from ARCHITECTURE.md taxonomy table, not from each agent's frontmatter directly]

### Full agent roster by category

| Category | Agents | Parallelism mode |
|---|---|---|
| Researchers | `gsd-project-researcher`, `gsd-phase-researcher`, `gsd-ui-researcher`, `gsd-advisor-researcher`, `gsd-ai-researcher`, `gsd-domain-researcher` | 4 parallel (stack / features / architecture / pitfalls) at new-project time |
| Synthesizers | `gsd-research-synthesizer` | Sequential after researchers complete |
| Planners | `gsd-planner`, `gsd-roadmapper`, `gsd-eval-planner`, `gsd-framework-selector`, `gsd-user-profiler` | Sequential |
| Checkers | `gsd-plan-checker`, `gsd-integration-checker`, `gsd-ui-checker`, `gsd-nyquist-auditor` | Sequential, loops up to 3 times |
| Executors | `gsd-executor`, `gsd-code-fixer` | Parallel within a wave, sequential across waves |
| Verifiers | `gsd-verifier`, `gsd-doc-verifier` | Sequential after all executors in a wave complete |
| Mappers | `gsd-codebase-mapper`, `gsd-pattern-mapper` | 4 parallel (tech / arch / quality / concerns) at map-codebase time |
| Debuggers | `gsd-debugger`, `gsd-debug-session-manager` | Sequential, interactive |
| Auditors | `gsd-eval-auditor`, `gsd-security-auditor`, `gsd-ui-auditor` | Sequential |
| Doc writers | `gsd-doc-writer`, `gsd-doc-classifier`, `gsd-doc-synthesizer` | Sequential |
| Analyzers | `gsd-assumptions-analyzer`, `gsd-code-reviewer`, `gsd-intel-updater` | Sequential |

### Dispatch pattern

The orchestrator is a thin workflow `.md` file. It calls the SDK once to load context, resolves the target model, spawns an agent, collects the result, and writes updated state. In pseudocode (from GSD ARCHITECTURE.md):

```
Orchestrator (workflow .md)
   ├── Load context: gsd-sdk query init.<workflow> <phase>
   ├── Resolve model: gsd-sdk query resolve-model <agent-name>
   │   Returns: opus | sonnet | haiku | inherit
   ├── Spawn Agent (Task/SubAgent call)
   ├── Collect result
   └── Update state: gsd-sdk query state.update / state.patch / state.advance-plan
```

### Wave-based parallel execution

Plans within a phase are analyzed for dependencies before execution begins. Dependency-free plans are grouped into Wave 1 and run in parallel. Plans with dependencies on Wave 1 are grouped into Wave 2, and so on:

```
Wave Analysis:
  Plan 01 (no deps)        ─┐
  Plan 02 (no deps)        ─┤── Wave 1 (parallel)
  Plan 03 (depends: 01)    ─┤── Wave 2 (waits for Wave 1)
  Plan 04 (depends: 02)    ─┘
  Plan 05 (depends: 03,04) ─── Wave 3 (waits for Wave 2)
```

Parallel executors commit with `--no-verify`; the orchestrator runs `git hook run pre-commit` once after each wave completes. All `writeStateMd()` calls go through lockfile-based mutual exclusion (`STATE.md.lock` with `O_EXCL` atomic creation, 10-second stale-lock timeout, jittered spin-wait). See also [`../topics/workflow-and-orchestration.md`](../topics/workflow-and-orchestration.md).

### Model profile system

Five profiles are defined in `CONFIGURATION.md`: `quality`, `balanced`, `budget`, `adaptive`, and `inherit`. Resolution follows a five-layer precedence order (highest to lowest):

```
1. model_overrides[<agent>]            ← per-agent specific override
2. dynamic_routing.tier_models[<tier>] ← when dynamic_routing.enabled
3. models[<phase_type>]                ← phase-level override
4. model_profile (per-agent column)    ← global tier strategy
5. Runtime default                     ← fallback
```

Built-in tier maps per runtime — for `claude`: `opus` resolves to `claude-opus-4-7`, `sonnet` to `claude-sonnet-4-6`, `haiku` to `claude-haiku-4-5`.

---

## 5. Skills System

GSD is distributed primarily as skills (the surface on most runtimes) and as slash commands (Claude Code local installs). The v1.40 redesign introduced the Skill Surface Budget Module (ADR-0011) in two phases.

### Install-time profile selection

Named profiles control which skills are installed:

- `--profile=core` — installs the six core-loop skills only
- `--profile=standard` — installs core plus phase management skills
- Full default — installs all skills
- Composition — `--profile=core,audit` installs two named clusters together
- `--minimal` is an alias for `--profile=core`

Closure over `requires:` frontmatter in each skill file ensures transitive install: selecting a skill that depends on another automatically includes the dependency.

### Runtime cluster toggle

At runtime, `/gsd:surface` enables or disables named skill clusters without reinstalling. Cluster definitions live in `bin/lib/clusters.cjs`. Active cluster state is persisted in `<config>/.gsd-surface.json`. This allows a developer to temporarily narrow the skill surface in contexts where tool-listing cost matters.

### Namespace meta-skill routers

Six router skills cover the full skill surface. Each router receives a user query and dispatches it to the appropriate sub-skill:

| Router | Routes to |
|---|---|
| `/gsd-workflow` | discuss / plan / execute / verify / phase / progress |
| `/gsd-project` | milestones, audits, summary |
| `/gsd-quality` | code review, debug, audit, security, eval, ui |
| `/gsd-context` | map, graphify, docs, learnings |
| `/gsd-manage` | config, workspace, workstreams, thread, update, ship, inbox |
| `/gsd-ideate` | explore, sketch, spike, spec, capture |

### Why keyword-dense tags

Router skill descriptions use "pipe-separated keyword tags (≤ 60 chars)" rather than prose. The documented rationale: "Tool Attention research showing keyword-dense tags outperform prose for routing at ~40% the token cost" (GSD ARCHITECTURE.md). This is the same principle applied to the router descriptions themselves — compact, high-information-density strings that the model's attention mechanism can match quickly against user intent.

---

## 6. Local Storage Layout

All project state is file-based and committable. Everything lives under `.planning/`. The full canonical layout from `ARCHITECTURE.md`:

```
.planning/
├── PROJECT.md
├── REQUIREMENTS.md
├── ROADMAP.md
├── STATE.md
├── config.json
├── MILESTONES.md
├── continue-here.md            # context handoff from /gsd-pause-work
├── research/                   # /gsd-new-project outputs
├── codebase/                   # /gsd-map-codebase outputs; last_mapped_commit YAML frontmatter
├── phases/XX-phase-name/
│   ├── XX-CONTEXT.md
│   ├── XX-RESEARCH.md
│   ├── XX-YY-PLAN.md
│   ├── XX-YY-SUMMARY.md
│   ├── XX-VERIFICATION.md
│   ├── XX-VALIDATION.md        # Nyquist test coverage map
│   ├── XX-UI-SPEC.md
│   └── XX-UAT.md
├── quick/YYMMDD-xxx-slug/      # ad-hoc /gsd-quick tasks
├── todos/{pending,done}/
├── threads/
├── seeds/
├── debug/                      # active sessions + resolved/ + knowledge-base.md
├── ui-reviews/                 # screenshots (gitignored)
├── workstreams/
├── graphs/                     # knowledge graph from /gsd-graphify
├── reports/
└── spikes/NNN-name/
```

See also [`../topics/local-storage-and-artifacts.md`](../topics/local-storage-and-artifacts.md).

### STATE.md YAML frontmatter schema

`STATE.md` is the "living memory" of the project (GSD ARCHITECTURE.md). Its YAML frontmatter is the canonical in-flight state store. Key fields:

- `current_phase` — integer index of the active phase
- `Status` — phase lifecycle status string
- `Last activity` — ISO timestamp of most recent mutation
- `progress.completed_plans` / `progress.total_plans` — numeric progress counters driving the progress bar display
- `decisions` — list of captured decisions with IDs and text
- `blockers` — list of active blockers
- `metrics` — per-plan record of `duration`, `tasks`, `files`
- `stopped-at` / `resume-file` — session continuity fields written by `/gsd-pause-work`, consumed by `/gsd-resume-work`
- `waiting` / `resume` — async signal fields for inter-session handoffs

All mutations are routed through `state-document.cjs`, which enforces a `shouldPreserveExistingProgress` invariant to prevent accidental progress loss on concurrent writes.

### Key `config.json` dials

| Key | Values / type | Effect |
|---|---|---|
| `mode` | `interactive` \| `yolo` | Controls whether human approval gates are enforced |
| `granularity` | `coarse` \| `standard` \| `fine` | Drives phase count: 3–5 / 5–8 / 8–12 phases |
| `model_profile` | `quality` \| `balanced` \| `budget` \| `adaptive` \| `inherit` | Global model tier strategy |
| `runtime` | `claude` \| `codex` \| … | Active runtime identifier |
| `context_window` | integer (default 200000) | At ≥ 500000 enables 1M-context enrichment path |
| `workflow.research` | boolean | Enables/disables research phase |
| `workflow.plan_check` | boolean | Enables/disables plan-checker loop |
| `workflow.verifier` | boolean | Enables/disables post-execute verifier |
| `workflow.ui_phase` | boolean | Enables/disables UI design phase |
| `workflow.ui_review` | boolean | Enables/disables UI review step |
| `workflow.node_repair` | boolean | Enables autonomous task repair on verification failure |
| `workflow.node_repair_budget` | integer (default 2) | Maximum repair attempts per failed task |
| `workflow.discuss_mode` | string | Default discuss mode (`--auto`, `--all`, etc.) |
| `workflow.nyquist_validation` | boolean | Enables Nyquist test coverage mapping |
| `workflow.context_coverage_gate` | boolean | Enables requirements-to-test coverage gate |
| `workflow.drift_threshold` | integer (default 3) | Commit count at which codebase drift is flagged |
| `workflow.drift_action` | `warn` \| `auto-remap` | Action on drift threshold exceeded |
| `code_quality.fallow.enabled` | boolean | Enables fallow structural code review pre-pass |
| `code_quality.fallow.scope` | string | File scope for fallow analysis |
| `code_quality.fallow.profile` | string | fallow profile to apply |
| `code_quality.fallow.mcp` | boolean | Whether fallow runs via MCP |
| `parallelization.enabled` | boolean | Master switch for wave-based parallel execution |

---

## 7. Hooks Architecture

GSD ships 13 hook files under `hooks/` (12 functional entry points; `gsd-check-update-worker.js` is a supporting worker file for the update check hook). All hooks wrap their logic in try/catch and exit silently on error. Any stdin read is bounded by a 3-second timeout. Stale metrics older than 60 seconds are ignored by the monitoring hook.

| Hook file | Event | Role |
|---|---|---|
| `gsd-statusline.js` (22.6 KB) | `statusLine` | Displays model, task, directory, and context utilization bar in the IDE status line; writes `/tmp/claude-ctx-{session}.json` bridge file |
| `gsd-context-monitor.js` | `PostToolUse` / `AfterTool` | Reads bridge file; injects WARNING at ≤35% remaining context, CRITICAL at ≤25%; 5-tool-use debounce |
| `gsd-check-update.js` | `SessionStart` | Triggers background update check for new GSD versions |
| `gsd-check-update-worker.js` | `SessionStart` (worker) | Performs the actual version fetch in a background thread |
| `gsd-update-banner.js` | — | Surfaces "new version available" banner to the user |
| `gsd-prompt-guard.js` | `PreToolUse` (Write/Edit to `.planning/`) | Advisory prompt-injection scan on planning artifact writes |
| `gsd-read-injection-scanner.js` | `PostToolUse` (Read) | Scans Read tool output for injected instructions in file content |
| `gsd-read-guard.js` | `PreToolUse` | Advisory: warns when the agent attempts to Edit or Write a file it has not Read this session |
| `gsd-workflow-guard.js` | `PreToolUse` (Write/Edit outside `.planning/`) | Advisory: warns on edits made outside an active GSD workflow context |
| `gsd-session-state.sh` | `PostToolUse` | Session state tracking for shell-based runtimes |
| `gsd-validate-commit.sh` | `PostToolUse` | Enforces conventional-commit format (`feat(NN-MM):`) on commits |
| `gsd-phase-boundary.sh` | `PostToolUse` | Detects phase boundary transitions and updates STATE.md accordingly |
| `gsd-graphify-update.sh` | — | Incremental knowledge-graph refresh triggered on `.planning/` file change |

---

## 8. Auxiliary Tooling

See also [`../topics/auxiliary-tooling.md`](../topics/auxiliary-tooling.md).

### `bin/install.js`

The monolithic installer is approximately 469 KB and approximately 10,700 lines. It handles: runtime detection, installation location selection (global `~/.runtime/` or local `./.runtime/`), file deployment, per-runtime content transformation (tool name mapping, hook event renaming, agent frontmatter conversion, command spelling), path normalization, settings file integration, patch backup, manifest tracking, and idempotent `--uninstall` mode. The design principle is "write once, transform at install time" — all source files are authored in Claude Code's native format, and the installer applies transformations at install time to produce the correct format for each target runtime. This means there is one source of truth and 15 install-time variants.

### `gsd-sdk` and `gsd-tools.cjs`

`bin/gsd-sdk.js` (1.5 KB) is a small CLI shim wrapping the `@gsd-build/sdk` package. `gsd-tools.cjs` is the CJS distribution CLI with 20+ domain modules under `get-shit-done/bin/lib/`: `core`, `state`, `phase`, `roadmap`, `config`, `verify`, `template`, `frontmatter`, `init`, `milestone`, `commands`, `model-profiles`, `security`, `uat`, `docs`, `workstream`, `schema-detect`, `profile-pipeline`, `profile-output`, `planning-workspace`, `graphify`, `learnings`, `audit`, `gsd2-import`, `intel`.

The TypeScript SDK in `sdk/` re-implements `gsd-tools.cjs` as a typed registry (`createRegistry()` in `sdk/src/query/index.ts`). The `GSDTools` facade is routed through the SDK Runtime Bridge Module (`sdk/src/query-runtime-bridge.ts`), which prefers native registry dispatch and falls back to subprocess. The Sync Runtime Bridge (`sdk/src/runtime-bridge-sync/`) uses `synckit` (Atomics.wait on a SharedArrayBuffer in a pooled Worker thread) for synchronous `executeForCjs()`, achieving approximately 80ms on the first call and approximately 0.1ms at steady state. Golden parity tests assert that CJS and SDK paths produce identical output for every query.

### 23+ scripts

The `scripts/` directory contains the engineering and CI toolchain:

- `audit-workflow-script-paths.cjs` — verifies `@-ref`s in workflow files resolve to disk paths
- `base64-scan.sh` — pre-commit guard against accidentally committed base64 blobs
- `build-hooks.js` — generates hook build artifacts
- `lint-command-contract.cjs` — enforces command interface contracts
- `lint-descriptions.cjs` — validates skill and agent description format
- `lint-docs-required.cjs` — enforces required documentation presence
- `lint-no-source-grep.cjs` — prohibits source-grep patterns in workflow files
- `lint-shared-module-handsync.cjs` — validates shared module sync between CJS and SDK
- `lint-shell-command-projection-drift.cjs` — detects drift between shell command projections and source
- `lint-skill-deps.cjs` — validates `requires:` dependency closures in skill frontmatter
- `prompt-injection-scan.sh` — pre-release scan for prompt injection vulnerabilities
- `secret-scan.sh` — pre-release scan for accidentally committed secrets
- `run-tests.cjs` — root test runner

### External integrations

- **`slopcheck`** — package legitimacy auditing tool (MIT, pip-installable). Used by the Package Legitimacy Gate to audit every WebSearch-discovered package recommendation before it enters a plan.
- **`fallow`** — optional structural code review pre-pass (`npm install -D fallow@^2.70.0` or `cargo install fallow`). Requires v2.70+ JSON schema; older versions silently emit zero findings.
- **`gh` CLI** — required for `/gsd-ship`; used to create the GitHub PR with the assembled rich body.
- **`graphify`** — built-in knowledge graph of `.planning/` contents; updated incrementally by `gsd-graphify-update.sh`.
- **`intel`** — queryable codebase intelligence index; used by the `gsd-intel-updater` agent.
- **Context7** — external documentation context provider; referenced in agent prompts for up-to-date library documentation.
- **Local models** — Ollama, llama.cpp, LM Studio supported for `/gsd-review` with per-reviewer token-budget trimming via `review.max_prompt_tokens`.

---

## 9. Self-Healing and Verification

GSD's verification is layered. Each layer either passes or produces a diagnosed artifact that the next loop iteration consumes. See also [`../topics/self-healing-and-verification.md`](../topics/self-healing-and-verification.md).

### Plan-time gates

**Plan-checker loop.** `gsd-plan-checker` reviews each `PLAN.md` against an 8-dimension check and re-runs the planner up to 3 times until plans pass. The dimensions are not enumerated in public docs [unverified], but the loop is documented as blocking progress to execution.

**Research gate.** Planning is blocked if `RESEARCH.md` contains unresolved open questions. This forces the researcher-synthesizer cycle to reach a resolved state before the planner is invoked.

**Package Legitimacy Gate.** `gsd-phase-researcher` runs `slopcheck install --json` on every package recommended in research output. Results are written as a `## Package Legitimacy Audit` table in `RESEARCH.md` recording Registry, Age, Downloads, Source Repo, and one of four verdicts:

- `[SLOP]` — package stripped from recommendations entirely
- `[SUS]` — planner injects a `checkpoint:human-verify` task before the install
- `[OK]` — package approved for direct use
- `[ASSUMED]` — package treated as unverified; planner injects `checkpoint:human-verify`

Every package discovered via WebSearch is treated as `[ASSUMED]` until `slopcheck` verifies it. Failed installs cause execution to stop rather than silently substituting an alternative.

**Requirements coverage gate.** Every REQ-ID in `REQUIREMENTS.md` must map to at least one plan. Planning cannot complete if any requirement is uncovered.

**Decision coverage gate (BLOCKING at plan-time).** After planning, GSD refuses to mark a phase planned until every trackable `D-id` from `CONTEXT.md`'s `<decisions>` block appears in at least one plan's `must_haves`, `truths`, or body text. Two match modes are supported: strict ID match and a 6+-word verbatim phrase match. Decision IDs tagged with `[informational]`, `[folded]`, or `[deferred]` are explicitly excluded from the gate.

**Nyquist validation.** `gsd-nyquist-auditor` maps each phase requirement to a specific test command before any code is written. The metaphor is the Nyquist sampling theorem: requirements must be covered at sufficient "frequency" (test granularity) or signal is lost.

### Execute-time gates

**Atomic commit per task.** Each executor commits its work as `feat(NN-MM):` before returning control to the orchestrator. This ensures each plan's output is an independently revertable git commit.

**STATE.md lockfile.** All `writeStateMd()` calls go through `STATE.md.lock` created with `O_EXCL` (atomic creation that fails if the file already exists). Stale locks older than 10 seconds are cleared automatically. Contending writers use jittered spin-wait to avoid thundering-herd behavior.

**Checkpoint heartbeats.** The orchestrator emits `[checkpoint] phase N wave W/M` at every wave and plan boundary. These checkpoints allow a resumed session to identify exactly where execution stopped.

**Executor failure classifier.** `sdk/src/query/agent-failure-classifier.ts` classifies executor failures into three categories with distinct recovery strategies:

- `quota-exceeded` — wait for quota reset; detected by runtime-specific sentinel strings:
  - Anthropic: `usage limit` / `rate limit` / `quota` / `429` / `retry-after`
  - Copilot: `rate_limit`
  - Codex: `429` / `usage_limit_reached` / `too many requests`
  - Gemini: `RESOURCE_EXHAUSTED` / `exceeded your`
- `classify-handoff-bug` — spot check and retry
- `unknown-failure` — continue or stop based on config

**`node_repair`.** When `workflow.node_repair: true` (the default) and `workflow.node_repair_budget: 2`, the orchestrator attempts autonomous repair of a failed task within the same execute pass, up to the configured budget, before surfacing the failure to the user.

### Post-execute gates

**`gsd-verifier` agent.** Reads the phase PLAN, SUMMARY, REQUIREMENTS, and CONTEXT files (plus RESEARCH on 1M-context models), checks the actual execution output against the phase goal, and writes `VERIFICATION.md` with a PASS or FAIL verdict.

**Decision coverage gate at verify time (NON-BLOCKING).** After execution, the verifier searches plans, `SUMMARY.md` files, modified files, and recent commit messages for each tracked `D-id`. Misses are logged as a warning section in `VERIFICATION.md` rather than blocking the phase.

**Schema drift gate.** For projects using ORM patterns (Prisma, Drizzle), the verifier checks for schema drift between what the plans specified and what the executors actually produced.

**Codebase drift gate.** After the last wave's commits, GSD compares `last_mapped_commit..HEAD` against `.planning/codebase/STRUCTURE.md`. When the number of commits exceeds `workflow.drift_threshold` (default 3), the action depends on `workflow.drift_action`:

- `warn` (default) — emit a warning and continue
- `auto-remap` — automatically re-run `/gsd-map-codebase` before proceeding

### UAT self-healing

When `/gsd-verify-work N` finds a failure, it spawns `gsd-debugger` (approximately 47 KB, the largest agent in the roster). The debugger writes a new `PLAN.md` into the same phase directory. The user re-runs `/gsd-execute-phase N` — the same loop, with no special "fix mode" or alternative code path. The self-healing is structural: diagnosis produces a plan, plans are consumed by executors, executors produce commits. The loop is identical regardless of whether the work is original or remedial.

**Cross-AI plan convergence** (`/gsd-plan-review-convergence`) runs `plan-phase → review → replan → re-review` cycles, up to 3 by default. The orchestrator handles loop control, HIGH-concern counting, stall detection (HIGH count not decreasing across cycles), and escalates when `--max-cycles` is reached.

---

## 10. Multi-Runtime Support

GSD is authored entirely in Claude Code's native format and transformed at install time. The installer (`bin/install.js`) supports 15 runtimes across global and local installation paths. See also [`../topics/multi-runtime-support.md`](../topics/multi-runtime-support.md).

### Installation directory matrix

| Runtime | Global path | Local path |
|---|---|---|
| Claude Code | `~/.claude/` | `./.claude/` |
| OpenCode | `~/.config/opencode/` | `./.opencode/` |
| Kilo | `~/.config/kilo/` | `./.kilo/` |
| Gemini CLI | `~/.gemini/` | `./.gemini/` |
| Codex | `~/.codex/` | `./.codex/` |
| Copilot | `~/.copilot/` | `./.github/` |
| Cursor | `~/.cursor/` | `./.cursor/` |
| Windsurf | `~/.codeium/windsurf/` | `./.windsurf/` |
| Antigravity | `~/.gemini/antigravity/` | `./.agent/` |
| Augment | `~/.augment/` | `./.augment/` |
| Cline | `~/.cline/` | project root `.clinerules` |
| Trae | [unverified — not in docs reviewed] | [unverified] |
| Qwen Code | [unverified] | [unverified] |
| Hermes | [unverified] | [unverified] |
| CodeBuddy | [unverified] | [unverified] |

### Four adaptation types

**Tool name mapping.** Claude Code's tool names are rewritten per runtime: `Bash` → Copilot's `execute`; `Read` → Gemini's `read_file`; and so on. The mapping table lives in the installer.

**Hook event renaming.** Claude Code's hook event names are translated: `PostToolUse` ↔ Gemini's `AfterTool`; other runtimes may have no hook system at all (Cline uses a single `.clinerules` file; Copilot has no GSD hooks).

**Agent frontmatter conversion.** Each runtime has its own agent definition format. The installer converts GSD's source agent frontmatter to the required format for the target runtime. For Codex this means per-agent TOML entries in `config.toml`; for Copilot it means `.agent.md` files.

**Command spelling.** Gemini CLI uses colon-separated command names (`/gsd:command-name`) where Claude Code uses hyphen-separated names (`/gsd-command-name`). The installer rewrites command references to match the target runtime's convention.

### Installer Migration Module (ADR-0008)

The migration module handles file moves, stale-artifact cleanup, config rewrites, and user-data preservation across GSD version upgrades. Locally modified files are backed up into `gsd-local-patches/` so `/gsd-update --reapply` can restore user customizations after an upgrade. `gsd-file-manifest.json` is written on every install to enable clean `--uninstall`.

Platform-specific handling: Windows uses `windowsHide` on child processes, EPERM/EACCES protection, path-separator normalization, and retry-and-fallback on EPERM/EBUSY/EACCES. WSL detection warns about path mismatches when Windows Node.js is running on WSL. Docker and CI environments are supported via the `CLAUDE_CONFIG_DIR` environment variable.

---

## 11. Key Insights for Framework Design

The following design decisions are distinctive to GSD and transferable to other spec-driven AI coding frameworks. They are drawn from the "Notable Patterns" section of the research cache. See also [`../topics/patterns-worth-stealing.md`](../topics/patterns-worth-stealing.md).

- **Compound init handlers eliminate per-workflow context re-discovery.** A single CLI call (`gsd-sdk query init.execute-phase 1`) returns all context needed for a workflow as one JSON blob. Over approximately 50 KB it spills to a tempfile. This removes scattered file-reading from every workflow, keeps context loading deterministic, and makes cache invalidation predictable.

- **Wave-based parallel execution with lockfile-protected shared state.** Dependency analysis groups plans into waves; parallel executors within a wave commit with `--no-verify` for speed; the orchestrator runs hooks once per wave for correctness; `STATE.md.lock` with `O_EXCL` atomic creation and jittered spin-wait prevents write conflicts without a server process.

- **Self-healing as plan generation, not a special mode.** When UAT fails, the debugger writes a new `PLAN.md`. The user re-runs `/gsd-execute-phase`. There is no "fix mode" or alternative code path — the repair artifact is the same type as the original artifact, consumed by the same executor. This keeps the system's behavior surface minimal and auditable.

- **Two-stage namespace routing reduces eager skill listing cost by ~94%.** Six routers at 120 tokens total replace 86 flat skills at 2,150 tokens. Router descriptions use pipe-separated keyword tags rather than prose, following evidence that keyword-dense tags outperform prose for routing at approximately 40% the token cost.

- **Decision coverage gates with strict ID tracking and explicit opt-outs.** The discuss phase produces `D-01`, `D-02` decision IDs. The plan-time gate is blocking: every decision must appear in a plan. The verify-time gate is non-blocking: misses produce warnings. Two match modes (strict ID, 6+-word verbatim phrase) handle decisions that are referenced differently in plan prose. Explicit opt-out tags (`[informational]`, `[folded]`, `[deferred]`) prevent false-positive blocking.

- **Package legitimacy gate as a first-class slopsquatting defense.** Every package discovered via a web search is initially `[ASSUMED]`. `slopcheck` audits each package and assigns a verdict. `[SLOP]` packages are removed; `[SUS]` packages require a human-verify checkpoint before install. Failed installs stop the workflow rather than silently substituting an alternative. The audit table is written to `RESEARCH.md` for human review.

- **Skill surface as a runtime-controllable budget, not a fixed list.** Install-time profiles narrow the installed surface; runtime cluster toggles narrow it further without reinstall. This means the token cost of tool listing is a dial, not a constant, and can be tuned to the model and task at hand.
