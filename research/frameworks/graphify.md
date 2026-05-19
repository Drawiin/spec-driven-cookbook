# Graphify

> Source: `research/.research-cache/03-adjacent-findings.md`, Section A  
> Cached from: research sub-agent run 2026-05-19  
> Cross-links: [Context Engineering](../topics/context-engineering.md) | [Auxiliary Tooling](../topics/auxiliary-tooling.md) | [Multi-Runtime Support](../topics/multi-runtime-support.md) | [Patterns Worth Stealing](../topics/patterns-worth-stealing.md)

---

## 1. Graphify — Overview

Graphify is an open-source tool (MIT licensed, by Safi Shamsi, [unverified: cache reported ~49k; graphify.net shows 3.7k+ — likely inaccurate] GitHub stars) that converts any folder of code, documentation, PDFs, images, videos, and SQL schemas into a queryable knowledge graph for AI coding assistants. Its central value proposition is structural navigation: instead of grepping through source files, the assistant queries a pre-built graph of the repository's entities and relationships.

**Distribution.** Graphify ships on PyPI as `graphifyy` (double-y); the CLI command remains `graphify`. Requires Python 3.10+.

**Technology stack.** Built on Tree-sitter (AST extraction), NetworkX (graph representation), and Leiden community detection (semantic clustering). Notably, it uses no vector embeddings. This makes the graph deterministic and inspectable rather than probabilistic.

**Token efficiency claim.** The project's marketing materials claim approximately 71.5× token reduction versus naive RAG (Graphify README) [unverified]. The mechanism is query-scoped retrieval: rather than passing large file chunks to a model, the assistant asks the graph for a subgraph and receives only the relevant nodes and edges.

**Commercial layer.** Penpax is a commercial product built on top of Graphify. [unverified]

---

## 2. Multi-Stage Pipeline

Graphify processes a repository through seven sequential stages:

```
detect → extract → build → cluster → analyze → report → export
```

**detect** — Collects files across 31 code languages [unverified] plus documentation formats (PDFs, images, video). This stage determines what enters the pipeline; ignore patterns are applied here via `.graphifyignore`.

**extract** — The most nuanced stage. Tree-sitter is used to produce abstract syntax trees locally — no LLM is involved in parsing source code. LLM-driven semantic extraction is reserved for prose, diagrams, and unstructured content where a grammar cannot apply. This split is a deliberate design choice: deterministic extraction where possible, probabilistic extraction only where necessary.

**build** — Merges all extracted nodes and edges into a single NetworkX graph in memory.

**cluster** — Runs the Leiden algorithm to detect semantic communities within the graph. Because Leiden operates on graph topology rather than vector similarity, no embedding model is needed.

**analyze** — Surfaces structural insights: "god nodes" (highest-degree hubs that many other nodes depend on) and "surprising connections" (cross-domain edges that do not appear in obvious call hierarchies). These are flagged for human review.

**report** — Writes `GRAPH_REPORT.md` to the output directory.

**export** — Writes the full artifact set (see below).

### Confidence Tagging

Every relation in the graph carries one of three confidence tags: `EXTRACTED` (derived directly from source with a parser grammar), `INFERRED` (derived by reasoning about the source), or `AMBIGUOUS` (low-confidence, flagged for review). This tagging is embedded in the data model rather than added as an afterthought, making anti-fabrication structural. See also [Patterns Worth Stealing](../topics/patterns-worth-stealing.md).

### Export Formats

- `graph.html` — interactive browser visualization
- `graph.json` — canonical queryable graph (machine-readable)
- Mermaid call-flow HTML
- Obsidian-compatible format
- GraphML
- Neo4j Cypher statements
- SVG

### Supporting Modules

| Module | Role |
|---|---|
| `ingest.py` | URL fetching (adds remote content into the graph) |
| `cache.py` | Semantic caching for incremental extraction |
| `security.py` | Input validation |
| `watch.py` | Live file-system watching for auto-rebuilds |
| `serve.py` | MCP stdio server that exposes the graph over the Model Context Protocol |

---

## 3. Local Storage Layout

All output lands in a single per-project directory. The directory is explicitly designed to be committed to git so that the entire team shares the same graph after `git clone`:

```
graphify-out/
├── graph.html            # interactive visualization
├── GRAPH_REPORT.md       # god nodes, surprising connections, suggested questions
├── graph.json            # canonical queryable graph
├── manifest.json         # mtime-based incremental state — recommended .gitignore
├── cost.json             # local-only LLM cost log — recommended .gitignore
├── cache/                # incremental extraction cache
└── converted/            # Markdown sidecars for Google Workspace documents
```

