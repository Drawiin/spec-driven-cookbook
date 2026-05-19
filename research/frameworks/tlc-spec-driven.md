# TLC Spec-Driven — Research Dossier

> Source: `tech-leads-club/agent-skills` — `tlc-spec-driven` skill v2.0.0
> Author: Felipe Rodrigues (`github.com/felipfr`)
> License: CC-BY-4.0
> Cache ref: `research/.research-cache/02-tlc-findings.md` (fetched 2026-05-19)

---

## 1. TLC Spec-Driven — Overview

`tlc-spec-driven` is a stack-agnostic AI coding skill that organizes project and feature work through four adaptive phases — Specify, Design, Tasks, and Execute — promising "Granular tasks. Clear dependencies. Right tools. Zero ceremony." (TLC SKILL.md). It ships as a single `SKILL.md` file plus sixteen lazy-loaded reference files; no scripts, binaries, or build tools are included. The skill was authored by Felipe Rodrigues and released under the CC-BY-4.0 license at version 2.0.0. Its defining characteristic is that it auto-sizes the pipeline to the work at hand: Specify and Execute are always required, while Design and Tasks are triggered only when the complexity justifies them.

```
SPECIFY → DESIGN → TASKS → EXECUTE
required   optional  optional  required
```

Core philosophy: "The complexity determines the depth, not a fixed pipeline." (TLC SKILL.md)

See also: `../topics/workflow-and-orchestration.md`

---

## 2. Auto-Sizing Matrix

### Phase matrix

| Scope   | What                                        | Specify                          | Design                      | Tasks                            | Execute                     |
|---------|---------------------------------------------|----------------------------------|-----------------------------|----------------------------------|-----------------------------|
| Small   | ≤3 files, one sentence                      | Quick mode — skip pipeline       | –                            | –                                | –                           |
| Medium  | Clear feature, <10 tasks                    | Spec (brief)                     | Skip — design inline        | Skip — tasks implicit            | Implement + verify          |
| Large   | Multi-component feature                     | Full spec + requirement IDs      | Architecture + components   | Full breakdown + dependencies    | Implement + verify per task |
| Complex | Ambiguity, new domain                       | Full spec + discuss gray areas   | Research + architecture     | Breakdown + parallel plan        | Implement + interactive UAT |

### Five hard rules governing phase skipping

1. "Specify and Execute are always required — you always need to know WHAT and DO it" (TLC SKILL.md)
2. "Design is skipped when the change is straightforward (no architectural decisions, no new patterns)" (TLC SKILL.md)
3. "Tasks is skipped when there are ≤3 obvious steps (they become implicit in Execute)" (TLC SKILL.md)
4. "Discuss is triggered within Specify only when the agent detects ambiguous gray areas" (TLC SKILL.md)
5. "Interactive UAT is triggered within Execute only for user-facing features with complex behavior" (TLC SKILL.md)

### Quick mode

Quick mode activates on natural-language trigger phrases: "quick fix", "quick task", "small change", "bug fix", "just do X".

**Four hard guardrails:** max 3 files, max 1 hour, no design decisions, no new dependencies.

**Pipeline:** Describe → Pre-Implementation Check (user approval) → Implement → Verify → Atomic commit → Track in STATE.md

**Storage location:** `.specs/quick/NNN-slug/{TASK.md, SUMMARY.md}`

**Self-policing rule:** "If you're doing 5+ quick tasks for the same area, it's a feature that needs planning." (TLC quick-mode.md)

---

## 3. Safety Valve

Execute always begins by listing atomic implementation steps inline, even when the Tasks phase was skipped. This is a hard rule, not a suggestion:

> "Even when Tasks is skipped, Execute ALWAYS starts by listing atomic steps inline. If that listing reveals >5 steps or complex dependencies, STOP and create a formal `tasks.md` — the Tasks phase was wrongly skipped." (TLC SKILL.md)

The inline-step listing is therefore a retroactive gate: the agent cannot discover mid-implementation that the scope was underestimated without triggering a formal planning pause.

