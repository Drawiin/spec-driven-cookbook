# Adjacent Frameworks Research Findings (Raw Cache)

> Sources: Graphify, GitHub Spec Kit, Fission-AI/OpenSpec, eyaltoledano/claude-task-master, bmad-code-org/BMAD-METHOD  
> Cached from: research sub-agent run 2026-05-19  
> Agent ID: ff83e72c-049d-4a6f-8820-ed0a9f107a05  
> Sources cited at end of document.

---

## A. Graphify

### 1. Overview

Graphify is an open-source skill (MIT licensed, by Safi Shamsi, ~49k GitHub stars) that turns any folder of code, docs, PDFs, images, videos, and SQL schemas into a queryable knowledge graph for AI coding assistants. Distributed on PyPI as `graphifyy` (double-y); CLI command remains `graphify`. Python 3.10+. Built on Tree-sitter + NetworkX + Leiden community detection — no vector embeddings. Marketing claim: ~71.5× token reduction vs naive RAG. The user invokes `/graphify .` inside their AI assistant and gets back a structural map they can query instead of grepping. Penpax is a commercial layer built on top.

### 2. Pipeline & Architecture

Multi-stage modular pipeline:

```
detect → extract → build → cluster → analyze → report → export
```

- **detect** — collect files (31 code languages + docs/PDFs/images/video).
- **extract** — Tree-sitter ASTs locally (no LLM on source code) + LLM-driven semantic extraction for prose/diagrams.
- **build** — merge nodes/edges into a NetworkX graph.
- **cluster** — Leiden algorithm for semantic communities (no vector embeddings).
- **analyze** — surface "god nodes" (highest-degree hubs) and "surprising" cross-domain edges.
- **report** — produce `GRAPH_REPORT.md`.
- **export** — `graph.html` (interactive), `graph.json` (queryable), Mermaid call-flow HTML, Obsidian, GraphML, Neo4j cypher, SVG.

Supporting modules: `ingest.py` (URL fetching), `cache.py` (semantic caching), `security.py` (input validation), `watch.py` (live updates), `serve.py` (MCP stdio server). Confidence tags on every relation: `EXTRACTED`, `INFERRED`, `AMBIGUOUS`.

### 3. Local Data Storage

Everything lands in a single per-project directory, designed to be committed to git:

```
graphify-out/
├── graph.html            # interactive vis
├── GRAPH_REPORT.md       # god nodes, surprises, suggested questions
├── graph.json            # canonical queryable graph
├── manifest.json         # mtime-based — recommended .gitignore
├── cost.json             # local-only — recommended .gitignore
├── cache/                # incremental extraction cache
└── converted/            # markdown sidecars for Google Workspace docs
```

Plus a global cross-project graph at `~/.graphify/global.json` (`graphify global add/remove/list`). Ignore patterns via `.graphifyignore` (gitignore syntax with `!` negation). A git merge driver installed via `graphify hook install` so concurrent commits union-merge `graph.json` automatically — no conflict markers ever.

### 4. Integration with AI Assistants

Graphify integrates with **17+ assistants**: Claude Code, Codex, OpenCode, Cursor, Gemini CLI, GitHub Copilot CLI, VS Code Copilot Chat, Aider, OpenClaw, Factory Droid, Trae/Trae CN, Hermes, Kimi Code, Kiro, Pi, Google Antigravity. Each gets a tailored install path (`graphify install --platform <name>` or per-tool subcommand like `graphify cursor install`).

Integration mechanisms:
- **Skill manifests** — per-platform `skill-*.md` files.
- **Persistent instruction files** — writes guidance into `AGENTS.md`, `.cursor/rules/`, `CLAUDE.md`, telling the assistant to prefer `graphify query "…"` over reading raw files.
- **PreToolUse hooks** — on Claude Code and Gemini CLI, fires before search-style tool calls, nudges toward the graph path.
- **MCP server** — `python -m graphify.serve graphify-out/graph.json` exposes: `query_graph`, `get_node`, `get_neighbors`, `shortest_path`, `list_prs`, `get_pr_impact`, `triage_prs`.
- **Slash commands**: `/graphify`, `/graphify query "…"`, `/graphify path "A" "B"`, `/graphify explain "X"`, `/graphify add <url>`. Codex uses `$graphify`; PowerShell uses `graphify .` (no leading slash).
- **Git hooks** — `graphify hook install` adds post-commit/post-checkout hooks for AST-only auto-rebuilds (no LLM cost).

