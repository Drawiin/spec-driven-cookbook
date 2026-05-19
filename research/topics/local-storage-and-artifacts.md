# Local Storage and Artifacts

## 1. Overview

Every framework studied uses file-based local storage — no server, no database. The choice is deliberate: files survive sessions, can be version-controlled, are readable by any AI agent regardless of runtime, and support fully offline workflows. The design philosophy shared across GSD, TLC, Spec Kit, OpenSpec, and Task Master is that the artifact folder is the source of truth: a fresh agent context can recover full project state by reading files, not by querying a running process.

---

## 2. Top-Level Layout Comparison

| Framework | Root artifact dir | Committed to git? | Notes |
|---|---|---|---|
| GSD | `.planning/` | Yes (recommended) | `ui-reviews/` gitignored by convention |
| TLC | `.specs/` | Yes (recommended) | No generated or binary files |
| Spec Kit | `.specify/` | Yes | Templates, presets, extensions also committed |
| OpenSpec | `openspec/` | Yes | Archive subfolder grows over time |
| Task Master | `.taskmaster/` | Yes | Per-editor MCP config lives outside in IDE dirs |
| Graphify | `graphify-out/` (committed) + `~/.graphify/global.json` (global) | `graphify-out/` yes; `manifest.json` and `cost.json` gitignored | Global cross-project graph stored in home directory |

The leading-dot convention (`.planning/`, `.specs/`, `.specify/`, `.taskmaster/`) signals that these are tool-managed directories, not application source. OpenSpec uses `openspec/` without a dot — a minor but intentional legibility choice. Graphify is the only framework with a meaningful user-global artifact (`~/.graphify/global.json`) that persists across projects.

---

## 3. GSD: `.planning/` Deep Dive

See also: `../frameworks/gsd.md`

### Directory tree

