# GSD-2 (now GSD Pi) Framework Deep-Dive

> Researched: 2026-05-27
> Compared against: research/frameworks/gsd.md (GSD v1 analysis)
> **Important provenance**: the user referenced GSD-2 at https://github.com/gsd-build/gsd-2. The gsd-build/gsd-2 README now redirects to **gsd-pi** at https://github.com/open-gsd/gsd-pi. Project moved due to maintainer abandonment of the original `gsd-build` org (see §1 — "Why this project exists" excerpt). This deep-dive covers both repos: gsd-2 is treated as historical scaffolding still containing useful architectural intent, gsd-pi is the live successor.

## 1. One-paragraph summary

**GSD Pi** (npm: `@opengsd/gsd-pi`, formerly `gsd-build/gsd-2` then `gsd-pi` unscoped) is a **local-first coding-agent product** that planning, executes, verifies, and ships project work from the CLI ([gsd-pi README](https://github.com/open-gsd/gsd-pi/blob/main/README.md)). It is **community-maintained under the `open-gsd` org** after the original GSD maintainer abandoned the project around 2026-04-01 and the related `$GSD` token was rugged 2026-05-22 (see [VISION.md "Why this project exists"](https://raw.githubusercontent.com/open-gsd/gsd-pi/main/VISION.md)). The v1 line continues as community-maintained `open-gsd/gsd-core`; GSD Pi is the v2 baseline starting at version 1.0.0. Surfaces: CLI (`gsd` binary), TUI, VSCode extension, web UI (`pi.opengsd.net` configurator), Studio app, native engine. It runs against any LLM provider and uses Git worktrees to isolate parallel implementation. State lives in `.gsd/` (SQLite + markdown projections).

## 2. Architecture overview

**Core abstractions** (from [gsd-pi CONTEXT.md](https://raw.githubusercontent.com/open-gsd/gsd-pi/main/CONTEXT.md) which inherits structure from gsd-2's CONTEXT):

- **Unit**: the smallest executable workflow step (plan slice, execute task, complete slice).
- **Unit progression**: movement from one Unit to the next under orchestration rules.
- **Milestone → Slice → Task** hierarchy ([gsd-pi README](https://github.com/open-gsd/gsd-pi/blob/main/README.md): "Plans work into milestones, slices, and tasks").
- **Auto Orchestration**: runtime coordination owning the start/advance/resume/stop/getStatus interface (gsd-2 CONTEXT, ADR-014).
- **Worktree-based isolation**: every source-writing Unit runs in a proven milestone worktree root; planning-only Units may write `.gsd/**` at project root.
- **Drift catalog**: discriminated union of state-shape mismatches between DB rows, disk artifacts, and in-memory state — each kind has an idempotent repair (gsd-2 CONTEXT, ADR-017).

**Primary artifacts**: `.gsd/` directory at project root holds SQLite database + markdown projections (plans, summaries, validation notes, completion records). `completed-units.json` lives at project root and is authoritative across crashes. In-flight artifacts live in the worktree until merge.

**SDK dependence**: GSD Pi is **NOT** built on the OpenAI Agents SDK [inference — neither the README nor VISION mentions it; package.json shows custom TypeScript packages]. It is provider-agnostic by stated principle ("**Provider-agnostic.** gsd-pi works with any LLM provider"). The "GSD-2 = Agents SDK" framing in the user's root README is **incorrect** — that may have been speculative or based on a now-stale signal.

**Runtime support**: ships as a single npm package targeting Node.js. Integrations live in `vscode-extension/`, `web/`, `studio/`, `native/`. It is NOT a multi-runtime install-time-transformer like GSD v1 (which generated content for 15+ runtimes).

**Greenfield vs brownfield**: both, but the surface is now product-shaped rather than workflow-template-shaped — `gsd` boots, you point it at a project directory, it reads/writes `.gsd/`.

## 3. What GSD Pi INHERITS from GSD v1

- **The `gsd` brand + slash-command UX**: still `/gsd auto`, `/gsd quick`, `/gsd status`, `/gsd config` (README "Common Session Commands").
- **Phase model**: planning → implementation → verification → shipping (CONTEXT "Domain glossary" Unit definitions, README "What GSD Pi Does").
- **Persistent project state in a `.gsd/`-style directory**: same instinct as v1's `.planning/`, but now backed by SQLite not pure markdown.
- **Slopsquatting awareness**: `.prompt-injection-scanignore` and `.secretscanignore` ship in the repo root, indicating the same supply-chain posture as v1's `slopcheck` (though the exact tool is not confirmed).
- **The "worktree per task" idea**: v1 had wave-based parallelism; v2 deepens this into formal Worktree Safety + Worktree Lifecycle + Worktree State Projection modules (gsd-2 CONTEXT.md).

## 4. What GSD Pi DROPS from GSD v1

- **Multi-runtime install-time transform** [inference — the `bin/install.js` 469KB monster of v1 is absent; gsd-pi installs as a single npm package]. v1 generated content per runtime (Claude Code / Cursor / Gemini / 12 others); v2 is one Node CLI.
- **33+ named agents organized into 11 categories** [inference — no `agents/` directory in gsd-pi root, unlike v1's prominent `agents/` listing]. The Auto Orchestration model in gsd-2 CONTEXT suggests Units are dispatched via a typed contract, not via 33 named persona agents.
- **86-skill flat surface + 6-router meta-skill consolidation** [inference — no `commands/gsd/` directory of 60+ command files]. The 4-or-5 slash commands in the README replace this.
- **`gsd-tools.cjs` 20+ domain modules with `init.<workflow>` compound init** [inference]. CONTEXT.md doesn't reference compound init; the architecture is now adapter-seam-based not init-blob-based.
- **15-runtime support** as a first-class concern. Gone in favour of a single Node runtime.
- **Heavy meta-prompting layer**: v1 was characterized as "meta-prompting + context engineering for 15+ AI runtimes" in the dossier; gsd-pi VISION explicitly rejects "Heavy orchestration layers. Don't duplicate what the agent infrastructure already provides. Build on top of it, don't wrap it."

## 5. What GSD Pi ADDS that v1 did not have

- **SQLite-backed state** with `sql.js` snapshot persistence: atomic temp-file + rename, fsync, cleanup ordering (gsd-2 CONTEXT "DB snapshot persistence module").
- **Four named first-class invariant modules**: State Reconciliation, Worktree Safety, Recovery Classification, Tool Contract (ADR-015).
- **Drift catalog**: typed `DriftRecord` discriminated union with idempotent repairs — `sketch-flag`, `merge-state`, `stale-render`, `stale-worker`, `unregistered-milestone`, `roadmap-divergence`, `missing-completion-timestamp` (ADR-017).
- **`reconcileBeforeDispatch` pre-dispatch pipeline**: derive → detect drift → apply repairs → re-derive, capped at 2 passes, throws `ReconciliationFailedError` to Recovery Classification.
- **Adapter-seam architecture** (ADR-014): Dispatch, Recovery, Worktree, Health, Runtime persistence, Notification are all adapter seams; the Auto Orchestration module owns the lifecycle pipeline explicitly.
- **Closeout Boundary Stop** ([gsd-pi CONTEXT.md](https://raw.githubusercontent.com/open-gsd/gsd-pi/main/CONTEXT.md)): foreground `/gsd next` and `/gsd auto` runs preserve the closeout transcript as the final visible terminal surface, instead of replacing it with a roll-up widget.
- **Explicit Tool Contract module**: prompt obligations + allowed tools + schema enum values + validation requirements + closeout tools are *compiled* before dispatch, reviewable as a single artifact per Unit type.
- **VSCode extension + Web UI + Studio + Native packaging**: v2 is a product, not a template repo.
- **Web configurator** at https://pi.opengsd.net/ for building configurations in-browser.
- **`completed-units.json` as crash-recovery authoritative artifact**: a deliberate flat-file marker that survives DB corruption.

## 6. The "Agents SDK shift" — corrected reading

The user's root README states GSD-2 is "focused on building specialized agents with the Agents SDK." **This claim does not appear to be supported by the live gsd-pi repo.** The VISION explicitly says "**Provider-agnostic.** gsd-pi works with any LLM provider. No architectural decisions should privilege one provider over another." Neither README nor CONTEXT mentions the OpenAI Agents SDK by name.

What's actually new vs v1 is **architectural maturity**: typed Unit lifecycle, explicit invariant modules, drift catalog, adapter seams, worktree safety. The "specialized agents" framing in the user's README is conceptually correct (v2 has tighter Unit specialization than v1's loose 33-agent roster) but the SDK attribution is misleading.

**Implication for mise-en-place**: if you choose to lean on OpenAI Agents SDK as a runtime, you cannot point to GSD Pi as precedent — GSD Pi went the *other* way (provider-agnostic, no SDK lock-in). If you want SDK leverage, you'd be following BMAD-METHOD or Spec Kit's runtime-bridging instincts, not GSD Pi.

## 7. Worker / specialized-agent model in GSD Pi

GSD Pi's worker abstraction is a **Unit**, not a "worker" or "agent":

- A Unit has a **type** (plan slice, execute task, complete slice) and an associated **Tool Contract** (prompt obligations + allowed tools + schema enum values + validation rules + closeout tools).
- The orchestrator (`advance()`) selects the next Unit via a fixed pipeline: State Reconciliation → Dispatch decision → Tool Contract → Worktree Safety → Runtime persistence/journal (gsd-2 CONTEXT, ADR-014).
- **Dispatch never owns repair**: `Dispatch` only selects the next Unit from already-reconciled state. DB/disk repair, tool-policy compilation, and worktree root preparation are owned by their respective invariant modules.
- The Recovery Classification module maps failures to one of: `retry`, `pause with remediation`, `self-heal`, `stop` — each failure class has an intentional action.
- **No 33-agent roster**: instead of named persona agents, you get a small set of Unit types with deep contract validation.

**How GSD Pi prevents v1's "too many tools / too many agents" feel**:

- Aggressive consolidation per the VISION's "Simplicity over abstraction" principle ("Three similar lines of code is better than a premature abstraction").
- One Auto Orchestration module with a 5-method interface (`start`/`advance`/`resume`/`stop`/`getStatus`) instead of v1's compound init + waves + lockfile + checkpoint heartbeats spread across many helpers.
- Extension-first design: anything that *can* be an extension *is* an extension; the core stays small.

**Explicit token-budget improvements vs v1**: I could not find a context-rot policy in CONTEXT.md (gsd-pi's CONTEXT focuses on state/worktree/recovery invariants, not token budgeting). The triage synthesis flags "context budgeting semantics" as a provider-specific concern not yet normalized — so token-budget improvements vs v1 are **not visible** in the docs read.

## 8. Patterns from the existing dossier that GSD Pi implements

- **Pattern 1 (Compound Init Handlers)**: not in the same form. GSD Pi's `reconcileBeforeDispatch` is structurally similar (one call returns/applies everything needed before dispatch) but is about repair, not context loading.
- **Pattern 7 (Wave-Based Parallelism with State Lockfile)**: still present in spirit (worktree isolation + lease ownership + atomic SQLite snapshot replaces the `STATE.md.lock` O_EXCL primitive). Sharper.
- **Pattern 8 (Diagnose-into-PLAN Self-Healing)**: NOT visible as-such. v1's `gsd-debugger`-writes-new-PLAN pattern is replaced by the Recovery Classification module → typed Recovery decisions (retry/pause/self-heal/stop). The "failures produce tasks" idea is **dropped in favor of typed Recovery decisions**.
- **Pattern 10 (Asymmetric Decision Coverage Gates)**: not visible in CONTEXT; may live in code, untestable from docs alone.
- **Pattern 11 (Test-as-Spec)**: VISION explicitly says "Tests are the contract. If you change behavior, the tests tell you what you broke." Direct adoption of the principle.
- **Pattern 13 (Confidence Tagging on Inferred Data)**: not visible; v1's INFERRED/EXTRACTED/AMBIGUOUS taxonomy doesn't appear in CONTEXT.
- **Pattern 14 (Package Legitimacy Gate / Slopsquatting)**: signaled via `.prompt-injection-scanignore` and `.secretscanignore` at repo root — implies an active scanning pipeline, but exact tool not named.
- **Pattern 15 (Install-Time Profile + Surface Toggle)**: NOT visible. Single npm install; no `--profile` flag in the README install instructions.
- **Pattern 16 (Constitution as Governance)**: VISION + CONTEXT collectively serve this role for the project itself; not surfaced as a per-user-project artifact.
- **Pattern 25 (Frozen Baseline with Ratchet)**: not visible.
- **Pattern 29 (Guides + Sensors)**: not labeled as such, but Tool Contract + verification gates are guides; Recovery Classification + drift detectors are sensors. **Implicit, not declared**.

**Patterns v1 had that v2 visibly dropped**: compound init handlers (1), two-stage namespace routing (2), wave parallelism + lockfile in its specific O_EXCL form (7 — replaced by worktrees/SQLite), 33-agent roster (Pattern 6 was extracted from TLC not GSD, but v1 had its own dispatch pattern that is gone), install-time profile + surface toggle (15).

## 9. Patterns GSD Pi introduces that are NOT in the dossier

- **Drift catalog with idempotent repairs** — typed discriminated union of state-shape mismatches each with a named repair function. Transferability: **MEDIUM-HIGH** for any framework with persisted state. New dossier slot in Group C (Verification and Quality).
- **Worktree Safety as a fail-closed module** — every source-writing Unit must run in a proven milestone worktree; never silently degrades to project-root writes. Transferability: **MEDIUM** for frameworks with Git-isolated parallel execution.
- **Pre-dispatch invariant pipeline** as an explicit ordered sequence (Reconciliation → Dispatch → Tool Contract → Worktree Safety → Persistence). Transferability: **HIGH** — the principle "advance() owns the invariant pipeline, Dispatch only selects the next Unit from reconciled state" is broadly applicable.
- **Tool Contract as a compiled artifact per Unit type** — prompts + allowed tools + schema enums + validation + closeout tools authored and reviewed together. Transferability: **HIGH**. This is sharper than the dossier's Pattern 24 (Self-Describing Skill Manifest) — the Tool Contract is the *Unit-specific composition* of manifest + policy + prompt.
- **Closeout Boundary Stop** as a UX-level invariant — foreground runs preserve the closeout transcript as the final visible terminal surface. Transferability: **MEDIUM** (TUI-specific but the principle "leave the user with the closeout artifact, not a widget" generalizes).
- **Recovery decision taxonomy as a first-class module** — `retry / pause with remediation / self-heal / stop` with explicit failure-class → decision mapping. Transferability: **HIGH** — a tighter version of Pattern 8.

## 10. Relevance to mise-en-place design

Cross-walked against the six root-README principles of mise-en-place:

| mise-en-place principle | GSD Pi position | Relevance |
|---|---|---|
| Orchestrators + specialized workers | **CONFIRMS**: Auto Orchestration module + Units with Tool Contracts. **BUT** GSD Pi's orchestrator is heavier than mise-en-place's intent — it owns crash recovery, DB persistence, worktree lifecycle. mise-en-place's orchestrator is workflow-skill-level, not runtime-level. | Borrow the *interface shape* (`start`/`advance`/`resume`/`stop`/`getStatus`) but not the runtime depth. |
| Self-healing | **CONFIRMS** with sharper taxonomy: Recovery Classification with typed `retry / pause / self-heal / stop` decisions + drift catalog with idempotent repairs. | mise-en-place's "Self-healing" principle should adopt the explicit decision taxonomy. The drift catalog idea is a strong adaptation target. |
| Humans are lazy | Not explicit in VISION; the `quick` slash command + setup flow imply the philosophy without naming it. | No tension; no direct lift. |
| Context rot (4 zones) | NOT VISIBLE in CONTEXT.md. GSD Pi's docs do not surface a context-rot model. | mise-en-place is *ahead* of GSD Pi here. Don't expect inspiration. |
| SPEC-driven (RESEARCH→SPEC→PLAN→TASK) | **EXTENDS**: GSD Pi uses milestone → slice → task and adds a runtime `Unit` abstraction one level below task. The `plan slice / execute task / complete slice` Unit type triad is the granular execution model. | Consider whether mise-en-place's TASK = GSD Pi's Unit, or whether a sub-task Unit concept is worth adding. |
| Worker as black-box (SUCCESS/FAILURE + pointer) | **EXTENDS**: GSD Pi's Recovery Classification adds typed failure classes beyond binary SUCCESS/FAILURE — provider-quota / tool-schema / deterministic-policy-block / stale-worker / worktree-invalid / reconciliation-drift / network / verification-drift. | mise-en-place should consider a *small* typed failure taxonomy (3-5 classes) instead of binary; binary is too coarse to drive distinct retry/escalate decisions. |

## 11. Recommendations for mise-en-place

| # | Action | Rationale | Source |
|---|---|---|---|
| 1 | **STEAL the `start/advance/resume/stop/getStatus` orchestrator interface** | Five-method surface is the right abstraction depth for an orchestrator; smaller than v1's 20+ tools, bigger than a single `run()` function. | gsd-pi CONTEXT.md ADR-014 |
| 2 | **STEAL the typed Recovery decision taxonomy** | `retry / pause with remediation / self-heal / stop` with one decision per failure class lets the framework prevent v1's "everything's a generic provider error" trap. | gsd-pi CONTEXT.md Recovery Classification module |
| 3 | **STEAL the drift catalog idea** | Detect drift between artifact disk-state and intended state; each drift kind has a named idempotent repair. Maps perfectly onto `.planning/` artifact reconciliation in mise-en-place. | gsd-pi CONTEXT.md ADR-017 |
| 4 | **STEAL the Tool Contract concept** | Compile per-Unit Tool Contract = prompt obligations + allowed tools + schema enums + validation + closeout tools. Sharper than dossier Pattern 24. | gsd-pi CONTEXT.md Tool Contract module |
| 5 | **STEAL the pre-dispatch invariant pipeline ordering** | `advance()` explicitly calls invariant modules in sequence; Dispatch never owns repair. Replaces v1's tangled pipeline. | gsd-pi CONTEXT.md ADR-014 |
| 6 | **STEAL the VISION's "What we won't accept" list as a CONTRIBUTING.md template** | Explicit anti-patterns (enterprise DI, framework swaps, cosmetic refactors, complexity without user value, heavy orchestration layers) save reviewer cycles. Use verbatim with attribution. | gsd-pi VISION.md |
| 7 | **AVOID adopting SQLite as state backend yet** | mise-en-place is intentionally stdlib-only; SQLite adds a binary dependency and a `sql.js` wrapper. Stick with markdown projections until size pressure justifies. | gsd-pi CONTEXT.md DB snapshot persistence module |
| 8 | **AVOID building a TUI / Studio / VSCode extension layer** | GSD Pi is a product; mise-en-place is a toolkit. Adding UI surfaces multiplies maintenance burden without solving the user's stated problem. | gsd-pi repo structure (vscode-extension/, studio/, web/, native/) |
| 9 | **AVOID worktree-per-task isolation in v0** | Defensible at scale but premature for mise-en-place's current state. Re-evaluate when parallel execution becomes load-bearing. | gsd-pi CONTEXT.md Worktree Safety/Lifecycle/Projection modules |
| 10 | **WATCH `open-gsd/gsd-core`** | The v1 community fork. May surface lessons about what to keep when subtracting v1 complexity. | https://github.com/open-gsd/gsd-core |
| 11 | **WATCH GSD Pi's extension model** | "Extension-first" principle is appealing but the actual extension API isn't in CONTEXT.md yet. See how it shakes out before borrowing. | gsd-pi VISION.md "Extension-first" |
| 12 | **DO NOT cite GSD Pi as evidence of an "OpenAI Agents SDK shift"** | The README in your root repo describes GSD-2 as "focused on building specialized agents with the Agents SDK." GSD Pi is explicitly provider-agnostic and does not depend on the OpenAI SDK. Correct the root README reference. | gsd-pi VISION.md "Provider-agnostic" |

## 12. Pages fetched

**Degree 0:**
- https://raw.githubusercontent.com/gsd-build/gsd-2/main/README.md (HTTP 200 — redirects to gsd-pi)
- https://raw.githubusercontent.com/gsd-build/gsd-2/main/VISION.md (HTTP 200 — historical philosophy)
- https://raw.githubusercontent.com/gsd-build/gsd-2/main/CONTEXT.md (HTTP 200 — full architecture: 18 KB)
- https://api.github.com/repos/gsd-build/gsd-2/contents (HTTP 200 — directory listing)
- https://raw.githubusercontent.com/open-gsd/gsd-pi/main/README.md (HTTP 200 — live README: 5.8 KB)
- https://raw.githubusercontent.com/open-gsd/gsd-pi/main/VISION.md (HTTP 200 — live VISION: 4.2 KB)
- https://api.github.com/repos/open-gsd/gsd-pi/contents (HTTP 200 — directory listing)

**Degree 1:** (referenced for context, not deep-fetched)
- https://pi.opengsd.net/ (web configurator — mentioned in README, not fetched)
- https://www.opengsd.net/promise (project history — mentioned in VISION, not fetched)
- https://github.com/open-gsd/gsd-core (v1 community fork — not deep-fetched)

## 13. Pages attempted but failed

- First WebFetch of `raw.githubusercontent.com/gsd-build/gsd-2/main/README.md` timed out on the initial attempt; retry succeeded.
- No 404s, no auth gates.
- gsd-pi CONTEXT.md was not re-fetched as a standalone (5.7 KB delta vs gsd-2's CONTEXT, structure inherited). Flagged as a confidence reduction in §14.

## 14. Confidence

**MEDIUM-HIGH.**

- HIGH on the project-identity facts: GSD-2 → GSD Pi pivot, provider-agnostic posture, repository layout, README/VISION content, the four named invariant modules, the Auto Orchestration interface.
- MEDIUM on architectural claims sourced from gsd-2's CONTEXT.md but not re-verified against gsd-pi's CONTEXT.md. The two repos share the architecture file structure and the gsd-pi README/repo strongly suggest the same architecture, but I did not diff the two CONTEXT files.
- MEDIUM-LOW on what GSD Pi "implements" vs "doesn't implement" from the 32-pattern dossier. I could only verify presence/absence from README + VISION + CONTEXT.md. Pattern presence in actual source code (the `src/`, `packages/`, `gsd-orchestrator/` directories I did not enumerate) may differ. Many pattern absences in §8 should read as "not visible in the docs read" rather than "definitely not present."
- LOW-MEDIUM on the OpenAI Agents SDK claim correction. The absence of evidence is not evidence of absence; the SDK could be used internally without being documented. But the explicit "provider-agnostic" principle makes any deep SDK lock-in unlikely.
- The MIGRATION FROM gsd-build/gsd-2 TO open-gsd/gsd-pi is HIGH-confidence (gsd-2 README literally says "GSD 2 Has Moved" and links to the new repo).

The `[inference]` tags throughout §3-§7 flag claims that are not stated verbatim in fetched sources but are reasonable reads of the file structure and stated principles.
