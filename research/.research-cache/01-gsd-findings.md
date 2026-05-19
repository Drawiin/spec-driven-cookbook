# GSD Research Findings (Raw Cache)

> Source: gsd-build/get-shit-done  
> Cached from: research sub-agent run 2026-05-19  
> Agent ID: ccfe45b2-f665-4a68-84af-cfcdab6d008b  
> All URLs fetched successfully unless noted.

---

## 1. Overview & Philosophy

**What it is.** GSD ("Get Shit Done") is a "light-weight meta-prompting, context engineering, and spec-driven development system" distributed as a Node.js installer (`npx get-shit-done-cc@latest`) that lays down skills, slash commands, agents, references, hooks, and a CLI/SDK toolchain into the directories of 15+ AI coding runtimes (Claude Code, OpenCode, Gemini CLI, Kilo, Codex, Copilot, Cursor, Windsurf, Antigravity, Augment, Trae, Qwen Code, Hermes, CodeBuddy, Cline).

**Headline problem it claims to solve.** "Context rot — the quality degradation that happens as your AI fills its context window." Three failures it explicitly targets in `README.md`:

1. **Context bloat** — main session degrades as it grows; GSD pushes heavy work into fresh subagent contexts.
2. **No shared memory** — sessions forget; GSD persists structured artifacts (`PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`, `CONTEXT.md`) that survive `/clear`.
3. **No verification** — "Code that 'runs' isn't code that 'works.'" Dedicated verifier and UAT step with auto-diagnosed fix plans.

**Target audience.** Explicitly framed for *solo developers* and small teams who don't want sprint ceremonies. README quote from the author: *"Other spec-driven tools exist, but they're all built for 50-person engineering orgs… The complexity is in the system, not in your workflow."* Comparable tools called out: SpecKit, OpenSpec, Taskmaster.

