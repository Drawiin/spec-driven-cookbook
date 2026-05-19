# Adjacent Frameworks

This file surveys four frameworks that informed the broader spec-driven landscape: GitHub Spec Kit, OpenSpec, Task Master, and BMAD-METHOD. They were analyzed less deeply than [GSD](./gsd.md) and [TLC](./tlc-spec-driven.md) but each contributes transferable patterns. Graphify, a knowledge-graph-oriented companion tool, has its own file at [./graphify.md](./graphify.md).

---

## 1. GitHub Spec Kit

### Overview

Spec Kit is an open-source toolkit by GitHub for Spec-Driven Development (SDD): specifications become executable, generating implementations rather than scaffolding. It ships as the `specify` CLI (Python, installed via `uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@vX.Y.Z`) and supports 30+ AI agents including Claude Code, Cursor, Copilot, Codex, Gemini, Qwen, opencode, Kiro, and Tabnine. It is greenfield-, brownfield-, and creative-exploration-friendly. Slash commands are the primary interface; most agents see `/speckit.*` while Codex CLI in skills mode uses `$speckit-*`.

### Core Workflow Commands

| Command | What it does | Artifacts produced |
|---|---|---|
| `/speckit.constitution` | Establish governing principles for the project | `.specify/memory/constitution.md` |
| `/speckit.specify` | Define what to build (what/why, not the stack) | Numbered branch `NNN-feature-name`; `specs/NNN-feature-name/spec.md` |
| `/speckit.clarify` | Sequential, coverage-based questioning loop before planning | Clarifications section appended to `spec.md` |
| `/speckit.plan` | Pick the tech stack; generate the planning artifact suite | `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, `contracts/` |
| `/speckit.tasks` | Break the plan into ordered, file-scoped tasks | `tasks.md` with `[P]` parallel markers and TDD ordering |
| `/speckit.analyze` | Cross-artifact consistency and coverage check | Analysis report (run after `/tasks`, before `/implement`) |
| `/speckit.implement` | Execute the task list in dependency order | Working implementation |
| `/speckit.checklist` | Generate quality checklists for the spec itself | Custom checklist artifact ("unit tests for English") |
| `/speckit.taskstoissues` | Push tasks to GitHub Issues | GitHub Issues created from `tasks.md` |

### Artifacts and Storage Layout

```
.specify/
├── memory/
│   └── constitution.md              # project-governing principles
├── scripts/bash/                    # check-prerequisites, common, create-new-feature, setup-plan, setup-tasks
├── specs/
│   └── 001-create-taskify/          # one folder per feature (numbered branch)
│       ├── spec.md
│       ├── plan.md
│       ├── research.md
│       ├── data-model.md
│       ├── quickstart.md
│       ├── contracts/               # api-spec.json, signalr-spec.md, etc.
│       └── tasks.md                 # ordered, dependency-aware, with [P] markers
├── templates/                       # spec-template.md, plan-template.md, tasks-template.md
│   └── overrides/                   # project-local overrides — priority 1
├── presets/templates/               # customize HOW Spec Kit works — priority 2
└── extensions/templates/            # add NEW capabilities — priority 3
                                     # Spec Kit core defaults are priority 4
