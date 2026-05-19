# TLC Spec-Driven Research Findings (Raw Cache)

> Source: tech-leads-club/agent-skills — `tlc-spec-driven` skill v2.0.0  
> Author: Felipe Rodrigues (github.com/felipfr)  
> License: CC-BY-4.0  
> Cached from: research sub-agent run 2026-05-19  
> Agent ID: 59e11448-8800-4db7-9f3c-6117bbff20b1  
> All 17 files (SKILL.md + 16 reference files) fetched successfully.

**Note:** The named principles "Beyoncé Rule" and "Chesterton's Fence" do NOT appear in this skill. They are part of a different rulebook (ArcTouch rules). Not attributed to tlc-spec-driven.

---

## 1. Overview & Philosophy

`tlc-spec-driven` is a stack-agnostic skill that orchestrates project and feature work through **four adaptive phases** — Specify → Design → Tasks → Execute — with the promise of "Granular tasks. Clear dependencies. Right tools. Zero ceremony."

**The four phases (from `SKILL.md`):**

```
┌──────────┐   ┌──────────┐   ┌─────────┐   ┌─────────┐
│ SPECIFY  │ → │  DESIGN  │ → │  TASKS  │ → │ EXECUTE │
└──────────┘   └──────────┘   └─────────┘   └─────────┘
   required      optional*      optional*     required
```

**Auto-Sizing as the load-bearing idea:**

> "The complexity determines the depth, not a fixed pipeline. Before starting any feature, assess its scope and apply only what's needed."

Specify and Execute are always required; Design and Tasks are auto-skipped when scope doesn't justify them. Discuss (sub-step of Specify) and Interactive UAT (sub-step of Execute) are triggered conditionally rather than scheduled.

**Named principles / behavioral rules present in the skill:**

| Principle | Where | What |
|---|---|---|
| Auto-Sizing | `SKILL.md` | Pipeline depth = task complexity. |
| Safety valve | `SKILL.md`, `implement.md` | Execute must list atomic steps inline; >5 steps = STOP, create formal `tasks.md`. |
| Knowledge Verification Chain | `SKILL.md` | Strict 5-step ordered ladder before any technical claim. |
| NEVER assume or fabricate | `SKILL.md`, `design.md` | "Uncertainty is always preferable to fabrication." |
| Scope Guardrail | `discuss.md`, `implement.md` | Discussion clarifies HOW, never WHETHER to add capabilities; during Execute, "Is this in my task definition?" is the only test. |
| Tests are the spec | `coding-principles.md`, `implement.md` | RED tests are immutable during GREEN; "implementation conforms to tests, not the other way around." |
| Test Integrity | `coding-principles.md` | Never weaken/skip/delete tests to pass. |
| Atomic commit per task | `implement.md` | "One task = one commit" using Conventional Commits 1.0.0. |
| SPEC_DEVIATION marker | `implement.md` | Inline code marker when implementation diverges from spec. |
| Stop the line | `validate.md` | "Non-zero exit code = STOP. Fix the failure. Re-run. Do not proceed until green." |
| Max 3 diagnostic iterations | `validate.md` | Anti-loop guardrail during UAT fixes. |

---

## 2. Workflow & Auto-Sizing

**Auto-sizing matrix (from `SKILL.md`):**

| Scope | What | Specify | Design | Tasks | Execute |
|---|---|---|---|---|---|
| Small | ≤3 files, one sentence | Quick mode — skip pipeline | – | – | – |
| Medium | Clear feature, <10 tasks | Spec (brief) | Skip — design inline | Skip — tasks implicit | Implement + verify |
| Large | Multi-component feature | Full spec + requirement IDs | Architecture + components | Full breakdown + dependencies | Implement + verify per task |
| Complex | Ambiguity, new domain | Full spec + discuss gray areas | Research + architecture | Breakdown + parallel plan | Implement + interactive UAT |

**Hard rules driving the size choice:**
- "Specify and Execute are always required — you always need to know WHAT and DO it"
- "Design is skipped when the change is straightforward (no architectural decisions, no new patterns)"
- "Tasks is skipped when there are ≤3 obvious steps (they become implicit in Execute)"
- "Discuss is triggered within Specify only when the agent detects ambiguous gray areas"
- "Interactive UAT is triggered within Execute only for user-facing features with complex behavior"

