# Phase 2: Spec Phase — Greenfield - Research

**Researched:** 2026-05-21
**Domain:** Cursor skill design, Python stdlib file I/O, agent-driven Q&A workflow, YAML front-matter parsing
**Confidence:** HIGH — all findings verified directly from the codebase; no external libraries involved

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Q&A Structure**
- D-01: Hybrid flow — fixed category spine always covered in order: Problem → Who it's for → Constraints → Success Criteria → Out-of-scope. Agent probes within each category (up to 3 follow-up turns) when answers are vague or underspecified.
- D-02: Category advances after 3 turns OR when the agent determines the answer is specific enough. The agent decides — not the user.

**Research Sub-tasks**
- D-03: Both trigger modes: (a) agent-suggested at end of Q&A if knowledge gaps are detected; user accepts/skips. (b) user-requested — user can say "research X" at any point to spawn immediately.
- D-04: Research form: spawned Cursor sub-agent (Task tool) with fresh context. Sub-agent writes a `RESEARCH-<topic>.md` file. Main spec flow reads that file before finalizing SPEC.md — main context never makes external calls directly.
- D-05: Multiple research sub-tasks may run; each produces its own `RESEARCH-<topic>.md`. All are read before spec is finalized.

**SPEC.md Format**
- D-06: Five mandatory sections only: Problem, Who it's for, Constraints, Success Criteria, Out-of-scope.
- D-07: YAML front-matter: `status: draft | approved`, `version`, `date`.

**Approval Gate**
- D-08: In-flow approval — present full SPEC.md, ask "Approve? (yes / edit / abort)". On "yes", write `status: approved`. On "edit", return to relevant section. On "abort", save as draft and exit.
- D-09: Belt-and-suspenders: (a) plan-phase SKILL.md instructs agent to verify `status == approved`; (b) Python `validate_spec.py` reads SPEC.md, checks status, exits non-zero with clear error if not approved.

### Claude's Discretion
- Exact wording of Q&A prompts within each category.
- Detection heuristic for "vague answer" (when to follow up vs. advance).
- Format of the research sub-task prompt passed to the spawned sub-agent.

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SPEC-01 | User can initiate a spec phase that opens a structured deep-questioning flow | SKILL.md contains the full Q&A protocol with category spine and probe logic |
| SPEC-02 | The spec phase produces a persisted spec file capturing what to build, why, constraints, and success criteria | Agent uses Write tool to create `.planning/SPEC.md` with YAML front-matter + five mandatory sections |
| SPEC-03 | Spec phase supports research sub-tasks (gathering domain knowledge before locking requirements) | Cursor Task tool spawns sub-agents; SKILL.md defines the research trigger and sub-task prompt template |
| SPEC-04 | Spec file must be explicitly approved by the user before planning begins | D-08 in-flow gate + D-09 belt-and-suspenders via `validate_spec.py` |
| SPEC-05 | Spec phase works on a clean context — can be invoked with no prior session history, using only local files | SKILL.md is self-contained; startup reads only local files via Shell/Read tools; no session-state dependency |
| PROJ-01 | Framework works on empty repos — the spec phase can be the first thing run | SKILL.md startup step scaffolds `.planning/` via `tool-planning-scaffold` before any reads |
</phase_requirements>

---

## Summary

Phase 2 delivers two discrete deliverables: a **workflow skill** (`mise-en-place/spec-phase/SKILL.md`) that drives an agent through a structured conversational Q&A, optional research sub-tasks, and an in-flow approval gate; and a **validation tool** (`mise-en-place/tool-validate-spec/`) consisting of a SKILL.md contract and a Python stdlib-only script that checks SPEC.md approval status before planning can proceed.

The spec-phase skill is **agent instructions only** — no Python companion script is needed because the Q&A is conversational (agent-native), research sub-tasks are spawned via the Cursor Task tool (already available), and SPEC.md is written/patched directly by the agent via the Write and StrReplace tools. This follows the framework's established pattern: workflow skills are pure SKILL.md; tool skills add a Python script for deterministic, exit-code-based operations.

