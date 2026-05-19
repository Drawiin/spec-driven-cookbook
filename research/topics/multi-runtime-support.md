# Multi-Runtime Support

## 1. Overview

The AI coding assistant landscape has fragmented into 15+ distinct runtimes — Claude Code, Cursor, Windsurf, Codex, Copilot, Gemini CLI, Kilo, OpenCode, Antigravity, Augment, Trae, Qwen, Hermes, CodeBuddy, Cline, and more — each with different skill/command surfaces, hook systems, and config file formats. Frameworks that want to be runtime-agnostic face significant adaptation overhead: the same workflow concept must be re-expressed as a slash-command `.md`, a `SKILL.md`, a TOML config entry, a `.clinerules` file, or a persistent instruction file depending on the target. The gap between runtimes that support interceptor hooks (Claude Code, Gemini CLI, Codex) and those that offer only passive skill loading (Cursor, Windsurf, Copilot, Cline) is as significant as the file-format differences.

---

## 2. GSD: "Write Once, Transform at Install Time"

GSD's core multi-runtime pattern is authorial primacy combined with install-time transformation. Everything is written in Claude Code's native format — agents in `agents/gsd-*.md`, commands in `commands/gsd/*.md`, hooks in `hooks/*.js`. The monolithic `bin/install.js` (~469 KB, ~10,700 lines) handles all runtime-specific transformations at install time. The user runs `npx get-shit-done-cc@latest`, selects a target runtime, and the installer produces the correct file layout and content for that runtime.

Four categories of transformation are applied:

### a. Tool Name Mapping

Claude Code names its built-in tools differently from other runtimes. The installer rewrites tool references in agent and command files at install time. Confirmed mappings from `ARCHITECTURE.md` (only the Copilot row is explicitly documented in ARCHITECTURE.md; other runtime mappings marked `[unverified]`):

| Claude Code name | Other runtime name | Runtime |
|---|---|---|
| `Bash` | `execute` | Copilot |
| `Read` | `read` | Copilot [unverified for other runtimes] |
| (others) | (runtime-specific equivalents) | [unverified — full mapping lives in `install.js`, not enumerated in public docs] |

### b. Hook Event Renaming

Hook event names are runtime-specific. The installer rewrites event names in `settings.json`/hook registration:

| Claude Code event | Equivalent | Runtime |
|---|---|---|
| `PostToolUse` | `AfterTool` | Gemini CLI |
| `PreToolUse` | (runtime-specific equivalent) | Gemini CLI |
| `PostToolUse` | — | Copilot, Cursor, Windsurf (no GSD hooks at all) |

Runtimes with no hook support (Copilot, Cursor, Windsurf, OpenCode, Kilo, Augment, Trae, Qwen, Hermes, CodeBuddy, Cline) receive no hook files. GSD's context-monitor and prompt-guard behaviors are therefore absent on those runtimes.

### c. Agent Frontmatter Conversion

Each runtime that supports agents has its own definition format. The installer converts Claude Code's native agent frontmatter into the target format. Codex, which does not use `.md` agent files, receives per-agent TOML entries in its `config.toml` under `[features].hooks`.

### d. Command Spelling

Slash-command names follow different conventions:

| Runtime | Form | Example |
|---|---|---|
| Most runtimes | `/gsd-command-name` (hyphen) | `/gsd-plan-phase` |
| Gemini CLI | `/gsd:command-name` (colon) | `/gsd:plan-phase` |

Gemini CLI namespaces all plugin commands under a colon-separated prefix; the installer rewrites command names accordingly at install time.

See `../frameworks/gsd.md` for the full GSD profile.

---

## 3. GSD: 15-Runtime Install Matrix

The installer targets 15 runtimes. Global paths are for user-wide installs; local paths are per-project. The invocation surface is how the AI assistant discovers and calls GSD commands. Hook support indicates whether GSD's event-driven hooks are functional on that runtime.