In quick mode, the pre-implementation check performs an analogous escalation. If the check reveals any of the following conditions, the agent must recommend the full pipeline rather than proceeding: more than 3 files touched, unclear dependencies, or design decisions needed. This makes quick mode self-ejecting when a task turns out to be non-trivial.

See also: `../topics/self-healing-and-verification.md`

---

## 4. Context Loading Strategy

The skill enforces an explicit three-zone loading policy to keep the working context bounded.

**Base load (~15k tokens) — always loaded:**
- `PROJECT.md` (if it exists)
- `ROADMAP.md` (when planning or working on features)
- `STATE.md` (persistent memory)

**On-demand load (fetched only when relevant):**
- Codebase docs when working in an existing project
- `CONCERNS.md` — when planning features that touch flagged areas, estimating risk, or modifying fragile components
- `TESTING.md` — when creating tasks or executing
- `spec.md` — for the specific feature being worked
- `context.md` — when designing or implementing from user decisions
- `design.md` — when implementing from design
- `tasks.md` — when executing tasks

**Never load simultaneously:**
- Multiple feature specs
- Multiple architecture docs
- Archived documents

### Per-file token limits

| File             | Max    | Warning at      |
|------------------|--------|-----------------|
| PROJECT.md       | 2,000  | 1,600 (80%)     |
| ROADMAP.md       | 3,000  | 2,400           |
| STATE.md         | 10,000 | 7,000 (70%)     |
| spec.md          | 5,000  | 4,000           |
| design.md        | 8,000  | 6,400           |
| tasks.md         | 10,000 | 8,000           |
| STACK.md         | 2,000  | 1,600           |
| ARCHITECTURE.md  | 4,000  | 3,200           |
| CONVENTIONS.md   | 3,000  | 2,400           |
| STRUCTURE.md     | 2,000  | 1,600           |
| TESTING.md       | 4,000  | 3,200           |
| INTEGRATIONS.md  | 5,000  | 4,000           |

(Source: TLC context-limits.md)

### Context health zones

| Zone     | Token range | Behavior                                      |
|----------|-------------|-----------------------------------------------|
| Healthy  | < 40k       | Silent — no notification                      |
| Moderate | 40–60k      | Discrete footer note                          |
| Critical | > 60k       | Active warning with optimization suggestion   |

Total context target: < 40k tokens. Reserve: 160k+ tokens for work, reasoning, and outputs. Monitoring activates when > 40k.

### STATE.md graduated cleanup

STATE.md uses a four-tier size management process (TLC state-management.md):

- **< 7k tokens:** no action
- **7–10k tokens:** footer note "Cleanup recommended"
- **> 10k tokens:** "STATE.md critical. Cleanup now?"
- **Cleanup process:** move decisions older than 60 days to `STATE-ARCHIVE.md`, retain only active blockers, preserve lessons learned under 60 days

The 60-day archive policy prevents unbounded growth while keeping recent institutional memory available in the base load.

See also: `../topics/context-engineering.md`, `../topics/local-storage-and-artifacts.md`

---

## 5. Sub-Agent Delegation

### Delegation matrix

| Activity                                           | Delegate? | Why                                                                       |
|----------------------------------------------------|-----------|---------------------------------------------------------------------------|
| Research (design phase, brownfield mapping)        | Yes       | "Research output is large; only the summary matters to the main context"  |
| Implementing a task                                | Yes       | "File reads, edits, test output consume context; only the result matters" |
| Parallel `[P]` tasks                              | Yes (one per task) | "The only way to actually run tasks in parallel"               |
| Sequential tasks with no `[P]`                    | Yes       | "Keeps implementation artifacts out of the main context"                  |
| Planning, task creation, validation reports        | No        | "These require the full accumulated context to be coherent"               |
| Quick mode tasks                                   | No        | "Too small to justify the overhead"                                       |

(Source: TLC SKILL.md)

### Sub-agent input contract

