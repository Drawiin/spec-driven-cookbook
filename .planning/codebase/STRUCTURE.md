# Codebase Structure

**Analysis Date:** 2026-05-20

## Directory Layout

```
spec-driven-cookbook/
├── README.md                          # Project vision and philosophy
├── mise-en-place/                     # Future cookbook content (currently empty)
│   └── README.md                      # Zero-byte placeholder
├── research/                          # Research dossier on spec-driven AI frameworks
│   ├── SUMMARY.md                     # Hub entry point — comparison table, top-10 patterns
│   ├── frameworks/                    # Per-framework deep dives (public dossier)
│   │   ├── gsd.md                     # GSD / get-shit-done deep dive
│   │   ├── tlc-spec-driven.md         # TLC Spec-Driven skill deep dive
│   │   ├── graphify.md                # Graphify knowledge-graph framework deep dive
│   │   └── adjacent-frameworks.md    # Spec Kit, OpenSpec, Task Master, BMAD-METHOD
│   ├── topics/                        # Cross-cutting topic analyses (public dossier)
│   │   ├── patterns-worth-stealing.md # 19 ranked transferable patterns
│   │   ├── workflow-and-orchestration.md
│   │   ├── context-engineering.md
│   │   ├── local-storage-and-artifacts.md
│   │   ├── multi-runtime-support.md
│   │   ├── self-healing-and-verification.md
│   │   └── auxiliary-tooling.md
│   └── .research-cache/               # Internal raw findings (not public)
│       ├── README.md                  # Cache metadata and gitignore policy
│       ├── 01-gsd-findings.md         # Raw GSD research (agent ccfe45b2)
│       ├── 02-tlc-findings.md         # Raw TLC research (agent 59e11448)
│       └── 03-adjacent-findings.md    # Raw adjacent-frameworks research (agent ff83e72c)
├── .planning/                         # GSD planning workspace
│   └── codebase/                      # Codebase analysis documents (this directory)
└── .cursor/                           # IDE configuration (Cursor/VSCode)
```

## Directory Purposes

**`research/` — Research Dossier:**
- Purpose: Complete research sweep of seven spec-driven AI coding frameworks conducted 2026-05-19
- Contains: One summary hub, four framework profiles, seven topic analyses, one internal cache
- Key files: `research/SUMMARY.md` (start here), `research/topics/patterns-worth-stealing.md` (fast design input)

**`research/frameworks/` — Framework Profiles:**
- Purpose: Self-contained deep dives on individual frameworks
- Contains: Architecture, commands, artifact layout, and transferable patterns per framework
- Key files: `gsd.md` (most comprehensive at 37 KB), `tlc-spec-driven.md`, `graphify.md`, `adjacent-frameworks.md`

**`research/topics/` — Topic Analyses:**
- Purpose: Cross-framework analyses of recurring design concerns
- Contains: Ranked patterns with origin, mechanism, transferability, and adaptation guidance
- Key files: `patterns-worth-stealing.md` (19 patterns, 30 KB), `workflow-and-orchestration.md` (34 KB)

**`research/.research-cache/` — Internal Cache:**
- Purpose: Preserve raw sub-agent findings as source-of-truth; not for public consumption
- Contains: Three timestamped findings files plus a README with gitignore guidance
- Generated: Yes (by research sub-agents on 2026-05-19)
- Committed: Optional (README.md recommends gitignoring this directory)

**`mise-en-place/` — Future Cookbook:**
- Purpose: Placeholder directory for future cookbook recipes, patterns, and implementation guidance
- Contains: Single empty `README.md`
- Status: No content yet — awaiting design decisions from research synthesis

**`.planning/` — GSD Planning Workspace:**
- Purpose: Phase tracking, codebase maps, and project state for the GSD framework
- Contains: `codebase/` subdirectory with analysis documents (ARCHITECTURE.md, STRUCTURE.md)
- Generated: By GSD commands; committed as project planning artifacts

## Key File Locations

**Entry Points:**
- `research/SUMMARY.md`: Hub for the entire research dossier; start here
- `research/topics/patterns-worth-stealing.md`: Fast-path to design inputs; 19 patterns ranked by transferability
- `README.md`: Project vision and philosophy

