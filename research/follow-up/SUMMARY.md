# Follow-Up Research — SUMMARY

> Compiled: 2026-05-27
> Triggered by: user feedback (GSD too complex / TLC too open) + updated repo READMEs (`README.md` + `mise-en-place/README.md`) pulled from `origin/main`.
> Three parallel research artifacts, each linked below.

## What you asked for

> "Pull remote develop … and do one more step of research" — you reported GSD is too complicated / token-heavy and TLC-spec-driven is too open (no clear agent execution workflow), and you wanted the new READMEs to inform the next research step.

## What this folder contains

| File | Scope | One-line takeaway |
|---|---|---|
| [`A-gsd2.md`](./A-gsd2.md) | GSD-2 deep-dive (now **GSD Pi**) | The user's referenced `gsd-build/gsd-2` repo has moved to `open-gsd/gsd-pi`; it is **provider-agnostic, NOT OpenAI Agents SDK-based** (correcting the root README's claim), and its sharpest contributions are the typed Recovery Classification taxonomy, the drift catalog, and the compiled-per-Unit Tool Contract. |
| [`B-mise-en-place-audit.md`](./B-mise-en-place-audit.md) | mise-en-place ↔ 32-pattern dossier coverage matrix | mise-en-place currently implements ~40% of its stated philosophy (SPEC slice only) and is **ahead of the dossier** on fail-closed secret scanning, brownfield Already-Built/To-Build dedup, and SKILL+stdlib contract tests. Top 5 SHOULD-ADOPTs: Pattern 8 (Diagnose-into-PLAN), 6 (Sub-Agent Contract), 1 (Compound Init), 22 (Precondition Scope Filter), 3 (Context-rot zones). |
| [`C-worker-contract.md`](./C-worker-contract.md) | Canonical worker contract spec for mise-en-place | Concrete `mise-en-place/contracts/worker.md` draft — file layout, YAML manifest fields, must-receive/must-NOT-receive lists, 5-state typed failure taxonomy (replaces binary SUCCESS/FAILURE without exploding into GSD v1's 8-class trap), per-worker-type specializations, and an explicit REJECT list of GSD complexity. |
| [`D-claude-code-workflows.md`](./D-claude-code-workflows.md) *(added 2026-05-29)* | Anthropic's Claude Code Dynamic Workflows as an inspiration source | Validates mise-en-place's thin-orchestrator + ephemeral-worker + context-discipline architecture, but solves a different layer. Core borrow: **plan-in-code, not plan-in-prose** — move Execute-phase orchestration control flow out of `SKILL.md` prose into authored code (confirms the Pattern 21 Recipe-DAG direction, and reopens the SUMMARY §2 "no Recipe DAG" rejection in *principle*). mise-en-place's moat (spec-driven methodology, git-durable state, approval gates, replication engine) is untouched — do not pivot. |

## Cross-cutting findings (where the three artifacts agree)

### 1. mise-en-place's positioning is correct, but its README mischaracterizes GSD-2

mise-en-place's design philosophy (orchestrator + ephemeral workers, self-healing, context-rot zones, SPEC-driven, black-box workers) is consistent across all three artifacts as a defensible sweet-spot between GSD v1's complexity and TLC's openness. **However, the root `README.md` reference to "GSD-2: Follow-up focused on building specialized agents with the Agents SDK" is inaccurate** — GSD Pi (the live successor to gsd-build/gsd-2) is explicitly provider-agnostic per its VISION.md. Recommend updating the root README's GSD-2 reference to:

> [GSD Pi (formerly GSD-2)](https://github.com/open-gsd/gsd-pi): Community-maintained successor to GSD; provider-agnostic, local-first; sharper architectural primitives (typed Recovery decisions, drift catalog, compiled per-Unit Tool Contract). Not Agents-SDK-based.

### 2. The "GSD-bloat" rejections are concrete and consistent

The B audit's REJECT list (Patterns 2, 7, 9, 15, 20, 21) and the C contract's "What this contract REJECTS from GSD" section name the same things by different routes:

- No two-stage namespace routing (8 tools don't need routers).
- No wave-based parallelism with O_EXCL lockfile (premature; `map-codebase` parallelism is enough until execute-phase ships).
- No three-role model config (delegate to host IDE).
- No install-time profile + surface toggle (stdlib toolkit; everything always available).
- No LST per-language IR substrate (contradicts stdlib-only).
- No Recipe DAG / YAML composition layer (linear workflow skills are sufficient).
- No SQLite state backend, no worktree-per-task isolation, no multi-runtime install-time transform.

This forms a coherent "GSD anti-pattern" stance that the mise-en-place README could codify as a "What we won't accept" section (modeled on [GSD Pi's VISION](https://github.com/open-gsd/gsd-pi/blob/main/VISION.md) which already does this well).

### 3. Three load-bearing borrowings from GSD Pi (despite the user's complexity rejection)

GSD Pi v2 has stripped down v1's complexity but kept (and sharpened) three patterns mise-en-place should adopt:

| GSD Pi pattern | mise-en-place adoption (via C-worker-contract.md) |
|---|---|
| `start/advance/resume/stop/getStatus` orchestrator interface | The orchestrator-as-SKILL.md in C §5 implements this shape without a runtime daemon. |
| Typed Recovery decision taxonomy (`retry / pause / self-heal / stop` mapped from explicit failure classes) | C §4.5 adapts this into a 5-class `failure_class` taxonomy on worker output frontmatter. |
| Compiled per-Unit Tool Contract (prompt + allowed tools + schema + validation + closeout) | C §4.2 captures this as YAML frontmatter fields on each worker's SKILL.md. |

GSD Pi's drift catalog and Worktree Safety are deferred — they're sharper than the dossier coverage but premature for mise-en-place's current scope.

### 4. mise-en-place is ahead of the dossier in three places

B's audit identifies three patterns mise-en-place implements that have no direct dossier coverage:

1. **Single-script-per-tool with SKILL.md contract** (stdlib Python, exit 0/1, agent reads SKILL for invocation) — the house style itself is a transferable pattern.
2. **Fail-closed secret scan between mapper writes and downstream reads** (`scan_map_secrets.py` exits 1 to block downstream phases) — sharper than the dossier's general slopcheck coverage.
3. **Brownfield map completeness gate** (seven canonical files, each >20 lines, before Q&A proceeds) — the dossier covers brownfield mapping but not the structured completeness gate.

These should be flagged in any future dossier-update pass as additions worth promoting to Patterns 33–35.

## Concrete next actions for mise-en-place

Ordered by leverage × tractability:

1. **Update the root `README.md` "References" section** to correct the GSD-2 attribution per finding 1 above. (5 min.)
2. **Add `mise-en-place/contracts/worker.md`** from C §4.1–§4.6 as the canonical worker contract. Cite C-worker-contract.md as source. (30 min.)
3. **Update existing 7 SKILL.md files** with the new frontmatter (`type`, `mode`, `control`, `inputs`, `outputs`, `retry_safe`, `estimated_tokens_max`). All current tools are `type: validator`, `mode: computation`, `control: sensor`. (1 hour.)
4. **Build `worker-debugger-default/`** as the second new worker (Pattern 8 mechanism). Demonstrates the diagnose-into-PLAN escalation loop end-to-end with the new contract. (Half day.)
5. **Build `tool-phase-init/`** (B audit SHOULD-ADOPT #3) — one Shell call returning JSON: scaffold status + brownfield detection + env check + spec status + map completeness + context snapshot path. Replaces repeated Step-1 shell sequences in `spec-phase` and future `plan-phase`. (Half day.)
6. **Build `tool-context-health/`** (B audit SHOULD-ADOPT #5) — token estimation for `.planning/*` artifacts; warn at 40–60%, block expansion at 80% per root README zones. Required before the first inferential worker ships safely. (Half day.)
7. **Draft `plan-phase/SKILL.md`** as the first orchestrator-workflow that consumes a PLAN and dispatches workers per the new contract. Treat as a prototype; expect to iterate. (1 day.)

Step 7 is the riskiest — it's the first real test of the orchestrator-as-SKILL.md model. Recommend prototyping against ONE concrete task (e.g. "run validate-spec then a single inferential worker") before generalizing.

## Pipeline summary (sub-agents used in this research)

| Wave | Agents | Outcome |
|---|---|---|
| Wave 1A — GSD-2 deep-dive | 1 generalPurpose subagent | Stalled after planning step. Parent agent took over directly: fetched gsd-build/gsd-2 + open-gsd/gsd-pi READMEs / VISIONs / CONTEXTs, wrote `A-gsd2.md`. |
| Wave 1B — mise-en-place audit | 1 readonly `explore` subagent | **Completed the audit work** but couldn't write the file (read-only mode — parent's error in tool selection). Parent extracted the full audit content from the subagent's transcript and wrote `B-mise-en-place-audit.md` verbatim. |
| Wave 1C — Worker contract synthesis | 1 generalPurpose subagent | Stalled after reading the two README files. Parent took over: fetched OpenAI Agents SDK overview (Claude Agent SDK timed out), read GSD Pi research from Wave 1A, synthesized `C-worker-contract.md`. |
| Wave 2 — Consolidation | Parent directly | This file. |

**Lesson re-learned from the previous pipeline**: long-form research subagents stall reliably after the initial planning step. Future research passes should default to either (a) parent-direct fetching with sub-summary slots, or (b) fan-out fetchers (1 URL each) + parent-side synthesis. The "one big synthesis agent" pattern is unreliable in this environment.

## Uncommitted dossier work from the prior session

The previous research pipeline (May 24) left modifications to four files uncommitted:
- `research/SUMMARY.md`
- `research/topics/patterns-worth-stealing.md`
- `research/topics/self-healing-and-verification.md`
- `research/topics/workflow-and-orchestration.md`

Plus `research/external-sources/` (the prior summaries/reviews/evaluations/INCORPORATION-REPORT). These coexist with the new `research/follow-up/` directory written today. **Not committed pending your instruction.**