The validate-spec tool is the only new Python script in this phase. It must parse a flat YAML front-matter block using stdlib primitives (no `yaml` library; Python 3.9 confirmed on this machine, `tomllib` is 3.11+). The simple three-key schema — `status`, `version`, `date` — is safely parsed with a line-by-line splitter without any external dependency.

**Primary recommendation:** Ship `spec-phase/SKILL.md` as a comprehensive agent workflow document with the category spine, probe logic, research trigger patterns, SPEC.md template, and approval gate logic all written inline. Ship `tool-validate-spec/validate_spec.py` as a slim stdlib script using a manual front-matter parser. Keep the two deliverables strictly separated — the workflow skill calls the validation tool, not the other way around.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Q&A conversational flow | Agent (SKILL.md instructions) | — | Multi-turn conversation is inherently agent-native; no script can substitute |
| Category advancement logic | Agent (judgment) | — | D-02 says "agent decides"; this is deliberate model-native behavior |
| Research sub-task spawning | Agent (Task tool) | — | D-04 specifies Cursor Task tool; spawning is Cursor-native |
| Research file writing | Sub-agent (spawned) | — | D-04: sub-agent writes `RESEARCH-<topic>.md`; main context reads the output |
| Research file reading | Agent (Read tool) | — | Main context reads research files before finalizing spec |
| SPEC.md writing | Agent (Write tool) | — | Simple file write with known template; no script overhead justified |
| SPEC.md status patching (draft→approved) | Agent (StrReplace tool) | — | Single-line change; StrReplace is exact and deterministic |
| `.planning/` scaffolding | Python (planning_scaffold.py) | Agent fallback | Reuse existing Phase 1 tool; idempotent and already tested |
| Spec status validation (gate) | Python (validate_spec.py) | Agent instruction | Belt-and-suspenders: Python provides deterministic exit code; agent instruction provides soft check |

---

## Standard Stack

### Core

| Component | Version/Form | Purpose | Why Standard |
|-----------|-------------|---------|--------------|
| SKILL.md (spec-phase) | Markdown agent contract | Drives the full spec workflow | Established pattern from Phase 1: D-08/D-09 in 01-CONTEXT.md |
| validate_spec.py | Python 3.x stdlib-only | Checks SPEC.md `status == approved` | D-01 in 01-CONTEXT.md: zero pip dependencies |
| pathlib | stdlib | File discovery and reading | Used in all Phase 1 scripts; `[VERIFIED: codebase]` |
| sys | stdlib | Exit codes, stderr output | Used in all Phase 1 scripts; `[VERIFIED: codebase]` |
| re | stdlib | YAML front-matter line parsing | Available in all Python 3.x; safer than manual split for edge cases |
| argparse | stdlib | CLI argument parsing for validate_spec | Used in planning_scaffold.py; `[VERIFIED: codebase]` |
| planning_scaffold.py | Existing Phase 1 tool | Scaffold `.planning/` before spec starts | Already tested; idempotent; `[VERIFIED: codebase]` |

### No Installation Required

All dependencies are either:
- Agent-native (Cursor tools: Write, StrReplace, Read, Shell, Task)
- Python stdlib (no `pip install` step)
- Reuse of Phase 1 tools already on disk

**This phase installs zero packages.** Package legitimacy audit: N/A.

---

## Architecture Patterns

### System Architecture Diagram