### 5. Notable Patterns Worth Stealing

- **Single-output convention (`graphify-out/`) committed to git** — team-wide artifact reuse, instant ramp-up after `git clone`.
- **Per-tool install/uninstall subcommands** (`graphify cursor install`, `graphify codex uninstall`, `graphify uninstall --purge`) — clean reversibility.
- **Multi-runtime hook strategy** — payload-bearing hooks where supported (Claude, Gemini), fall back to instruction files (`AGENTS.md`, `.cursor/rules/`) where not.
- **Confidence tagging on every inferred relation** (`EXTRACTED` / `INFERRED` / `AMBIGUOUS`) — anti-fabrication built into the data model.
- **Git merge driver for the canonical artifact** — eliminates merge conflicts in shared specs/graphs. Union-merge `graph.json` automatically.
- **`--update` re-extracts only changed files; `--cluster-only` reruns clustering without re-extracting** — cheap incremental rebuilds.
- **Surfacing "god nodes" + "surprising connections"** as a deliberate report section — actively highlights things the human should review.
- **Suggested questions in the report** — gives the human a curated entry point.
- **Token-budget control on queries** (`--budget 1500`) — explicit context-bloat governance.

---

## B. GitHub Spec Kit

### 1. Overview

Open-source toolkit by GitHub for Spec-Driven Development (SDD): specifications become executable, generating implementations rather than scaffolding. Ships as the `specify` CLI (Python, installed via `uv tool install specify-cli`). Greenfield-, brownfield-, and creative-exploration-friendly. Supports 30+ AI agents (Claude Code, Cursor, Copilot, Codex, Gemini, Qwen, opencode, Kiro, Tabnine, and more).

### 2. Workflow & Commands

Slash-command driven. Most agents see `/speckit.*`; Codex CLI in skills mode uses `$speckit-*`.

**Core flow:**
1. `/speckit.constitution` — establish governing principles (writes `.specify/memory/constitution.md`).
2. `/speckit.specify` — define what to build (creates a numbered branch like `001-create-taskify` and `specs/001-create-taskify/spec.md`). Focus on what/why, not stack.
3. `/speckit.clarify` — structured, sequential coverage-based questioning that records answers in a Clarifications section. Recommended before `/plan`.
4. `/speckit.plan` — pick the tech stack; generates `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, and `contracts/`.
5. `/speckit.tasks` — break the plan into ordered, file-scoped tasks with `[P]` parallel markers and TDD ordering.
6. `/speckit.analyze` — cross-artifact consistency & coverage check (run after `/tasks`, before `/implement`).
7. `/speckit.implement` — execute the task list in dependency order.

Optional commands: `/speckit.checklist` (custom quality checklists — "unit tests for English"), `/speckit.taskstoissues` (push tasks to GitHub Issues).

### 3. Artifacts/Storage

```
.specify/
├── memory/
│   └── constitution.md            # project-governing principles
├── scripts/bash/                  # check-prerequisites, common, create-new-feature, setup-plan, setup-tasks
├── specs/
│   └── 001-create-taskify/        # one folder per feature (numbered branch)
│       ├── spec.md
│       ├── plan.md
│       ├── research.md
│       ├── data-model.md
│       ├── quickstart.md
│       ├── contracts/             # api-spec.json, signalr-spec.md, etc.
│       └── tasks.md               # ordered, dependency-aware, with [P] markers
├── templates/                     # spec-template.md, plan-template.md, tasks-template.md
│   └── overrides/                 # project-local overrides (priority 1)
├── presets/templates/             # customize HOW Spec Kit works (priority 2)
└── extensions/templates/          # add NEW capabilities (priority 3)
                                   # Spec Kit core defaults are priority 4
