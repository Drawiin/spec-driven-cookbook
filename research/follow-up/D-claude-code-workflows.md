# Claude Code Dynamic Workflows — Inspiration Deep-Dive

> Researched: 2026-05-29
> Trigger: user spotted Anthropic's newly-shipped "Dynamic Workflows" feature and observed it "looks a lot like what we are trying to do, but more professional — actually running scripts to execute stuff."
> Primary source: [Claude Code — Orchestrate subagents at scale with dynamic workflows](https://code.claude.com/docs/en/workflows) (official docs).
> Related internal docs: [`../topics/workflow-and-orchestration.md`](../topics/workflow-and-orchestration.md) (§8 Pattern 21 — authored composition / Recipe-DAG), [`./C-worker-contract.md`](./C-worker-contract.md) (orchestrator-as-SKILL.md model).

## 1. One-paragraph summary

A **dynamic workflow** is a JavaScript script that orchestrates [subagents](https://code.claude.com/docs/en/sub-agents) at scale. Claude *writes the script* for the task you describe, and a dedicated runtime executes it in the background while your session stays responsive. The defining move: **the plan lives in code, not in the model's turn-by-turn context**. The loop, the branching, and the intermediate results all live in script variables, so the orchestrator's context window holds only the final answer. This lets a single run fan out to dozens-to-hundreds of agents (up to 16 concurrent, 1,000 total per run) and apply *repeatable quality patterns* — e.g. independent agents adversarially reviewing each other's findings, or drafting a plan from several angles and weighing them — rather than just running more agents. Runs are resumable within a session, approval-gated before launch, and savable as reusable `/commands`. It is **Claude-Code-only**, currently in research preview (requires v2.1.154+). The feature is strong external validation of mise-en-place's core architecture, while solving a *different layer* of the problem.

## 2. What it actually is (architecture)

From the docs' own comparison table, the distinction between primitives is "who holds the plan":

| | Subagents | Skills | Workflows |
|---|---|---|---|
| What it is | A worker Claude spawns | Instructions Claude follows | **A script the runtime executes** |
| Who decides what runs next | Claude, turn by turn | Claude, following the prompt | **The script** |
| Where intermediate results live | Claude's context window | Claude's context window | **Script variables** |
| What's repeatable | The worker definition | The instructions | **The orchestration itself** |
| Scale | A few per turn | Same as subagents | **Dozens to hundreds per run** |
| Interruption | Restarts the turn | Restarts the turn | **Resumable in the same session** |

Key runtime facts:

- **Isolated runtime.** The script runs in an environment separate from the conversation. The script itself has **no direct filesystem or shell access** — agents read/write/run commands; the script only coordinates them.
- **Limits.** Up to 16 concurrent agents (fewer on low-core machines); 1,000 agents total per run (runaway-loop guard); **no mid-run user input** (only agent permission prompts can pause a run — "for sign-off between stages, run each stage as its own workflow").
- **Resumability is in-session only.** Completed agents return cached results on resume; **exiting Claude Code restarts the workflow fresh** next session.
- **Approval + permissions.** A per-run approval card shows planned phases and a token-usage caution. Spawned subagents always run in `acceptEdits` mode and inherit the tool allowlist regardless of session mode.
- **Authoring paths.** Ask in-prompt with the keyword `workflow`; or `/effort ultracode` (xhigh reasoning + automatic workflow orchestration for every substantive task). Saved scripts become `/commands` in `.claude/workflows/` (project) or `~/.claude/workflows/` (personal).
- **Bundled example.** `/deep-research` fans web searches across angles, cross-checks sources, **votes on each claim**, and returns a cited report with claims that didn't survive cross-checking filtered out.

## 3. Side-by-side vs mise-en-place

| Concern | mise-en-place (this project) | Claude Code Workflows | Verdict |
|---|---|---|---|
| Core architecture | Thin orchestrator + specialized ephemeral workers | Orchestration script + subagents | **SAME idea** — strong validation |
| Context discipline | Each worker gets only what it needs; no context bloat (a core requirement) | Intermediate results in script variables; only final answer in context | **SAME goal**, different mechanism |
| Orchestrator substrate | Markdown `SKILL.md` interpreted by an LLM turn-by-turn | **JavaScript script executed by a runtime** | **DIFFERENT** — the gap the user spotted |
| Parallelism | Wave-based dependency parallelism (GSD pattern, deferred to Execute phase) | Fan-out, 16 concurrent / 1,000 per run | They ship it as a runtime primitive |
| Quality patterns | Self-healing: verifier, spec-drift reconciliation (Phase 6) | Adversarial cross-review; multi-angle planning; claim voting | Convergent — both move past "single pass" |
| State durability | Version-controlled `.planning/` files; survives sessions; diff-reviewable | Ephemeral script variables; resume **in-session only**, restarts fresh on exit | **mise-en-place is ahead here** |
| Human gating | Explicit approval gates between Spec / Plan / Execute phases | **No mid-run input**; one stage = one workflow for sign-off | **Different philosophy** (steered vs autonomous batch) |
| Methodology | Spec-driven (Spec → Plan → Execute) with requirement traceability | General-purpose orchestration (audit, migrate, research) | **mise-en-place's moat** |
| Replication | Generates tailored, self-contained `.cursor/` per project (Phases 7–8) | "Save as command" — not project-tailored | **No analog** |
| Runtime / ecosystem | Cursor-first; portable text artifacts | Claude-Code-only; tied to their runtime | Different ecosystems |

## 4. The core idea worth internalizing: plan-in-code, not plan-in-prose

Today mise-en-place's orchestrator is a **markdown `SKILL.md` an LLM interprets turn-by-turn** (the `orchestrator-as-SKILL.md` model in [`C-worker-contract.md`](./C-worker-contract.md) §5). Claude Code's central insight is that the orchestration *control flow* — fan-out, branching, intermediate-result handling, cross-review — is **more reliable, cheaper, and inspectable when it is a script**, with the LLM confined to the worker agents.

mise-en-place is already halfway there and **its own dossier predicted this destination**:

- It has a deterministic Python tooling layer (`validate_spec`, `detect_brownfield`, `scan_map_secrets`) — but those are **leaf-level gates**, not the control flow. Sequencing still lives in prose.
- [`../topics/workflow-and-orchestration.md`](../topics/workflow-and-orchestration.md) §8 already names the target — **Pattern 21 (OpenRewrite Recipe-DAG)**: *"Authored composition of typed transformations belongs in the workflow layer … high-level specs are then a YAML DAG of skills. The planner does tool-selection over the DAG, not over chat prompts."* Anthropic just shipped a production form of exactly that insight.

Note the **tension with prior follow-up research**: the [follow-up SUMMARY](./SUMMARY.md) §2 lists "No Recipe DAG / YAML composition layer (linear workflow skills are sufficient)" on the GSD-bloat REJECT list. Claude Code Workflows is a reason to **revisit that rejection** — not to adopt a heavy DAG today, but to recognize that *moving orchestration control flow out of prose and into code* is the direction a mature Execute phase should head. The reconciliation: reject the *premature* DAG; keep the *principle* that the orchestration loop is authored code, not LLM-interpreted markdown.

## 5. What it does NOT do (mise-en-place's moat)

Workflows are an orchestration **runtime**, not a methodology. The things it explicitly does not provide are precisely mise-en-place's value:

1. **Spec-driven discipline.** No Spec → Plan → Execute pipeline, no requirement traceability, no spec-drift reconciliation. Workflows are general-purpose ("audit endpoints", "migrate 500 files").
2. **Human approval gates / steering.** "No mid-run user input." mise-en-place is built around explicit per-phase approval gates and steering as a unit of work ([`../topics/workflow-and-orchestration.md`](../topics/workflow-and-orchestration.md) §8, Böckeler).
3. **Git-durable, inspectable state.** Their intermediate state is ephemeral script variables; resume works only within the same session. `.planning/` is version-controlled and survives sessions.
4. **The replication engine.** No per-project tailored `.cursor/` output. "Save as command" is reuse, not replication.
5. **Runtime portability.** Claude-Code-only vs mise-en-place's portable text artifacts.

## 6. Recommendations

| # | Action | Rationale | Source |
|---|---|---|---|
| 1 | **STEAL the plan-in-code principle for the Execute phase** | Move orchestration control flow (sequencing, fan-out, result-collection) out of `SKILL.md` prose into authored code; confine the LLM to workers. More reliable, cheaper, inspectable. | workflows docs §"When to use a workflow" |
| 2 | **STEAL the adversarial cross-review / claim-voting quality pattern** | A repeatable pattern where independent agents review each other's output beats a single pass — directly relevant to the Phase 6 self-healing/verifier design. | workflows docs §"When to use a workflow"; `/deep-research` |
| 3 | **REVISIT the Recipe-DAG REJECT decision** | The follow-up SUMMARY rejected a YAML composition layer as premature GSD-bloat. Keep rejecting the *heavy* form, but record that authored-code orchestration is the validated long-term direction. | this note §4; [`./SUMMARY.md`](./SUMMARY.md) §2 |
| 4 | **KEEP git-durable `.planning/` state as a deliberate advantage** | Their ephemeral, in-session-only state is a real limitation; do not trade away version-controlled, diff-reviewable state to chase their model. | workflows docs §"Resume after a pause" |
| 5 | **KEEP explicit approval gates** | Their "no mid-run input / one stage = one workflow" confirms gates are a design choice, not a deficiency. mise-en-place optimizes for steered delivery, they optimize for autonomous batch. | workflows docs §"Behavior and limits" |
| 6 | **WATCH as a future multi-runtime execution backend** | `PROJECT.md` defers multi-runtime as out-of-scope. Long term, their workflow runtime is a plausible executor target: mise-en-place spec/plan artifacts in, their runtime as one of several backends. | `PROJECT.md` Out of Scope; workflows docs |
| 7 | **DO NOT pivot the project** | The architecture is validated; the spec-driven methodology + replication engine remain uniquely mise-en-place's. This is a sharpening input, not a competitor that obsoletes the work. | this note §5 |

## 7. Implications for the roadmap

- **Phase 5 (Execute — Thin Orchestrator)**: the strongest target. Its design (`ROADMAP.md` Phase 5) should treat the orchestrator's control flow as *authored code* invoking workers, not an LLM-interpreted markdown loop. This is the single highest-leverage takeaway.
- **Phase 6 (Self-Healing Layer)**: adopt the adversarial cross-review / voting pattern as a verifier strategy, complementing the existing verifier + spec-drift reconciliation design.
- **Phases 7–8 (Replication Engine)**: unaffected — no analog exists in Claude Code; remains the project's differentiator.

## 8. Source and confidence

**Confidence: HIGH on the feature description**, MEDIUM on durability of specifics.

- HIGH: all factual claims about the feature trace directly to the official docs page ([code.claude.com/docs/en/workflows](https://code.claude.com/docs/en/workflows)) — architecture, the plan-in-code distinction, limits (16 concurrent / 1,000 total / no mid-run input), in-session-only resumability, approval/permission model, `/deep-research`, save-as-command.
- MEDIUM: the feature is explicitly a **research preview** (requires Claude Code v2.1.154+). Specifics (concurrency caps, ultracode behavior, exact phase UI) may drift as it leaves preview. Re-verify against the live docs before acting on any number.
- The comparison and recommendations are this project's synthesis, not Anthropic claims.

**No code fetched** — single authoritative source (official docs) was sufficient; no external verification beyond it was warranted.