```
Developer invokes /spec-phase
          │
          ▼
[SKILL.md loads] ── reads ──► planning_scaffold.py scaffold (ensures .planning/ exists)
          │                   reads .planning/SPEC.md (if exists → offer resume/restart)
          ▼
[Q&A Phase]
  Category: Problem
    ├── agent asks opening question
    ├── ≤3 follow-up probes if vague
    └── advance when specific enough
  Category: Who it's for → same pattern
  Category: Constraints → same pattern
  Category: Success Criteria → same pattern
  Category: Out-of-scope → same pattern
          │
          │  user says "research X"  (D-03b: inline trigger)
          ├──────────────────────────────────────────────────►
          │                                                  │
          │                         [Task tool spawns sub-agent]
          │                         sub-agent writes RESEARCH-<topic>.md
          │                         ◄──────────────────────────
          │  (main context reads RESEARCH-<topic>.md)
          │
          ▼
[End-of-Q&A Research Suggestion] (D-03a: agent-suggested)
  If gaps detected → propose research topics → user accepts/skips
  Each accepted → Task tool spawns sub-agent → RESEARCH-<topic>.md written
          │
          ▼
[SPEC.md Assembly]
  Merge Q&A answers + all RESEARCH-<topic>.md content
  Write .planning/SPEC.md (YAML front-matter: status: draft)
          │
          ▼
[Approval Gate] (D-08)
  Present full SPEC.md content
  "Approve? (yes / edit / abort)"
  yes  → StrReplace status: draft → status: approved in SPEC.md
  edit → return to relevant section
  abort → save as draft, exit (status remains: draft)
          │
          ▼
.planning/SPEC.md  (status: approved or draft)
.planning/research/RESEARCH-<topic>.md  (one per research sub-task)
```

**Validation gate (separate tool, invoked by plan-phase):**

```
/plan-phase invoked
    │
    ▼
[tool-validate-spec invoked]
python3 mise-en-place/tool-validate-spec/validate_spec.py
    │
    ├── .planning/SPEC.md not found → exit 1, stderr message
    ├── no front-matter → exit 1, stderr message
    ├── status: draft → exit 1, stderr message
    └── status: approved → exit 0, stdout confirmation
```

### Recommended Project Structure

```
mise-en-place/
├── spec-phase/
│   └── SKILL.md              # Full agent workflow (no Python companion)
└── tool-validate-spec/
    ├── SKILL.md              # Agent-facing contract
    ├── validate_spec.py      # Stdlib-only status checker
    └── test_validate_spec.py # Pytest tests
```

SPEC.md and research artifacts (written at runtime, not shipped):
```
.planning/
├── SPEC.md                           # Written by spec-phase agent
└── research/
    ├── RESEARCH-<topic1>.md          # Written by research sub-agent
    └── RESEARCH-<topic2>.md
```

### Pattern 1: Workflow Skill (SKILL.md only, no Python companion)

**What:** A SKILL.md that contains agent instructions for a multi-step conversational workflow. No Python script; the agent is the executor.

**When to use:** When the task is inherently conversational or multi-turn (Q&A, approval flows, sub-agent spawning). Python scripts are for deterministic, exit-code-based work only.

**Example (adapted from tool-env-check SKILL.md structure):**
```markdown
---
name: spec-phase
description: "Structured deep-questioning flow → SPEC.md → explicit approval gate"
---

<cursor_skill_adapter>
## A. Skill Invocation
...
</cursor_skill_adapter>

<objective>
Take a developer from an empty repo to an explicitly approved SPEC.md.
</objective>

<process>
## Step 1: Startup
...
## Step 2: Q&A Flow (Category Spine)
...
## Step 3: Research Sub-tasks
...
## Step 4: SPEC.md Assembly
...
## Step 5: Approval Gate
...
</process>
```

**Source:** `[VERIFIED: codebase]` — established in Phase 1 SKILL.md files (tool-env-check/SKILL.md, tool-planning-scaffold/SKILL.md, tool-context-builder/SKILL.md).

### Pattern 2: YAML Front-Matter Parsing (stdlib, no yaml library)

**What:** Parse a simple flat YAML header in a markdown file using stdlib line splitting. Safe for the known schema: `status`, `version`, `date` (all scalar string values, no nesting, no lists).

**When to use:** Any time SPEC.md front-matter must be read by a Python script. The schema is intentionally constrained — never add lists or nested keys to the front-matter, as this parser will not handle them.

