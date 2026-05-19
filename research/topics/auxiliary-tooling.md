# Auxiliary Tooling

The range of auxiliary tooling across spec-driven frameworks spans from "pure markdown, no
binaries" (TLC) to a 469KB monolithic Node.js installer plus a full TypeScript SDK (GSD).
This file catalogs what each framework ships, why each choice was made, and what the
patterns imply for a new framework's tooling strategy. Cross-framework signals on supply-chain
defense, runtime hooks, and lint infrastructure are covered in dedicated sections.

---

## 1. Overview

Auxiliary tooling decisions are one of the most differentiating axes across this landscape.
GSD ships a compiled CLI (`gsd-tools.cjs`), a typed TypeScript SDK, 13 hook files (12 functional entry points — `gsd-check-update-worker.js` is a supporting worker), 23+
CI/lint scripts, and a monolithic installer that handles 15+ target runtimes. TLC ships zero
executables — it is a markdown skill that the agent loads from a known path, and delegates
external tool needs to a small set of named MCP servers and peer skills. The other frameworks
(OpenSpec, Spec Kit, Task Master, BMAD) fall between these poles, each making distinct
trade-offs between distribution simplicity and capability depth.

---

## 2. Installers and Distribution Mechanisms

### GSD

Entry point: `npx get-shit-done-cc@latest`

`bin/install.js` (~469KB, ~10,700 lines) is the entire distribution mechanism in a single
Node.js file. It handles:

- Runtime detection (15+ targets: Claude Code, OpenCode, Gemini CLI, Kilo, Codex, Copilot,
  Cursor, Windsurf, Antigravity, Augment, Trae, Qwen Code, Hermes, CodeBuddy, Cline)
- Location selection (global `~/.runtime/` vs local `./.<runtime>/`)
- File deployment with per-runtime content transformation (tool-name mapping, hook event
  names, agent frontmatter format, skill placement conventions)