The orchestrator MUST pass to each sub-agent:
- The specific task definition from `tasks.md` (What, Where, Depends on, Reuses, Done when, Tests, Gate)
- Relevant `coding-principles.md` and `CONVENTIONS.md`
- `TESTING.md` if it exists (for gate commands and test patterns)
- Any spec or design context the task references

Sub-agents must NOT receive: other tasks' definitions, accumulated chat history, validation reports from other tasks, or `STATE.md` (unless the task explicitly references a specific decision or blocker ID).

### Sub-agent output contract

Each sub-agent returns a fixed-shape report:

| Field              | Description                                     |
|--------------------|-------------------------------------------------|
| Status             | Complete \| Blocked \| Partial                  |
| Files changed      | List of modified files                          |
| Gate check result  | pass/fail + test counts                         |
| SPEC_DEVIATION     | Inline markers, if any                          |
| Issues encountered | Free-text, if any                               |

### Parallel execution mechanics

> "Tasks marked `[P]` are executed via sub-agents — one sub-agent per task, launched concurrently. The orchestrating agent waits for all sub-agents in a phase to complete before advancing to the next phase." (TLC tasks.md)

The `[P]` marker is gated by THREE conditions, all of which must hold:

1. No unfinished dependencies
2. Required test type is parallel-safe (per `TESTING.md` Parallelism Assessment)
3. No shared mutable state with other `[P]` tasks in the same phase

The test-parallelism condition is the most constraining:

> "If a task's tests are NOT parallel-safe, it MUST run sequentially even if its implementation code has no dependencies. The test execution is the bottleneck." (TLC tasks.md)

See also: `../topics/workflow-and-orchestration.md`

---

## 6. Artifacts and Local Storage

### `.specs/` directory tree

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

### File purposes and token limits

| File             | Purpose                                                                                                   | Token limit |
|------------------|-----------------------------------------------------------------------------------------------------------|-------------|
| PROJECT.md       | Vision (1–2 sentences), target users, problem solved, goals, tech stack, scope (in/out), constraints     | 2,000       |
| ROADMAP.md       | Milestones → features (PLANNED / IN PROGRESS / COMPLETE) + Future Considerations                         | 3,000       |
| STATE.md         | Persistent memory: Recent Decisions (`AD-NNN`), Active Blockers (`B-NNN`), Lessons Learned (`L-NNN`), Quick Tasks table, Deferred Ideas, Todos, Preferences | 10,000 |
| HANDOFF.md       | Session checkpoint (~500 tokens); overwrites previous; contains Completed / In Progress / Pending / Blockers / Context (branch, uncommitted files) | ~500 |
| spec.md          | Problem, Goals, Out of Scope, User Stories (P1/P2/P3), Acceptance Criteria (WHEN/THEN/SHALL format), Edge Cases, Requirement Traceability, Success Criteria | 5,000 |
| context.md       | Feature Boundary, Implementation Decisions, Agent's Discretion areas, Specific References, Deferred Ideas | (on-demand) |
| design.md        | Architecture overview (mermaid), Code Reuse Analysis, Components, Data Models, Error Handling Strategy, Tech Decisions | 8,000 |
| tasks.md         | Execution Plan (phases + parallel-execution diagram), Task Breakdown, Parallel Execution Map, three pre-approval validation tables | 10,000 |
| TESTING.md       | Test Coverage Matrix, Parallelism Assessment, Gate Check Commands table                                   | 4,000       |
| CONCERNS.md      | Risk catalog: tech debt, known bugs, security, performance, fragile areas, scaling limits, deprecated deps, missing features, test gaps (each concern requires file paths and a fix approach) | (on-demand) |

### Traceability IDs

- **Requirement IDs:** `[CATEGORY]-[NUMBER]` (e.g., `AUTH-01`, `CART-03`)
- **Requirement status states:** `Pending → In Design → In Tasks → Implementing → Verified`
- **Decision IDs:** `AD-NNN`
- **Blocker IDs:** `B-NNN`
- **Lesson IDs:** `L-NNN`
- **Quick task IDs:** numeric `NNN-slug`