**Implementation:**
```python
# Source: [ASSUMED — design pattern for this codebase]
def parse_frontmatter(text: str) -> dict:
    """Parse flat YAML front-matter. Returns {} if none found."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end].strip()
    result = {}
    for line in block.splitlines():
        line = line.strip()
        if ":" in line and not line.startswith("#"):
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result
```

**Edge cases handled:**
- Missing `---` block → returns `{}`
- Comment lines in front-matter (start with `#`) → skipped
- Values containing colons (e.g., `date: 2026-05-21`) → `partition(":")` takes first colon only, so `2026-05-21` is returned correctly — no issue
- Extra whitespace → `.strip()` on both key and value
- CRLF line endings — `.splitlines()` handles `\r\n` correctly in stdlib

**Known limitation:** Multi-line values and nested YAML are not supported. D-07 front-matter is flat scalars only; this limitation is intentional and acceptable.

### Pattern 3: Research Sub-Agent Spawning

**What:** SKILL.md instructs the agent to spawn a research sub-agent via the Cursor Task tool. The sub-agent receives a focused prompt describing the research topic, writes its output to a file, and returns. The main agent reads the file.

**When to use:** D-03/D-04 research trigger. This pattern mirrors the GSD researcher sub-agent model established in the framework that this project is built with.

**Agent instructions in SKILL.md (example wording):**
```markdown
## Spawning a Research Sub-Agent

When a research topic is triggered:

1. Use the Task tool to spawn a sub-agent:
   ```
   Task(
     subagent_type="generalPurpose",
     description="Research: <topic>",
     prompt="""
       Research the following topic for a software spec: <topic>

       Context: <brief description of what the user is building>

       Write your findings to: .planning/research/RESEARCH-<topic-slug>.md

       Format:
       # Research: <topic>
       ## Summary
       ## Key Findings
       ## Implications for Spec
       ## Sources
     """
   )
   ```
2. After the sub-agent completes, read `.planning/research/RESEARCH-<topic-slug>.md`.
3. Incorporate findings into the relevant SPEC.md sections.
```

**Source:** `[VERIFIED: codebase]` — Task tool used in existing GSD framework SKILL.md files; sub-agent-writes-to-file pattern is the GSD researcher model.

### Pattern 4: In-Flow Approval Gate + Status Patch

**What:** Agent presents full SPEC.md, prompts for approval, and patches the YAML front-matter `status` field in place using StrReplace.

**When to use:** D-08 approval gate. StrReplace is exact; patching a single known line (`status: draft`) is safe.

**Agent instructions in SKILL.md (example wording):**
```markdown
## Approval Gate

1. Present the complete SPEC.md content to the developer.
2. Ask: "Approve this spec? Reply with: yes / edit / abort"
3. On **yes**:
   - Use StrReplace on `.planning/SPEC.md`:
     - old_string: `status: draft`
     - new_string: `status: approved`
   - Confirm: "Spec approved. You may now run /plan-phase."
4. On **edit**:
   - Ask which section to revise.
   - Return to that section's Q&A.
   - Re-present updated SPEC.md and re-prompt approval.
5. On **abort**:
   - Leave status as draft.
   - Confirm: "Spec saved as draft in .planning/SPEC.md. Resume later with /spec-phase."
```

**Source:** `[VERIFIED: codebase]` — StrReplace used throughout GSD framework for in-place file edits.

### Anti-Patterns to Avoid