```

Templates are resolved top-down at runtime; first match wins. Extension and preset commands are written into agent directories at install time. On uninstall, the next-priority version is automatically restored.

### Template Priority Cascade

Overrides (1) → Presets (2) → Extensions (3) → Core defaults (4). Project-local customization never requires forking the framework.

### Notable Patterns

- **Explicit constitution as a separate artifact.** A persistent governance document in `.specify/memory/constitution.md` is consulted during every phase, not just at project start.
- **Phase gate with `/speckit.clarify`.** Forces a sequential, coverage-based questioning loop before planning begins. Structures the "ask one focused question at a time" discipline into the workflow rather than relying on ad-hoc prompting.
- **`/speckit.analyze` cross-artifact consistency check.** Validates spec ↔ plan ↔ tasks coherence before any code is written. A built-in pre-implementation validation layer. See also [../topics/workflow-and-orchestration.md](../topics/workflow-and-orchestration.md).
- **Numbered feature branch tied to numbered spec folder.** `001-create-taskify` branch and `.specify/specs/001-create-taskify/` folder are created together, giving end-to-end traceability from decision to artifact to code.
- **`[P]` parallel-execution markers in `tasks.md`.** Explicit, machine-readable parallelism hints embedded in the task list itself, enabling orchestrators to identify safe concurrent work without re-analyzing dependencies.
- **Skills mode toggle.** `--integration-options="--skills"` delivers the same workflow in two runtime formats: slash commands or agent skills, depending on the target assistant's capability.

---

## 2. OpenSpec (Fission-AI)

### Overview

OpenSpec is a lightweight, brownfield-first SDD framework by Fission-AI ("the most loved spec framework" — OpenSpec README). Distributed via npm: `npm install -g @fission-ai/openspec@latest` (Node 20.19+). Works with 25+ AI tools via slash commands.

Its philosophy stands in explicit contrast to Spec Kit: fluid not rigid, iterative not waterfall, easy not complex, brownfield over greenfield, no hard phase gates. The README positions it against Spec Kit ("thorough but heavyweight, rigid phase gates, lots of Markdown, Python setup") and Kiro ("locked into their IDE and Claude"). The primary design decision is separating **current truth** from **proposed truth** within the spec folder itself — a mini branch model inside the repository.

### Core Workflow Commands

| Command | What it does |
|---|---|
| `/opsx:propose <idea>` | AI generates a change folder: `proposal.md`, `specs/` deltas, `design.md`, `tasks.md` |
| `/opsx:apply` | Execute the tasks incrementally, with checklist updates |
| `/opsx:archive` | Move a completed change to `openspec/changes/archive/YYYY-MM-DD-<name>/`; merge spec deltas back into `openspec/specs/` |

Expanded profile adds: `/opsx:new`, `/opsx:continue`, `/opsx:ff` (fast-forward), `/opsx:verify`, `/opsx:bulk-archive`, `/opsx:onboard`.

### The Current-vs-Proposed Conceptual Model

OpenSpec separates two distinct states of knowledge:

- `openspec/specs/` — the **current source-of-truth** specs, reflecting what is actually implemented.
- `openspec/changes/<name>/` — **proposed truth**: spec deltas, design decisions, and tasks for a change that has not yet been merged back.

After implementation, `/opsx:archive` merges the deltas back into `openspec/specs/`, keeping the source-of-truth current without manual hygiene. This is analogous to a pull request model applied to the spec layer rather than the code layer.

### Artifacts and Storage Layout

```
openspec/
├── specs/                                        # current source of truth
└── changes/
    ├── add-dark-mode/
    │   ├── proposal.md                           # why + what is changing
    │   ├── specs/                                # spec deltas only
    │   ├── design.md                             # technical approach
    │   └── tasks.md                              # implementation checklist
    └── archive/
        └── 2025-01-23-add-dark-mode/             # archived, merged into specs/
