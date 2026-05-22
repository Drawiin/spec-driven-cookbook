# Phase 3: Brownfield Codebase Onboarding - Research

**Researched:** 2026-05-22
**Domain:** Brownfield detection, codebase mapping, spec-phase extension
**Confidence:** HIGH

## Summary

Phase 3 extends the Phase 2 greenfield `/spec-phase` workflow so a developer can run the framework on a repo with existing code, automatically map the codebase, and produce a `SPEC.md` that cleanly separates validated existing capabilities from new requirements. The implementation should follow established Phase 1–2 patterns: Python stdlib-only deterministic tools in `mise-en-place/tool-*`, workflow logic in `SKILL.md` files, and file-based artifacts under `.planning/`.

The primary architectural split mirrors GSD and TLC: **deterministic detection and scaffolding** (Python) vs **semantic codebase analysis** (Cursor sub-agents writing to `.planning/codebase/`). `context_builder.py` already produces raw structural context (tree, deps, git, previews) but cannot infer architecture, conventions, or capabilities — that requires agent mappers, following the GSD `gsd-codebase-mapper` four-focus parallel pattern documented in [research/frameworks/gsd.md](../../research/frameworks/gsd.md) and implemented locally at `.cursor/get-shit-done/workflows/map-codebase.md`. [CITED: `.cursor/get-shit-done/bin/lib/init.cjs` brownfield detection logic]

**Primary recommendation:** Add `tool-detect-brownfield` (stdlib Python exit-code/JSON contract), add `map-codebase/SKILL.md` (parallel mapper sub-agents → seven `.planning/codebase/*.md` files using GSD templates as format reference), extend `spec-phase/SKILL.md` with **Step 1.4: Brownfield Detection (runs after scaffold, before Step 2 Q&A)** that runs detection → mapping → loads map into Q&A context on every Step 1 branch, extend `validate_spec.py` to require `## Already Built` and `## To Build` when `project_type: brownfield` (plus inverse rule when brownfield sections present without frontmatter), and keep greenfield behavior unchanged when detection returns greenfield.

<user_constraints>
## User Constraints (from available sources)

### Locked Decisions (from PROJECT.md, Phase 1/2 CONTEXT, ROADMAP)

- **Python stdlib only** for all tool scripts — zero pip dependencies at runtime (Phase 1 D-01)
- **Cursor-only v1** — no multi-runtime adapter layer (PROJECT.md)
- **File-based state** in `.planning/` — version-control friendly, no databases (PROJECT.md)
- **Skills in `mise-en-place/`** with `tool-*` pattern for deterministic utilities; workflow skills (`spec-phase`) are SKILL.md-only (Phase 1 D-02–D-04, Phase 2 pattern)
- **Phase 2 spec-phase is the base** — Phase 3 extends, does not replace greenfield flow (ROADMAP depends-on Phase 2)
- **Exit-code contract:** tools exit 0 on success/pass, non-zero on failure with stderr message (Phase 1/2)
- **Research output path:** `.planning/research/RESEARCH-<topic-slug>.md` (Phase 2 portability override)
- **Approval gate preserved:** `validate_spec.py` must still enforce `status: approved` before planning (Phase 2 D-08, D-09)
- **Clean context:** spec phase reads only local files — no session history assumed (SPEC-05, PROJ-01)

### Claude's Discretion (proposed for discuss-phase — not yet locked)

- Exact brownfield detection depth threshold (GSD uses depth 3 file walk; recommend matching)
- Whether `map-codebase` is invokable standalone vs only via spec-phase (recommend: both — GSD pattern)
- Fast/single-agent map mode for trivial repos (<5 source files) vs always 4-agent parallel (recommend: offer `--fast` in map-codebase SKILL, default full map for spec-phase integration)
- Confidence tagging on inferred capabilities in `## Already Built` (`[observed]` / `[inferred]` / `[unverified]` per Pattern 13 in patterns-worth-stealing.md)
- Whether brownfield Q&A reorders categories or only skips redundant probes (recommend: same five-category spine, but Problem/Success Criteria focus on delta not inventory)

### Deferred Ideas (OUT OF SCOPE)