The full canonical layout from GSD documentation (synthesized from `ARCHITECTURE.md`, `FEATURES.md`, and `USER-GUIDE.md` — note: `workstreams/`, `graphs/`, `reports/`, `spikes/` are documented in GSD features docs but do not appear in `ARCHITECTURE.md`'s tree directly):

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

### STATE.md

`STATE.md` is GSD's "living memory." Its YAML frontmatter is the canonical persistent store. Key fields:

- `current_phase` — phase index and name
- `Status` — current workflow state
- `Last activity` — timestamp of most recent mutation
- `progress.completed_plans` / `progress.total_plans` — displayed as a progress bar
- `decisions: [...]` — YAML array of tracked decision entries
- `blockers: [...]` — YAML array of active blockers
- `metrics: [...]` — per-plan records of `duration`, `tasks`, `files`
- `stopped-at` — where the session halted
- `resume-file` — which file to read first on resumption
- Waiting/resume signals — coordination flags for the pause/resume flow

All writes are routed through `state-document.cjs`, which enforces a `shouldPreserveExistingProgress` invariant so that a misbehaving agent cannot overwrite recorded progress. Concurrent write safety is enforced via `STATE.md.lock` — created with `O_EXCL` (atomic), 10-second stale-lock timeout, and jittered spin-wait. This matters because wave-based parallel executors all write to the same state file.

### config.json

Key dials with non-obvious effect:

- `mode`: `interactive` | `yolo` — whether the agent pauses for user approval at gates
- `granularity`: `coarse` | `standard` | `fine` — drives phase count (3–5 / 5–8 / 8–12)
- `model_profile`: `quality` | `balanced` | `budget` | `adaptive` | `inherit`
- `context_window`: integer — when ≥ 500,000, executor and verifier prompts are enriched with prior wave `SUMMARY.md` files; below the threshold, truncated cache-friendly versions are used
- `workflow.research`, `workflow.plan_check`, `workflow.verifier`, `workflow.ui_phase`, `workflow.ui_review`, `workflow.node_repair`, `workflow.node_repair_budget`, `workflow.nyquist_validation`, `workflow.context_coverage_gate`, `workflow.drift_threshold`, `workflow.drift_action` — each toggles or tunes a specific workflow subsystem
- `code_quality.fallow.{enabled,scope,profile,mcp}` — optional structural pre-pass via the `fallow` tool
- `parallelization.enabled` — wave-level parallel execution on/off

The "absent = enabled" convention applies to workflow flags: a missing key defaults to `true`, so GSD's behavior when a fresh `config.json` is missing a flag is to run that subsystem.

### Sidecar folders with non-obvious purposes

Several directories are worth calling out because their purpose is not obvious from the name:

- **`todos/{pending,done}/`** — lightweight task queue for work items that don't merit a full plan. Not the same as `phases/XX/XX-YY-PLAN.md`.
- **`threads/`** — multi-session conversation continuity. Each thread is an independent context slice for a parallel line of investigation.
- **`seeds/`** — starter prompts or partial specs that haven't been elevated into a formal phase yet. Captures ideas before they're commitments.
- **`debug/knowledge-base.md`** — accumulated diagnostic findings from resolved debug sessions. Not just a log; it's a queryable reference that the `gsd-debugger` agent can re-read when a similar failure recurs.
- **`spikes/NNN-name/`** — time-boxed research experiments. A spike never becomes a plan directly; its output feeds back into `research/` or `REQUIREMENTS.md`.
- **`workstreams/`** — parallel streams of phase work that can run independently. Used when two features need simultaneous planning.

### continue-here.md

`continue-here.md` is written by `/gsd-pause-work` as a session handoff artifact. It summarizes exactly where the session stopped and what to do first when resuming, keeping the critical path short enough for a fresh context window. Unlike `STATE.md` (which tracks all history), `continue-here.md` is forward-looking: it is intentionally overwritten on every pause.

---

## 4. TLC: `.specs/` Deep Dive

See also: `../frameworks/tlc-spec-driven.md`

### Directory tree

The full layout from TLC's `SKILL.md`:

```
.specs/
├── project/
│   ├── PROJECT.md      # Vision & goals
│   ├── ROADMAP.md      # Features & milestones
│   └── STATE.md        # Memory: decisions, blockers, lessons, todos, deferred ideas
├── codebase/           # Brownfield analysis (existing projects)
│   ├── STACK.md
│   ├── ARCHITECTURE.md
│   ├── CONVENTIONS.md
│   ├── STRUCTURE.md
│   ├── TESTING.md
│   ├── INTEGRATIONS.md
│   └── CONCERNS.md
├── features/
│   └── [feature]/
│       ├── spec.md     # Requirements with traceable IDs
│       ├── context.md  # User decisions for gray areas (only when discuss triggered)
│       ├── design.md   # Architecture & components (only for Large/Complex)
│       └── tasks.md    # Atomic tasks with verification (only for Large/Complex)
└── quick/
    # Note: HANDOFF.md is documented in session-handoff.md but does not appear
    # as a node in SKILL.md's .specs/ tree diagram.
    └── NNN-slug/
        ├── TASK.md
        └── SUMMARY.md
```

### STATE.md: ID-based schema

TLC's `STATE.md` uses Markdown with ID-based lists rather than YAML frontmatter:

- **`AD-NNN`** — Architecture Decisions, sequentially numbered
- **`B-NNN`** — Active Blockers
- **`L-NNN`** — Lessons Learned
- **Quick Tasks table** — tabular log of quick-mode completions
- **Deferred Ideas** — scope-creep capture; items are logged here rather than acted upon during implementation
- **Preferences** — persistent agent behavior preferences across sessions

Size governance uses a graduated cleanup zone: below 7,000 tokens no action is taken; between 7,000 and 10,000 tokens a footer note appears ("Cleanup recommended"); above 10,000 tokens the agent surfaces "STATE.md critical. Cleanup now?" Cleanup moves decisions older than 60 days to `STATE-ARCHIVE.md`, retains only active blockers, and preserves lessons from the past 60 days. This 60-day archive policy is explicit in `state-management.md`.

### HANDOFF.md

`HANDOFF.md` sits at `.specs/HANDOFF.md` (not inside a feature folder), giving it project-scope visibility. It is the session checkpoint artifact, targeting approximately 500 tokens, and overwrites the previous version on every session end. It captures: what was Completed, what is In Progress, what is Pending, active Blockers, and Context (current branch, uncommitted files). Unlike GSD's `continue-here.md` which is written by a dedicated `/gsd-pause-work` command, TLC's `HANDOFF.md` is written by the natural-language trigger "pause work / end session."

### CONCERNS.md

`CONCERNS.md` is the project's risk catalog. Categories it tracks: technical debt, known bugs, security issues, performance problems, fragile areas, scaling limits, deprecated dependencies, missing features, test gaps. The critical constraint: every concern entry must include file paths and a fix approach. Concerns without file paths are not actionable. It is loaded on-demand — only when planning features that touch flagged areas, estimating risk, or modifying fragile components.

### TESTING.md

`TESTING.md` is the authority on test infrastructure and parallelism. It contains three sections that serve the task-execution layer:

- **Test Coverage Matrix** — maps feature areas to test types and coverage status
- **Parallelism Assessment** — declares which test types are parallel-safe; this is the source of truth for the `[P]` marker. A task marked `[P]` requires that its tests pass the Parallelism Assessment — "If a task's tests are NOT parallel-safe, it MUST run sequentially even if its implementation code has no dependencies."
- **Gate Check Commands** — the exact CLI commands agents must run to pass each verification gate

---

## 5. Spec Kit: `.specify/` Layout

See also: `../frameworks/adjacent-frameworks.md`

### Directory tree (abbreviated)

```
.specify/
├── memory/
│   └── constitution.md            # project-governing principles (persistent governance)
├── scripts/bash/                  # check-prerequisites, common, create-new-feature,
│                                  # setup-plan, setup-tasks
├── specs/
│   └── 001-create-taskify/        # one folder per numbered feature
│       ├── spec.md
│       ├── plan.md
│       ├── research.md
│       ├── data-model.md
│       ├── quickstart.md
│       ├── contracts/             # api-spec.json, signalr-spec.md, etc.
│       └── tasks.md
├── templates/                     # spec-template.md, plan-template.md, tasks-template.md
│   └── overrides/                 # project-local overrides (priority 1)
├── presets/templates/             # customize HOW Spec Kit works (priority 2)
└── extensions/templates/          # add NEW capabilities (priority 3)
                                   # Spec Kit core defaults are priority 4
```

### memory/constitution.md

`constitution.md` is Spec Kit's persistent governance document. It is written once via `/speckit.constitution` and consulted during every subsequent phase. It captures the principles under which the project operates — not requirements, not architecture, but the meta-rules the AI agent must follow when making decisions within this project. It is the closest Spec Kit comes to GSD's `PROJECT.md` "evolution rules" concept.

### Numbered feature folders

Feature folders are numbered (`001-create-taskify`, `002-add-auth`, …) and tied to a correspondingly numbered git branch. This numbering is the primary traceability mechanism: any git commit, PR, or artifact can be traced to a specific spec folder by its number. The number is assigned at `/speckit.specify` time and never reused.

### Template priority cascade

Templates are resolved at runtime from highest to lowest priority:

1. **Overrides** (`.specify/templates/overrides/`) — project-local, wins over everything
2. **Presets** (`.specify/presets/templates/`) — customize how Spec Kit behaves, can be shared
3. **Extensions** (`.specify/extensions/templates/`) — add new capabilities, also shareable
4. **Core defaults** — Spec Kit's bundled templates, lowest priority

First match wins. When a layer is removed or uninstalled, the next-priority template automatically takes effect. This means customization never requires forking the framework.

---

## 6. OpenSpec: Current-vs-Proposed Model

See also: `../frameworks/adjacent-frameworks.md`

OpenSpec has the most conceptually distinctive storage model of the frameworks studied. Rather than a flat or phase-based layout, it separates current truth from proposed truth at the directory level.

### Structure

```
openspec/
├── specs/                                        # current source of truth
└── changes/
    ├── add-dark-mode/                            # one folder per proposed change
    │   ├── proposal.md                           # why + what's changing
    │   ├── specs/                                # spec deltas only (not full specs)
    │   ├── design.md                             # technical approach
    │   └── tasks.md                              # implementation checklist
    └── archive/
        └── 2025-01-23-add-dark-mode/             # completed, deltas merged back into specs/
```

### How it works

- `openspec/specs/` is the permanent source of truth. It represents what has been implemented and accepted.
- `openspec/changes/<name>/` is a proposed update. The `specs/` subfolder inside a change folder contains only deltas — the parts of the spec that would change, not a full copy.
- When implementation is complete, `/opsx:archive` moves the change folder to `openspec/changes/archive/YYYY-MM-DD-<name>/` and merges the spec deltas back into `openspec/specs/`.

The archive step is the key mechanical insight: specs in `openspec/specs/` stay current automatically. There is no separate "merge PR into main spec" ceremony. The `/opsx:archive` command does it.

### Contrast with GSD's phase-snapshot model

GSD accumulates phase artifacts forward: `01-PLAN.md`, `01-SUMMARY.md`, `01-VERIFICATION.md` are snapshots of what happened during phase 1. They are not deleted or merged; they remain as an audit trail. The current state of the project is represented by reading the most recent artifacts plus `STATE.md`.

OpenSpec's model inverts this: the archive is the audit trail (`changes/archive/`), and `openspec/specs/` is always the clean current truth. The conceptual model is closer to a version-control merge than to a file accumulation. One way to describe it: OpenSpec is a "mini PR inside the spec folder" — propose in a branch-like `changes/` directory, then archive-merge when done. GSD is more like "commit a snapshot and move on."

Neither model is universally superior. GSD's approach makes it easy to audit what happened in a phase; OpenSpec's approach makes it easy to know the current state of a spec without reading a history.

---

## 7. State Schema Comparison

| Dimension | GSD STATE.md | TLC STATE.md |
|---|---|---|
| Format | YAML frontmatter + Markdown body | Markdown with ID-based lists |
| Decisions | `decisions: [...]` YAML array | `AD-NNN` sequentially numbered entries |
| Blockers | `blockers: [...]` YAML array | `B-NNN` sequentially numbered entries |
| Lessons | `metrics: [...]` per-plan (duration, tasks, files) | `L-NNN` lessons with dates |
| Size governance | DEFECT.STATE-TRAMPLE invariant enforced in `state-document.cjs` | 7k/10k graduated zones; 60-day archive policy to `STATE-ARCHIVE.md` |
| Write safety | `STATE.md.lock` with `O_EXCL` + jittered spin-wait + 10s stale-lock timeout | Not addressed in cached docs |
| Session continuity | `stopped-at`, `resume-file` fields + `continue-here.md` handoff artifact | `HANDOFF.md` at `.specs/HANDOFF.md` (~500 tokens, overwrites on each session end) |
| Deferred ideas | Not a dedicated field; captured in `seeds/` folder | `Deferred Ideas` section explicitly in `STATE.md` |
| Scope creep handling | `seeds/` folder for incubating ideas | Deferred Ideas section absorbs in-session scope creep inline |

GSD's write-safety model is more mechanically hardened because multiple subagents can write to `STATE.md` concurrently during wave-based parallel execution. TLC does not face this problem because it does not use subagent parallelism for STATE writes — planning, task creation, and validation reports are always done in the main context without delegation.

---

## 8. Traceability Mechanisms

How each framework links requirements through to implementation:

### GSD

- Requirements are assigned `REQ-IDs` in `REQUIREMENTS.md` with scope markers (`v1`, `v2`, `out-of-scope`).
- Decisions produced by `/gsd-discuss-phase` receive `D-ids` (`D-01`, `D-02`) written into `{phase}-CONTEXT.md`.
- Plan-time gate: every `REQ-ID` must map to at least one plan (requirement coverage gate). Every `D-id` must appear in at least one plan's `must_haves`, `truths`, or body (decision coverage gate — blocking at plan time).
- Verify-time gate: decision coverage is re-checked non-blockingly; misses appear as a warning section in `VERIFICATION.md`.
- Commit IDs use `feat(NN-MM):` Conventional Commit format where `NN` is phase and `MM` is plan number.
- The `plan.must_haves` and `plan.truths` fields in each `PLAN.md` are the explicit traceability joints linking plan decisions back to discuss-phase decisions.

### TLC

- Requirements carry `[CATEGORY]-[NUMBER]` IDs (e.g., `AUTH-01`, `CART-03`) defined in `spec.md`.
- Status states track progress: `Pending → In Design → In Tasks → Implementing → Verified`.
- `spec.md` includes a Requirement Traceability section that tracks X total requirements / Y mapped to tasks / Z unmapped — providing a coverage count visible at a glance.
- Decisions (`AD-NNN`), blockers (`B-NNN`), and lessons (`L-NNN`) in `STATE.md` are ID-referenced from other documents, creating cross-document links.
- Commits use Conventional Commits 1.0.0 format; "one task = one commit" is a hard rule in `implement.md`.

### Spec Kit

- Features are numbered (`001-create-taskify`) and the number carries through: branch name, spec folder name, and task references.
- `/speckit.analyze` cross-checks consistency between `spec.md`, `plan.md`, and `tasks.md` before implementation begins.
- `tasks.md` tasks carry `[P]` markers for explicit machine-readable parallelism.
- `/speckit.taskstoissues` pushes tasks to GitHub Issues, creating a bridge between the spec folder and the project management system. This is the only framework in this study with a native issue-tracker integration built in.

---

## 9. Implications for Our Framework

- **File-based state is the right default**, but state file write safety is non-trivial the moment multiple agents write concurrently. If our framework supports any form of parallelism, adopt a lockfile convention (GSD's `O_EXCL` + jittered spin-wait pattern) from day one rather than retrofitting it.

- **Separate "current truth" from "accumulated history."** OpenSpec's `specs/` vs `changes/` split is the cleanest model for keeping specs readable over time. GSD's phase-snapshot accumulation is better for audit trails. We should decide which we value more — or design a layout that keeps both: a `current/` or `specs/` directory that is always clean, plus a `history/` or `phases/` directory that is the audit trail.

- **Deferred ideas need a home in STATE.md, not a separate folder.** TLC's Deferred Ideas section in `STATE.md` absorbs scope creep at the moment it arises, without creating a new artifact. GSD's `seeds/` folder is lower-friction for ideation but creates a folder that agents have to actively check. For a framework aimed at minimal ceremony, the inline Deferred Ideas section is the simpler choice.

- **Numbered artifacts are worth the discipline.** Spec Kit's numbered feature folders and GSD's `feat(NN-MM):` commit convention both demonstrate that sequential numbering creates durable traceability at low cost. The overhead is one number at creation time; the payoff is stable cross-references across all subsequent artifacts.

- **Template customization should be layered, not forked.** Spec Kit's Overrides → Presets → Extensions → Core cascade is the most maintainable customization model in this study. Framework users should be able to override templates without modifying the core installation. Any framework we build should treat core defaults as the lowest-priority layer so that project-local conventions always win without code changes.

---

*Cross-links:*
- `../frameworks/gsd.md`
- `../frameworks/tlc-spec-driven.md`
- `../frameworks/adjacent-frameworks.md`
- `../frameworks/graphify.md`
- `./context-engineering.md`
- `./self-healing-and-verification.md`
- `./patterns-worth-stealing.md`