The `spec.md` Requirement Traceability table tracks coverage from requirement through to verified state, providing a lightweight audit trail across the full pipeline.

See also: `../topics/local-storage-and-artifacts.md`

---

## 7. Trigger System

Triggers are natural-language phrase matches that cause the skill to lazy-load a specific reference file. There are no slash commands, no scripts, and no special syntax — the agent pattern-matches the user's words and fetches only the relevant guidance. This keeps the base load at approximately 15k tokens while making the full ~16-file reference library available on demand.

### Project-level triggers

| Trigger Pattern                                   | Reference file                        |
|---------------------------------------------------|---------------------------------------|
| Initialize project, setup project                 | `references/project-init.md`          |
| Create roadmap, plan features                     | `references/roadmap.md`               |
| Map codebase, analyze existing code               | `references/brownfield-mapping.md`    |
| Document concerns, find tech debt, what's risky   | `references/concerns.md`              |
| Record decision, log blocker, add todo            | `references/state-management.md`      |
| Pause work, end session                           | `references/session-handoff.md`       |
| Resume work, continue                             | `references/session-handoff.md`       |

### Feature-level triggers (auto-sized)

| Trigger Pattern                                        | Reference file              |
|--------------------------------------------------------|-----------------------------|
| Specify feature, define requirements                   | `references/specify.md`     |
| Discuss feature, capture context, how should this work | `references/discuss.md`     |
| Design feature, architecture                           | `references/design.md`      |
| Break into tasks, create tasks                         | `references/tasks.md`       |
| Implement task, build, execute                         | `references/implement.md`   |
| Validate, verify, test, UAT, walk me through it        | `references/validate.md`    |
| Quick fix, quick task, small change, bug fix           | `references/quick-mode.md`  |

Total: 14 trigger patterns across 13 distinct reference files (`session-handoff.md` handles both pause and resume).

---

## 8. Knowledge Verification Chain

Before making any technical claim or decision, the skill requires a strict five-step ordered ladder (TLC SKILL.md):

```
Step 1: Codebase → check existing code, conventions, and patterns already in use
Step 2: Project docs → README, docs/, inline comments, .specs/codebase/
Step 3: Context7 MCP → resolve library ID, then query for current API/patterns
Step 4: Web search → official docs, reputable sources, community patterns
Step 5: Flag as uncertain → "I'm not certain about X — here's my reasoning, but verify"
```

### Three hard rules

1. "Never skip to Step 5 if Steps 1–4 are available" (TLC SKILL.md)
2. "Step 5 is ALWAYS flagged as uncertain — never presented as fact" (TLC SKILL.md)
3. "NEVER assume or fabricate. Inventing APIs, patterns, or behaviors causes cascading failures across design → tasks → implementation. Uncertainty is always preferable to fabrication." (TLC SKILL.md)

### Context7 MCP (Step 3)

Step 3 names **Context7 MCP** specifically, not a generic "documentation lookup." The prescribed sequence is a two-call pattern: first resolve the library ID, then query for the current API or pattern. This makes the verification step deterministic and reproducible rather than leaving the search strategy up to the agent.

The "NEVER assume or fabricate" principle is reinforced across multiple reference files: `SKILL.md`, `design.md` ("Inventing an API, a pattern, or a behavior that doesn't exist is far worse than admitting uncertainty."), and `coding-principles.md` ("State assumptions explicitly. If uncertain, ask.").

See also: `../topics/auxiliary-tooling.md`, `../topics/self-healing-and-verification.md`

---

## 9. Skill Integrations

Two named peer-skill integrations use a consistent **probe-or-fallback** pattern: check whether the peer skill is available, delegate if it is, fall back to a built-in alternative if not, and issue an install recommendation only once per session.

### mermaid-studio