```

Templates resolved runtime top-down; first match wins. Extension/preset commands written into agent dirs at install time. On uninstall, the next-priority version automatically restored.

### 4. Notable Patterns Worth Stealing

- **Explicit constitution as a separate artifact** — persistent governance document consulted during every phase.
- **Phase gate with `/speckit.clarify`** — forces sequential coverage questioning before planning. Structured "ask one focused question" loop.
- **`/speckit.analyze`** — cross-artifact consistency check (spec ↔ plan ↔ tasks). Built-in pre-code validation.
- **Numbered feature branch tied to numbered spec folder** (`001-create-taskify`) — traceable end-to-end.
- **`[P]` parallel-execution markers in `tasks.md`** — explicit, machine-readable parallelism hints.
- **Overrides → Presets → Extensions → Core priority cascade** — clean customization without forking the framework.
- **`/speckit.taskstoissues`** — bridges spec artifacts into GitHub project management.
- **Skills mode toggle** (`--integration-options="--skills"`) — same flow, two runtime delivery formats (slash commands vs agent skills).
- **`/speckit.checklist` ("unit tests for English")** — generates checklists that validate the spec itself, not the code.

---

## C. OpenSpec (Fission-AI/OpenSpec)

### 1. Overview

"The most loved spec framework" — lightweight, brownfield-first SDD by Fission-AI. Distributed via npm: `npm install -g @fission-ai/openspec@latest` (Node 20.19+). Works with 25+ AI tools via slash commands. Philosophy: **fluid not rigid, iterative not waterfall, easy not complex, brownfield over greenfield, no hard phase gates**. Pitched explicitly against Spec Kit ("thorough but heavyweight, rigid phase gates, lots of Markdown, Python setup") and Kiro ("locked into their IDE and Claude").

### 2. Workflow & Commands

Lighter-weight, artifact-guided. New `/opsx:*` workflow:

- `/opsx:propose <idea>` — AI generates a change folder containing `proposal.md`, `specs/`, `design.md`, `tasks.md`.
- `/opsx:apply` — execute the tasks (incremental, with checklist updates).
- `/opsx:archive` — move completed change to `openspec/changes/archive/YYYY-MM-DD-<name>/` and merge updates back into source-of-truth specs.

Expanded profile adds: `/opsx:new`, `/opsx:continue`, `/opsx:ff` (fast-forward), `/opsx:verify`, `/opsx:bulk-archive`, `/opsx:onboard`.

**Key conceptual model:** separate **current truth** from **proposed truth**.
- `openspec/specs/` — current source-of-truth specs.
- `openspec/changes/<name>/` — proposed updates (proposal + spec deltas + design + tasks).
- After implementation, `archive` merges deltas into `openspec/specs/`.

### 3. Artifacts/Storage

```
openspec/
├── specs/                                        # current source of truth
└── changes/
    ├── add-dark-mode/
    │   ├── proposal.md                           # why + what's changing
    │   ├── specs/                                # spec deltas only
    │   ├── design.md                             # technical approach
    │   └── tasks.md                              # implementation checklist
    └── archive/
        └── 2025-01-23-add-dark-mode/             # archived, merged into specs/