```

Telemetry is anonymous (command name + version only) and can be disabled via `OPENSPEC_TELEMETRY=0` or `DO_NOT_TRACK=1`.

### Notable Patterns

- **Current-vs-proposed separation.** `specs/` holds truth; `changes/` holds proposed deltas. The split eliminates ambiguity about what is implemented vs what is planned, and is conceptually portable to any framework. Relevant to [../topics/workflow-and-orchestration.md](../topics/workflow-and-orchestration.md).
- **Archive step with automatic spec reconciliation.** `/opsx:archive` merges deltas back into the source-of-truth `specs/` folder automatically. No manual merge step, no stale specs.
- **Profiles as workflow tiers.** The default profile is minimal; the expanded profile adds ceremony (`/opsx:verify`, `/opsx:onboard`, etc.) only when opted into. This avoids forcing overhead on every change.
- **No phase gates.** Any artifact can be edited at any time. An explicit, documented counter-position to Spec Kit's ordered phase progression. Useful for teams that need to iterate on specs concurrently with implementation.
- **`/opsx:onboard` as an explicit AI agent ramp-up command.** Provides a named entry point for orienting a fresh AI session into an existing project's spec state, rather than relying on implicit context loading.
- **Hard model-quality expectation documented as a usage note.** "OpenSpec works best with high-reasoning models. Recommend Opus 4.5 and GPT 5.2." [unverified — model version names from README; version strings may be aspirational] Explicit documentation of capability dependencies is a pattern worth adopting regardless of the specific models named.

---

## 3. Task Master (claude-task-master)

### Overview

Task Master (`task-master-ai` on npm, ~26k stars [unverified]) is an MCP-server-based task-management system built by Eyal Toledano and Crunchyman-ralph. It integrates into Cursor 1.0+, Windsurf, VS Code, Claude Code, Q CLI, Roo, Lovable, and others via MCP server configuration. It is multi-provider: Anthropic, OpenAI, Gemini, Perplexity, xAI, OpenRouter, Mistral, Groq, Azure OpenAI, Ollama, and zero-API-key paths via Claude Code CLI or Codex CLI OAuth. Task Master is now part of Hamster (docs at `tryhamster.com/docs/taskmaster`).

The workflow is PRD-driven and decomposition-first: a PRD drives an initial task list, which is progressively expanded into subtasks, with complexity analysis available before committing to a plan.

### Core Workflow

1. Author a PRD at `.taskmaster/docs/prd.txt`.
2. `parse-prd <prd.txt>` — generate the initial task list.
3. Use `expand <id>` to decompose any task into subtasks; `complexity-report` and `analyze-project-complexity` to surface complexity signals.
4. `next` — fetch the next actionable task; `show <id>` — inspect a specific task.
5. `set-status`, `update-subtask`, `add-task`, `remove-task` — lifecycle management.
6. Tags and workstreams — tasks belong to tags; cross-tag movement is supported (`--from-tag=backlog --to-tag=in-progress --with-dependencies`).
7. `task-master research "…"` — first-class research command grounded in project context (via Perplexity or similar), separate from the implementation model.
8. `loop` — automation primitive for autonomous multi-task execution.

### Tiered Tool Loading

This is Task Master's standout design pattern for context budgeting. The number of MCP tools exposed to the agent is configurable, with a measured impact on token consumption per session:

| Mode | Tools exposed | Approximate token cost |
|---|---|---|
| `all` (default) | 36 | ~21,000 |
| `standard` | 15 | ~10,000 |
| `core` / `lean` | 7 | ~5,000 |
| `custom` | comma-separated list | variable |

Configured via the `TASK_MASTER_TOOLS` environment variable in the MCP config. The core 7 tools are: `get_tasks`, `next_task`, `get_task`, `set_task_status`, `update_subtask`, `parse_prd`, `expand_task`.

This is the most explicit and measurable "tool budget" knob in the frameworks surveyed. See [../topics/context-engineering.md](../topics/context-engineering.md) for the broader context-bloat problem this addresses.

### Three-Role Model Configuration

Task Master separates model responsibilities across three named roles, all configurable independently:

- **main** — primary implementation reasoning.
- **research** — web-grounded research queries (Perplexity or equivalent).
- **fallback** — used when the main model is unavailable or rate-limited.

This makes it explicit that different operations in the same workflow have different model requirements. The research role in particular uses a separate provider with live web access, grounded against the project's own task context.

### Artifacts and Storage Layout

```
.taskmaster/
├── docs/
│   └── prd.txt                  # source PRD
├── templates/
│   └── example_prd.txt
└── tasks/                       # generated task files
```

Per-editor MCP configuration at `~/.cursor/mcp.json`, `~/.codeium/windsurf/mcp_config.json`, `.vscode/mcp.json`, etc. Rules are added after initialization via `task-master rules add cursor,windsurf,roo,vscode`.

### Notable Patterns

- **Tiered tool loading via env var.** `TASK_MASTER_TOOLS=core|standard|all|custom` is the best-documented, explicitly measured "tool budget" governance knob in this landscape. The ~4× token difference between `core` and `all` makes the trade-off concrete. See [../topics/context-engineering.md](../topics/context-engineering.md).
- **Three-role model config.** `main` / `research` / `fallback` separates concerns at the model-selection level rather than requiring one model to handle all operation types with equal cost.
- **First-class `research` command.** A named, provider-backed research operation with project context is separated from implementation, rather than ad-hoc web searching mixed into the coding model's context.
- **Tags as task-level workstream branches.** Cross-tag task movement with dependency tracking gives workstream isolation without requiring git branch ceremony. Relevant to [../topics/workflow-and-orchestration.md](../topics/workflow-and-orchestration.md).
- **`expand_task` as an explicit decomposition primitive.** Making "task to subtasks" a named, callable operation — rather than an implicit LLM behavior — is a pattern worth preserving in any orchestration design.
- **`complexity-report` before planning.** Surface a complexity signal before committing to a plan. This is a pre-work gate analogous to Spec Kit's `/speckit.analyze`, applied at the task level rather than the artifact level.
- **Zero-API-key path via IDE OAuth.** Uses existing Claude Code CLI or Codex CLI authentication — no additional key management for teams already authenticated to those platforms.

---

## 4. BMAD-METHOD

### Overview

BMAD ("Breakthrough Method for Agile AI-Driven Development") is an MIT-licensed multi-agent agile framework (~47k stars [unverified]) on `bmad-code-org/BMAD-METHOD`. Node 20.12+ / Python 3.10+ / uv; installed via `npx bmad-method install`.

The core design premise inverts the common AI-tool dynamic: instead of "AI does the thinking for you," BMAD provides 12+ specialized expert agent personas (PM, Architect, Developer, UX Expert, Scrum Master, Analyst, and others) that facilitate the human's thinking through a structured agile workflow. Two architectural primitives distinguish it:

- **Scale-adaptive intelligence** — planning depth adjusts automatically based on detected project complexity.
- **Party Mode** — multiple agent personas collaborate in a single session.

BMAD splits its agents into two explicit tiers. Planning agents (Analyst, PM, Architect) produce PRDs and architecture docs. Execution agents — primarily the Scrum Master — convert those plans into hyper-detailed stories with all required context pre-baked, so the Developer agent can implement without needing to re-fetch architecture.

### Story Automator (v6.6+)

The Story Automator automates the full cycle end-to-end: spec creation → implementation → test automation → code review → retrospective, across multiple stories. Complexity assessment drives which agents are selected for each story. This is a named, installable automation primitive rather than an emergent behavior from chaining prompts. `[unverified — Story Automator and v6.6+ version number not confirmed in the live BMAD README landing page; sourced from cache only]`

### Module Ecosystem

BMAD distributes domain-specific extensions as independent installable modules:

| Module | Scope |
|---|---|
| BMM | Core framework, 34+ workflows |
| BMB | Build Your Own Agents toolkit |
| TEA | Test Architect module |
| BMGD | Game development extension |
| CIS | Creative Intelligence Suite |

### `bmad-help` as Self-Discovery Primitive

Rather than requiring users to consult external documentation, BMAD exposes a `bmad-help` skill that can answer "what should I do next?" from within the agent session. The framework documents itself via an invokable skill rather than a static README section.

### Artifacts and Storage

Agent persona files and workflow configurations are installed into IDE config directories by `npx bmad-method install`. Non-interactive installation is supported with `--set <module>.<key>=<value>` for CI/CD reproducibility.

### Notable Patterns

- **Scale-adaptive depth.** Framework auto-adjusts ceremony based on detected complexity. Small changes do not pay the overhead of a full agile workflow; large projects get the full planning suite. Related to [../topics/workflow-and-orchestration.md](../topics/workflow-and-orchestration.md).
- **Persona separation between planning and execution agents.** Context relevant for design is not loaded during implementation, and vice versa. This is an architectural approach to the context-bloat problem. See [../topics/context-engineering.md](../topics/context-engineering.md).
- **Hyper-detailed stories with embedded context.** The Scrum Master agent's output is engineered so the Developer agent has everything it needs in the story artifact itself. Context is pre-baked at handoff rather than re-fetched at implementation time.
- **`bmad-help` as a built-in self-discovery primitive.** The framework answers "what should I do next?" as an invokable operation. This pattern is applicable to any framework that accumulates enough commands to warrant it. See [../topics/patterns-worth-stealing.md](../topics/patterns-worth-stealing.md).
- **Module ecosystem with independent installable repos.** Domain-specific extensions (TEA, BMGD, CIS) are standalone; teams adopt only what applies. This scales the framework's reach without bloating the core install.
- **Party Mode.** Explicit support for multi-persona collaboration in a single session — multiple agents with distinct roles coordinating on the same problem. The framework names and exposes this as a capability rather than leaving it as an emergent prompt-engineering pattern.
- **Story Automator (v6.6+) `[unverified]`.** End-to-end automation of the spec-to-retro cycle with per-story complexity assessment. A named automation primitive, not an ad-hoc script.
- **Non-interactive install with `--set <module>.<key>=<value>`.** Every module configuration option is overridable from the command line. Enables reproducible CI/CD setup without interactive prompts.

---

## 5. Quick Comparison Table

The table below reproduces the comparative summary from the research cache. Graphify is included for completeness; see [./graphify.md](./graphify.md) for its full analysis.

| Dimension | Graphify | Spec Kit | OpenSpec | Task Master | BMAD-METHOD |
|---|---|---|---|---|---|
| Core abstraction | Knowledge graph (nodes + communities) | Specs + phases + constitution | Spec deltas (current vs proposed) | Tasks + subtasks + tags | Specialized agents + agile workflows |
| Primary artifact | `graph.json` + `GRAPH_REPORT.md` | `specs/NNN-feature/spec.md`, `plan.md`, `tasks.md` | `openspec/specs/` + `openspec/changes/` | `.taskmaster/tasks/` (PRD-derived) | PRDs, architecture docs, stories |
| Greenfield vs brownfield | Both (excels at brownfield) | Both | Brownfield-first | Both (PRD-driven) | Both (scale-adaptive) |
| Context-bloat handling | Scoped graph queries; `--budget N` token caps | Phase-scoped artifacts; `[P]` markers | Profiles; minimal vs expanded | Tiered tool loading (`TASK_MASTER_TOOLS`) ~5k vs ~21k tokens | Persona separation; pre-baked story context |
| Sub-agent / parallelism | N/A | `[P]` task markers | `/opsx:bulk-archive`; expanded profile | `expand_task`; tags as workstreams | 12+ specialized agents; sub-agents in V6; Party Mode |
| Self-healing / verification | Confidence tags (`EXTRACTED/INFERRED/AMBIGUOUS`); git merge-driver | `/speckit.clarify`, `/speckit.analyze`, `/speckit.checklist` | `/opsx:verify`; archive merges deltas | `complexity-report`; fallback model | Multiple agent reviews; TEA module; retro phase |
| Local artifact layout | `graphify-out/` (committed) + `~/.graphify/global.json` | `.specify/{memory,specs,scripts,templates,presets,extensions}/` | `openspec/{specs,changes,archive}/` | `.taskmaster/{docs,tasks,templates}/` | Module-installed agent files in IDE config dirs |
| Multi-runtime support | 17+ assistants; per-platform install + uninstall; PreToolUse hooks where supported | 30+ agents; slash commands or skills mode | 25+ tools; slash commands | MCP server (Cursor / Windsurf / VS Code / Claude Code / Q CLI) | Claude Code, Cursor via `npx bmad-method install` |
| License | MIT | MIT | MIT | MIT + Commons Clause | MIT |

> Graphify column is a summary only. Full analysis at [./graphify.md](./graphify.md).

---

## Cross-links

- Deeper framework comparisons: [./gsd.md](./gsd.md) and [./tlc-spec-driven.md](./tlc-spec-driven.md)
- Context-bloat and tool-budget patterns: [../topics/context-engineering.md](../topics/context-engineering.md)
- Workflow and orchestration patterns: [../topics/workflow-and-orchestration.md](../topics/workflow-and-orchestration.md)
- Distilled patterns worth adopting: [../topics/patterns-worth-stealing.md](../topics/patterns-worth-stealing.md)