**Built around six guiding ideas** (extracted from `ARCHITECTURE.md` "Design Principles"):
1. Fresh context per agent (each subagent gets up to 200K, or up to 1M for big-context models).
2. Thin orchestrators (workflows never do the heavy work themselves).
3. File-based state (no DB, no server, all in `.planning/`).
4. **"Absent = enabled"** — feature flags default to true when missing.
5. Defense in depth (plans verified before execution, verification before "done").
6. Multi-runtime portability (everything written in Claude Code's format, transformed at install time).

---

## 2. Workflow

The "main loop" is six commands; each is a one-line orchestrator that bootstraps a workflow file under `get-shit-done/workflows/*.md`. Each phase under `.planning/phases/XX-name/` accumulates a known set of artifacts.

| Step | Command | What it does | Artifacts produced |
|---|---|---|---|
| 1. Initialize | `/gsd-new-project` | Asks questions, spawns 4 parallel research agents (stack, features, architecture, pitfalls), extracts requirements, drafts roadmap, awaits approval | `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`, `config.json`, `research/{SUMMARY,STACK,FEATURES,ARCHITECTURE,PITFALLS}.md`, `CLAUDE.md` |
| 1b. Brownfield prep | `/gsd-map-codebase` | Spawns 4 parallel `gsd-codebase-mapper` agents (tech, arch, quality, concerns) so a brownfield project gets analyzed before new-project | `.planning/codebase/{STACK,ARCHITECTURE,CONVENTIONS,CONCERNS,STRUCTURE,TESTING,INTEGRATIONS}.md` with `last_mapped_commit` YAML frontmatter |
| 2. Discuss | `/gsd-discuss-phase N` | Phase-scoped interactive Q&A to lock implementation decisions before any planning; modes: `--all`, `--auto`, `--batch`, `--analyze`, `--power`, `--assumptions` | `{phase}-CONTEXT.md` with numbered `<decisions>` (`D-01`, `D-02`…), `{phase}-DISCUSSION-LOG.md` audit trail |
| 2b. UI design | `/gsd-ui-phase N` | Optional design contract for frontend phases (6-pillar contract: copywriting, visuals, color, typography, spacing, registry safety) | `{phase}-UI-SPEC.md` |
| 3. Plan | `/gsd-plan-phase N` | Research → plan → verify loop. 4 parallel researchers, then a planner, then a `plan-checker` that loops up to 3× | `{phase}-RESEARCH.md`, `{phase}-{NN}-PLAN.md` files, `{phase}-VALIDATION.md` |
| 4. Execute | `/gsd-execute-phase N` | Plans grouped into dependency waves; each plan dispatched to a `gsd-executor` agent in a fresh 200K context; atomic git commit per task | `{phase}-{NN}-SUMMARY.md` per plan, atomic git commits (`feat(NN-MM):`), `{phase}-VERIFICATION.md` |
| 5. Verify | `/gsd-verify-work N` | Walks the user through phase goal acceptance criteria; on failure invokes debug/diagnosis agent that writes a fix plan | `{phase}-UAT.md`, optional new fix-PLAN |
| 6. Ship | `/gsd-ship N` | Generates GitHub PR via `gh` with rich body assembled from PLAN/SUMMARY/VERIFICATION | GitHub PR, updated `STATE.md` |
| 6b. Auto-advance | `/gsd-progress --next` | Auto-detects current state and runs the right next command | — |
| 7. Close milestone | `/gsd-complete-milestone` → `/gsd-new-milestone` | Archive milestone to `MILESTONES.md`, tag release in git, start fresh requirements/roadmap | `MILESTONES.md` entry, git tag |

Beyond the loop, `commands/gsd/` ships dozens of additional skills. After v1.40 consolidation, GSD ships 59 sub-skills (plus 6 namespace meta-skills).

---

## 3. Context Engineering

**Persistent project state (`.planning/`)** — `ARCHITECTURE.md` documents every file:

- `PROJECT.md` — vision, constraints, decisions, evolution rules. Read by *all* agents.
- `REQUIREMENTS.md` — scoped REQ-IDs (v1/v2/out-of-scope). Read by planner, verifier, auditor.
- `ROADMAP.md` — phase breakdown with status table. Read by orchestrators.
- `STATE.md` — "living memory" with `## Current Position`, decisions, blockers, metrics, progress bar. Read by all agents.
- `config.json` — every dial (mode, model_profile, workflow toggles, parallelization, code_quality, ship sections).
- Per-phase: `XX-CONTEXT.md`, `XX-RESEARCH.md`, `XX-YY-PLAN.md`, `XX-YY-SUMMARY.md`, `XX-VERIFICATION.md`, `XX-VALIDATION.md`, `XX-UI-SPEC.md`, `XX-UAT.md`.

**Compound init handlers.** Workflows never read files piecemeal — they call one CLI/SDK seam that returns everything needed for that specific workflow as a single JSON blob:

```
node gsd-tools.cjs init execute-phase 1
node gsd-tools.cjs init plan-phase 1
node gsd-tools.cjs init new-project
```

When the JSON exceeds ~50 KB it spills to a tempfile and returns `@file:/tmp/gsd-init-XXXXX.json`, which workflows expand. One loader call per workflow, deduplicated, ready to inject.

**Fresh subagent context per task.** From `ARCHITECTURE.md`: "Every agent spawned by an orchestrator gets a clean context window (up to 200K tokens). This eliminates context rot." Researchers/planners/executors are *always* invoked through the runtime's subagent/Task primitive, never inline.

**Adaptive enrichment on 1M-context models.** `config.context_window ≥ 500000` causes executor and verifier prompts to be enriched with prior wave `SUMMARY.md` files and phase context. Below the threshold, prompts use truncated, cache-friendly versions.

**Token budget controls documented:**
- Two-stage namespace routing meta-skills reduce eager skill listing from "~2,150 tokens for 86 flat skills" to "~120 tokens for 6 routers."
- A `validate context` CLI verb emits `{utilization, status, suggestion}`; warn/critical at 60% / 70%.
- Hook `gsd-context-monitor.js` (`PostToolUse`/`AfterTool`) injects warnings at ≤35% remaining ("avoid starting new complex work") and ≤25% ("inform user"). 5-tool-use debounce; bridge file at `/tmp/claude-ctx-{session}.json`.
- `review.max_prompt_tokens` and per-reviewer overrides for small-context local models (Ollama, llama.cpp, LM Studio).
- Per-workflow size budget enforced in CI: `XL` ≤ 1700 lines for top orchestrators, `LARGE` ≤ 1500, `DEFAULT` ≤ 1000.
- Per-agent file cap: agent `.md` files must stay under ~45K chars with a hard 50K char invariant. Overflow extracted to `references/*.md`.

---

## 4. Sub-Agent Orchestration

`ARCHITECTURE.md` advertises 31–33 agents (minor docs drift). All live in `agents/gsd-*.md`. The full roster from the GitHub API listing of `/agents`:

`gsd-advisor-researcher`, `gsd-ai-researcher`, `gsd-assumptions-analyzer`, `gsd-code-fixer`, `gsd-code-reviewer`, `gsd-codebase-mapper`, `gsd-debug-session-manager`, `gsd-debugger`, `gsd-doc-classifier`, `gsd-doc-synthesizer`, `gsd-doc-verifier`, `gsd-doc-writer`, `gsd-domain-researcher`, `gsd-eval-auditor`, `gsd-eval-planner`, `gsd-executor`, `gsd-framework-selector`, `gsd-integration-checker`, `gsd-intel-updater`, `gsd-nyquist-auditor`, `gsd-pattern-mapper`, `gsd-phase-researcher`, `gsd-plan-checker`, `gsd-planner`, `gsd-project-researcher`, `gsd-research-synthesizer`, `gsd-roadmapper`, `gsd-security-auditor`, `gsd-ui-auditor`, `gsd-ui-checker`, `gsd-ui-researcher`, `gsd-user-profiler`, `gsd-verifier`.

**Spawn taxonomy:**

| Category | Agents | Parallelism |
|---|---|---|
| Researchers | `gsd-project-researcher`, `gsd-phase-researcher`, `gsd-ui-researcher`, `gsd-advisor-researcher` | 4 parallel (stack / features / architecture / pitfalls) |
| Synthesizers | `gsd-research-synthesizer` | Sequential after researchers |
| Planners | `gsd-planner`, `gsd-roadmapper` | Sequential |
| Checkers | `gsd-plan-checker`, `gsd-integration-checker`, `gsd-ui-checker`, `gsd-nyquist-auditor` | Sequential, loop up to 3× |
| Executors | `gsd-executor` | Parallel **within** a wave, sequential across waves |
| Verifiers | `gsd-verifier` | Sequential after all executors complete |
| Mappers | `gsd-codebase-mapper` | 4 parallel (tech / arch / quality / concerns) |
| Debuggers | `gsd-debugger` | Sequential, interactive |

**Dispatch pattern pseudocode (from `ARCHITECTURE.md`):**
```
Orchestrator (workflow .md)
   ├── Load context: gsd-sdk query init.<workflow> <phase>
   ├── Resolve model: gsd-sdk query resolve-model <agent-name>
   │   Returns: opus | sonnet | haiku | inherit
   ├── Spawn Agent (Task/SubAgent call)
   ├── Collect result
   └── Update state: gsd-sdk query state.update / state.patch / state.advance-plan
```

**Wave-based parallel execution:**
```
Wave Analysis:
  Plan 01 (no deps)        ─┐
  Plan 02 (no deps)        ─┤── Wave 1 (parallel)
  Plan 03 (depends: 01)    ─┤── Wave 2 (waits for Wave 1)
  Plan 04 (depends: 02)    ─┘
  Plan 05 (depends: 03,04) ─── Wave 3 (waits for Wave 2)
```

Parallel-commit safety: parallel executors commit with `--no-verify`; the orchestrator runs `git hook run pre-commit` once after each wave. All `writeStateMd()` calls go through lockfile-based mutual exclusion (`STATE.md.lock` with `O_EXCL` atomic creation, 10s stale-lock timeout, jittered spin-wait).

**Model profiles.** Five profiles (`quality`, `balanced`, `budget`, `adaptive`, `inherit`) defined in `CONFIGURATION.md`. Resolution precedence is five layers (highest-to-lowest):

```
1. model_overrides[<agent>]            ← per-agent specific
2. dynamic_routing.tier_models[<tier>] ← when dynamic_routing.enabled
3. models[<phase_type>]                ← phase-level
4. model_profile (per-agent column)    ← global tier strategy
5. Runtime default                     ← fallback
```

Built-in tier maps per runtime — for `claude`: opus = `claude-opus-4-7`, sonnet = `claude-sonnet-4-6`, haiku = `claude-haiku-4-5`.

---

## 5. Skills System

GSD ships as **skills** (primary surface on most runtimes) and **slash commands** (Claude Code local installs).

**Skill Surface Budget Module (ADR-0011):**
- **Phase 1 — install-time profile selection.** Named profiles: `--profile=core` (six core-loop skills), `--profile=standard` (core + phase management), full default. Profiles compose: `--profile=core,audit`. `--minimal` is an alias for `--profile=core`. Closure over `requires:` frontmatter ensures transitive install.
- **Phase 2 — runtime enable/disable.** `/gsd:surface` toggles cluster-level skill groups without reinstall; cluster definitions in `bin/lib/clusters.cjs`; state in `<config>/.gsd-surface.json`.

**Namespace meta-skills (v1.40 two-stage routing):**

| Router | Routes to |
|---|---|
| `/gsd-workflow` | discuss / plan / execute / verify / phase / progress |
| `/gsd-project` | milestones, audits, summary |
| `/gsd-quality` | code review, debug, audit, security, eval, ui |
| `/gsd-context` | map, graphify, docs, learnings |
| `/gsd-manage` | config, workspace, workstreams, thread, update, ship, inbox |
| `/gsd-ideate` | explore, sketch, spike, spec, capture |

Router descriptions use "pipe-separated keyword tags (≤ 60 chars)" — "Tool Attention research showing keyword-dense tags outperform prose for routing at ~40% the token cost."

**Runtime → install surface mapping:**

| Runtime | Invocation surface | Agents | Config & hooks |
|---|---|---|---|
| Claude Code | Global: `skills/gsd-*/SKILL.md`; Local: `commands/gsd/*.md` | `agents/gsd-*.md` | `settings.json` hook + statusLine |
| OpenCode / Kilo | `command/gsd-*.md` | `agents/gsd-*.md` | `opencode.json`/`kilo.json` |
| Gemini CLI | `commands/gsd/*.toml` (colon form `/gsd:command-name`) | `agents/gsd-*.md` | `settings.json` hooks + statusline |
| Codex | `skills/gsd-*/SKILL.md` | per-agent TOML in `config.toml` | hook tables under `[features].hooks` |
| Copilot | `skills/gsd-*/SKILL.md` + `copilot-instructions.md` | `.agent.md` | no GSD hooks |
| Cursor | `skills/gsd-*/SKILL.md` | `agents/gsd-*.md` | rule references under `rules/` |
| Windsurf | `skills/gsd-*/SKILL.md` | `agents/gsd-*.md` | rule references under `rules/` |
| Cline | `.clinerules` | rules only | no hooks |

---

## 6. Local Data Storage

**Per-project (committable):** everything under `.planning/`. Full canonical layout from `ARCHITECTURE.md`:

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

**STATE.md schema** — YAML frontmatter is the canonical store. Fields: `current_phase`, `Status`, `Last activity`, `progress.{completed_plans,total_plans}`, decisions list, blockers list, metrics (per-plan `duration, tasks, files`), session continuity (`stopped-at`, `resume-file`), waiting/resume signals. Mutations routed through `state-document.cjs` with a `shouldPreserveExistingProgress` invariant.

**`config.json` schema highlights:**
- `mode`: `interactive` | `yolo`
- `granularity`: `coarse` | `standard` | `fine` (drives phase count: 3–5 / 5–8 / 8–12)
- `model_profile`: `quality` | `balanced` | `budget` | `adaptive` | `inherit`
- `runtime`: `claude` | `codex` | …
- `context_window`: integer (default 200000; ≥ 500000 enables 1M-context enrichment)
- `workflow.*`: `research`, `plan_check`, `verifier`, `ui_phase`, `ui_review`, `node_repair` (+ `node_repair_budget`, default 2), `discuss_mode`, `nyquist_validation`, `context_coverage_gate`, `drift_threshold`, `drift_action`
- `code_quality.fallow.{enabled,scope,profile,mcp}`
- `parallelization.enabled`

**Installation directories per runtime:**

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

---

## 7. Auxiliary Tooling

**`bin/`:**
- `bin/gsd-sdk.js` (1.5 KB) — small CLI shim wrapping the `@gsd-build/sdk` package.
- `bin/install.js` (~469 KB) — the monolithic installer (~10,700 lines). Handles runtime detection, location selection, file deployment, per-runtime content transformation, path normalization, settings integration, patch backup, manifest tracking, idempotent `--uninstall` mode.

**`gsd-tools.cjs`** (CJS distribution CLI) with 20+ domain modules under `get-shit-done/bin/lib/`: `core`, `state`, `phase`, `roadmap`, `config`, `verify`, `template`, `frontmatter`, `init`, `milestone`, `commands`, `model-profiles`, `security`, `uat`, `docs`, `workstream`, `schema-detect`, `profile-pipeline`, `profile-output`, `planning-workspace`, `graphify`, `learnings`, `audit`, `gsd2-import`, `intel`.

**`scripts/`** — 23+ engineering/CI scripts:
- `audit-workflow-script-paths.cjs` — verifies `@-ref`s in workflows resolve to disk
- `base64-scan.sh` — pre-commit guard for accidentally-committed base64 blobs
- `build-hooks.js` — generates hook artifacts
- `lint-command-contract.cjs`, `lint-descriptions.cjs`, `lint-docs-required.cjs`, `lint-no-source-grep.cjs`, `lint-shared-module-handsync.cjs`, `lint-shell-command-projection-drift.cjs`, `lint-skill-deps.cjs` — custom lint suite
- `prompt-injection-scan.sh`, `secret-scan.sh` — pre-release security scans
- `run-tests.cjs` — root test runner

**`hooks/`** — 12 runtime hooks:

| File | Event | Role |
|---|---|---|
| `gsd-statusline.js` (22.6 KB) | `statusLine` | Displays model, task, directory, context bar; writes `/tmp/claude-ctx-{session}.json` bridge |
| `gsd-context-monitor.js` | `PostToolUse`/`AfterTool` | Injects WARNING/CRITICAL context-budget hints into next turn |
| `gsd-check-update.js` + `gsd-check-update-worker.js` | `SessionStart` | Background update check |
| `gsd-update-banner.js` | — | Surfaces "new version available" banner |
| `gsd-prompt-guard.js` | `PreToolUse` (Write/Edit to `.planning/`) | Advisory prompt-injection scan on planning artifacts |
| `gsd-read-injection-scanner.js` | `PostToolUse` (Read) | Scans Read tool output for injected instructions |
| `gsd-read-guard.js` | `PreToolUse` | Advisory: prevent Edit/Write on files not Read this session |
| `gsd-workflow-guard.js` | `PreToolUse` (Write/Edit outside `.planning/`) | Advisory: edits outside a GSD workflow context |
| `gsd-session-state.sh` | `PostToolUse` | Session state tracking for shell-based runtimes |
| `gsd-validate-commit.sh` | `PostToolUse` | Conventional-commit enforcement |
| `gsd-phase-boundary.sh` | `PostToolUse` | Phase boundary detection |
| `gsd-graphify-update.sh` | — | Incremental knowledge-graph refresh on file change |

Safety design: every hook wraps in try/catch and exits silently on error; 3s stdin timeout; stale metrics (>60s) ignored.

**`sdk/`** — TypeScript SDK with `src/`, `shared/`, `prompts/`, `test-fixtures/`, handover docs.

SDK key features:
- Re-implements CJS `gsd-tools.cjs` as a typed registry (`createRegistry()` in `sdk/src/query/index.ts`).
- `GSDTools` façade routed through **SDK Runtime Bridge Module** (`sdk/src/query-runtime-bridge.ts`) — prefers native registry dispatch, falls back to subprocess, supports `strictSdk`, emits structured `onDispatchEvent` observability.
- **Sync Runtime Bridge** (`sdk/src/runtime-bridge-sync/`) uses `synckit` (Atomics.wait on SharedArrayBuffer in a pooled Worker thread) for synchronous `executeForCjs()` — ~80ms first call, ~0.1ms steady state.
- Golden parity tests assert CJS and SDK paths produce identical output.

**External tool integrations:**
- `slopcheck` — package legitimacy auditing (MIT, pip-installable).
- `fallow` — optional structural code review pre-pass (`npm install -D fallow@^2.70.0` or `cargo install fallow`). v2.70+ JSON schema required; older versions silently emit zero findings.
- `gh` CLI — required for `/gsd-ship`.
- `graphify` — built-in knowledge graph of `.planning/`.
- `intel` — queryable codebase intelligence index.
- Local Ollama/llama.cpp/LM Studio — supported for `/gsd-review` with token-budget trimming.

---

## 8. Self-Healing & Verification

GSD's verification is layered. Each layer either passes or produces a diagnosed fix that the next loop iteration consumes.

**Plan-time gates:**
- **Plan-checker loop.** `gsd-plan-checker` reviews each `PLAN.md` and re-runs the planner up to 3× until plans pass an 8-dimension check.
- **Research gate.** Blocks planning if `RESEARCH.md` has unresolved open questions.
- **Package Legitimacy Gate.** `gsd-phase-researcher` runs `slopcheck install --json` on every recommended package. Writes a `## Package Legitimacy Audit` table to `RESEARCH.md` recording Registry, Age, Downloads, Source Repo, verdict (`[SLOP]`, `[SUS]`, `[OK]`). `[SLOP]` stripped entirely; `[SUS]` and `[ASSUMED]` cause planner to inject `checkpoint:human-verify` before install task.
- **Requirements coverage gate.** Every REQ-ID must map to at least one plan.
- **Decision coverage gate (BLOCKING at plan-time).** After planning, GSD refuses to mark the phase planned until every trackable D-id from `CONTEXT.md`'s `<decisions>` block appears in at least one plan's `must_haves`, `truths`, or body.
- **Nyquist validation.** `gsd-nyquist-auditor` maps each phase requirement to a specific test command before any code is written.

**Execute-time gates:**
- Atomic commit per task (`feat(NN-MM):`).
- STATE.md file locking (`STATE.md.lock` with `O_EXCL`, 10s stale-lock timeout, jittered spin-wait).
- Checkpoint heartbeats (`[checkpoint] phase N wave W/M`) at every wave/plan boundary.
- **Executor failure classifier** (`sdk/src/query/agent-failure-classifier.ts`). Classifies into `quota-exceeded` | `classify-handoff-bug` | `unknown-failure`:
  - Anthropic: `usage limit` / `rate limit` / `quota` / `429` / `retry-after`
  - Copilot: `rate_limit`
  - Codex: `429` / `usage_limit_reached` / `too many requests`
  - Gemini: `RESOURCE_EXHAUSTED` / `exceeded your`
- **`node_repair`** — `workflow.node_repair: true` (default) + `workflow.node_repair_budget: 2` enables autonomous task repair on verification failure within a single execute pass.

**Post-execute gates:**
- **`gsd-verifier` agent.** Reads everything (PLAN, SUMMARY, REQUIREMENTS, CONTEXT, RESEARCH on 1M models), checks against phase goal, writes `VERIFICATION.md` (PASS/FAIL).
- **Decision coverage gate at verify time (NON-BLOCKING)** — searches plans, SUMMARY.md, modified files, recent commit messages for each tracked D-id. Misses logged as warning section.
- **Schema drift gate** — ORM patterns (Prisma, Drizzle).
- **Codebase drift gate.** After last wave's commits, compares `last_mapped_commit..HEAD` against `.planning/codebase/STRUCTURE.md`. At `workflow.drift_threshold` (default 3): warns (default) or auto-remaps (`workflow.drift_action = auto-remap`).

**UAT (`/gsd-verify-work N`):**

When failure found, spawns `gsd-debugger` (~47 KB, largest agent) which writes a *new* `PLAN.md` into the same phase. User re-runs `/gsd-execute-phase N` — same loop, no special "fix mode."

**Cross-AI plan convergence** (`/gsd-plan-review-convergence`). Runs `plan-phase → review → replan → re-review` cycles (max 3 by default). Orchestrator handles loop control, HIGH-concern counting, stall detection (HIGH count not decreasing across cycles), escalation gate when `--max-cycles` hit.

**Quota-aware execution recovery.** Executor classifier plus class-distinct prompts: quota → wait for reset; classify-handoff-bug → spot check; unknown → continue/stop.

---

## 9. Runtime Adapters

GSD writes everything in Claude Code's native format and transforms at install time via `bin/install.js`. Key adaptation points:

1. **Tool name mapping** — Claude's `Bash` → Copilot's `execute`, `Read` → Gemini's `read_file`, etc.
2. **Hook event names** — Claude `PostToolUse` ↔ Gemini `AfterTool`.
3. **Agent frontmatter** — each runtime has its own definition format; installer converts.
4. **Path conventions** — see installation directory table above.
5. **Model references** — `model_profile: "inherit"` defers to runtime's session model.
6. **Hyphen/colon command spelling** — installer rewrites for Gemini.
7. **Skill placement** — most runtimes get `skills/gsd-*/SKILL.md`; Claude Code uses `commands/gsd/*.md` for local installs; Codex uses `~/.codex/skills/<name>/SKILL.md`; Cline uses a single `.clinerules`.

The **Installer Migration Module** (ADR-0008): file moves, stale-artifact cleanup, config rewrites, user-data preservation. Backs up locally modified files into `gsd-local-patches/` so `/gsd-update --reapply` can restore user customizations. `gsd-file-manifest.json` written for clean uninstall.

**Platform handling:**
- Windows: `windowsHide` on child processes, EPERM/EACCES protection, path-separator normalization, retry-and-fallback on EPERM/EBUSY/EACCES.
- WSL: detects Windows Node.js running on WSL, warns about path mismatches.
- Docker/CI: `CLAUDE_CONFIG_DIR` env var.

---

## 10. Notable Patterns Worth Stealing

1. **Compound init handlers.** `gsd-sdk query init.execute-phase 1` returns project info, config, state, and phase details as a single JSON. Over ~50 KB, spills to tempfile (`@file:/tmp/gsd-init-XXXXX.json`). Removes per-workflow re-discovery cost and keeps cache-friendly ordering deterministic.

2. **Wave-based parallel execution with `--no-verify` + lockfile-protected state writes.** Dependency analysis groups plans into waves; parallel executors commit with `--no-verify`; orchestrator runs hooks once per wave; `STATE.md.lock` with `O_EXCL` creation + 10s stale-timeout + jittered spin-wait.

3. **Diagnose-into-a-PLAN.md self-healing.** When `/gsd-verify-work` finds a failure, the debug agent writes a *new* `PLAN.md`. User re-runs `/gsd-execute-phase` — same loop, no special "fix mode."

4. **Two-stage namespace routing meta-skills.** Six routers reduce eager skill listing cost from ~2,150 tokens to ~120 tokens. Skill descriptions use pipe-separated keyword tags rather than prose ("keyword-dense tags outperform prose for routing at ~40% the token cost").

5. **Decision coverage gates with strict ID match and soft phrase match.** Discuss-phase produces `D-01`, `D-02` decision IDs; plan-time gate is blocking (every decision must appear in a plan); verify-time gate is non-blocking (warns). Two match modes (strict id, or 6+-word phrase verbatim) plus explicit opt-out tags (`[informational]`, `[folded]`, `[deferred]`).

6. **Skill Surface Budget Module.** `--profile=core` (six skills), `--profile=standard`, full default, composition (`--profile=core,audit`). At runtime `/gsd:surface` enables/disables clusters without reinstall. Closure over `requires:` frontmatter ensures transitive install.

7. **Package Legitimacy Gate (slopsquatting defense).** Every WebSearch-discovered package treated as `[ASSUMED]`; `slopcheck` run per package; audit table written to `RESEARCH.md`; `[SUS]` installs gated behind `checkpoint:human-verify`; failed installs stop instead of silently substituting alternatives.

---

## 11. Sources Cited

All URLs fetched successfully (HTTP 200) on 2026-05-19:

1. `https://raw.githubusercontent.com/gsd-build/get-shit-done/main/README.md`
2. `https://raw.githubusercontent.com/gsd-build/get-shit-done/main/AGENTS.md`
3. `https://raw.githubusercontent.com/gsd-build/get-shit-done/main/CONTEXT.md` (65 KB, 551 lines)
4. `https://raw.githubusercontent.com/gsd-build/get-shit-done/main/docs/ARCHITECTURE.md` (43 KB, 772 lines)
5. `https://raw.githubusercontent.com/gsd-build/get-shit-done/main/docs/COMMANDS.md` (55 KB, 1437 lines)
6. `https://raw.githubusercontent.com/gsd-build/get-shit-done/main/docs/CONFIGURATION.md` (67 KB, 1112 lines)
7. `https://raw.githubusercontent.com/gsd-build/get-shit-done/main/docs/CLI-TOOLS.md`
8. `https://raw.githubusercontent.com/gsd-build/get-shit-done/main/docs/FEATURES.md` (142 KB, 3070 lines)
9. `https://raw.githubusercontent.com/gsd-build/get-shit-done/main/docs/USER-GUIDE.md` (60 KB, 1399 lines)

GitHub API folder listings (all 200):
- `https://api.github.com/repos/gsd-build/get-shit-done/contents/agents` — 33 agent `.md` files
- `https://api.github.com/repos/gsd-build/get-shit-done/contents/bin` — 2 files: `gsd-sdk.js`, `install.js`
- `https://api.github.com/repos/gsd-build/get-shit-done/contents/commands/gsd` — 60+ command `.md` files
- `https://api.github.com/repos/gsd-build/get-shit-done/contents/hooks` — 12 hook files + `lib/` directory
- `https://api.github.com/repos/gsd-build/get-shit-done/contents/scripts` — 23+ scripts
- `https://api.github.com/repos/gsd-build/get-shit-done/contents/sdk`

**Unverified / not found in docs reviewed:**
- Full per-runtime install-path-per-skill matrix (authoritative roster in `docs/INVENTORY-MANIFEST.json` not fetched).
- Exact contents of `agents/gsd-*.md` (agent roles paraphrased from `ARCHITECTURE.md` taxonomy table, not from each agent's frontmatter directly).
- Whether `/gsd-ultraplan-phase` is general-purpose or Claude-only; docs label it `[BETA]`.