**Quick mode (`quick-mode.md`):**
- Trigger phrases: "quick fix", "quick task", "small change", "bug fix", "just do X"
- Hard guardrails: **Max 3 files, max 1 hour, no design decisions, no new dependencies**
- Pipeline: Describe → Pre-Implementation Check (user approval) → Implement → Verify → Atomic commit → Track in STATE.md
- Stored under `.specs/quick/NNN-slug/{TASK.md, SUMMARY.md}`
- Self-policing: "If you're doing 5+ quick tasks for the same area, it's a feature that needs planning"

**Safety valve:**

> "Even when Tasks is skipped, Execute ALWAYS starts by listing atomic steps inline. If that listing reveals >5 steps or complex dependencies, STOP and create a formal `tasks.md` — the Tasks phase was wrongly skipped."

The pre-implementation check in quick mode also escalates: if the task reveals >3 files, unclear dependencies, or design decisions needed → recommend full pipeline.

---

## 3. Context Loading Strategy

The skill enforces an explicit token budget and a what-loads-when policy.

**Base load (~15k tokens) — always loaded:**
- `PROJECT.md` (if exists)
- `ROADMAP.md` (when planning/working on features)
- `STATE.md` (persistent memory)

**On-demand load:**
- Codebase docs (when working in existing project)
- `CONCERNS.md` — when planning features that touch flagged areas, estimating risk, or modifying fragile components
- `TESTING.md` — when creating tasks or executing
- `spec.md` — for the specific feature being worked
- `context.md` — when designing/implementing from user decisions
- `design.md` — when implementing from design
- `tasks.md` — when executing tasks

**Never load simultaneously:**
- Multiple feature specs
- Multiple architecture docs
- Archived documents

**Budgets:**
- Target: <40k tokens total context
- Reserve: 160k+ tokens for work, reasoning, outputs
- Monitoring kicks in when >40k

**Per-file size limits (`context-limits.md`):**

| File | Max | Warning at |
|---|---|---|
| PROJECT.md | 2,000 | 1,600 (80%) |
| ROADMAP.md | 3,000 | 2,400 |
| STATE.md | 10,000 | 7,000 (70%) |
| spec.md | 5,000 | 4,000 |
| design.md | 8,000 | 6,400 |
| tasks.md | 10,000 | 8,000 |
| STACK.md | 2,000 | 1,600 |
| ARCHITECTURE.md | 4,000 | 3,200 |
| CONVENTIONS.md | 3,000 | 2,400 |
| STRUCTURE.md | 2,000 | 1,600 |
| TESTING.md | 4,000 | 3,200 |
| INTEGRATIONS.md | 5,000 | 4,000 |

**Context zones (`context-limits.md`):**
- Healthy (<40k): silent
- Moderate (40–60k): discrete footer note
- Critical (>60k): active warning with optimization suggestion

**STATE.md size management uses a graduated cleanup zone (`state-management.md`):**
- <7k: no action
- 7–10k: footer note "Cleanup recommended"
- >10k: "STATE.md critical. Cleanup now?"
- Cleanup process: move decisions >60 days to `STATE-ARCHIVE.md`, keep only active blockers, preserve <60-day learnings.

---

## 4. Sub-Agent Delegation

**When to delegate (table from `SKILL.md`):**

| Activity | Delegate? | Why |
|---|---|---|
| Research (design phase, brownfield mapping) | Yes | "Research output is large; only the summary matters to the main context" |
| Implementing a task | Yes | "File reads, edits, test output consume context; only the result matters" |
| Parallel `[P]` tasks | Yes (one per task) | "The only way to actually run tasks in parallel" |
| Sequential tasks with no `[P]` | Yes | "Keeps implementation artifacts out of the main context" |
| Planning, task creation, validation reports | No | "These require the full accumulated context to be coherent" |
| Quick mode tasks | No | "Too small to justify the overhead" |

**Sub-agent input contract — orchestrator MUST pass:**
- The specific task definition from `tasks.md` (What, Where, Depends on, Reuses, Done when, Tests, Gate)
- Relevant `coding-principles.md` and `CONVENTIONS.md`
- `TESTING.md` if it exists (for gate commands and test patterns)
- Any spec/design context the task references