- **Checking YAML front-matter status in the spec-phase SKILL.md via regex**: The SKILL.md should just read the file and check if the string `status: approved` is present — agent reading is reliable. Save complex parsing for the Python validation script.
- **Writing SPEC.md with a Python script when the agent can Write directly**: Adds an unnecessary intermediary. The agent has Write tool; use it.
- **Hardcoding phase directory paths in the research file output location**: When the skill is replicated to new projects, `.planning/phases/02-spec-phase-greenfield/` is meaningless. Use `.planning/research/` as the canonical research output path.
- **Treating `tomllib` as available**: Python 3.9 confirmed on this machine; `tomllib` requires 3.11+. YAML parsing must use stdlib only.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| `.planning/` directory creation | Custom mkdir logic in validate_spec.py | `planning_scaffold.py scaffold` | Already tested, idempotent; `[VERIFIED: codebase]` |
| Research sub-task parallelism | Custom process spawning | Cursor Task tool | Task tool is the established Cursor sub-agent mechanism; `[VERIFIED: codebase]` |
| SPEC.md writing | Custom file formatter | Agent Write tool with template | Simple text write; no abstraction needed |
| Status patching | Custom file diff/patch | Agent StrReplace | Exact line replacement; already the project pattern |
| Multi-turn conversation state | Custom state machine | Agent's native context window | The conversation IS the state machine |

**Key insight:** The spec-phase workflow is conversational — it lives in the agent's context window, not in a Python state machine. Resist the urge to encode the Q&A state in files; the agent advances categories naturally through conversation. The only persistent state is the SPEC.md file on disk.

---

## Common Pitfalls

### Pitfall 1: Research File Path Not Portable

**What goes wrong:** SKILL.md writes research files to `.planning/phases/02-spec-phase-greenfield/RESEARCH-<topic>.md`. When this skill is replicated to a new project, that path has no meaning and the files end up in the wrong location.

**Why it happens:** The developer conflates the current project's phase directory (which is this project's self-documentation) with the output location the skill should use when running on any project.

**How to avoid:** The spec-phase SKILL.md must write research files to `.planning/research/RESEARCH-<topic>.md` (a generic, project-agnostic path). Ensure `.planning/research/` is created by the startup scaffolding step.

**Warning signs:** SKILL.md references a hardcoded directory name like `02-spec-phase-greenfield`.

---

### Pitfall 2: YAML Front-Matter Parser Fails on Windows Line Endings

**What goes wrong:** SPEC.md written on a Windows machine or with a Windows-newline editor has `\r\n` line endings. The front-matter parser uses `splitlines()`, which handles this correctly, but a naive `split("\n")` would leave trailing `\r` on every key and value, causing `"status\r"` != `"status"` lookups to silently fail.

**Why it happens:** `split("\n")` does not handle `\r\n`.

**How to avoid:** Use `.splitlines()` in the front-matter parser (not `.split("\n")`). This is already accounted for in the Pattern 2 code above.

**Warning signs:** `parse_frontmatter` returns empty dict on files that visually look correct.

---

### Pitfall 3: validate_spec.py Silently Passes on Missing `.planning/` Directory

**What goes wrong:** If `validate_spec.py` is run before `.planning/` exists (e.g., on a truly empty repo), `Path(".planning/SPEC.md").exists()` returns `False` and the script exits 1 — which is correct. But the error message must be clear: "SPEC.md not found — run /spec-phase first" rather than a generic "file not found."

**Why it happens:** Generic error messages send developers on a debugging hunt.

**How to avoid:** Detect both "`.planning/` missing" and "SPEC.md missing" as distinct states and emit clear actionable error messages for each.

---

### Pitfall 4: Spec-Phase Invoked Twice — SPEC.md Overwritten Without Warning

**What goes wrong:** Developer runs `/spec-phase` a second time (perhaps to revise), and the skill silently overwrites the existing approved SPEC.md, reverting status to `draft`.

**Why it happens:** The startup step doesn't check for an existing SPEC.md.

**How to avoid:** The SKILL.md startup step must check for `.planning/SPEC.md`. If found, present its current status and ask: "An existing spec was found (status: `<status>`). Continue from here, start fresh, or abort?"

---

### Pitfall 5: Research Sub-Agent Writes to Wrong File Name

**What goes wrong:** If the SKILL.md doesn't specify an exact file name convention for research sub-tasks, two sub-agents may both write to `RESEARCH.md`, causing the second to overwrite the first.

**Why it happens:** Loose research prompt without strict naming requirement.