- **Purpose:** diagram generation (used primarily in `design.md` architecture overviews)
- **Probe:** check for `mermaid-studio` in Skill Integrations
- **Delegate if available**
- **Fallback:** inline mermaid code blocks
- **One-shot nudge:** recommend install once per session, then drop the recommendation
- **Referenced in:** `SKILL.md`, `design.md` ("check mermaid-studio in Skill Integrations")

### codenavi

- **Purpose:** code exploration and navigation (used primarily in `brownfield-mapping.md`)
- **Probe:** same probe-or-fallback pattern
- **Delegate if available**
- **Fallback:** built-in `code-analysis.md` tool chain — `ast-grep` (`sg`) → `ripgrep` (`rg`) → `grep`
- **One-shot nudge:** one-time-per-session install suggestion for `ast-grep` if absent
- **Referenced in:** `SKILL.md`, `brownfield-mapping.md` ("If available, prefer it for all discovery and navigation tasks below")

The fallback chain for code analysis (`ast-grep → ripgrep → grep`) is ordered by capability: `ast-grep` offers AST-aware structural search; `ripgrep` provides fast regex search; `grep` is the universal last resort.

See also: `../topics/auxiliary-tooling.md`

---

## 10. Self-Healing and Stop Conditions

### Stop-condition table

| Where                              | Stop trigger                                                            | Action                                                  |
|------------------------------------|-------------------------------------------------------------------------|---------------------------------------------------------|
| Execute (`implement.md`)           | Inline-step listing reveals > 5 steps                                   | Stop, create formal `tasks.md`                          |
| Quick mode                         | Pre-impl check reveals > 3 files / unclear deps / design decisions      | Recommend full pipeline                                 |
| Execute Step 4b (GREEN)            | A test seems "wrong"                                                    | Stop, ask user; never silently change a test            |
| Execute Step 5 (Gate)              | Non-zero exit code                                                      | Stop. Fix. Re-run. Do not proceed until green.          |
| Validate Step 4                    | Build-level gate fails                                                  | Stop. Do not proceed to Code Quality Check.             |
| Validate Step 7                    | Issue diagnosis                                                         | Max 3 diagnostic iterations per issue → flag for human  |
| Tasks (pre-approval)               | Granularity / Diagram-Definition / Test Co-location validation fails    | Restructure; do not show failing tasks to user          |

### SPEC_DEVIATION marker

When implementation diverges from the spec, the agent marks the code inline rather than silently updating the spec or the test:

```
// SPEC_DEVIATION: [what diverged]
// Reason: [why the deviation was necessary]
```

SPEC_DEVIATION markers are surfaced in sub-agent output reports so the orchestrator can make an explicit decision about each divergence. (TLC implement.md)

### Test integrity guardrails

Five rules from `coding-principles.md` and `implement.md`:

1. Never weaken assertions
2. Never delete a test to reduce failure count
3. Never use skip/disable/pending to bypass failures
4. Never modify RED-phase tests during GREEN
5. "Tests are the spec — implementation conforms to tests, not the other way around" (TLC coding-principles.md)

Additionally, validation includes a Test Integrity Check that compares the current test count against the pre-feature count; any decrease must be investigated.

### Scope guardrails

The skill distinguishes between clarifying ambiguity (allowed in Discuss) and expanding scope (not allowed). From `discuss.md`:

- Allowed: "How should posts be displayed?" (clarifying ambiguity)
- Not allowed: "Should we also add comments?" (new capability)

During Execute, the scope test is a single binary question: "Is this in my task definition? If no, don't touch it." (TLC implement.md, Step 8). Drive-by improvements are not discarded — they are logged to `STATE.md` Deferred Ideas for future consideration.

### Severity inference table

During validation, the agent infers severity from the user's reported symptoms without asking the user to classify the issue (TLC validate.md):

| Symptom keywords          | Inferred severity |
|---------------------------|-------------------|
| "crash", "broken"         | Blocker           |
| "doesn't work", "missing" | Major             |
| "slow", "weird"           | Minor             |
| "color", "font"           | Cosmetic          |
| unclear                   | Major (default)   |