**Framework Profiles:**
- `research/frameworks/gsd.md`: GSD deep dive (37 KB)
- `research/frameworks/tlc-spec-driven.md`: TLC Spec-Driven deep dive (27 KB)
- `research/frameworks/graphify.md`: Graphify deep dive (15 KB)
- `research/frameworks/adjacent-frameworks.md`: Spec Kit, OpenSpec, Task Master, BMAD-METHOD (21 KB)

**Topic Analyses:**
- `research/topics/patterns-worth-stealing.md`: Design patterns ranked by transferability (30 KB)
- `research/topics/workflow-and-orchestration.md`: Pipeline, orchestration, and agent-dispatch patterns (34 KB)
- `research/topics/context-engineering.md`: Token budget, context rot, namespace routing (21 KB)
- `research/topics/local-storage-and-artifacts.md`: Artifact layout, local storage patterns (22 KB)
- `research/topics/self-healing-and-verification.md`: Debugging, verification, spec-deviation patterns (24 KB)
- `research/topics/multi-runtime-support.md`: Multi-runtime support patterns (14 KB)
- `research/topics/auxiliary-tooling.md`: Supporting tooling patterns (20 KB)

**Internal Cache:**
- `research/.research-cache/01-gsd-findings.md`: Raw GSD findings (29 KB)
- `research/.research-cache/02-tlc-findings.md`: Raw TLC findings (21 KB)
- `research/.research-cache/03-adjacent-findings.md`: Raw adjacent findings (21 KB)

**Codebase Analysis:**
- `.planning/codebase/ARCHITECTURE.md`: Information architecture of this repository
- `.planning/codebase/STRUCTURE.md`: This file

## Naming Conventions

**Files:**
- Public dossier documents: `kebab-case.md` (e.g., `patterns-worth-stealing.md`, `adjacent-frameworks.md`)
- Internal cache files: `NN-name-findings.md` with sequential numeric prefix (e.g., `01-gsd-findings.md`)
- Hub/summary files: `UPPERCASE.md` (e.g., `SUMMARY.md`, `README.md`)
- GSD codebase analysis: `UPPERCASE.md` in `.planning/codebase/`

**Directories:**
- `research/` top-level: singular noun, lowercase
- `research/frameworks/`: plural noun, lowercase
- `research/topics/`: plural noun, lowercase
- Internal/tooling dirs: dot-prefixed (`.research-cache/`, `.planning/`, `.cursor/`)

## Where to Add New Code

**New framework profile:**
- File: `research/frameworks/<framework-name>.md`
- Cross-link from: `research/SUMMARY.md` frameworks table and navigation section

**New topic analysis:**
- File: `research/topics/<topic-name>.md`
- Cross-link from: `research/SUMMARY.md` topics section

**Cookbook recipes (when ready):**
- Directory: `mise-en-place/<recipe-name>/` or `mise-en-place/<recipe-name>.md`
- Prerequisite: `research/SUMMARY.md` synthesis and top-pattern decisions complete

**New raw research findings:**
- File: `research/.research-cache/NN-<subject>-findings.md` (increment NN from last file)
- Update: `research/.research-cache/README.md` file table

**Codebase analysis updates:**
- Directory: `.planning/codebase/`
- Follow GSD codebase mapper templates

## Special Directories

**`.research-cache/`:**
- Purpose: Raw sub-agent research outputs; source-of-truth for dossier writers
- Generated: Yes (by research sub-agents)
- Committed: Optional — `research/.research-cache/README.md` provides gitignore instructions

**`.planning/`:**
- Purpose: GSD framework planning workspace — phase state, plans, codebase analysis
- Generated: Partially (by GSD commands)
- Committed: Yes (planning artifacts are version-controlled)

**`.cursor/`:**
- Purpose: IDE configuration, GSD agent definitions, skills, and rules
- Generated: Partially (by GSD install and skill commands)
- Committed: Yes (team-shared IDE configuration)

---

*Structure analysis: 2026-05-20*