| Runtime | Global path | Local path | Invocation surface | GSD hooks |
|---|---|---|---|---|
| Claude Code | `~/.claude/` | `./.claude/` | `skills/gsd-*/SKILL.md` + `commands/gsd/` | Yes (11 hooks per ARCHITECTURE.md) |
| OpenCode | `~/.config/opencode/` | `./.opencode/` | `command/gsd-*.md` | No |
| Kilo | `~/.config/kilo/` | `./.kilo/` | `command/gsd-*.md` | No |
| Gemini CLI | `~/.gemini/` | `./.gemini/` | `commands/gsd/*.toml` (colon form) | Yes |
| Codex | `~/.codex/` | `./.codex/` | `skills/gsd-*/SKILL.md` | Yes (TOML hook tables) |
| Copilot | `~/.copilot/` | `./.github/` | `skills/gsd-*/SKILL.md` + `copilot-instructions.md` | No |
| Cursor | `~/.cursor/` | `./.cursor/` | `skills/gsd-*/SKILL.md` | No (rule refs only) |
| Windsurf | `~/.codeium/windsurf/` | `./.windsurf/` | `skills/gsd-*/SKILL.md` | No (rule refs only) |
| Antigravity | `~/.gemini/antigravity/` | `./.agent/` | Gemini-style | Yes |
| Augment | `~/.augment/` | `./.augment/` | `skills/gsd-*/SKILL.md` | No |
| Trae | `~/.trae/` | `./.trae/` | `skills/gsd-*/SKILL.md` | No |
| Qwen | `~/.qwen/` | `./.qwen/` | `skills/gsd-*/SKILL.md` | No |
| Hermes | `~/.hermes/` | `./.hermes/` | `skills/gsd-*/SKILL.md` (category-based) | No |
| CodeBuddy | `~/.codebuddy/` | `./.codebuddy/` | `skills/gsd-*/SKILL.md` | No |
| Cline | `~/.cline/` | project root `.clinerules` | `.clinerules` | No |

Note: Trae, Qwen, Hermes, CodeBuddy, and Antigravity paths are drawn from the installer's behavior as documented in `ARCHITECTURE.md`; the authoritative per-skill inventory lives in `docs/INVENTORY-MANIFEST.json`, which was not fetched [unverified].

---

## 4. GSD: Runtime-Aware Model Profiles

GSD's `config.json` includes a `runtime` field (`claude`, `codex`, etc.) that drives model ID resolution at agent-spawn time. The same abstract tier — `opus`, `sonnet`, `haiku` — resolves to different concrete model IDs per runtime.

**Claude runtime:**
- `opus` → `claude-opus-4-7`
- `sonnet` → `claude-sonnet-4-6`
- `haiku` → `claude-haiku-4-5`

**Codex runtime:**
- `opus` → `gpt-5.4` (xhigh reasoning)
- `sonnet` → `gpt-5.3-codex`
- `haiku` → `gpt-5.4-mini`

Setting `model_profile: "inherit"` defers model selection entirely to the runtime's current session model — useful when the user has already configured their preferred model in the IDE.

Model resolution follows a five-layer precedence stack (highest to lowest): per-agent `model_overrides` → dynamic routing tier models → phase-level `models[]` → global `model_profile` tier → runtime default.

Issue #2612 [unverified] tracks dedicated install-path support for `opencode`, `gemini`, `qwen`, and `copilot`. As of the research snapshot, runtime-aware model profiles are fully implemented at install time only for Codex; other runtimes rely on `inherit` or manual `config.json` edits.

---

## 5. GSD: Installer Migration and Stability

The installer (`bin/install.js`) is designed to be re-run safely. Key stability mechanisms:

- **`gsd-file-manifest.json`** — tracks every file the installer deployed, enabling a clean `--uninstall` that removes only GSD-owned files.
- **`gsd-local-patches/`** — before overwriting any file the user has locally modified, the installer backs it up here. `/gsd-update --reapply` restores user customizations after an upgrade.
- **Idempotent reinstall** — `npx get-shit-done-cc@latest` is safe to re-run; the Installer Migration Module (ADR-0008) handles file moves, stale-artifact cleanup, config rewrites, and user-data preservation.
- **`CLAUDE_CONFIG_DIR` env var** — overrides the default config directory, enabling Docker and CI environments to install into a custom path without root access.
- **Windows-specific handling** — `windowsHide` on child processes, EPERM/EACCES protection, path-separator normalization, retry-and-fallback on `EPERM`/`EBUSY`/`EACCES` errors.
- **WSL detection** — the installer detects when Windows Node.js is running inside WSL and warns about path mismatches between the Windows and Linux views of the filesystem.
- **Baseline scan** — on each install, the Installer Migration Module scans for legacy install artifacts from prior versions and migrates or removes them.

---

## 6. Alternative Approaches

### Graphify

Graphify (`graphify install --platform <name>` or per-tool subcommands like `graphify cursor install`) supports 17+ assistants. The multi-runtime strategy is two-tier: use payload-bearing PreToolUse hooks where the runtime supports them (Claude Code, Gemini CLI), and fall back to persistent instruction files (`AGENTS.md`, `.cursor/rules/`, `CLAUDE.md`) where it does not. Reversibility is explicit: `graphify uninstall --purge` removes all installed artifacts. This approach keeps the framework's core logic runtime-agnostic; only the integration shim varies per platform. See `../frameworks/graphify.md`.

### Spec Kit

Spec Kit's multi-runtime answer is a toggle: `--integration-options="--skills"` installs the same workflow as agent skills rather than slash commands. The `specify integration list` command provides a view of active multi-runtime integrations. In skills mode, templates are installed into agent directories (e.g., `.claude/commands/`). Supporting 30+ agents, Spec Kit uses slash commands as the primary surface on most runtimes, falling back to skills format where slash commands are unavailable. See `../frameworks/adjacent-frameworks.md`.