```

Telemetry: anonymous command-name + version only. Opt-out via `OPENSPEC_TELEMETRY=0` or `DO_NOT_TRACK=1`.

### 4. Notable Patterns Worth Stealing

- **Current-vs-proposed separation** — `specs/` (truth) vs `changes/` (proposed deltas). Mini PR/branch model inside the spec folder.
- **Archive step that merges spec deltas back into source-of-truth** — automated reconciliation. Specs stay current without manual hygiene.
- **Profiles as workflow tiers** (default minimal vs expanded with `verify`, `ff`, `onboard`) — opt into ceremony only when needed.
- **No phase gates** — any artifact can be edited at any time. Pragmatic counter to Spec Kit's strictness.
- **Explicit `/opsx:onboard`** for ramp-up of an AI agent into an existing project.
- **Community schemas** — third-party schema bundles in standalone repos.
- **Hard requirement: "OpenSpec works best with high-reasoning models. Recommend Opus 4.5 and GPT 5.2"** — explicit model-quality expectations documented as a usage note.

---

## D. Task Master (eyaltoledano/claude-task-master)

### 1. Overview

Task Master (`task-master-ai` on npm, ~26k stars) is an MCP-server-based task-management system. Built by Eyal Toledano + Crunchyman-ralph. Drops into Cursor 1.0+, Windsurf, VS Code, Claude Code, Q CLI, Roo, Lovable, etc. via MCP server config. Multi-provider: Anthropic, OpenAI, Gemini, Perplexity, xAI, OpenRouter, Mistral, Groq, Azure OpenAI, Ollama, plus zero-API-key paths via Claude Code CLI or Codex CLI OAuth. Now part of Hamster (docs at `tryhamster.com/docs/taskmaster`).

### 2. Workflow & Commands

Decomposition-first, PRD-driven:

1. Author a PRD at `.taskmaster/docs/prd.txt`.
2. `parse-prd <prd.txt>` — generate the initial task list.
3. Three-tier model config: **main**, **research**, **fallback**.
4. `next` / `show <id>` / `expand <id>` (decompose into subtasks) / `set-status` / `update-subtask` / `add-task` / `remove-task` / `complexity-report` / `analyze-project-complexity`.
5. **Tags & workstreams** — tasks belong to tags; cross-tag movement supported.
6. **Research command** — first-class `task-master research "…"` with project context (via Perplexity or similar).
7. **Loop command** — automation primitive for autonomous task execution.

**Tool-loading tiers (the unique part for context budgeting):**

| Mode | Tools | ~Token Cost |
|---|---|---|
| `all` (default) | 36 | ~21,000 |
| `standard` | 15 | ~10,000 |
| `core` / `lean` | 7 | ~5,000 |
| `custom` | comma-separated | variable |

Configured via `TASK_MASTER_TOOLS` env var in the MCP config. Core 7 = `get_tasks, next_task, get_task, set_task_status, update_subtask, parse_prd, expand_task`.

### 3. Artifacts/Storage

```
.taskmaster/
├── docs/
│   └── prd.txt                  # source PRD
├── templates/
│   └── example_prd.txt
└── tasks/                       # generated task files
```

Plus per-editor MCP config at `~/.cursor/mcp.json`, `~/.codeium/windsurf/mcp_config.json`, `.vscode/mcp.json`, etc. Rules added post-init: `task-master rules add cursor,windsurf,roo,vscode`.

### 4. Notable Patterns Worth Stealing

- **Tiered tool-loading via env var** (`TASK_MASTER_TOOLS=core|standard|all|custom`) — explicit, measured (~5k vs ~21k tokens) governance of MCP context bloat. Best-documented "tool budget" knob in this landscape.
- **Three-role model config**: `main` / `research` / `fallback` — different models for different jobs in the same workflow.
- **First-class `research` command with project-context grounding** — uses Perplexity / live web with repo as context, separate from implementation model.
- **Tags as task-level branches** (`--from-tag=backlog --to-tag=in-progress --with-dependencies`) — workstream isolation without git ceremony.
- **`expand_task` as an explicit decomposition primitive** — task → subtasks is a named operation.
- **`complexity-report` / `analyze-project-complexity`** — surface a complexity signal before committing to a plan.
- **Zero-API-key path via Claude Code CLI / Codex CLI OAuth** — uses existing IDE auth, no new key management.
- **Loop command** — named primitive for autonomous multi-task execution.
- **MIT + Commons Clause** licensing — "you may not resell or host as a service."

---

## E. BMAD-METHOD (brief)

### 1. Overview & key idea

**BMAD** = "Breakthrough Method for Agile AI-Driven Development." MIT-licensed (~47k stars on `bmad-code-org/BMAD-METHOD`), Node 20.12+ / Python 3.10+ / uv. Installed via `npx bmad-method install`. Key idea: a **multi-agent agile framework** that swaps "the AI does the thinking for you" for "12+ specialized expert agents (PM, Architect, Developer, UX, Scrum Master, Analyst, …) that facilitate *your* thinking through a structured agile workflow." Two distinguishing primitives:
- **Scale-adaptive intelligence** — adjusts planning depth automatically based on project complexity.
- **Party Mode** — multiple agent personas collaborate in one session.

Splits planning agents (Analyst, PM, Architect produce PRDs and architecture docs) from execution agents (Scrum Master converts plans into hyper-detailed stories with embedded context; Developer implements). V6 adds Skills Architecture, sub-agents, Story Automator, and Dev Loop Automation. Module ecosystem: BMM (core, 34+ workflows), BMB (build your own agents), TEA (Test Architect), BMGD (game dev), CIS (creative intelligence). Help system: invoke `bmad-help` skill anytime.

### 2. Notable Patterns Worth Stealing

- **Scale-adaptive depth** — framework auto-adjusts ceremony based on detected complexity.
- **Persona separation between planning and execution agents** — context relevant for design is not loaded for implementation, and vice versa.
- **Hyper-detailed stories with embedded context** — Scrum Master agent's output is engineered so the developer agent doesn't need to re-fetch the architecture; context is pre-baked at handoff.
- **`bmad-help` skill as a built-in self-discovery primitive** — instead of docs, the framework can answer "what should I do next?" itself.
- **Module ecosystem with separate repos** (BMM/BMB/TEA/BMGD/CIS) — domain-specific extensions are independent installables.
- **Party Mode** — explicit multi-persona collaboration in a single session.
- **Story Automator (v6.6+)** — automates spec creation → implementation → test automation → code review → retro across multiple stories with complexity assessment driving agent selection.
- **Non-interactive install with `--set <module>.<key>=<value>`** for CI/CD — every module config option overridable from the command line. Strong reproducibility.

---

## F. Quick Comparative Table

| Dimension | Graphify | Spec Kit | OpenSpec | Task Master | BMAD-METHOD |
|---|---|---|---|---|---|
| Core abstraction | Knowledge graph (nodes + communities) | Specs + phases + constitution | Spec deltas (current vs proposed) | Tasks + subtasks + tags | Specialized agents + agile workflows |
| Primary artifact | `graph.json` + `GRAPH_REPORT.md` | `specs/NNN-feature/spec.md`, `plan.md`, `tasks.md` | `openspec/specs/` + `openspec/changes/` | `.taskmaster/tasks/` (PRD-derived) | PRDs, architecture docs, stories |
| Greenfield vs brownfield | Both (excels at brownfield) | Both | Brownfield-first | Both (PRD-driven) | Both (scale-adaptive) |
| Context-bloat handling | Scoped graph queries; `--budget N` token caps | Phase-scoped artifacts; `[P]` markers | Profiles; minimal vs expanded | Tiered tool loading (`TASK_MASTER_TOOLS`) ~5k vs ~21k tokens | Persona separation; pre-baked story context |
| Sub-agent / parallelism | N/A | `[P]` task markers | `/opsx:bulk-archive`; expanded profile | `expand_task`; tags as workstreams | 12+ specialized agents; sub-agents in V6; Party Mode |
| Self-healing / verification | Confidence tags (`EXTRACTED/INFERRED/AMBIGUOUS`); git merge-driver | `/speckit.clarify`, `/speckit.analyze`, `/speckit.checklist` | `/opsx:verify`; archive merges deltas | `complexity-report`; fallback model | Multiple agent reviews; TEA module; retro phase |
| Local artifact layout | `graphify-out/` (committed) + `~/.graphify/global.json` | `.specify/{memory,specs,scripts,templates,presets,extensions}/` | `openspec/{specs,changes,archive}/` | `.taskmaster/{docs,tasks,templates}/` | Module-installed agent files in IDE config dirs |
| Multi-runtime support | 17+ assistants; per-platform install + uninstall; PreToolUse hooks where supported | 30+ agents; slash commands or skills mode | 25+ tools; slash commands | MCP server (Cursor / Windsurf / VS Code / Claude Code / Q CLI) | Claude Code, Cursor via `bmad-method install` |
| License | MIT | MIT | MIT | MIT + Commons Clause | MIT |

---

## G. Sources Cited

Fetched successfully:
- `https://graphify.net/` — Graphify landing page
- `https://github.com/safishamsi/graphify` — Graphify GitHub repo
- `https://raw.githubusercontent.com/github/spec-kit/main/README.md` — Spec Kit README
- `https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/README.md` — OpenSpec README
- `https://raw.githubusercontent.com/eyaltoledano/claude-task-master/main/README.md` — Task Master README
- `https://github.com/bmad-code-org/BMAD-METHOD` — BMAD repo metadata
- `https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/README.md` — BMAD README

Web searches used as secondary context (not primary citations):
- "graphify knowledge graph AI coding github safishamsi"
- "OpenSpec AI coding spec-driven github"
- "eyaltoledano claude-task-master github"
- "BMAD-METHOD bmadcode github AI agent framework"

Initial fetch that timed out (later retried): `https://raw.githubusercontent.com/bmadcode/BMAD-METHOD/main/README.md` — the active org is `bmad-code-org`, not `bmadcode`.

**No fabricated claims.** Where search snippet conflicted with primary README content, the README/repo metadata took precedence.

**Note on aider, sweep, devin:** None are spec-driven frameworks in the sense the other five are. Aider is an in-terminal pair-programming agent (no spec abstraction), Sweep was a GitHub-issue-to-PR bot (now sunset/pivoted), Devin is a closed-source autonomous coding agent product. None contribute distinctive spec-driven patterns.