- Path normalization including Windows EPERM/EACCES protection and WSL detection
- Settings integration (writes into each runtime's `settings.json` or equivalent)
- Patch backup: locally modified files written to `gsd-local-patches/` so
  `/gsd-update --reapply` can restore them
- Manifest tracking: `gsd-file-manifest.json` for clean `--uninstall`
- Idempotent `--uninstall` mode: removes only files the installer placed

The **Installer Migration Module** (ADR-0008) layers on top: it handles file renames, stale
artifact cleanup, config rewrites, and user-data preservation across version upgrades.

Platform notes: `windowsHide` on child processes; retry-and-fallback on EPERM/EBUSY/EACCES;
`CLAUDE_CONFIG_DIR` env var for Docker/CI.

### OpenSpec

`npm install -g @fission-ai/openspec@latest` (Node 20.19+). `openspec update` refreshes
agent instructions. Lightweight by design — philosophy is "fluid not rigid."

### Spec Kit

`uv tool install specify-cli` (Python). Multi-runtime managed via `specify integration list`.
Scripts live at `.specify/scripts/bash/` (check-prerequisites, common, create-new-feature,
setup-plan, setup-tasks).

### Task Master

`npm install -g task-master-ai`. Post-install, per-editor MCP config files are written via
`task-master rules add cursor,windsurf,roo,vscode`. Config lands at `~/.cursor/mcp.json`,
`~/.codeium/windsurf/mcp_config.json`, `.vscode/mcp.json`, etc.

### BMAD

`npx bmad-method install` (Node 20.12+ / Python 3.10+ / uv). Non-interactive install supports
`--set <module>.<key>=<value>` for CI/CD reproducibility. [unverified: exact module install
paths not checked against repo source]

### TLC

No installer. No binaries. The skill is a markdown file loaded by the agent from a known
path (`~/.cursor/skills/tlc-spec-driven/SKILL.md` in this workspace). All external tool
needs are delegated to named MCP servers or peer skills via probe-or-fallback patterns.

---

## 3. CLI Tools and SDKs

### GSD `gsd-tools.cjs`

The CJS distribution CLI. 20+ domain modules under `get-shit-done/bin/lib/`:

| Module | Purpose |
|---|---|
| `core` | Shared primitives |
| `state` | STATE.md mutations, lock, patch |
| `phase` | Phase lifecycle |
| `roadmap` | Roadmap management |
| `config` | config.json read/write |
| `verify` | Verification logic |
| `template` | Workflow template rendering |
| `frontmatter` | YAML frontmatter parsing |
| `init` | **Compound-init handlers** (see below) |
| `milestone` | Milestone archive/tag |
| `commands` | Command surface |
| `model-profiles` | Model tier resolution |
| `security` | Security scan helpers |
| `uat` | UAT orchestration |
| `docs` | Doc invariant enforcement |
| `workstream` | Workstream management |
| `schema-detect` | ORM schema detection (Prisma, Drizzle) |
| `profile-pipeline` | Profile composition |
| `planning-workspace` | `.planning/` utilities |
| `graphify` | Knowledge-graph integration |
| `learnings` | Learning capture |
| `audit` | Audit workflows |
| `gsd2-import` | Migration from GSD v2 |
| `intel` | Codebase intelligence index |

**Compound-init handlers** (`init` module): every workflow calls a single CLI seam that
returns all context needed for that workflow as one JSON blob:

```
node gsd-tools.cjs init execute-phase 1
node gsd-tools.cjs init plan-phase 1
node gsd-tools.cjs init new-project
```

When the blob exceeds ~50KB it spills to a tempfile and returns
`@file:/tmp/gsd-init-XXXXX.json`. One loader call per workflow, deduplicated, injection-ready.

### GSD TypeScript SDK (`sdk/`)

A typed re-implementation of `gsd-tools.cjs` as a registry (`createRegistry()` in
`sdk/src/query/index.ts`). Key components:

- **`GSDTools` façade** — single entry point, routed through the SDK Runtime Bridge.
- **SDK Runtime Bridge** (`sdk/src/query-runtime-bridge.ts`) — prefers native registry
  dispatch, falls back to subprocess, supports `strictSdk` mode, emits structured
  `onDispatchEvent` observability callbacks.
- **Sync Runtime Bridge** (`sdk/src/runtime-bridge-sync/`) — uses `synckit`
  (Atomics.wait on SharedArrayBuffer in a pooled Worker thread) for synchronous
  `executeForCjs()`. First call ~80ms; steady state ~0.1ms.
- **Golden parity tests** — assert that CJS and SDK paths produce identical output for
  every command. SDK can never silently diverge from the CJS reference.

### Task Master MCP Server

Exposes tools in three load tiers, selected via the `TASK_MASTER_TOOLS` env var in the
MCP config:

| Mode | Tools exposed | Approx. token cost |
|---|---|---|
| `all` (default) | 36 | ~21,000 |
| `standard` | 15 | ~10,000 |
| `core` / `lean` | 7 | ~5,000 |
| `custom` | comma-separated list | variable |

Core 7: `get_tasks`, `next_task`, `get_task`, `set_task_status`, `update_subtask`,
`parse_prd`, `expand_task`.

This is the most explicit "tool budget" knob in the landscape — token cost is measured and
documented per tier.

See also `../frameworks/adjacent-frameworks.md` for Task Master's three-role model config
(`main` / `research` / `fallback`) which is closely coupled to MCP tool selection.

### Graphify MCP Server

`python -m graphify.serve graphify-out/graph.json`

Tools exposed: `query_graph`, `get_node`, `get_neighbors`, `shortest_path`, `list_prs`,
`get_pr_impact`, `triage_prs`.

Token-budget governance on queries via `--budget <N>` flag (e.g. `--budget 1500`).

See `../frameworks/graphify.md` for the full pipeline (detect → extract → build → cluster →
analyze → report → export).

---

## 4. Runtime Hooks

### GSD's 12 Hooks

The most developed hook system in this landscape. All hooks wrap in try/catch and exit
silently on error. Stdin timeout: 3 seconds. Stale metrics (>60s old) are ignored.

| Hook file | Event | Role |
|---|---|---|
| `gsd-statusline.js` (22.6KB) | `statusLine` | Displays model, task, directory, context bar; writes `/tmp/claude-ctx-{session}.json` bridge file |
| `gsd-context-monitor.js` | `PostToolUse` / `AfterTool` | Injects WARNING/CRITICAL context-budget hints; 5-tool-use debounce; warns at ≤35% remaining, critical at ≤25% |
| `gsd-check-update.js` + `gsd-check-update-worker.js` | `SessionStart` | Background update check; non-blocking worker thread |
| `gsd-update-banner.js` | — | Surfaces "new version available" banner |
| `gsd-prompt-guard.js` | `PreToolUse` (Write/Edit to `.planning/`) | Advisory prompt-injection scan on planning artifacts before write |
| `gsd-read-injection-scanner.js` | `PostToolUse` (Read) | Scans Read tool output for injected instructions in untrusted file content |
| `gsd-read-guard.js` | `PreToolUse` | Advisory: prevent Edit/Write on files not Read this session |
| `gsd-workflow-guard.js` | `PreToolUse` (Write/Edit outside `.planning/`) | Advisory: flags edits made outside a GSD workflow context |
| `gsd-session-state.sh` | `PostToolUse` | Session state tracking for shell-based runtimes |
| `gsd-validate-commit.sh` | `PostToolUse` | Conventional-commit format enforcement |
| `gsd-phase-boundary.sh` | `PostToolUse` | Phase boundary detection |
| `gsd-graphify-update.sh` | — | Incremental knowledge-graph refresh on file change |

The `statusLine` hook bridges to the `gsd-context-monitor.js` via the shared
`/tmp/claude-ctx-{session}.json` file, allowing the context budget bar and the injection
warnings to share the same underlying usage data without a second runtime call.

Hook event name differences across runtimes are handled at install time by `bin/install.js`:
Claude Code uses `PostToolUse` / `PreToolUse`; Gemini CLI uses `AfterTool`. The hook source
is authored for Claude Code and transformed at deploy time.

### Graphify's PreToolUse Hook Strategy

On Claude Code and Gemini CLI, Graphify fires a `PreToolUse` hook before search-style tool
calls, nudging the assistant toward `graphify query "…"` over raw file reads. On runtimes
where hooks are not supported, this guidance is delivered via persistent instruction files
(`AGENTS.md`, `.cursor/rules/`) instead.

### Graphify's Git Hooks

`graphify hook install` adds `post-commit` and `post-checkout` hooks. These trigger AST-only
incremental rebuilds (Tree-sitter only, no LLM invocation), so the knowledge graph stays
current without incurring any model cost. A git merge driver is also installed to
union-merge `graph.json` automatically on concurrent commits, eliminating merge conflicts
in the shared graph artifact.

### No Hooks in TLC

TLC ships no hooks. Context budget monitoring is enforced through inline guidelines in
`context-limits.md` (per-file token caps, graduated cleanup zones) and through the agent's
own reading of STATE.md size. There is no runtime mechanism to intercept tool calls. See
`../frameworks/tlc-spec-driven.md` for the full context-limit table.

---

## 5. Lint and CI Scripts

### GSD's Custom Lint Suite (23+ scripts in `scripts/`)

Key scripts:

| Script | Purpose |
|---|---|
| `lint-command-contract.cjs` | Enforces command frontmatter/contract requirements across all 59 skills |
| `lint-no-source-grep.cjs` | Prevents `grep` shell calls in agent prompts — agents should use tools, not raw shell |
| `lint-no-source-grep-extras.cjs` | Extended grep-in-prompts detection for edge cases |
| `lint-shared-module-handsync.cjs` | Detects shared-module drift between CJS and SDK paths |
| `lint-skill-deps.cjs` | Validates `requires:` frontmatter dependency declarations in skills |
| `lint-shell-command-projection-drift.cjs` | Detects shell command surface drift across runtimes after install transforms |
| `lint-docs-required.cjs` | Enforces doc invariants (e.g. doc-required commands have docs) |
| `audit-workflow-script-paths.cjs` | Verifies all `@-ref`s in workflow files resolve to real paths on disk |
| `diff-touches-shipped-paths.cjs` | CI gate: decides which changesets a given diff needs to trigger |
| `prompt-injection-scan.sh` | Pre-release security scan for injected instructions in prompt artifacts |
| `secret-scan.sh` | Pre-commit/pre-release scan for accidentally committed secrets |
| `base64-scan.sh` | Guard for accidentally committed base64 blobs |
| `build-hooks.js` | Generates hook artifact files at build time |
| `run-tests.cjs` | Root test runner |

The `lint-no-source-grep.cjs` rule is particularly instructive: it encodes the team
convention that agents must use IDE tools (Read, Grep, Glob) rather than shell `grep` calls,
and enforces this as a CI gate rather than relying on documentation alone.

The `lint-shared-module-handsync.cjs` + golden parity tests (SDK) form a two-layer system:
lint catches drift at the source level, parity tests catch it at the output level.

Per-workflow file size budgets are also enforced in CI:
- `XL` workflows: ≤ 1,700 lines
- `LARGE` workflows: ≤ 1,500 lines
- `DEFAULT` workflows: ≤ 1,000 lines
- Per-agent `.md` files: soft cap ~45K chars, hard invariant 50K chars (overflow extracted
  to `references/*.md`)

### No Lint Suite in TLC

TLC's equivalent governance is expressed as per-file token limits in `context-limits.md`
and as workflow rules in `implement.md` and `validate.md`. These are agent-readable
constraints rather than machine-executable checks.

---

## 6. External Tool Integrations

### GSD

| Tool | How integrated | Notes |
|---|---|---|
| `slopcheck` | `slopcheck install --json` run per package in research phase | MIT, pip-installable. Required for Package Legitimacy Gate. Falls back to treating every package as `[ASSUMED]` when unavailable. |
| `fallow` | `npm install -D fallow@^2.70.0` or `cargo install fallow`; configured via `config.json` `code_quality.fallow.*` | Structural code review pre-pass. v2.70+ required — older versions silently emit zero findings. |
| `gh` CLI | Required for `/gsd-ship` | Generates GitHub PRs with body assembled from PLAN/SUMMARY/VERIFICATION. |
| `graphify` | Built-in knowledge graph of `.planning/` | Incremental; `gsd-graphify-update.sh` hook refreshes on file change. |
| `intel` | Queryable codebase intelligence index | Separate from graphify; focused on source code rather than planning artifacts. |
| Ollama / llama.cpp / LM Studio | Supported for `/gsd-review` | Token-budget trimming applied via `review.max_prompt_tokens` and per-reviewer overrides for small-context local models. |

### TLC

| Tool | How integrated | Notes |
|---|---|---|
| Context7 MCP | Step 3 of Knowledge Verification Chain | Two-call sequence: resolve library ID, then query. Hard-coded into the verification ladder — not optional. |
| `mermaid-studio` skill | Probe-or-fallback for diagram work | Recommendation fires only once per session to avoid noise. Falls back to inline mermaid code blocks. |
| `codenavi` skill | Probe-or-fallback for code exploration | Falls back to the `code-analysis.md` chain (see below). |
| `ast-grep` (`sg`) | Preferred code-analysis tool | One-time install nudge per session. |
| `ripgrep` (`rg`) | Second fallback | Used when `ast-grep` is unavailable. |
| `grep` | Third fallback | Plain grep as last resort. |

The `ast-grep` → `ripgrep` → `grep` chain is the `code-analysis.md` fallback sequence. See
`../frameworks/tlc-spec-driven.md` for the full Knowledge Verification Chain.

### Graphify

| Dependency | Role | License |
|---|---|---|
| Tree-sitter (31 languages) | Local AST extraction — no LLM on source code | MIT |
| NetworkX | Graph construction and traversal | BSD |
| Leiden algorithm | Community detection — no vector embeddings | BSD/LGPL [unverified] |

The no-LLM-on-source-code design is a deliberate choice: Tree-sitter provides structural
analysis at zero inference cost. Only prose documents, PDFs, images, and videos route through
LLM-driven semantic extraction.

### Task Master

Context7, Perplexity, and any OpenRouter-compatible provider can be wired to the `research`
role model slot. Zero-API-key path available via Claude Code CLI or Codex CLI OAuth, which
re-uses existing IDE authentication.

---

## 7. Supply-Chain Defense

GSD's Package Legitimacy Gate is the most developed supply-chain defense mechanism in this
landscape. Motivation: "AI-hallucinated package names get pre-registered with malicious
post-install scripts" (GSD README — slopsquatting defense).

**The seven-step gate:**

1. Every package surfaced via web search is tagged `[ASSUMED]` regardless of `npm view`
   or similar verification — the mere fact that a search result returned it is not proof
   of legitimacy.
2. `slopcheck install --json` run per package during the research phase.
3. Audit table written to `{phase}-RESEARCH.md` under `## Package Legitimacy Audit`, with
   columns: Registry, Age, Downloads, Source Repo, verdict.
4. Verdict classes: `[SLOP]` (clearly invalid) stripped entirely from plans;
   `[SUS]` / `[ASSUMED]` inject a `checkpoint:human-verify` task before any install task.
5. `[OK]` packages proceed without a gate.
6. Failed or unavailable installs surface as checkpoints — the framework never silently
   substitutes an alternative package.
7. If `slopcheck` is unavailable, every package is treated as `[ASSUMED]`, ensuring
   degraded-mode behavior is conservative rather than permissive.

No other framework in this research set implements an equivalent gate. TLC's Knowledge
Verification Chain (Step 4: web search; Step 5: flag as uncertain) provides a weaker analog
— it governs what the agent claims about packages but does not mandate an external legitimacy
check tool.

See also `./self-healing-and-verification.md` for the broader research-gate and plan-checker
system that this gate feeds into.

---

## 8. Implications for Our Framework

- **Installer scope is a first-principles decision.** GSD's monolithic installer achieves
  broad multi-runtime reach at the cost of a large, hard-to-audit artifact. TLC proves that
  zero-tooling distribution is viable when the target runtime universe is narrow. A framework
  targeting 2–3 runtimes can stay markdown-only; one targeting 10+ likely needs a programmatic
  installer to keep per-runtime transform logic maintainable. Decide the runtime target set
  before committing to either extreme.

- **Compound-init handlers are worth adopting regardless of tooling level.** The pattern of
  collecting all workflow-needed context into a single seam call (and spilling to a tempfile
  above a size threshold) has nothing to do with installer complexity — it is a workflow
  architecture decision. It removes per-workflow re-discovery cost and keeps cache-friendly
  ordering deterministic. Applicable even in a markdown-only framework via a single
  structured front-matter file the agent reads before every workflow entry.

- **Tiered MCP tool loading (Task Master's `TASK_MASTER_TOOLS`) should be a first-class
  design concern.** The difference between 5,000 and 21,000 tokens per session is material.
  If our framework ships an MCP server, document the tool budget per tier and expose a
  configuration knob for it from day one.

- **Lint rules that encode conventions are more reliable than doc-only conventions.** GSD's
  `lint-no-source-grep.cjs` enforces the "use tools, not shell" norm as a CI gate. Any
  convention strong enough to matter — commit format, file size limits, `@-ref` resolution —
  is worth encoding as a check rather than a README paragraph.

- **Supply-chain defense should be explicit and conservative by default.** The "treat every
  search-discovered package as `[ASSUMED]`" default is a strong prior that respects how AI
  agents actually hallucinate (confidently, not hedgingly). If our framework produces
  research artifacts that name packages, building a legitimacy gate in — even a lightweight
  one — is cheaper than discovering a slopsquatting incident after the fact.

---

## Cross-links

- `../frameworks/gsd.md` — full GSD architecture, workflow, and agent roster
- `../frameworks/tlc-spec-driven.md` — TLC skill structure, Knowledge Verification Chain,
  context-limit table
- `../frameworks/graphify.md` — Graphify pipeline, MCP server tools, git merge driver
- `../frameworks/adjacent-frameworks.md` — Task Master tool tiers, BMAD installer, OpenSpec
  and Spec Kit distribution
- `./self-healing-and-verification.md` — plan-checker loop, research gate, Package
  Legitimacy Gate integration into the verification stack
- `./multi-runtime-support.md` — per-runtime install surfaces, content transformation at
  deploy time, hook event name differences
- `./patterns-worth-stealing.md` — compound-init handlers, wave-based execution, probe-or-
  fallback skill delegation