See also: `../topics/self-healing-and-verification.md`

---

## 11. Auxiliary Tooling

The skill ships no scripts, binaries, package files, or executables — it is pure markdown. All tooling is referenced by name with fallback strategies built into the reference files.

### Context7 MCP

Referenced at Step 3 of the Knowledge Verification Chain. Prescribed as a two-call sequence: (1) resolve the library ID, (2) query for the current API or pattern. This is the only external service called by name with a defined interaction protocol. No fallback is described for Step 3 failure; the chain continues to Step 4 (web search).

### mermaid-studio

A peer skill rather than an external tool. Used for architecture diagrams in `design.md`. Fallback: inline mermaid code blocks rendered by the agent directly. See Section 9.

### codenavi

A peer skill for code exploration and navigation. Used in brownfield mapping. Fallback: the `code-analysis.md` chain. See Section 9.

### Code analysis fallback chain (`code-analysis.md`)

`ast-grep` (`sg`) → `ripgrep` (`rg`) → `grep`

Each tool is tried in order. A one-time-per-session install nudge is issued for `ast-grep` if it is absent, but the fallback chain operates without it.

### Conventional Commits 1.0.0

Referenced by URL as the commit format specification. The skill enforces one task = one atomic commit using this format. No version-specific deviations are noted.

See also: `../topics/auxiliary-tooling.md`

---

## 12. Key Insights for Framework Design

The following patterns are the most transferable from `tlc-spec-driven` to a new spec-driven AI coding framework. All are drawn from the Notable Patterns section of the research cache.

- **Auto-sized pipeline with hard escape valves.** A single workflow scales from a one-line bug fix to a greenfield epic by applying deterministic size rules. The critical mechanism is the escape valve: if inline step listing reveals more than five steps, the agent stops and retroactively creates a formal `tasks.md`. This prevents scope underestimation from silently compounding into a mid-implementation disaster.

- **Triggers as natural-language → reference-file index.** Keeping `SKILL.md` thin (~15k base load) and deferring all deep guidance to 16 lazy-loaded reference files means context cost is proportional to the work being done. The trigger table is the index; phrase matching is the loader. Frameworks that front-load all guidance pay a constant token tax on every task.

- **Pre-approval validation tables baked into the artifact.** Before showing tasks to the user, the agent must render and pass three internal gates (Task Granularity Check, Diagram-Definition Cross-Check, Test Co-location Validation) directly in the `tasks.md` document. Failed checks must be restructured, not negotiated with the user. This makes quality enforcement automatic rather than conversational.

- **Test co-location as a hard contract.** Tests are authored as part of the same task that creates the code layer, enforcing "no task produces unverified code." When tests cannot run yet due to dependencies, two explicit restructuring strategies are defined (merge forward / merge backward) rather than leaving the agent to improvise.

- **Explicit sub-agent context contract.** Defining exactly what each sub-agent receives (task definition, conventions, test patterns) and what it must not receive (other tasks' definitions, accumulated chat history, STATE.md) keeps parallelism cheap and main-context pollution minimal. The fixed return shape (Status / Files changed / Gate result / SPEC_DEVIATION / Issues) makes orchestration predictable.

- **Parallel-safety as a property of tests, not code.** The `[P]` parallel marker requires `TESTING.md` Parallelism Assessment as the source of truth. Even if implementation code has no shared state, a task must run sequentially if its tests are not parallel-safe. This prevents flaky parallel test runs from masquerading as implementation bugs.

- **STATE.md as ID-based, ageable persistent memory.** Sequential IDs for Decisions (`AD-NNN`), Blockers (`B-NNN`), and Lessons (`L-NNN`) make cross-references stable across sessions. Deferred Ideas absorb scope creep without losing it. Graduated cleanup zones (7k, 10k thresholds) with a 60-day archive policy prevent the memory store from growing until it crowds out working context.

See also: `../topics/patterns-worth-stealing.md`