**How to avoid:** The research sub-task prompt must specify the exact output path: `.planning/research/RESEARCH-<topic-slug>.md` where `topic-slug` is a lowercase-hyphenated summary of the topic. The SKILL.md must include this as a required output in the sub-task prompt template.

---

### Pitfall 6: Approval Gate Bypassed by StrReplace on Wrong Target

**What goes wrong:** Agent uses StrReplace on SPEC.md but the `old_string` is `status: draft` — if the developer has already edited status manually to `status: approved`, StrReplace fails (nothing to replace) and the agent may silently skip the approval write.

**Why it happens:** StrReplace requires the old_string to exist verbatim.

**How to avoid:** SKILL.md approval instructions must handle both cases: (a) if `status: draft` is present, replace with `status: approved`; (b) if already `status: approved`, confirm and skip the patch (idempotent). The validate_spec.py tool provides the authoritative check regardless.

---

## Code Examples

### validate_spec.py (full reference implementation)

```python
#!/usr/bin/env python3
"""
tool-validate-spec — Check that SPEC.md exists and has status: approved.
Exit 0: approved. Exit 1: not approved or file not found (message to stderr).
"""
# Source: [ASSUMED — design consistent with Phase 1 exit-code pattern]
import pathlib
import sys


SPEC_CANDIDATES = [
    pathlib.Path(".planning/SPEC.md"),
    pathlib.Path("SPEC.md"),
]


def parse_frontmatter(text: str) -> dict:
    """Parse flat YAML front-matter. Returns {} if none found or malformed."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end].strip()
    result = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result


def main() -> None:
    spec_path = None
    for candidate in SPEC_CANDIDATES:
        if candidate.exists():
            spec_path = candidate
            break

    if spec_path is None:
        print(
            "ERROR: SPEC.md not found in .planning/ or project root.\n"
            "Run /spec-phase first to create and approve a spec.",
            file=sys.stderr,
        )
        sys.exit(1)

    text = spec_path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)

    if not fm:
        print(
            f"ERROR: {spec_path} has no valid YAML front-matter.\n"
            "Expected format:\n---\nstatus: approved\nversion: 1\ndate: YYYY-MM-DD\n---",
            file=sys.stderr,
        )
        sys.exit(1)

    status = fm.get("status", "")
    if status != "approved":
        print(
            f"ERROR: SPEC.md status is '{status}' — must be 'approved' before planning.\n"
            "Run /spec-phase and complete the approval gate.",
            file=sys.stderr,
        )
        sys.exit(1)

    version = fm.get("version", "?")
    date = fm.get("date", "?")
    print(f"✓ SPEC.md approved (version {version}, {date})")
    sys.exit(0)


if __name__ == "__main__":
    main()
```

### SPEC.md template (agent writes this via Write tool)

```markdown
---
status: draft
version: 1
date: 2026-05-21
---

# Spec: <project name>

## Problem

<what problem does this project solve and why does it need solving>

## Who It's For

<primary user(s), their context, what they need to be true>

## Constraints

<technical, time, budget, team, or scope constraints>

## Success Criteria

<measurable conditions that define "done" — how will you know it worked>

## Out of Scope

<what this project explicitly will NOT do in this version>
```

### Research sub-task prompt template (agent includes in Task call)

```
Research the following topic for a software spec:

Topic: <topic>

Project context: <1-2 sentences describing what the user is building, from the Q&A so far>

Write your findings to: .planning/research/RESEARCH-<topic-slug>.md

File format:
# Research: <topic>

## Summary
[2-3 sentence executive summary]

## Key Findings
[Bullet points of factual findings relevant to the spec]

## Implications for Spec
[How these findings should shape the spec's constraints or success criteria]

## Sources
[URLs or source descriptions]

Keep the file concise — the spec author will read this before writing the final spec.
```