- Codebase drift gate / auto-remap after execute (GSD Phase 5+ concern; ROADMAP Phase 6)
- Replication engine bootstrap (ROADMAP Phase 7–8)
- Graph/knowledge-graph indexing (GSD `intel.enabled` / graphify — out of v1 scope per PROJECT.md)
- Multi-runtime support (v2 RTME-* requirements)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PROJ-02 | Framework works on existing codebases — a codebase mapping step runs before the spec phase if code exists | `tool-detect-brownfield` detection contract; `map-codebase/SKILL.md` mapper workflow; spec-phase Step 1.4 branch triggers map when `needs_codebase_map: true` |
| PROJ-03 | Codebase map is used to seed the spec with what already exists (validated capabilities) vs. what is new (active requirements) | Load `.planning/codebase/*.md` into Q&A context; SPEC.md sections `## Already Built` + `## To Build`; validate_spec enforcement; Q&A skips re-asking mapped facts |
</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Brownfield vs greenfield detection | Deterministic tool (Python stdlib) | spec-phase orchestrator reads JSON | File-walk heuristics are repeatable; must not depend on session memory |
| Raw structural snapshot | `tool-context-builder` (Python) | Mapper sub-agent prompts | Tree/deps/git are mechanical; already implemented |
| Semantic codebase analysis | Agent sub-agents (Task tool) | Templates in SKILL.md | Architecture, conventions, concerns require code reading — not hand-rollable in stdlib |
| Codebase map persistence | File storage (`.planning/codebase/`) | planning_scaffold scaffold | File-based state model; directory already created by scaffold |
| Already-built vs to-build separation | SPEC.md document contract | validate_spec.py gate | Spec is the contract for downstream plan phase |
| Q&A that avoids re-asking | spec-phase orchestrator (SKILL.md) | Codebase map as loaded context | Orchestrator decides what to probe; map supplies "known facts" |
| Approval before planning | validate_spec.py | plan-phase (future) | Phase 2 belt-and-suspenders pattern continues |

## Standard Stack

### Core

| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| Python | 3.9+ (verified: 3.9.6 in env) | Deterministic detection + validation | Phase 1 locked decision; stdlib-only |
| pytest | dev-only (not bundled) | Test gate for new tools | Existing pattern — 22 tests in `mise-en-place/` |
| Cursor Task tool | Cursor default model | Parallel codebase mapper sub-agents | Phase 2 research sub-agent pattern; GSD mapper pattern |
| `.planning/codebase/` layout | 7 files (GSD/TLC convention) | Persistent codebase map | Already exists in this repo; TLC + GSD both use same set [CITED: research/frameworks/tlc-spec-driven.md §6] |

**Seven codebase map files (canonical):**
`STACK.md`, `ARCHITECTURE.md`, `CONVENTIONS.md`, `STRUCTURE.md`, `TESTING.md`, `INTEGRATIONS.md`, `CONCERNS.md`

**Template source (format reference, not runtime dependency):**
`.cursor/get-shit-done/templates/codebase/*.md` — copy section structure into mapper sub-agent prompts [VERIFIED: local repo]

### Supporting

| Component | Version | Purpose | When to Use |
|-----------|---------|---------|-------------|
| `context_builder.py` | Phase 1 | Seed mapper prompts with tree/deps/git/previews | Before spawning mappers; reduces mapper token waste |
| `planning_scaffold.py scaffold` | Phase 1 | Ensure `.planning/codebase/` exists | spec-phase Step 1 (already called) |
| `validate_spec.py` | Phase 2 | Gate planning on approved spec + sections | Extended for brownfield headers |
| GSD `init.cjs` detection logic | GSD v1.42.3 (reference) | Detection heuristic parity | Port algorithm to Python in `tool-detect-brownfield` |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| New `tool-detect-brownfield.py` | Inline checks in spec-phase SKILL only | SKILL-only detection is non-testable and duplicates logic; violates Phase 1 tool pattern |
| 4 parallel mapper agents | Single agent writes all 7 docs | Faster/cheaper but context rot on large repos; GSD/TLC delegate mapping to sub-agents for this reason |
| Extend `context_builder.py` only | Full mapper workflow | context_builder outputs raw data, not semantics — insufficient for PROJ-03 |
| Separate `/brownfield-spec` command | Extend `/spec-phase` | Violates "one command" UX; ROADMAP says "run the framework on a repo" not a new command |