### TLC

TLC (the skill from which this project's skill system derives) has no multi-runtime adapter layer. It is a pure markdown skill file that any agent can load from any path the user provides. This is the simplest possible approach: one file, no installer, no transformation. The cost is the absence of runtime-specific optimization — no hooks, no native command registration, no model-profile resolution. Any runtime that can load a skill file can use TLC.

### Task Master

Task Master takes the MCP server path: instead of installing files into each runtime's config directory, it runs as a local MCP server that any MCP-capable runtime can connect to. Per-runtime rules injection is handled post-init via `task-master rules add cursor,windsurf,roo,vscode`. One-click MCP install configs are provided for Cursor, Windsurf, VS Code, and Claude Code. A zero-API-key path is available via Claude Code CLI or Codex CLI OAuth, which reuses the IDE's existing authentication. See `../frameworks/adjacent-frameworks.md`.

---

## 7. Skill Surface Types Across Runtimes

A taxonomy of the "surfaces" frameworks use to inject themselves into different runtimes:

| Surface type | Used by | Pros | Cons |
|---|---|---|---|
| Skill manifests (`SKILL.md`) | GSD on Cursor/Codex/Augment/Trae/Windsurf/Copilot, TLC on any | Near-universal format; lazy-loaded by the runtime; low maintenance | No hook capabilities; passive — cannot intercept tool calls |
| Slash commands (`.md` in `commands/`) | GSD on Claude Code local; OpenCode/Kilo variants | Rich tool access; hooks available; explicit invocation surface | Claude Code-specific format for the richest variant; per-runtime file format differences |
| TOML config (Codex) | GSD on Codex | Native Codex integration; hooks via `[features].hooks` tables | Per-runtime maintenance; not portable to non-Codex runtimes |
| `.clinerules` | GSD on Cline | Simple; single file | Single flat file; no agent definitions; no hooks |
| Persistent instruction files | Graphify (`AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`) | Runtime-agnostic; works anywhere the runtime reads its instruction files | Passive guidance only — cannot be invoked as a command; no hooks |
| MCP server | Task Master, Graphify | Platform-agnostic; rich typed tool API; single server serves all connected clients | Requires a running server process; network/port management; not all runtimes support MCP |
| PreToolUse / PostToolUse hooks | GSD on Claude Code/Gemini CLI/Codex, Graphify on Claude Code/Gemini CLI | Interceptor pattern — can observe or modify tool calls before/after they execute | Runtime-specific event names (`PostToolUse` vs `AfterTool`); unavailable on most runtimes |

The practical consequence is a capability gradient: runtimes with hook support (Claude Code, Gemini CLI, Codex, Antigravity) can support active behaviors — context monitoring, prompt-injection scanning, commit validation — while the majority of runtimes that only support skill loading receive a passive version of the same framework.

See `./patterns-worth-stealing.md` for a deeper treatment of hook strategies and `./auxiliary-tooling.md` for MCP server infrastructure patterns.

---

## 8. Implications for Our Framework

- **Choose an authorial runtime, not a neutral format.** GSD's "write in Claude Code format, transform at install" is the most complete multi-runtime approach observed, but it requires a large installer and ongoing per-runtime maintenance. The alternative — writing in a deliberately neutral format (plain `SKILL.md` with no runtime-specific features) — is simpler to maintain but gives up hooks and native command registration on every runtime. The decision should be made explicitly, not defaulted into.

- **Separate capability tiers by hook availability.** Runtimes divide cleanly into those that support hooks (Claude Code, Gemini CLI, Codex, Antigravity) and those that do not (everything else). Features that depend on hooks — context monitoring, guard rails, commit validation — should be documented as Claude Code / Gemini / Codex-only, not presented as universally available. Users on hook-capable runtimes get a materially different experience.

- **Treat the MCP path as a first-class option.** Task Master's MCP server approach sidesteps file-format fragmentation entirely. If our framework's core logic can be expressed as MCP tool calls, it becomes runtime-agnostic by default. The trade-off is operational: users must run a server process. For teams already running MCP servers (e.g., for database or code-search tools), the marginal cost is low.

- **Install-time idempotency and clean uninstall are non-negotiable at scale.** GSD's `gsd-file-manifest.json` + `gsd-local-patches/` + idempotent reinstall pattern is directly worth adopting. Without a manifest-tracked install, users cannot safely upgrade the framework and cannot cleanly remove it. This becomes a support burden quickly.

- **Model profile indirection pays for itself.** Abstracting `opus` / `sonnet` / `haiku` tiers away from concrete model IDs, then resolving at runtime, insulates every skill and agent file from model version churn. When Anthropic releases a new Claude version, one config change updates all agents. Frameworks that hard-code model IDs (`claude-sonnet-4-6`) in skill files will require mechanical edits across dozens of files on every model release.