---

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| Monolithic spec Q&A in one long prompt | Category spine with per-category probe limits (D-01/D-02) | Prevents open-ended drift; each category reaches closure |
| Spec as free-form text | YAML front-matter + five mandatory sections (D-06/D-07) | Makes status machine-readable; validate_spec.py can enforce the gate |
| Planning gated by honor system | Python script exits non-zero if spec not approved (D-09) | Hard enforcement: plan-phase cannot proceed if validate_spec.py fails |
| Research done inline (pollutes main context) | Sub-agent writes file; main context reads file (D-04) | Preserves clean-context constraint (SPEC-05); sub-agent handles external calls |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | SPEC.md lives at `.planning/SPEC.md` (not explicitly stated in CONTEXT.md) | Architecture, Code Examples | validate_spec.py searches wrong path; planner should confirm or parameterize the path |
| A2 | Research files live at `.planning/research/RESEARCH-<topic>.md` | Architecture, Pitfall 1 | Files land in wrong directory; planner should confirm |
| A3 | spec-phase SKILL.md has no Python companion (pure agent instructions) | Architecture | If Python is needed for state persistence, this assumption is wrong; low risk given conversational nature |
| A4 | The parse_frontmatter design in Pattern 2 handles all edge cases for D-07 schema | Code Examples | Parser fails on edge-case input; mitigated by test coverage |

---

## Open Questions

1. **Where does SPEC.md live?**
   - What we know: `.planning/` contains STATE.md, REQUIREMENTS.md, ROADMAP.md as first-class artifacts
   - What's unclear: Not locked in CONTEXT.md
   - Recommendation: `.planning/SPEC.md` — consistent with existing first-class artifacts; validate_spec.py searches this path first with `.` fallback

2. **Where do research files live?**
   - What we know: D-04 mentions `.planning/phases/02-spec-phase-greenfield/` — but this is the CURRENT project's phase dir, not a replicable path
   - What's unclear: Not locked in CONTEXT.md
   - Recommendation: `.planning/research/RESEARCH-<topic>.md` — generic, project-agnostic, clearly namespaced

3. **Does spec-phase detect an existing SPEC.md and offer resume?**
   - What we know: Not addressed in CONTEXT.md; PROJ-01 focuses on empty repos
   - What's unclear: UX when developer runs `/spec-phase` twice
   - Recommendation: Startup checks for existing SPEC.md; if found, presents status and offers: continue / restart / abort. Prevents silent overwrite.

4. **Should validate_spec.py accept a `--spec` path argument?**
   - What we know: planning_scaffold.py uses `--root` for path override; consistent CLI pattern exists
   - What's unclear: Whether non-standard SPEC.md paths will ever occur
   - Recommendation: Add `--spec PATH` optional arg defaulting to `.planning/SPEC.md`. Low cost, high future flexibility.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| python3 | validate_spec.py | ✓ | 3.9.6 | — (tool-env-check already validates this) |
| pytest | test_validate_spec.py | ✓ | (from Phase 1 test runs) | — |
| Cursor Task tool | Research sub-agent spawning | ✓ | Cursor IDE | — (Cursor-only constraint; no fallback needed) |
| pathlib | validate_spec.py | ✓ | stdlib | — |
| planning_scaffold.py | Startup scaffolding | ✓ | Phase 1 deliverable | Agent can mkdir manually if tool unavailable |