**Installation:** None — stdlib only. No external packages for Phase 3 deliverables.

## Package Legitimacy Audit

> Phase 3 installs no external runtime packages. Dev dependency `pytest` already used in Phase 1–2.

| Package | Registry | slopcheck | Disposition |
|---------|----------|-----------|-------------|
| (none) | — | — | N/A — stdlib-only phase |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
Developer runs /spec-phase
        │
        ▼
┌───────────────────┐
│ planning_scaffold │──► .planning/ + .planning/codebase/ (idempotent)
└─────────┬─────────┘
          │
          ▼
┌───────────────────────┐     greenfield          ┌─────────────────┐
│ tool-detect-brownfield│────────────────────────►│ Phase 2 Q&A     │
│ (stdlib JSON stdout)  │                         │ (unchanged)     │
└─────────┬─────────────┘                         └────────┬────────┘
          │ brownfield + needs_map                       │
          ▼                                              │
┌───────────────────────┐                                │
│ context_builder.py    │── raw snapshot ──────────────┤
└─────────┬─────────────┘                                │
          ▼                                              │
┌───────────────────────┐                                │
│ map-codebase SKILL    │                                │
│ 4× Task sub-agents    │──► .planning/codebase/*.md (7)│
└─────────┬─────────────┘                                │
          │ map loaded                                   │
          ▼                                              ▼
┌───────────────────────────────────────────────────────────────┐
│ spec-phase Q&A (brownfield mode)                              │
│ - Pre-load codebase map summaries                             │
│ - Skip probes for facts already in map                        │
│ - Focus Success Criteria on NEW work only                     │
└─────────────────────────┬─────────────────────────────────────┘
                          ▼
┌───────────────────────────────────────────────────────────────┐
│ SPEC.md assembly                                              │
│ - project_type: brownfield in frontmatter                     │
│ - ## Already Built  (from map + user confirmation)            │
│ - ## To Build       (active requirements — no overlap)        │
│ - + existing 5 greenfield sections where applicable           │
└─────────────────────────┬─────────────────────────────────────┘
                          ▼
┌───────────────────────┐
│ validate_spec.py      │── exit 0 only if approved + sections
└───────────────────────┘
```

### Recommended Project Structure

```
mise-en-place/
├── tool-detect-brownfield/
│   ├── SKILL.md
│   ├── detect_brownfield.py      # NEW — stdlib detection + JSON stdout
│   └── test_detect_brownfield.py # NEW — pytest
├── map-codebase/
│   └── SKILL.md                  # NEW — workflow skill (no Python)
├── spec-phase/
│   └── SKILL.md                  # MODIFIED — Step 1.4 brownfield branch
├── tool-validate-spec/
│   ├── validate_spec.py          # MODIFIED — brownfield section checks
│   └── test_validate_spec.py     # MODIFIED — brownfield cases
└── README.md                     # MODIFIED — catalog entries

.planning/
├── codebase/                     # OUTPUT — 7 mapper documents
│   ├── STACK.md
│   ├── ARCHITECTURE.md
│   ├── CONVENTIONS.md
│   ├── STRUCTURE.md
│   ├── TESTING.md
│   ├── INTEGRATIONS.md
│   └── CONCERNS.md
└── SPEC.md                       # OUTPUT — includes Already Built / To Build
```

### Pattern 1: Detect → Map → Spec (GSD Brownfield Prep)

**What:** Before Q&A opens, deterministic detection decides whether mapping is required; semantic mapping runs via sub-agents; spec flow consumes map as read-only context.

**When to use:** Any repo where `has_existing_code || has_package_file` (GSD `is_brownfield` definition). [CITED: `.cursor/get-shit-done/bin/lib/init.cjs` lines 470–474]

**Detection outputs (JSON to stdout):**
```json
{
  "is_brownfield": true,
  "has_existing_code": true,
  "has_package_file": false,
  "has_codebase_map": false,
  "needs_codebase_map": true,
  "code_extensions_found": [".py"]
}
```

**Exit codes:** Always 0 on successful detection (like `context_builder.py` graceful pattern); non-zero only on invalid `--root` path.

### Pattern 2: Parallel Focus Mappers (GSD map-codebase)

**What:** Four sub-agents with fresh context, each writing directly to disk — orchestrator never ingests full map content.

| Agent focus | Writes |
|-------------|--------|
| tech | STACK.md, INTEGRATIONS.md |
| arch | ARCHITECTURE.md, STRUCTURE.md |
| quality | CONVENTIONS.md, TESTING.md |
| concerns | CONCERNS.md |

**When to use:** Brownfield repos with more than trivial code (>5 source files per GSD skip guidance). [CITED: `.cursor/skills/gsd-map-codebase/SKILL.md`]

**Sub-agent type:** `Task(subagent_type="generalPurpose")` — cookbook v1 does not ship `gsd-codebase-mapper` inside `mise-en-place/`; embed mapper prompt + template sections in `map-codebase/SKILL.md` (Phase 2 uses generalPurpose for research).

### Pattern 3: Current Truth vs Proposed Truth in SPEC.md (OpenSpec + GSD brownfield)

**What:** SPEC.md explicitly separates validated existing capabilities from new requirements — no mixed bullets.

**Proposed brownfield SPEC.md body sections:**
```markdown
## Already Built
<!-- Capabilities confirmed from codebase map + user validation during Q&A -->
<!-- Tag inferred items: [observed] direct code evidence, [inferred] pattern-based -->

## To Build
<!-- Active requirements for THIS spec cycle — must not duplicate Already Built -->

## Problem
## Who It's For
## Constraints
## Success Criteria   <!-- scoped to To Build items only in brownfield mode -->
## Out of Scope
```

**Frontmatter addition:**
```yaml
---
status: draft
version: 1
date: YYYY-MM-DD
project_type: brownfield   # or greenfield
codebase_map_commit: abc1234  # optional — git HEAD when map completed
---
```

### Pattern 4: Brownfield Q&A Context Loading (TLC three-zone)

**What:** Before opening Q&A, orchestrator reads `.planning/codebase/STACK.md`, `ARCHITECTURE.md`, `STRUCTURE.md` (minimum); uses them as "known facts" — probes only gaps and new intent.

**When to use:** After map completes or when stale map exists (offer refresh/skip/update per GSD map-codebase check_existing step). [CITED: `.cursor/get-shit-done/workflows/map-codebase.md`]

### Anti-Patterns to Avoid

- **Dumping full codebase map into Q&A prompt:** Load summaries only; mappers already wrote files — re-read selectively (TLC on-demand load pattern)
- **Mixing built and new in Success Criteria:** Violates PROJ-03 and ROADMAP success criterion #3
- **Skipping user confirmation of "Already Built":** Map inferences are not requirements until user validates (GSD PROJECT.md brownfield template: "Present inferred current state")
- **Hand-rolling architecture analysis in Python:** stdlib cannot replace semantic code reading
- **Breaking greenfield validate_spec contract:** Brownfield sections additive only when `project_type: brownfield`

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Detect source files in repo | Custom bash/find one-offs | `tool-detect-brownfield.py` porting GSD `init.cjs` logic | Cross-platform, testable, single contract |
| Directory tree + deps snapshot | Re-parse in mapper agents | `context_builder.py` | Already handles gitignore, exclusions, entry points |
| Architecture/convention inference | Regex over all files | Mapper sub-agents + templates | Needs semantic understanding; GSD/TLC both delegate |
| `.planning/` directory creation | mkdir in SKILL ad-hoc | `planning_scaffold.py scaffold` | Idempotent, tested, creates codebase dir |
| Spec approval gate | SKILL-only check | `validate_spec.py` | Phase 2 belt-and-suspenders; plan-phase relies on exit code |
| Seven-file map format | Invent new schema | GSD templates + existing `.planning/codebase/` in repo | Downstream phases expect consistent map shape |

**Key insight:** Phase 3 adds a **thin deterministic shell** (detect + validate) around **existing agent mapping and spec workflows** — not a new pipeline.

## Project Constraints (from .cursor/rules/)

- Workflow enforcement: spec approved before planning; atomic commits; no drive-by refactors; verification gates; clean context (`.cursor/rules/gsd-workflow.md`)
- ArcTouch rules apply to implementation quality but do not override stdlib-only / file-based state project decisions

## Common Pitfalls

### Pitfall 1: False Greenfield on Docs-Heavy Repos

**What goes wrong:** Repo has Python in `mise-en-place/` but detection only checks root — or conversely, treats `research/` markdown as "no code" while missing `mise-en-place/*.py`.

**Why it happens:** Shallow detection or wrong skip dirs.

**How to avoid:** Port GSD's depth-3 recursive walk with code extensions set and skip dirs including `.planning`, `.git`, `node_modules`, `__pycache__`. [CITED: init.cjs lines 406–436]

**Warning signs:** `/spec-phase` opens greenfield Q&A on repo with `tool-validate-spec/validate_spec.py`.

### Pitfall 2: Stale Codebase Map

**What goes wrong:** `.planning/codebase/` exists from prior session but code changed; spec seeds wrong "Already Built".

**Why it happens:** `needs_codebase_map` false when directory exists but content is stale.

**How to avoid:** MVP — if map exists, prompt refresh/skip (GSD check_existing). Optional: compare `codebase_map_commit` in SPEC frontmatter to `git rev-parse HEAD`. Defer auto-drift to Phase 6.

**Warning signs:** STACK.md references dependencies removed from manifest.

### Pitfall 3: Already Built / To Build Duplication

**What goes wrong:** Same capability listed in both sections; planner double-implements.

**Why it happens:** Q&A assembles sections independently without dedup pass.

**How to avoid:** Assembly step rule: every `To Build` item must reference a gap not covered in `Already Built`; validate_spec optional lint for overlapping requirement IDs.

**Warning signs:** Success Criteria mentions "add auth" while Already Built says "JWT auth in `src/auth/`".

### Pitfall 4: validate_spec Regression for Greenfield

**What goes wrong:** Adding brownfield headers breaks existing 6 pytest functions and greenfield `/spec-phase`.

**Why it happens:** Unconditional new REQUIRED_SECTIONS.

**How to avoid:** Brownfield sections required only when `project_type: brownfield` in frontmatter; greenfield specs unchanged.

**Warning signs:** `test_approved_spec_exits_zero` fails after Phase 3.

### Pitfall 5: Mapper Context Bloat

**What goes wrong:** Single orchestrator reads all seven map files plus full repo into spec Q&A context.

**Why it happens:** Ignoring TLC/GSD "sub-agent writes file, orchestrator reads summary" pattern.

**How to avoid:** Mappers write files; spec-phase reads targeted summaries (STACK + ARCHITECTURE + STRUCTURE for Q&A seed; full files available on disk for research sub-tasks).

**Warning signs:** Context warnings before Q&A question 1.

## Code Examples

### Detection heuristic (port from GSD init.cjs)

```python
# Source: .cursor/get-shit-done/bin/lib/init.cjs (brownfield detection)
CODE_EXTENSIONS = {
    ".ts", ".js", ".py", ".go", ".rs", ".swift", ".java",
    ".kt", ".kts", ".c", ".cpp", ".h", ".cs", ".rb", ".php",
    ".dart", ".m", ".mm", ".scala", ".groovy", ".lua", ".r", ".R",
    ".zig", ".ex", ".exs", ".clj",
}
SKIP_DIRS = {
    "node_modules", ".git", ".planning", ".claude", ".codex",
    "__pycache__", "target", "dist", "build",
}
PACKAGE_FILES = (
    "package.json", "requirements.txt", "Cargo.toml", "go.mod",
    "pyproject.toml", "pom.xml", "Gemfile", "composer.json",
)

def find_code_files(root: pathlib.Path, depth: int = 0, max_depth: int = 3) -> bool:
    if depth > max_depth:
        return False
    for entry in root.iterdir():
        if entry.is_file() and entry.suffix in CODE_EXTENSIONS:
            return True
        if entry.is_dir() and entry.name not in SKIP_DIRS:
            if find_code_files(entry, depth + 1, max_depth):
                return True
    return False
```

### spec-phase brownfield branch (SKILL.md insertion — Step 1.4)

```markdown
## Step 1.4: Brownfield Detection (runs after scaffold, before Step 2 Q&A)

Runs at END of Step 1 on EVERY branch (Start fresh AND Continue with existing SPEC.md).

1. Run detection:
   python3 mise-en-place/tool-detect-brownfield/detect_brownfield.py

2. Parse JSON from stdout — if invalid JSON, ERROR and STOP (do not proceed to Q&A).

3. If `is_brownfield` is false → continue to Step 2 (greenfield Q&A).

4. If `is_brownfield` is true:
   a. Set brownfield mode flag immediately (not deferred to Step 4)
   b. If `needs_codebase_map` is true → run map-codebase workflow (read map-codebase/SKILL.md)
   c. If map exists → offer (1) Refresh (2) Skip (3) Update specific docs; warn if codebase_map_commit != HEAD on Skip
   d. Require all 7 map files with >20 lines each — partial maps fail with retry prompt
   e. Read one-line summaries from ALL seven `.planning/codebase/*.md` files
   f. Present 3–5 bullet summary; require user confirm/correct before Q&A
   g. Continue to Step 2 with brownfield mode: do NOT re-ask facts already in map
```

### validate_spec brownfield extension

```python
# Source: pattern from mise-en-place/tool-validate-spec/validate_spec.py
BROWNFIELD_SECTIONS = [
    "## Already Built",
    "## To Build",
]

def main() -> None:
    # ... existing frontmatter + greenfield REQUIRED_SECTIONS checks ...
    project_type = fm.get("project_type", "greenfield")
    if project_type == "brownfield":
        for header in BROWNFIELD_SECTIONS:
            if header not in text:
                print(f"ERROR: brownfield SPEC.md missing: {header}", file=sys.stderr)
                sys.exit(1)
```

### Mapper sub-agent prompt skeleton

```markdown
# Sub-agent: codebase mapper (focus: arch)
# Output files (write directly with Write tool):
#   - .planning/codebase/ARCHITECTURE.md
#   - .planning/codebase/STRUCTURE.md
#
# Template sections: see .cursor/get-shit-done/templates/codebase/architecture.md
# Raw snapshot (optional): output of context_builder.py appended below
#
# Rules:
# - Include concrete file paths with backticks
# - Describe current state only (what IS)
# - Mark uncertain claims [unverified]
# - Do NOT return full document contents in your final message — confirm paths + line counts only
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Greenfield-only `/spec-phase` | Detect brownfield → map → delta-focused spec | Phase 3 (this) | PROJ-02, PROJ-03 satisfied |
| Manual codebase paste | Structured `.planning/codebase/` map | GSD map-codebase / TLC brownfield-mapping | Reusable across plan/execute phases |
| Spec = all requirements | Spec splits Already Built vs To Build | OpenSpec current/proposed model; GSD PROJECT brownfield block | Prevents replanning existing work |

**Deprecated/outdated:**
- Phase 2 spec-phase opening line "including an empty repo" remains true but incomplete — update to "empty or existing repo" after Phase 3

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | GSD depth-3 code walk is sufficient for MVP detection | Pattern 1 | Misses deeply nested monorepo code — may false-greenfield |
| A2 | `generalPurpose` sub-agents suffice without shipping `gsd-codebase-mapper` in mise-en-place | Pattern 2 | Lower map quality vs GSD-native mapper prompts |
| A3 | Seven-file map set is enough for spec seeding | Standard Stack | Some stacks need extra docs — defer custom files to v2 |
| A4 | `project_type: brownfield` frontmatter is acceptable extension to Phase 2 SPEC format | Pattern 3 | May require plan-phase updates later |

## Open Questions (RESOLVED)

1. **Should greenfield specs gain optional `## Already Built` with "N/A — greenfield"?**
   - RESOLVED: No — omit brownfield sections entirely when `project_type: greenfield` (default). Plan 03-01 implements conditional BROWNFIELD_SECTIONS gate.

2. **Standalone `/map-codebase` vs spec-phase-only mapping?**
   - RESOLVED: Ship `map-codebase/SKILL.md` invokable standalone AND from spec-phase Step 1.4. Plan 03-02 Slice 1.

3. **Human confirmation gate for Already Built before Q&A?**
   - RESOLVED: Yes — one confirmation turn after map, before Problem category. Plan 03-02 Task 2.

4. **Confidence tags on inferred Already Built items?**
   - RESOLVED: Yes — [observed] / [inferred] / [unverified] tags. Plan 03-02 Task 3.

5. **Fast single-agent map for trivial repos?**
   - RESOLVED: Optional `--fast` documented in map-codebase SKILL; default remains 4-agent parallel. Plan 03-02 Task 1.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3 | tool scripts | ✓ | 3.9.6 | — |
| pytest | dev tests | ✓ (when installed) | — | `pip install pytest` dev-only per README |
| git | context_builder, map commit stamp | ✓ | — | Skip commit in frontmatter if not repo |
| Cursor Task tool | map-codebase mappers | ✓ | — | Block — agent mapping requires Task |
| Node.js | Phase 3 deliverables | ✗ | — | Not required — stdlib Python only |

**Missing dependencies with no fallback:**
- Cursor IDE with agent Task spawning (project constraint: Cursor-only v1)

**Missing dependencies with fallback:**
- None blocking for deterministic tools

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (dev-only) |
| Config file | none — pytest discovers `test_*.py` under `mise-en-place/` |
| Quick run command | `python3 -m pytest mise-en-place/ -x -q` |
| Full suite command | `python3 -m pytest mise-en-place/ -q` |

**Current baseline:** 22 tests passing (verified 2026-05-22)

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PROJ-02 | Detect brownfield when `.py` files exist under `mise-en-place/` | unit | `pytest mise-en-place/tool-detect-brownfield/test_detect_brownfield.py -x` | ❌ Wave 0 |
| PROJ-02 | Detect greenfield on empty tmp dir | unit | same | ❌ Wave 0 |
| PROJ-02 | `needs_codebase_map` true when brownfield + no `.planning/codebase/` | unit | same | ❌ Wave 0 |
| PROJ-03 | validate_spec rejects brownfield spec missing `## Already Built` | unit | `pytest mise-en-place/tool-validate-spec/test_validate_spec.py -x` | ❌ Wave 0 (extend) |
| PROJ-03 | validate_spec rejects brownfield spec missing `## To Build` | unit | same | ❌ Wave 0 (extend) |
| PROJ-03 | validate_spec passes brownfield approved spec with all sections | unit | same | ❌ Wave 0 (extend) |
| PROJ-02/03 | Greenfield specs still pass without brownfield sections | regression | `pytest mise-en-place/tool-validate-spec/test_validate_spec.py -x` | ✅ (extend, must stay green) |
| SPEC-04 | Draft brownfield spec exits 1 | unit | same as Phase 2 | ✅ (extend) |

### Sampling Rate

- **Per task commit:** `python3 -m pytest mise-en-place/tool-detect-brownfield/ mise-en-place/tool-validate-spec/ -x -q`
- **Per wave merge:** `python3 -m pytest mise-en-place/ -q`
- **Phase gate:** Full suite green (22 + new tests) before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `mise-en-place/tool-detect-brownfield/detect_brownfield.py` — covers PROJ-02 detection contract
- [ ] `mise-en-place/tool-detect-brownfield/test_detect_brownfield.py` — unit tests with tmp_path fixtures
- [ ] `mise-en-place/tool-detect-brownfield/SKILL.md` — invocation contract
- [ ] Extend `validate_spec.py` + `test_validate_spec.py` — brownfield section gates (PROJ-03)
- [ ] `mise-en-place/map-codebase/SKILL.md` — mapper workflow (manual UAT for agent spawning)
- [ ] Extend `spec-phase/SKILL.md` — Step 1.4 + brownfield Q&A + assembly rules
- [ ] Manual UAT script in phase VERIFICATION: run `/spec-phase` on this repo (brownfield) and confirm map + SPEC sections

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | yes | `--root` path validation (same as context_builder/planning_scaffold — reject paths outside cwd) |
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V6 Cryptography | no | — |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal via `--root` | Tampering | Resolve path; reject if outside cwd (existing Phase 1 pattern) |
| Mapper reads `.env` secrets | Information disclosure | SKILL.md instructs: note `.env` existence only, never read contents (GSD mapper rule) |
| Over-broad filesystem walk | DoS (slow run) | Depth limit 3; skip dirs; timeout on git subprocess (context_builder uses 10s) |

## Sources

### Primary (HIGH confidence)
- `.cursor/get-shit-done/bin/lib/init.cjs` — brownfield detection algorithm (`is_brownfield`, `needs_codebase_map`)
- `.cursor/get-shit-done/workflows/map-codebase.md` — parallel mapper orchestration, check_existing flow
- `.cursor/get-shit-done/templates/codebase/*.md` — seven-file map templates
- `mise-en-place/spec-phase/SKILL.md` — Phase 2 workflow to extend
- `mise-en-place/tool-context-builder/context_builder.py` — raw context assembly
- `mise-en-place/tool-validate-spec/validate_spec.py` — approval gate contract
- `.planning/codebase/` — live reference output format in this repo

### Secondary (MEDIUM confidence)
- `research/frameworks/gsd.md` — GSD brownfield prep step and artifact layout
- `research/frameworks/tlc-spec-driven.md` — TLC `.specs/codebase/` layout and delegation matrix
- `research/topics/patterns-worth-stealing.md` — Patterns 6, 13 (sub-agent contract, confidence tagging)
- `.cursor/get-shit-done/templates/project.md` `<brownfield>` block — Validated vs Active requirements flow

### Tertiary (LOW confidence — propose for discuss-phase)
- OpenSpec current-vs-proposed spec model — inferred from `research/frameworks/adjacent-frameworks.md`; not verified against OpenSpec source in this session

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — built entirely from Phase 1–2 code + local GSD reference implementation
- Architecture: HIGH — GSD/TLC patterns verified in research dossier and local `.cursor/` workflows
- Pitfalls: MEDIUM — mapper quality and stale-map edge cases depend on discuss-phase decisions

**Research date:** 2026-05-22
**Valid until:** 2026-06-22 (30 days — stable patterns)

## RESEARCH COMPLETE

**Phase:** 3 - Brownfield Codebase Onboarding
**Confidence:** HIGH

### Key Findings

- Phase 3 should extend `/spec-phase`, not create a parallel command — add deterministic `tool-detect-brownfield`, workflow `map-codebase/SKILL.md`, and brownfield branches in spec assembly/validation
- GSD's `init.cjs` detection algorithm ports cleanly to stdlib Python; semantic mapping must stay agent-driven with seven-file output under `.planning/codebase/`
- PROJ-03 requires dedicated `## Already Built` and `## To Build` SPEC.md sections with validate_spec enforcement when `project_type: brownfield`
- `context_builder.py` seeds mappers but does not replace them; greenfield Phase 2 flow must remain unchanged for non-brownfield repos
- Wave 0 needs new detect tool tests + validate_spec extensions before SKILL.md workflow changes; 22 existing tests must stay green

### File Created

`.planning/phases/03-brownfield-codebase-onboarding/03-RESEARCH.md`

### Confidence Assessment

| Area | Level | Reason |
|------|-------|--------|
| Standard Stack | HIGH | Stdlib-only constraint + existing tools verified in repo |
| Architecture | HIGH | GSD map-codebase workflow available locally as reference |
| Pitfalls | MEDIUM | Stale-map and mapper-quality risks need discuss-phase locks |

### Open Questions

- Standalone `/map-codebase` exposure (recommended: yes)
- Confidence tags on inferred Already Built items (recommended: yes, lightweight)
- Fast single-agent map for trivial repos (recommended: optional flag, not default)

### Ready for Planning

Research complete. Planner can now create PLAN.md files.
