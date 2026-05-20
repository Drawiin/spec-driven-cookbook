<!-- refreshed: 2026-05-20 -->
# Architecture

**Analysis Date:** 2026-05-20

## System Overview

This is a **knowledge/documentation repository**, not a software application. It functions as a research dossier and design-input library for building a new spec-driven AI coding framework ("the cookbook"). There is no runtime, no server, no build pipeline, and no application code. The "architecture" is an information architecture.

```text
┌──────────────────────────────────────────────────────────────┐
│                     Project Vision                           │
│                       README.md                              │
└───────────────────────────┬──────────────────────────────────┘
                            │ informs
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    Research Dossier                          │
│                     research/                                │
├──────────────────┬───────────────────┬───────────────────────┤
│  Entry Hub       │  Framework Dives  │  Cross-cutting Topics │
│  SUMMARY.md      │  frameworks/      │  topics/              │
└──────────────────┴────────┬──────────┴───────────────────────┘
                            │ raw findings produced by
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    Internal Cache                            │
│              research/.research-cache/                       │
│       (not public; source-of-truth for dossier writers)      │
└──────────────────────────────────────────────────────────────┘
                            │ feeds
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                   Future Cookbook                            │
│                   mise-en-place/                             │
│              (placeholder — content not yet added)           │
└──────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File/Path |
|-----------|----------------|-----------|
| Project vision | High-level purpose and philosophy of the cookbook | `README.md` |
| Research hub | Entry point that summarises all dossier content, comparison tables, and top-10 patterns | `research/SUMMARY.md` |
| Framework deep dives | Per-framework profiles: GSD, TLC Spec-Driven, Graphify, and four adjacent frameworks | `research/frameworks/` |
| Cross-cutting topics | Seven theme analyses cutting across all frameworks | `research/topics/` |
| Internal research cache | Raw findings from sub-agent research runs; source-of-truth for dossier writers | `research/.research-cache/` |
| Cookbook placeholder | Future home of recipes, patterns, and implementation guidance | `mise-en-place/` |
| GSD planning workspace | Phase tracking, codebase maps, and project state managed by the GSD framework | `.planning/` |

## Pattern Overview

**Overall:** Hub-and-spoke knowledge graph with a single synthesis hub (`SUMMARY.md`) and specialised detail leaves.

**Key Characteristics:**
- The hub (`research/SUMMARY.md`) is the canonical entry point; it cross-links to every detail document
- Framework profiles and topic analyses are independent leaf documents — each is self-contained and readable without the hub
- The internal `.research-cache/` holds raw findings; the public dossier (`frameworks/`, `topics/`) holds refined, validated output
- `mise-en-place/` is intentionally empty — it is the future output layer, not the current content layer
- No circular dependencies between documents; links flow from hub → leaves

## Layers

**Vision Layer:**
- Purpose: Describe the project's "why" and philosophical direction
- Location: `README.md`
- Contains: Project rationale, philosophy statement
- Depends on: Nothing
- Used by: Readers orienting to the project

**Research Synthesis Layer:**
- Purpose: Distil seven framework deep dives and seven topic analyses into a navigable summary
- Location: `research/SUMMARY.md`
- Contains: Comparison table, top-10 patterns, framework catalogue, navigation links
- Depends on: `research/frameworks/`, `research/topics/`, `research/.research-cache/`
- Used by: Anyone needing a fast answer about frameworks or patterns

**Framework Profile Layer:**
- Purpose: Per-framework deep dives covering architecture, commands, artifact layout, and transferable patterns
- Location: `research/frameworks/`
- Files: `gsd.md`, `tlc-spec-driven.md`, `graphify.md`, `adjacent-frameworks.md`
- Depends on: `research/.research-cache/`
- Used by: `research/SUMMARY.md`, future cookbook recipes

**Topic Analysis Layer:**
- Purpose: Cross-cutting analyses that identify patterns spanning multiple frameworks
- Location: `research/topics/`
- Files: `patterns-worth-stealing.md`, `workflow-and-orchestration.md`, `context-engineering.md`, `local-storage-and-artifacts.md`, `multi-runtime-support.md`, `self-healing-and-verification.md`, `auxiliary-tooling.md`
- Depends on: `research/.research-cache/`
- Used by: `research/SUMMARY.md`, future cookbook design

**Internal Cache Layer:**
- Purpose: Preserve raw sub-agent research findings as the source-of-truth for all writing and validation agents
- Location: `research/.research-cache/`
- Files: `01-gsd-findings.md`, `02-tlc-findings.md`, `03-adjacent-findings.md`, `README.md`
- Depends on: Nothing
- Used by: `research/frameworks/`, `research/topics/`

**Future Cookbook Layer:**
- Purpose: Home for distilled recipes, implementation patterns, and guidance derived from the research
- Location: `mise-en-place/`
- Contents: Currently empty (`README.md` is a zero-byte placeholder)
- Depends on: Research layers (when content is added)
- Used by: Framework builders, future AI agents implementing the cookbook

## Data Flow

### Research Production Path

1. Sub-agents run external research → produce raw findings saved to `research/.research-cache/`
2. Writer agents read `.research-cache/` → produce refined `research/frameworks/*.md` and `research/topics/*.md`
3. Synthesis agent reads all refined docs → produces `research/SUMMARY.md`
4. Reader/planner starts at `research/SUMMARY.md` → follows cross-links to detail as needed

### Future Cookbook Authoring Path

1. Design decisions drawn from `research/topics/patterns-worth-stealing.md` and framework profiles
2. Recipes and patterns authored into `mise-en-place/`
3. `README.md` updated to reflect cookbook sections when content is stable

## Key Abstractions

**Research Dossier:**
- Purpose: A versioned snapshot of framework research produced at a point in time
- Examples: `research/SUMMARY.md`, `research/frameworks/gsd.md`
- Pattern: Hub-and-spoke — one summary document links to specialised leaves

**Framework Profile:**
- Purpose: Self-contained deep dive on one framework covering its architecture, commands, artifact layout, and transferable patterns
- Examples: `research/frameworks/gsd.md`, `research/frameworks/tlc-spec-driven.md`
- Pattern: Standalone markdown document; cross-links back to topic analyses for shared themes

**Topic Analysis:**
- Purpose: Cross-framework study of one recurring design concern (context engineering, self-healing, etc.)
- Examples: `research/topics/patterns-worth-stealing.md`, `research/topics/context-engineering.md`
- Pattern: Ranked patterns with origin, mechanism, transferability score, and adaptation guidance

**Internal Cache:**
- Purpose: Immutable raw findings from initial research runs; the canonical source for validation
- Examples: `research/.research-cache/01-gsd-findings.md`
- Pattern: Named by sequential index with agent ID metadata; separated from public dossier

## Entry Points

**Primary Reader Entry Point:**
- Location: `research/SUMMARY.md`
- Triggers: Any reader or agent needing to understand framework landscape
- Responsibilities: Comparison table, framework catalogue, top-10 patterns, cross-links to all detail

**Fast-Path Entry Point:**
- Location: `research/topics/patterns-worth-stealing.md`
- Triggers: When design input is needed quickly; SUMMARY.md itself recommends this as the fast path
- Responsibilities: 19 ranked patterns by transferability with full mechanism detail

**Project Context Entry Point:**
- Location: `README.md`
- Triggers: New contributor or agent orienting to the project
- Responsibilities: Vision, philosophy, motivation

## Architectural Constraints

- **No application code:** The repository contains only markdown documentation and research artifacts. There is no runtime, server, tests, or build pipeline.
- **Public vs. internal split:** `research/.research-cache/` is flagged in its own `README.md` as potentially gitignore-able; the public dossier (`frameworks/`, `topics/`, `SUMMARY.md`) is intended for commit.
- **Temporal snapshot:** The dossier was produced on 2026-05-19 and treats the post-validation framework files as source of truth at that date. It is not continuously updated.
- **Forward pointer:** `mise-en-place/` exists as an intentional empty placeholder; its presence signals the intended output layer of the repository.

## Anti-Patterns

### Editing framework profiles without consulting the cache

**What happens:** A writer updates `research/frameworks/gsd.md` directly without cross-checking `research/.research-cache/01-gsd-findings.md`
**Why it's wrong:** The cache is the source-of-truth; the profile is the derived output. Updating the profile without the cache creates an unverifiable claim.
**Do this instead:** Read `research/.research-cache/01-gsd-findings.md` first, then update the profile with an inline source reference.

### Adding content to `mise-en-place/` before research synthesis is complete

**What happens:** Cookbook recipes are written while the research dossier is still in draft
**Why it's wrong:** Recipes will be based on incomplete pattern analysis; the SUMMARY.md top-10 and topic analyses should gate cookbook authoring
**Do this instead:** Complete `research/SUMMARY.md` and validate against the cache before adding content to `mise-en-place/`

## Error Handling

**Strategy:** Not applicable (documentation repository — no runtime errors).

## Cross-Cutting Concerns

**Versioning:** Research snapshot dated 2026-05-19; documents contain their production date in prose.
**Navigation:** All documents use relative markdown links; `SUMMARY.md` is the canonical hub.
**Visibility split:** Internal cache vs. public dossier separation is managed by gitignore policy documented in `research/.research-cache/README.md`.

---

*Architecture analysis: 2026-05-20*