**Missing dependencies with no fallback:** None.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (established in Phase 1) |
| Config file | None (pytest auto-discovers `test_*.py`) |
| Quick run command | `python3 -m pytest mise-en-place/tool-validate-spec/ -x -q` |
| Full suite command | `python3 -m pytest mise-en-place/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SPEC-04 | validate_spec exits 0 on approved SPEC.md | unit | `pytest test_validate_spec.py::test_approved_spec_exits_zero -x` | ❌ Wave 0 |
| SPEC-04 | validate_spec exits 1 on draft SPEC.md | unit | `pytest test_validate_spec.py::test_draft_spec_exits_one -x` | ❌ Wave 0 |
| SPEC-04 | validate_spec exits 1 when SPEC.md missing | unit | `pytest test_validate_spec.py::test_missing_spec_exits_one -x` | ❌ Wave 0 |
| SPEC-04 | validate_spec exits 1 on malformed front-matter | unit | `pytest test_validate_spec.py::test_malformed_frontmatter_exits_one -x` | ❌ Wave 0 |
| SPEC-02 | SPEC.md template contains all five required sections | integration | `pytest test_validate_spec.py::test_approved_spec_has_required_sections -x` | ❌ Wave 0 |
| SPEC-01/05 | SKILL.md structure coverage (doc review) | manual | Reviewer confirms category spine + clean-context instructions present | N/A |

### Sampling Rate
- **Per task commit:** `python3 -m pytest mise-en-place/tool-validate-spec/ -x -q`
- **Per wave merge:** `python3 -m pytest mise-en-place/ -q`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `mise-en-place/tool-validate-spec/test_validate_spec.py` — covers SPEC-04 unit tests (4 cases above)
- [ ] `mise-en-place/tool-validate-spec/validate_spec.py` — the implementation under test

---

## Project Constraints (from .cursor/rules/)

From `.cursor/rules/gsd-workflow.md`:
- **No skipping phases**: Spec must be approved before planning; plan must be approved before execution → validate_spec.py is the enforcement mechanism
- **Atomic commits**: Each plan task gets its own commit → planner must ensure spec-phase SKILL.md and validate-spec tool are separate plan tasks
- **No drive-by refactors**: Phase 2 must not modify Phase 1 tools → validate_spec.py must call planning_scaffold.py as an external subprocess, not inline the scaffold logic
- **Clean context**: Each phase reads only local files → SKILL.md must not reference session state; all context comes from local files read at startup
- **Verification gates**: Tests must pass before advancing → validate_spec.py tests run in the phase gate

---

## Sources

### Primary (HIGH confidence — verified from codebase)
- `mise-en-place/tool-env-check/SKILL.md` — SKILL.md structure; cursor_skill_adapter pattern; exit-code contract
- `mise-en-place/tool-env-check/env_check.py` — stdlib-only script pattern; `shutil`, `subprocess`, `sys` usage
- `mise-en-place/tool-planning-scaffold/planning_scaffold.py` — `pathlib`, `argparse`, `sys.exit`, idempotent file ops
- `mise-en-place/tool-planning-scaffold/SKILL.md` — `write-artifact`, `scaffold` subcommands available for reuse
- `mise-en-place/tool-planning-scaffold/test_planning_scaffold.py` — pytest fixtures, `tmp_path`, `SystemExit` assertion pattern
- `mise-en-place/tool-env-check/test_env_check.py` — `unittest.mock.patch`, timing tests, integration test pattern
- `.planning/phases/01-tooling-foundation/01-CONTEXT.md` — D-01 through D-09: locked tool conventions
- `.planning/phases/02-spec-phase-greenfield/02-CONTEXT.md` — locked decisions D-01 through D-09
- `.planning/PROJECT.md` — Cursor-only, Python stdlib-only, file-based state, tools inside skill folder
- `.cursor/rules/gsd-workflow.md` — workflow enforcement rules

### Secondary (MEDIUM confidence)
- Python 3.9.6 confirmed via `python3 --version` on this machine — `tomllib` not available (requires 3.11+); front-matter must use manual parser

### Tertiary (LOW confidence — ASSUMED)
- validate_spec.py design (Pattern 2 parser, full reference implementation) — consistent with established patterns but new code for this phase

---

## Metadata

**Confidence breakdown:**
- Standard stack (what tools/libraries to use): HIGH — all from codebase inspection
- Architecture (skill structure, file locations): HIGH for pattern; MEDIUM for SPEC.md/research path (see Assumptions Log)
- Pitfalls: HIGH — derived from direct reading of Phase 1 code patterns and constraints
- Code examples: MEDIUM — Pattern 2 and validate_spec.py are new designs consistent with established patterns but untested until implementation

**Research date:** 2026-05-21
**Valid until:** Stable (file-based, no external dependencies; no staleness risk)