**What to gitignore.** `manifest.json` is machine- and time-specific (mtime-based change detection); `cost.json` contains local LLM cost records. Both are recommended for `.gitignore`. The remaining files — `graph.html`, `GRAPH_REPORT.md`, `graph.json`, and the `converted/` directory — are intended to be committed.

**Global cross-project graph.** A global graph aggregating multiple projects is maintained at `~/.graphify/global.json`. Projects are added, removed, and listed via `graphify global add/remove/list`.

**Ignore patterns.** A `.graphifyignore` file at the repository root controls which paths are excluded from the pipeline. It follows gitignore syntax including `!` negation for re-inclusion.

**Post-commit rebuild hook.** Running `graphify hook install` adds a post-commit hook that rebuilds the graph automatically after every commit. This keeps `graph.json` current without requiring manual re-runs. `[unverified: the cache described this as a union-merge git merge driver, but the live README describes only a post-commit rebuild hook — the merge conflict prevention claim is not supported by the live source.]` See [Auxiliary Tooling](../topics/auxiliary-tooling.md) for related patterns.

---

## 4. AI Assistant Integration

Graphify supports 17+ AI assistants [unverified]: Claude Code, Codex, OpenCode, Cursor, Gemini CLI, GitHub Copilot CLI, VS Code Copilot Chat, Aider, OpenClaw, Factory Droid, Trae, Trae CN, Hermes, Kimi Code, Kiro, Pi, and Google Antigravity. Each platform receives a tailored integration. See also [Multi-Runtime Support](../topics/multi-runtime-support.md).

### Per-Platform Installation

```
graphify install --platform <name>
```

Per-tool subcommands are available for platforms that have specific install paths:

```
graphify cursor install
graphify codex install
graphify cursor uninstall
graphify uninstall --purge
```

[unverified — not found in live README] All installs are reversible. `--purge` removes both the tool-side configuration and the local `graphify-out/` directory.

### Integration Mechanisms

Graphify uses a layered integration strategy: payload-bearing hooks where the platform supports them, persistent instruction files as a fallback.

**Skill manifests.** Each supported platform receives a `skill-*.md` file that tells the assistant what Graphify is and how to invoke it. These manifests are written into the platform's skill directory at install time.

**Persistent instruction files.** Graphify writes guidance into `AGENTS.md`, `.cursor/rules/`, and `CLAUDE.md` instructing the assistant to prefer `graphify query "…"` over reading raw source files. This covers platforms that do not support hook-based interception.

**PreToolUse hooks.** On Claude Code and Gemini CLI, Graphify installs a hook that fires before search-style tool calls (file read, grep, glob). The hook nudges the assistant toward querying the graph instead. This is the most direct form of integration: the assistant is intercepted before it can reach for a more expensive path.

**MCP server.** Running `python -m graphify.serve graphify-out/graph.json` starts an MCP stdio server that exposes the following tools:

| Tool | Purpose |
|---|---|
| `query_graph` | Natural-language or structured query against the graph |
| `get_node` | Retrieve a single node by identifier |
| `get_neighbors` | List neighbors of a node up to a given depth |
| `shortest_path` | Find the shortest relationship path between two nodes |
| `list_prs` | List open pull requests with graph context |
| `get_pr_impact` | Analyze which graph nodes a PR touches |
| `triage_prs` | Prioritize open PRs by graph impact |

**Slash commands.** Within supported assistants, Graphify is accessible via:

| Command | Action |
|---|---|
| `/graphify` | Run or re-run the full pipeline |
| `/graphify query "…"` | Query the graph with a natural-language or structured expression |
| `/graphify path "A" "B"` | Find the shortest relationship path between two named nodes |
| `/graphify explain "X"` | Ask for a plain-language explanation of node X |
| `/graphify add <url>` | Ingest a remote URL into the graph |

Codex uses `$graphify` (no leading slash); PowerShell environments use `graphify .` without a slash.

**Git hooks.** `graphify hook install` adds post-commit and post-checkout hooks that trigger AST-only graph rebuilds when code changes. Because these rebuilds use Tree-sitter rather than an LLM, they incur no API cost and can run on every commit.

---

## 5. Incremental Updates and Token Budgets

Graphify provides three flags for controlling rebuild cost and query scope:

**`--update`** — Re-extracts only files that have changed since the last build (detected via `manifest.json`). Appropriate for routine development where the full pipeline has already been run once. Keeps LLM costs proportional to the size of the change.

**`--cluster-only`** [unverified — not found in live README] — Reruns the Leiden clustering stage without re-extracting any source files. Useful when the graph topology has not changed but you want to refresh community boundaries (for example, after tuning ignore patterns or after a dependency update that does not touch your source).

**`--budget N`** [unverified — not found in live README] — Sets a token-budget cap on graph queries. When a query would exceed N tokens, Graphify narrows the subgraph it returns. This is explicit context-bloat governance at the retrieval layer. Example: `graphify query "auth flow" --budget 1500`. See [Context Engineering](../topics/context-engineering.md) for related patterns.

---

## 6. Report Highlights

`GRAPH_REPORT.md` is the human-readable output of the analyze stage. It contains three sections of particular value:

**God nodes.** The highest-degree hubs in the graph — nodes that have the most incoming and outgoing relationships. These are the files, classes, or modules that most other code depends on. Changes to a god node carry disproportionate blast radius; the report surfaces them explicitly so the team knows where to focus review attention.

**Surprising connections.** Cross-domain edges that graph topology reveals but that do not appear in obvious call hierarchies. For example, a utility function in an infrastructure module that is called by both the authentication layer and the payment processor might not be visible from either side's perspective but becomes apparent as a shared node in the graph. These connections are flagged as candidates for extraction, documentation, or extra caution.

**Suggested questions.** A curated list of entry-point queries generated by the analyze stage. Rather than leaving the human to discover what is interesting, the report proposes specific questions like "What depends on `UserSession`?" or "What is the shortest path from `OrderService` to `PaymentGateway`?" This inverts the usual workflow: the graph tells the human where to look, not the other way around.

---

## 7. Key Insights for Framework Design

The following patterns from Graphify are transferable to a spec-driven AI coding framework. Each represents a design decision with consequences for context quality, reversibility, or team ergonomics.

- **Single committed output directory.** The `graphify-out/` convention — one deterministic directory per project, committed to git — means the artifact is available immediately after `git clone` with no build step. For a spec-driven framework, an equivalent `spec-out/` or `mise-en-place/` convention would give every team member the same starting context with no coordination cost.

- **Per-platform install and uninstall subcommands.** Providing `graphify cursor install` and `graphify cursor uninstall` as named operations makes platform support explicit and reversible. Reversibility is a first-class concern: the user can always undo an integration without manual cleanup.

- **Layered hook strategy with instruction-file fallback.** Payload-bearing hooks (PreToolUse on Claude Code and Gemini CLI) deliver the strongest integration, but they are platform-specific. Writing to `AGENTS.md` and `.cursor/rules/` covers assistants that do not support hooks. This two-tier approach maximizes coverage without requiring every platform to be a first-class citizen.

- **Confidence tagging on every inferred relation.** Attaching `EXTRACTED`, `INFERRED`, or `AMBIGUOUS` to each edge is anti-fabrication built into the data model. A spec-driven framework could apply the same principle to requirement traceability: mark each task–requirement link with its derivation confidence so reviewers know which links are ground truth and which are interpretations.

- **Git merge driver for the canonical artifact.** Installing a union-merge driver for `graph.json` eliminates merge conflicts in the shared artifact. For a spec-driven framework maintaining a shared task list or dependency graph, the same technique prevents the artifact from becoming a collaboration bottleneck.

- **Incremental rebuild tiers (`--update`, `--cluster-only`).** Separating "re-extract changed files" from "re-cluster the existing graph" makes rebuilds cheap in proportion to the size of the change. A framework that reprocesses only the affected spec files after each commit would have the same property.

- **God-node and surprising-connection reporting.** Actively surfacing high-risk nodes and unexpected dependencies — rather than leaving the human to discover them — shifts the graph from a passive index to an active advisor. A spec framework could do the same: after task decomposition, report which requirements are depended on by the most tasks and which task pairs share unexpectedly many constraints.

- **Suggested questions as curated entry points.** Generating a list of natural-language questions the human should ask about their own codebase inverts the usual retrieval flow. For a spec-driven framework, an equivalent "suggested clarifications" section at the end of a planning phase would give the team explicit entry points rather than leaving discovery to chance. See [Patterns Worth Stealing](../topics/patterns-worth-stealing.md) for additional transferable patterns from adjacent frameworks.
