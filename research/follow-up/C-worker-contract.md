# Worker Contract Design — Synthesis for mise-en-place

> Researched: 2026-05-27
> Inputs: mise-en-place README, dossier (TLC sub-agent contract, GSD v1, BMAD personas, Task Master tool loading), OpenAI Agents SDK overview, GSD Pi Tool Contract / Recovery Classification (from companion file A-gsd2.md). Claude Agent SDK fetch timed out and was not included.
> Companion: A-gsd2.md (GSD Pi deep-dive), B-mise-en-place-audit.md (32-pattern coverage matrix; flags Pattern 6 as #2 SHOULD-ADOPT)

## 1. The design tension

mise-en-place's root README states two things that are in tension with the dossier:

1. **"Workers behave like black-box commands: invoke with context and input, receive a simple signal (`SUCCESS`/`FAILURE`) and a pointer to detailed output (usually markdown)."** — a *binary* outcome.
2. **"Self-healing"** as a core principle — but binary SUCCESS/FAILURE is too coarse to drive distinct retry/pause/self-heal/stop decisions (the lesson GSD Pi learned the hard way; see its Recovery Classification module).

Meanwhile, the user has explicitly rejected GSD v1's complexity (too many steps, too many tokens, equal-or-worse results) and TLC's openness (no clear execution workflow). Pattern 6 (Sub-Agent Context Contract) in the dossier is the most concrete TLC contribution but is "PARTIAL" in mise-en-place's audit — research sub-agents have an output file format but no explicit must-receive / must-NOT-receive lists. Pattern 24 (Self-Describing Skill Manifest) is also PARTIAL — current SKILL.md frontmatter has `name` + `description` only.

**This synthesis proposes a worker contract that keeps mise-en-place's binary stdlib exit-code semantics at the OS level while adding a small typed taxonomy at the artifact level — preserving the black-box principle while making self-healing actually buildable.**

## 2. Comparison: existing worker contracts

| Framework | Worker definition | Input contract | Output contract | Failure semantics | Multi-runtime? |
|---|---|---|---|---|---|
| **TLC spec-driven** | `tasks.md` task entry + SKILL.md reference | Fixed must-receive list (task def, coding-principles.md, CONVENTIONS.md, TESTING.md, referenced spec/design context). Fixed must-NOT-receive list (other tasks, chat history, validation reports, STATE.md unless referenced). | Fixed 5-field shape: Status (Complete/Blocked/Partial), Files changed, Gate check result, SPEC_DEVIATION markers, Issues encountered. | 3-tuple Status. `SPEC_DEVIATION` markers surfaced to orchestrator. Max 3 diagnostic iterations. | Stack-agnostic single SKILL.md |
| **GSD v1** | One of 33 named agent files in 11 categories | Compound-init JSON blob (project info, config, phase details, state). | Per-agent file output (`PLAN.md`, `RESEARCH.md`, `VERIFICATION.md` etc.). | Wave-based; failed agents trigger `gsd-debugger` → writes new `PLAN.md`. Binary fail/succeed per agent. | 15+ runtimes via install-time transform |
| **GSD Pi** | Typed `Unit` (plan slice / execute task / complete slice) with compiled Tool Contract per Unit type | Tool Contract: prompt obligations + allowed tools + schema enum values + validation rules + closeout tools. State pre-reconciled via `reconcileBeforeDispatch`. | SQLite + `.gsd/` markdown projections; typed `DriftRecord[]` for state issues; `completed-units.json` is crash-recovery authoritative. | **Typed Recovery decision**: `retry / pause with remediation / self-heal / stop` mapped from failure class (tool-schema / deterministic-policy / stale-worker / worktree-invalid / provider-quota / network / verification-drift / reconciliation-drift). | Single Node CLI; provider-agnostic |
| **BMAD personas** | 12+ specialized agent persona files (PM, Architect, Dev, QA, SM, Analyst, etc.) | Persona-specific prompts; pre-baked story context delivered to Developer agent. | Persona-specific markdown artifacts (PRD, architecture, story, etc.). | Multi-agent reviews; TEA module; retro phase. Persona handoff is the failure surface. | Claude Code, Cursor via npx |
| **Task Master tools** | MCP tool calls (typed parameters, single output) | Tiered tool loading (~5k–21k tokens depending on tier). | Single MCP tool response. | `complexity-report` + fallback model role. | MCP server across 5 IDEs |
| **OpenAI Agents SDK** | `Agent(name, instructions, tools)` + Handoff (agent-as-tool) | Instructions string + tool definitions (Python functions auto-schemed by Pydantic) + optional MCP servers + optional Session. | Final output via `Runner.run_sync(agent, input)`; `result.final_output`; intermediate run items inspectable. | Guardrails (parallel input/output validation, fail-fast). Sandbox agents for isolated workspace + resumable sessions. | OpenAI-default, supports non-OpenAI providers via Models config |
| Claude Agent SDK | (fetch timed out — not included; see §10) | — | — | — | — |

## 3. What the dossier already says

- **Pattern 6 (Sub-Agent Context Contract)** — TLC's fixed input/output contract is the closest analog. The 5-field output shape (Status / Files / Gate / Deviations / Issues) is reusable verbatim; the "must NOT receive" list is what prevents context pollution.
- **Pattern 24 (Self-Describing Skill Manifest with Estimated Effort)** — OpenRewrite's recipe descriptor model: every skill publishes parameters, displayName, description, tags, `estimatedEffortPerOccurrence`. Sibling to Pattern 15 (install-time profile) but addresses planner tool-selection rather than install scope.
- **Pattern 29 (Guides + Sensors Taxonomy)** — every control declares whether it's a guide (feedforward), sensor (feedback), or both. mise-en-place's SKILL.md files are implicit guides; `tool-*` validators are sensors; explicit labeling forces designers to notice when a "spec" item has no paired sensor (unverifiable).
- **Pattern 30 (Computational vs Inferential Control Labelling)** — second axis: deterministic (linters, type checkers) vs LLM-based. Drives lifecycle placement (cheap deterministic checks on hot path, expensive inferential checks at phase gates).
- **Pattern 21 (Recipe DAG)** — declarative YAML composition surface for skills; planner does tool-selection over the DAG, not over chat prompts. **Note**: B's audit marked this REJECT for mise-en-place ("GSD/OpenRewrite complexity; mise-en-place is intentionally flat SKILL + script"). The worker contract below honors that rejection — workers compose via linear workflow skills, not via a YAML DAG planner.

## 4. Proposed canonical worker contract for mise-en-place

### 4.1 Worker file layout

A worker lives at `mise-en-place/worker-<type>-<name>/` (sibling to existing `tool-*/` and workflow-skill dirs). Each worker contains:

```
mise-en-place/worker-<type>-<name>/
├── SKILL.md              # Agent contract: when to invoke, inputs, outputs, frontmatter manifest (see §4.2)
├── worker.py             # Optional: stdlib Python entrypoint for deterministic workers; absent for inferential
├── prompt.md             # Optional: required for inferential workers (LLM-driven); the system-prompt baked into the worker
├── test_worker_contract.py  # pytest contract test (mirrors mise-en-place/spec-phase/test_spec_phase_contract.py)
└── README.md             # Optional: long-form human docs
```

Rationale: matches the existing `tool-*/` house style; `prompt.md` separation lets inferential workers ship their prompt as a versioned artifact (not buried in SKILL.md prose).

### 4.2 Manifest (SKILL.md frontmatter)

Required YAML frontmatter fields (minimum viable; bias to fewer fields):

```yaml
name: worker-<type>-<name>
description: One sentence, ≤140 chars, for routing.
type: researcher | planner | validator | executor | debugger | reviewer
mode: computation | inference          # Pattern 30 axis (deterministic vs LLM-based)
control: guide | sensor | both          # Pattern 29 axis (feedforward vs feedback)
inputs:                                 # explicit, ordered
  - name: spec_path
    kind: file
    required: true
  - name: codebase_root
    kind: dir
    required: true
outputs:
  artifact_path: .planning/workers/<worker_id>/output.md   # see §4.4
  side_effects: []                      # list of files/dirs the worker may write outside its artifact_path
retry_safe: true                        # true = transient failure (exit 1) may be retried; false = exit 2+ on any failure
estimated_tokens_max: 4000              # for context-rot budgeting (root README zones)
```

**Why each field is load-bearing:**

- `type` — drives orchestrator dispatch + maps to the six README-named worker types.
- `mode` (Pattern 30) — orchestrator uses this to decide hot-path eligibility: `computation` workers may run on the pre-commit hot path; `inference` workers only at phase gates.
- `control` (Pattern 29) — design-time check: every `spec`/`plan`/`task` item should have a paired `sensor` worker that can verify it. Refuse to mark unverifiable items "complete."
- `inputs` — explicit must-receive list (replaces TLC's prose contract). Orchestrator validates these exist before dispatch.
- `outputs.artifact_path` — see §4.4; convention not free choice.
- `outputs.side_effects` — explicit declaration so the orchestrator can verify no unauthorized writes (GSD Pi's Worktree Safety idea, lighter).
- `retry_safe` — drives the retry rule in §4.5.
- `estimated_tokens_max` — feeds the context-rot health zones (root README); orchestrator refuses dispatch if loading this worker would push aggregate context past 60% (Danger zone).

**Fields explicitly NOT included** (cut for minimalism):

- `parameters` — workers consume positional `inputs`; parameter polymorphism is a v2 concern.
- `tags` — the six `type` values are taxonomy enough.
- `version` — git history is the version.
- `estimatedEffortPerOccurrence` (from Pattern 24) — overkill for a stdlib toolkit; revisit when there are 30+ workers.

### 4.3 Invocation contract

**Orchestrator invokes worker via Shell** (mise-en-place's house contract):

```shell
python3 mise-en-place/worker-<type>-<name>/worker.py \
  --spec-path .planning/SPEC.md \
  --codebase-root . \
  --artifact-path .planning/workers/<worker_id>/output.md
```

Or for inferential workers, the orchestrator (a workflow SKILL.md) does:

> 1. Read `worker-<type>-<name>/SKILL.md` and `prompt.md`.
> 2. Spawn a sub-agent (Task tool / equivalent) passing ONLY the must-receive list.
> 3. Sub-agent writes its output to `.planning/workers/<worker_id>/output.md`.
> 4. Sub-agent returns the path; orchestrator never reads the body.

**Must receive** (orchestrator MUST pass):
- Resolved `inputs` from the manifest (file/dir paths only — never file contents inline).
- The `artifact_path` where the worker will write its output.
- Optional: a `worker_id` (UUID or `<type>-<name>-<ts>` slug) for traceability.

**Must NOT receive** (borrowed from TLC Pattern 6 — explicit):
- Other workers' output artifacts (read on demand by file path if truly needed).
- Accumulated chat history.
- The orchestrator's full `.planning/STATE.md` (unless an input explicitly references a decision/blocker ID).
- Previous workers' detailed failure reports (only the typed status).
- Repository-wide file contents (workers read what they need from declared `inputs`).

**Required environment / preconditions:**
- All `inputs` (files/dirs) exist and are readable.
- Aggregate context after loading this worker stays in the Smart (0–40%) or Warning (40–60%) zones; if Danger (60–80%) or Rot (80–100%), abort dispatch and trigger context compaction first.
- `tool-validate-spec` has run (if the worker needs an approved SPEC).
- `tool-scan-map-secrets` has passed (if the worker reads `.planning/codebase/*.md`).

### 4.4 Output contract

Workers write their output to **one canonical file**:

```
.planning/workers/<worker_id>/output.md
```

Required header (YAML frontmatter):

```yaml
---
worker: worker-<type>-<name>
worker_id: <id>
status: SUCCESS | FAILURE | PARTIAL    # 3-state, not binary; mirrors TLC's Status
failure_class: <see §4.5>              # required iff status != SUCCESS
runtime: cursor | claude-code | gemini | other
model: <model id>                       # for traceability (Pattern 11 extension: per-hunk attribution)
started_at: <ISO 8601>
finished_at: <ISO 8601>
inputs_consumed:                       # ordered, resolved paths
  - .planning/SPEC.md
side_effects_written:                  # files actually touched outside artifact_path
  - .planning/codebase/STACK.md
next_step: <one of: continue | review | retry | escalate>
---
```

Body sections (recommended, not enforced):

```markdown
## Summary
3-5 sentences. What was done, what wasn't, why.

## Files changed
(omit for researcher/reviewer types)

## Gate results
(for validator/reviewer types: PASS / FAIL per gate)

## SPEC_DEVIATION markers
(if applicable — Pattern 11)

## Issues encountered
(if applicable)
```

**Orchestrator consumes the output as follows:**

- Reads ONLY the frontmatter to decide next step.
- Treats the body as a pointer for human review or downstream worker input — never inlines into orchestrator context.
- Token-budget cap on body: **≤ 4000 tokens** (per Pattern 3 health zones; matches the manifest's `estimated_tokens_max` default). Workers that need to produce more must split into multiple worker invocations.

### 4.5 Failure semantics and retry

Exit code mapping (stdlib `sys.exit(N)`):

| Exit | Status frontmatter | Meaning | Orchestrator action |
|---|---|---|---|
| 0 | SUCCESS | Worker completed; `next_step` field drives flow | Read `next_step`, proceed |
| 1 | FAILURE / `failure_class: transient` | Network blip, model timeout, rate-limit — retry-safe | Retry up to 2x with exponential backoff; if still failing, escalate |
| 2 | FAILURE / `failure_class: input_invalid` | Required `inputs` missing/malformed; precondition not met | Do NOT retry; surface the missing precondition to the user |
| 3 | FAILURE / `failure_class: spec_violation` | Worker would produce a SPEC_DEVIATION but cannot autonomously decide | Do NOT retry; pause for human review; debugger worker may be invoked |
| 4 | FAILURE / `failure_class: tool_contract_breach` | Worker tried to write outside `side_effects` or `artifact_path`, or exceeded `estimated_tokens_max` by >50% | Do NOT retry; escalate as bug in worker; debugger worker may be invoked |
| 5 | PARTIAL / `failure_class: scope_overrun` | Worker did meaningful but incomplete work; `next_step: continue` with sub-task list | Retry with narrowed scope OR accept partial as new baseline |

Rationale for the small taxonomy (5 typed classes, not GSD Pi's 8):

- **`transient`** vs **`input_invalid`**: separates "try again, may work" from "fix the inputs."
- **`spec_violation`** = the diagnose-into-PLAN trigger (Pattern 8): debugger worker reads this, drafts a SPEC_DEVIATION acceptance proposal, surfaces to human.
- **`tool_contract_breach`** = GSD Pi's Worktree Safety equivalent, but for file-write scope rather than git-worktree validity. Worker violated the contract; this is a bug, not a recoverable failure.
- **`scope_overrun`** = vertical-slice constraint (Pattern 5 extension). Worker tried to do too much; partial result is salvageable.

**Retry policy**: max 2 retries for `transient`; **never** retry for `input_invalid`, `spec_violation`, or `tool_contract_breach`; for `scope_overrun`, retry once with explicit narrowing instructions.

**On failure escalation**: orchestrator spawns the `worker-debugger-default` (Pattern 8 — Diagnose-into-PLAN). Debugger reads the failed worker's output frontmatter (NOT the body), classifies the root cause, and writes a repair plan to `.planning/workers/<debugger_id>/output.md` with `next_step: continue` pointing at a fix worker. No "fix mode" — debugger is just another worker.

### 4.6 Per-worker-type specializations

- **researcher**: `control: sensor`, `mode: inference`. Outputs `summary` + `evidence` + `confidence` (HIGH/MEDIUM/LOW per Pattern 13). `next_step: continue` with handoff to planner.
- **planner**: `control: guide`, `mode: inference`. Outputs `tasks: [...]` list (each with id, dependencies, retry_safe, estimated_tokens_max). `next_step: continue` to first executor.
- **validator**: `control: sensor`, `mode: computation`. Pure-stdlib script (no LLM). Outputs `gate_results` table. Exit 0 = pass, exit 1 = soft fail (warn), exit 2 = hard fail (block).
- **executor**: `control: both` (carries its own guides + emits its own sensor signals via diff hunks). `mode: inference`. Outputs `files_changed` + `commit_message_draft`. Required: each diff hunk carries `worker_id` + `model` provenance (Pattern 11 extension).
- **debugger**: `control: sensor`, `mode: inference`. Reads upstream worker output frontmatter only; outputs a repair plan with `next_step: continue` to a fix worker. Pattern 8 mechanism.
- **reviewer**: `control: sensor`, `mode: inference`. Reads diff hunks + spec; outputs `findings` list per Pattern 11 redundancy axis (flags duplicate tests, over-engineered abstractions). `next_step: review` (human gate) by default.

## 5. Composition primitives

**Workers compose into a PLAN, not via a YAML DAG** (per B's audit REJECT of Pattern 21):

- The PLAN is a numbered Markdown task list (per mise-en-place's existing `spec-phase` pattern + GSD Pi's milestone → slice → task hierarchy).
- Each task in the PLAN names exactly one worker invocation + its resolved `inputs`.
- Tasks declare dependencies inline (`depends_on: [task-id, ...]`).
- Parallel-safe tasks carry `[P]` (TLC Pattern 12, three-condition gate adapted for workers).
- The orchestrator (a workflow SKILL.md, NOT a runtime daemon) reads the PLAN, dispatches workers per task in dependency order, retries per the §4.5 rules, and stops at the first hard-fail (`failure_class: input_invalid / spec_violation / tool_contract_breach`).

**Where the orchestrator lives**: as a workflow SKILL.md (matching `spec-phase/SKILL.md` and `map-codebase/SKILL.md`). NOT as a Python daemon or a long-running process. The orchestrator is just a skilled-prompt that reads the PLAN and invokes workers via Shell / sub-agent dispatch. This preserves mise-en-place's stdlib-only runtime posture.

## 6. What this contract REJECTS from GSD

Following the user's stated objections (too many steps / too many tokens / equal-or-worse results), this contract explicitly does NOT include:

- **No `requires:` frontmatter dependency closure** (Pattern 15) — eight workers don't need install-time profile machinery.
- **No 33-named-persona-agent roster** (v1 model) — six `type` values cover the worker taxonomy.
- **No two-stage namespace routing** (Pattern 2) — direct worker invocation by name; no router meta-skill.
- **No compound init handlers** (Pattern 1 in its v1 form) — workers receive resolved `inputs`, not a compound state blob. Init is the orchestrator's job, not boilerplate inside every worker.
- **No wave-based parallelism with O_EXCL lockfile** (Pattern 7) — sequential workers by default; `[P]` markers allow narrow parallelism (e.g. multiple researchers) without lockfile machinery.
- **No SQLite state backend** — `.planning/` markdown files only, per mise-en-place's stdlib-only stance.
- **No worktree-per-task isolation** — git is left to the user / IDE; workers write to `.planning/workers/<id>/output.md` which is artifact-namespaced.
- **No runtime daemon / persistent process** — the orchestrator is a SKILL.md that the IDE agent runs, not a long-running Node process.
- **No multi-runtime install-time transform** (v1's 469KB `install.js`) — single Python stdlib toolkit; the SKILL.md is the cross-runtime interface.

## 7. What this contract BORROWS from each source

| Borrowed from | What | Why |
|---|---|---|
| TLC Pattern 6 | Fixed must-receive / must-NOT-receive lists; 5-field output shape (adapted to 4 + frontmatter) | The single most concrete and tested worker contract in the dossier. |
| TLC Pattern 11 | SPEC_DEVIATION markers in worker output frontmatter; surfaced as `failure_class: spec_violation` | Composable with the diagnose-into-PLAN escalation. |
| GSD Pi Tool Contract module | The idea that prompt + allowed tools + schema + validation are *compiled* per worker type | Concrete way to prevent prompt/policy/schema drift the user complained about in v1. |
| GSD Pi Recovery Classification | Typed `failure_class` taxonomy with intentional action per class | Replaces binary SUCCESS/FAILURE without exploding into v1's "everything is generic provider error" trap. |
| GSD Pi `advance()` interface | Orchestrator pattern: read state → dispatch worker → handle outcome → repeat | 5-method orchestrator interface is the right depth (not 20+ tools, not 1 `run()`). |
| OpenAI Agents SDK | Guardrails as parallel input/output validation; Agents-as-tools / Handoffs | Validates the worker-type taxonomy; `guide`/`sensor` label maps onto SDK's tools + guardrails distinction. |
| OpenAI Agents SDK | Function tools auto-schemed from Python signatures | Justifies keeping workers as Python scripts — the SDK shows the abstraction works at this granularity. |
| OpenRewrite (Pattern 24) | Self-describing skill manifest with typed fields | Adopted; trimmed to load-bearing fields only. |
| Harness Engineering (Patterns 29/30) | guide/sensor + computation/inference axes | Forces unverifiable specs to be flagged at design time. |
| mise-en-place existing | SKILL.md + Python stdlib + exit 0/1; idempotent scaffolds; fail-closed gates | The new contract extends, not replaces, the house style. |

## 8. Implementation roadmap for mise-en-place

A minimal vertical slice that proves the contract works end-to-end:

1. **Add `mise-en-place/contracts/worker.md`** documenting §4.1–§4.6 of this file as the canonical contract (cite this synthesis file).
2. **Update existing `tool-*/SKILL.md` files** with the new frontmatter (`type`, `mode`, `control`, `inputs`, `outputs`, `retry_safe`, `estimated_tokens_max`) — they're all `type: validator`, `mode: computation`, `control: sensor`.
3. **Build `worker-validator-spec-approved/`** as the first worker (wraps existing `tool-validate-spec`) — demonstrates that an existing tool can become a worker without rewriting the script, just by adding manifest + artifact-write + frontmatter to stdout.
4. **Build `worker-debugger-default/`** as the second worker (per §4.5 escalation) — minimum viable to demonstrate the diagnose-into-PLAN loop.
5. **Build `plan-phase/SKILL.md`** as the first orchestrator-workflow-skill that consumes a PLAN, dispatches workers per task, and handles failures per §4.5.

Each step should ship behind a pytest contract test mirroring the existing `test_spec_phase_contract.py` pattern.

## 9. Open questions

- **Worker ID generation**: UUIDv4 or `<type>-<name>-<ts>` slug? UUID is safer for concurrent dispatch; slug is more human-readable in `.planning/workers/` directory listings. **Recommendation**: slug for the common case; UUID suffix only on collision.
- **Inferential worker prompt versioning**: when an executor's `prompt.md` changes, do existing worker output artifacts become invalid? **Recommendation**: track `prompt_hash` in output frontmatter; invalidation policy is the orchestrator's call.
- **Sub-agent runtime portability**: the orchestrator-as-SKILL.md model assumes the host IDE has a Task / sub-agent dispatch tool. Cursor + Claude Code do; Gemini's equivalent is less clear. **Recommendation**: workflow SKILL.md documents both the sub-agent dispatch path AND a fallback "user runs the Python script directly" path for runtimes without sub-agent support.
- **Claude Agent SDK alignment**: I could not fetch the Claude Agent SDK docs (timeout). Whether the contract above maps cleanly to Claude's agent primitives is unverified. Risk: low (the SKILL.md + Shell-invoked Python pattern is runtime-agnostic by design), but the SDK may have a more idiomatic invocation surface.
- **Context-rot enforcement before dispatch**: §4.3 says the orchestrator must refuse dispatch if loading the worker pushes context past 60%. The orchestrator needs a way to *estimate* aggregate context before dispatch. **Recommendation**: build `tool-context-health/` (B audit's SHOULD-ADOPT #5) before the first inferential worker ships.
- **Reviewer worker scope**: does `reviewer` mean "human-gated review" or "AI-as-judge review"? §4.6 says `next_step: review` by default but the line between these is fuzzy. **Recommendation**: ship `worker-reviewer-ai-judge` (inferential) and `worker-reviewer-human-pause` (just sets `next_step: review` and writes a summary) as two distinct worker types from the start.

## 10. Confidence

**MEDIUM-HIGH.**

- HIGH on the synthesized contract's internal consistency: §4.1–§4.6 compose; the failure taxonomy (§4.5) maps cleanly to the dispatch contract (§4.3); the artifact-path convention (§4.4) extends mise-en-place's existing `.planning/` layout naturally.
- HIGH on the borrowings from TLC Pattern 6 (the single most-cited contract in the dossier and the closest match for mise-en-place's intent).
- MEDIUM-HIGH on the GSD Pi Tool Contract / Recovery Classification adaptations — read from A-gsd2.md which was MEDIUM-HIGH confidence itself (architectural claims sourced from gsd-2 CONTEXT not re-verified against gsd-pi CONTEXT).
- MEDIUM on the OpenAI Agents SDK comparison — I read only the overview page; quickstart and sandbox-agents pages would sharpen the comparison.
- MEDIUM-LOW on multi-runtime portability claims — the contract assumes a host IDE with a sub-agent dispatch tool. This is true for Cursor and Claude Code; less verified for Gemini, VSCode-with-Continue, and other long-tail runtimes. Flagged as Open Question #3.
- LOW on the Claude Agent SDK alignment — fetch timed out; not researched. Flagged as Open Question #4.
- Did NOT read (deliberately, for token economy): all `frameworks/*.md` deep-dives in full (used Grep against the patterns file instead); GSD Pi `src/` source code; OpenAI Agents SDK quickstart pages beyond the overview.

This contract should be treated as a **first draft for the user to mark up**, not a finished spec. The five "Open questions" in §9 are blockers for finalization; the orchestrator-as-SKILL.md model in §5 is the highest-risk design choice and would benefit from a prototype before committing.