**Sub-agent must NOT receive:** other tasks' definitions, accumulated chat history, validation reports from other tasks, or `STATE.md` (unless the task explicitly references a decision/blocker).

**Sub-agent output contract — each returns:**
- Status: Complete | Blocked | Partial
- Files changed: [list]
- Gate check result: pass/fail + test counts
- SPEC_DEVIATION markers (if any)
- Issues encountered (if any)

**Parallel execution mechanics (`tasks.md`):**

> "Tasks marked `[P]` are executed via sub-agents — one sub-agent per task, launched concurrently. The orchestrating agent waits for all sub-agents in a phase to complete before advancing to the next phase."

`[P]` is gated by THREE conditions:
1. No unfinished dependencies
2. Required test type is parallel-safe (per `TESTING.md` Parallelism Assessment)
3. No shared mutable state with other `[P]` tasks in the same phase

> "If a task's tests are NOT parallel-safe, it MUST run sequentially even if its implementation code has no dependencies. The test execution is the bottleneck."

---

## 5. Artifacts & Local Storage

**Layout from `SKILL.md`:**

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
    └── NNN-slug/
        ├── TASK.md
        └── SUMMARY.md
```

**Per-file purpose:**

- `PROJECT.md` — Vision (1–2 sentences), target users, problem solved, goals, tech stack, scope (in/out), constraints. Limit 2,000 tokens.
- `ROADMAP.md` — Milestones → features (PLANNED / IN PROGRESS / COMPLETE) + Future Considerations. Limit 3,000 tokens.
- `STATE.md` — Persistent memory: Recent Decisions (`AD-NNN`), Active Blockers (`B-NNN`), Lessons Learned (`L-NNN`), Quick Tasks table, Deferred Ideas, Todos, Preferences. ID-based, archive to `STATE-ARCHIVE.md` after 60 days.
- `HANDOFF.md` (at `.specs/HANDOFF.md`) — Session checkpoint, ~500 tokens, overwrites previous; contains Completed / In Progress / Pending / Blockers / Context (branch, uncommitted files).
- `TESTING.md` — Test Coverage Matrix, Parallelism Assessment, Gate Check Commands table.
- `CONCERNS.md` — Risk catalog: tech debt, known bugs, security, performance, fragile areas, scaling limits, deprecated deps, missing features, test gaps. Every concern needs file paths and a fix approach.
- `spec.md` — Problem, Goals, Out of Scope, User Stories (P1/P2/P3), Acceptance Criteria in **WHEN/THEN/SHALL** format, Edge Cases, Requirement Traceability, Success Criteria.
- `context.md` — Feature Boundary, Implementation Decisions, Agent's Discretion areas, Specific References, Deferred Ideas.
- `design.md` — Architecture overview (mermaid), Code Reuse Analysis, Components, Data Models, Error Handling Strategy, Tech Decisions.
- `tasks.md` — Execution Plan (phases + parallel-execution diagram), Task Breakdown (each: What/Where/Depends on/Reuses/Requirement/Tools/Done when/Tests/Gate), Parallel Execution Map, three pre-approval validation tables.

**Traceability and IDs:**
- Requirement IDs: `[CATEGORY]-[NUMBER]` (e.g., `AUTH-01`, `CART-03`).
- Status states: `Pending → In Design → In Tasks → Implementing → Verified`.
- The spec.md Requirement Traceability table tracks coverage.
- Decisions: `AD-NNN`, Blockers: `B-NNN`, Lessons: `L-NNN`.
- Quick tasks: numeric `NNN-slug`.

---

## 6. Built-in Commands / Triggers

The skill exposes a trigger-pattern table. Triggers are *natural-language phrase matches* that load specific reference files — no slash commands or scripts.

**Project-level triggers:**

| Trigger Pattern | Reference |
|---|---|
| Initialize project, setup project | `references/project-init.md` |
| Create roadmap, plan features | `references/roadmap.md` |
| Map codebase, analyze existing code | `references/brownfield-mapping.md` |
| Document concerns, find tech debt, what's risky | `references/concerns.md` |
| Record decision, log blocker, add todo | `references/state-management.md` |
| Pause work, end session | `references/session-handoff.md` |
| Resume work, continue | `references/session-handoff.md` |

**Feature-level triggers (auto-sized):**

| Trigger Pattern | Reference |
|---|---|
| Specify feature, define requirements | `references/specify.md` |
| Discuss feature, capture context, how should this work | `references/discuss.md` |
| Design feature, architecture | `references/design.md` |
| Break into tasks, create tasks | `references/tasks.md` |
| Implement task, build, execute | `references/implement.md` |
| Validate, verify, test, UAT, walk me through it | `references/validate.md` |
| Quick fix, quick task, small change, bug fix | `references/quick-mode.md` |

---

## 7. Knowledge Verification Chain

A strict 5-step ordered ladder enforced before any technical decision (from `SKILL.md`):

```
Step 1: Codebase → check existing code, conventions, and patterns already in use
Step 2: Project docs → README, docs/, inline comments, .specs/codebase/
Step 3: Context7 MCP → resolve library ID, then query for current API/patterns
Step 4: Web search → official docs, reputable sources, community patterns
Step 5: Flag as uncertain → "I'm not certain about X — here's my reasoning, but verify"
```

**Hard rules:**
- "Never skip to Step 5 if Steps 1–4 are available"
- "Step 5 is ALWAYS flagged as uncertain — never presented as fact"
- "NEVER assume or fabricate. Inventing APIs, patterns, or behaviors causes cascading failures across design → tasks → implementation. Uncertainty is always preferable to fabrication."

Step 3 names a specific MCP — **Context7** — and prescribes the two-call sequence (resolve library ID, then query).

---

## 8. Skill Integrations

Two named integrations with conditional delegation:

**1. Diagrams → `mermaid-studio`**
- Pattern: probe → delegate if available → fall back gracefully → recommend install once per session.
- Fallback: inline mermaid code blocks.

**2. Code Exploration → `codenavi`**
- Pattern: same probe-or-fallback approach.
- Fallback: built-in `code-analysis.md` (ast-grep → ripgrep → grep).

The conditional-delegation pattern appears in `SKILL.md`, `design.md` ("check mermaid-studio in Skill Integrations"), and `brownfield-mapping.md` ("If available, prefer it for all discovery and navigation tasks below").

---

## 9. Self-Healing & Stop Conditions

**Anti-fabrication / anti-hallucination:**
- 5-step verification chain with "NEVER assume or fabricate" clause (`SKILL.md`).
- `coding-principles.md`: "State assumptions explicitly. If uncertain, ask."
- `design.md`: "Inventing an API, a pattern, or a behavior that doesn't exist is far worse than admitting uncertainty."

**Stop-the-line / safety valves:**

| Where | Stop trigger | Action |
|---|---|---|
| Execute (`implement.md`) | Inline-step listing reveals >5 steps | Stop, create formal `tasks.md` |
| Quick mode | Pre-impl check reveals >3 files / unclear deps / design decisions | Recommend full pipeline |
| Execute Step 4b (GREEN) | A test seems "wrong" | Stop, ask user; never silently change a test |
| Execute Step 5 (Gate) | Non-zero exit code | Stop. Fix. Re-run. Do not proceed until green. |
| Validate Step 4 | Build-level gate fails | Stop. Do not proceed to Code Quality Check. |
| Validate Step 7 | Issue diagnosis | Max 3 diagnostic iterations per issue → flag for human |
| Tasks (pre-approval) | Granularity / Diagram-Definition / Test Co-location validation fails | Restructure; do not show failing tasks to user |

**`SPEC_DEVIATION` markers:**
```
// SPEC_DEVIATION: [what diverged]
// Reason: [why the deviation was necessary]
```
Surfaced in sub-agent reports so the orchestrator can decide.

**Test integrity guardrails (`coding-principles.md` + `implement.md`):**
- Never weaken assertions
- Never delete a test to reduce failure count
- Never use skip/disable/pending to bypass failures
- Never modify RED-phase tests during GREEN
- "Tests are the spec — implementation conforms to tests, not the other way around"
- Test Integrity Check at validation: compare current test count against pre-feature count; investigate decreases.

**Scope guardrails:**
- `discuss.md`: "Allowed: 'How should posts be displayed?' (clarifying ambiguity). Not allowed: 'Should we also add comments?' (new capability)."
- `implement.md` Step 8: "Is this in my task definition? If no, don't touch it."
- Drive-by improvements logged to `STATE.md` Deferred Ideas instead of acted upon.

**Severity inference (never ask the user)** — `validate.md` defines a deterministic mapping from user-reported symptoms:
- "crash"/"broken" → Blocker
- "doesn't work"/"missing" → Major
- "slow"/"weird" → Minor
- "color"/"font" → Cosmetic
- unclear → Major default

---

## 10. Auxiliary Tooling

The skill is lightweight — **no shipped scripts or binaries**.

**Referenced external tools:**
- **Context7 MCP** — Step 3 of Knowledge Verification Chain. Two-call sequence: resolve library ID, then query.
- **`mermaid-studio` skill** — preferred for diagram work.
- **`codenavi` skill** — preferred for code exploration.
- **Code analysis fallback chain (`code-analysis.md`):** `ast-grep` (`sg`) → `ripgrep` (`rg`) → `grep`, with one-time-per-session install nudge for ast-grep.
- **Conventional Commits 1.0.0** — referenced by URL as the commit format spec.

No install commands, package files, or executables in the skill directory — pure markdown.

---

## 11. Notable Patterns Worth Stealing

1. **Auto-sized pipeline with hard escape valves.** Single workflow scales from bug fix to greenfield epic, gated by deterministic rules. The escape valve (>5 steps revealed → STOP) is the key anti-chaos mechanism.

2. **Triggers as natural-language → reference-file index.** Thin `SKILL.md` plus 16 lazy-loaded reference files. Base load stays ~15k tokens; deep guidance fetched only when needed.

3. **Pre-approval validation tables baked into the artifact.** Before showing tasks to user, agent must render three gates (Task Granularity Check, Diagram-Definition Cross-Check, Test Co-location Validation) in the document. Failed checks must be fixed, not negotiated.

4. **Test co-location as a hard contract.** Tests are part of the task that creates the code layer. "No task produces unverified code." Two restructuring strategies when tests can't run yet: merge forward / merge backward.

5. **Sub-agent context contract.** Explicit list of what each sub-agent receives and does NOT receive, plus a fixed return shape. Makes parallelism cheap and main-context pollution minimal.

6. **Parallel-safety as a property of tests, not code.** `[P]` requires THREE conditions, and `TESTING.md` Parallelism Assessment is the source of truth. "If a task's tests are NOT parallel-safe, it MUST run sequentially even if its implementation code has no dependencies."

7. **`SPEC_DEVIATION` markers + RED→GREEN test immutability.** Tests written in RED are the contract; if reality forces a divergence, mark it inline with a reason instead of mutating the spec or the test.

8. **STATE.md as ID-based, ageable persistent memory.** Decisions/Blockers/Lessons get sequential IDs, Deferred Ideas absorb scope creep, graduated cleanup zone prevents unbounded growth, 60-day archive policy.

9. **Conditional delegation to peer skills with one-shot install nudges.** Probe-or-fallback for `mermaid-studio` and `codenavi`, but the recommendation fires only once per session.

10. **Severity inference instead of severity prompting.** Agent infers severity from the user's word choice via a fixed table. Removes friction without losing fidelity.

---

## 12. Sources Cited

All 17 files fetched successfully on 2026-05-19:

**Base file:**
- `https://raw.githubusercontent.com/tech-leads-club/agent-skills/main/packages/skills-catalog/skills/(development)/tlc-spec-driven/SKILL.md`

**Reference files (all 16):**
- `discuss.md`, `design.md`, `specify.md`, `tasks.md`, `implement.md`, `validate.md`, `quick-mode.md`, `project-init.md`, `roadmap.md`, `brownfield-mapping.md`, `concerns.md`, `state-management.md`, `session-handoff.md`, `context-limits.md`, `code-analysis.md`, `coding-principles.md`

(Base URL pattern: `https://raw.githubusercontent.com/tech-leads-club/agent-skills/main/packages/skills-catalog/skills/(development)/tlc-spec-driven/references/<file>`)

**Directory listing:**
- `https://api.github.com/repos/tech-leads-club/agent-skills/contents/packages/skills-catalog/skills/(development)/tlc-spec-driven/references` — returned exactly 16 files.

**Unverified:**
- The top-level repo's README or `packages/skills-catalog/` siblings — not explored. No higher-level loader or installer was identified.
