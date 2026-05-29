# Graph Report - research  (2026-05-29)

## Corpus Check
- 115 files · ~186,719 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 612 nodes · 1201 edges · 32 communities (29 shown, 3 thin omitted)
- Extraction: 93% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 77 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Phase 1 Tooling Plans|Phase 1 Tooling Plans]]
- [[_COMMUNITY_Frameworks & Patterns Index|Frameworks & Patterns Index]]
- [[_COMMUNITY_Phase 2 Spec Workflow|Phase 2 Spec Workflow]]
- [[_COMMUNITY_Spec Validation Tests|Spec Validation Tests]]
- [[_COMMUNITY_Planning Scaffold Tool|Planning Scaffold Tool]]
- [[_COMMUNITY_Brownfield Detection Tests|Brownfield Detection Tests]]
- [[_COMMUNITY_Context Builder Tool|Context Builder Tool]]
- [[_COMMUNITY_Codebase Map & Concerns|Codebase Map & Concerns]]
- [[_COMMUNITY_Brownfield Mapping Gates|Brownfield Mapping Gates]]
- [[_COMMUNITY_Developer Skills & Reuse|Developer Skills & Reuse]]
- [[_COMMUNITY_Core Stealable Patterns|Core Stealable Patterns]]
- [[_COMMUNITY_Env Check & Map Tooling|Env Check & Map Tooling]]
- [[_COMMUNITY_OpenRewrite LST & Recipes|OpenRewrite LST & Recipes]]
- [[_COMMUNITY_Thin Orchestrator & Verifier|Thin Orchestrator & Verifier]]
- [[_COMMUNITY_Planning Config Fields|Planning Config Fields]]
- [[_COMMUNITY_Env Check Tool & Tests|Env Check Tool & Tests]]
- [[_COMMUNITY_Harness Engineering|Harness Engineering]]
- [[_COMMUNITY_Decision Gates & Self-Healing|Decision Gates & Self-Healing]]
- [[_COMMUNITY_BMAD & TLC Auto-Sizing|BMAD & TLC Auto-Sizing]]
- [[_COMMUNITY_ArchUnit Architecture Rules|ArchUnit Architecture Rules]]
- [[_COMMUNITY_Spec-Phase Contract Tests|Spec-Phase Contract Tests]]
- [[_COMMUNITY_Spec Kit & Test-as-Spec|Spec Kit & Test-as-Spec]]
- [[_COMMUNITY_Prototype Learnings & Contracts|Prototype Learnings & Contracts]]
- [[_COMMUNITY_Graphify Knowledge Graph|Graphify Knowledge Graph]]
- [[_COMMUNITY_Brownfield Detection Tool|Brownfield Detection Tool]]
- [[_COMMUNITY_Spec Validator Tool|Spec Validator Tool]]
- [[_COMMUNITY_Phase 2 Decisions|Phase 2 Decisions]]
- [[_COMMUNITY_Map-Codebase Contract Tests|Map-Codebase Contract Tests]]
- [[_COMMUNITY_Approved Scenarios & Sources|Approved Scenarios & Sources]]
- [[_COMMUNITY_Install Profiles & Surface|Install Profiles & Surface]]
- [[_COMMUNITY_OpenSpec Current-vs-Proposed|OpenSpec Current-vs-Proposed]]
- [[_COMMUNITY_PR & Ship Config|PR & Ship Config]]

## God Nodes (most connected - your core abstractions)
1. `Patterns Worth Stealing` - 42 edges
2. `Patterns Worth Stealing (32 Patterns)` - 30 edges
3. `mise-en-place` - 26 edges
4. `Self-Healing and Verification` - 22 edges
5. `GSD (Get Shit Done)` - 21 edges
6. `GSD (Get Shit Done)` - 19 edges
7. `TLC Spec-Driven` - 18 edges
8. `ArchUnit` - 17 edges
9. `tool-validate-spec (validate_spec.py)` - 16 edges
10. `mise-en-place Worker Contract` - 16 edges

## Surprising Connections (you probably didn't know these)
- `tool-context-builder` --part_of--> `mise-en-place (v1 Prototype)`  [INFERRED]
  research/prototype/mise-en-place/tool-context-builder/context_builder.py → research/README.md
- `Planning Config (config.json)` --part_of--> `mise-en-place (v1 Prototype)`  [INFERRED]
  research/prototype/planning/config.json → research/README.md
- `Planning Config (config.json)` --conceptually_related_to--> `Graphify`  [INFERRED]
  research/prototype/planning/config.json → research/SUMMARY.md
- `Planning Config (config.json)` --conceptually_related_to--> `GSD (get-shit-done)`  [INFERRED]
  research/prototype/planning/config.json → research/SUMMARY.md
- `tool-planning-scaffold` --part_of--> `mise-en-place (v1 Prototype)`  [INFERRED]
  research/prototype/mise-en-place/tool-planning-scaffold/planning_scaffold.py → research/README.md

## Communities (32 total, 3 thin omitted)

### Community 0 - "Phase 1 Tooling Plans"
Cohesion: 0.07
Nodes (71): Phase 1 Plan 01 (tool-env-check walking skeleton), env_check.py (tool-env-check), mise-en-place README.md (tool catalog), Phase 1 Plan 02 (tool-context-builder), context_builder.py (tool-context-builder), Phase 1 Plan 03 (tool-planning-scaffold), planning_scaffold.py (tool-planning-scaffold), Phase 1 Discussion Log (+63 more)

### Community 1 - "Frameworks & Patterns Index"
Cohesion: 0.09
Nodes (71): ArchUnit, Auto-Sizing Matrix, BMAD-METHOD, Claude Code Dynamic Workflows, Context7 MCP, Context Rot, Follow-Up Research Summary, Graphify (+63 more)

### Community 2 - "Phase 2 Spec Workflow"
Cohesion: 0.08
Nodes (63): tool-env-check, GSD Framework, Phase 2 Plan 02 Summary, tool-planning-scaffold (planning_scaffold.py), cursor_skill_adapter Block, Phase 2 Pattern Map, parse_frontmatter(), pytest Contract Tests (+55 more)

### Community 3 - "Spec Validation Tests"
Cohesion: 0.09
Nodes (30): _brownfield_spec_body(), Tests for validate_spec.py, Approved SPEC.md missing ## Constraints exits 1., Build SPEC.md body with optional brownfield sections., Brownfield approved spec missing ## Already Built → exit 1., Brownfield approved spec missing ## To Build → exit 1., Brownfield with all sections and distinct bullets → exit 0., Brownfield sections without project_type → exit 1. (+22 more)

### Community 4 - "Planning Scaffold Tool"
Cohesion: 0.11
Nodes (28): Path, str, format_file(), main(), Idempotent: mkdir exist_ok=True + conditional file writes., Normalize: strip trailing whitespace per line + ensure single trailing newline., Resolve root and reject paths outside the working directory., read_artifact() (+20 more)

### Community 5 - "Brownfield Detection Tests"
Cohesion: 0.13
Nodes (26): CompletedProcess, Path, str, _parse_json(), Tests for detect_brownfield.py, Symlink to outside dir must not count toward has_existing_code., Code at depth 4 must not be detected., Code under node_modules must not count. (+18 more)

### Community 6 - "Context Builder Tool"
Cohesion: 0.13
Nodes (24): int, bool, Path, str, build_tree(), find_entry_points(), git_summary(), is_excluded() (+16 more)

### Community 7 - "Codebase Map & Concerns"
Cohesion: 0.18
Nodes (19): Architecture (Codebase Map), mise-en-place Cookbook Layer, patterns-worth-stealing.md, Internal Research Cache, Research Dossier, research/SUMMARY.md Hub, Codebase Concerns, Empty mise-en-place Placeholder (+11 more)

### Community 8 - "Brownfield Mapping Gates"
Cohesion: 0.19
Nodes (19): Seven-File Completeness Gate, Parallel Mapper Sub-Agents, Fail-Closed Secret Gate (scan_map_secrets), map-codebase, mise-en-place, Spec Driven Cookbook (Project), Prototype Requirements (v1/v2), Prototype Roadmap (8 phases) (+11 more)

### Community 9 - "Developer Skills & Reuse"
Cohesion: 0.16
Nodes (18): Three Impact Radiuses (commit/iteration/maintainability), Role of Developer Skills (Böckeler Memo #13), Reuse-Awareness Pre-Check (mechanism), Steering as the Unit of Work, Evaluator A: Source Fidelity, Evaluator B: Structural Integrity, Incorporation Report (2026-05-24), Graphify Knowledge-Graph Index (graphify-out/) (+10 more)

### Community 10 - "Core Stealable Patterns"
Cohesion: 0.19
Nodes (18): GSD (get-shit-done), OpenRewrite, Pattern 2: Auto-Sized Pipeline with Hard Escape Valves, Pattern 1: Compound Init Handlers, Pattern 8: Asymmetric Decision Coverage Gates, Pattern 4: Diagnose-into-PLAN Self-Healing, Pattern 6: ID-Based Ageable Persistent Memory, Pattern 23: Isomorphic vs Non-Isomorphic Edits (+10 more)

### Community 11 - "Env Check & Map Tooling"
Cohesion: 0.19
Nodes (17): tool-context-builder, Codebase Map Marker (.planning/codebase/STACK.md), tool-detect-brownfield, Cursor Detection via CURSOR_TRACE_ID, Runtime Prerequisite Checks (git/python3/bun/cursor), tool-env-check, Seven Canonical Codebase Map Files, map-codebase SKILL (+9 more)

### Community 12 - "OpenRewrite LST & Recipes"
Cohesion: 0.14
Nodes (17): Compound Init Handlers, OpenRewrite, ExecutionContext, Lossless Semantic Tree (LST), Markers, Preconditions, Recipe (OpenRewrite), Declarative recipeList Composition (+9 more)

### Community 13 - "Thin Orchestrator & Verifier"
Cohesion: 0.14
Nodes (16): Task Master, Fresh Subagent Context, Two-Stage Namespace Routing, node_repair, Nyquist Auditor, Plan-Checker Loop, GSD .planning/ State, slopcheck / Package Legitimacy (+8 more)

### Community 14 - "Planning Config Fields"
Cohesion: 0.12
Nodes (15): commit_docs, granularity, graphify, enabled, mode, model_profile, parallelization, ship (+7 more)

### Community 15 - "Env Check Tool & Tests"
Cohesion: 0.14
Nodes (13): str, main(), Returns (status_char, detail_str) where status_char is '✓' or '✗'., run_check(), Tests for env_check.py, main() exits 0 when all subprocess checks return successfully., main() exits 1 when git is not found in PATH., env_check.py completes in under 5 seconds (SC-1 timing requirement). (+5 more)

### Community 16 - "Harness Engineering"
Cohesion: 0.21
Nodes (14): Ashby's Law of Requisite Variety, Behaviour Harness, Computational vs Inferential Controls, Harness Engineering, Guides and Sensors (Feedforward/Feedback), Harness Engineering (Fowler / Böckeler), Harnessability, Outer Harness (+6 more)

### Community 17 - "Decision Gates & Self-Healing"
Cohesion: 0.14
Nodes (14): FreezingArchRule / ViolationStore, gsd-debugger (Diagnose-into-PLAN), Decision Coverage Gate, Steering Loop, Pattern 10: Asymmetric Decision Coverage Gates, Pattern 8: Diagnose-into-PLAN, Pattern 20: Frozen Baseline with Ratchet Semantics, DX Guardrails (+6 more)

### Community 18 - "BMAD & TLC Auto-Sizing"
Cohesion: 0.18
Nodes (13): BMAD-METHOD, Scale-Adaptive Intelligence, Specialized Agent Personas, Pattern 5: Auto-Sized Pipeline with Hard Escape Valves, Research Cache (internal findings), Auto-Sizing, Context7 MCP, TLC Four Adaptive Phases (+5 more)

### Community 19 - "ArchUnit Architecture Rules"
Cohesion: 0.24
Nodes (11): Layered/Onion Architecture Primitives, ArchUnit, FreezingArchRule / ViolationStore, Named Architectural Primitives, PlantUML-as-Rules, ArchUnit Dossier Review, Fitness Functions, Pattern 26: Diagram-as-Executable-Spec (+3 more)

### Community 21 - "Spec Kit & Test-as-Spec"
Cohesion: 0.20
Nodes (10): GitHub Spec Kit, ArchRule, PlantUML Diagram-as-Rule, Approved Scenarios, Pattern 16: Constitution as Governance, Pattern 21: Diagram-as-Executable-Spec, Pattern 11: Test-as-Spec & SPEC_DEVIATION, /speckit.analyze (+2 more)

### Community 22 - "Prototype Learnings & Contracts"
Cohesion: 0.22
Nodes (10): Brownfield Delta Model, Fail-Closed Deterministic Gates, Prototype Learnings, Self-Consistency as a Feature, Worker/Context Contract, GSD Installed Stack (v1.42.3), Prototype Tech Stack, SPEC.md (spec-as-contract) (+2 more)

### Community 23 - "Graphify Knowledge Graph"
Cohesion: 0.31
Nodes (9): Graphify, EXTRACTED/INFERRED/AMBIGUOUS Tags, Git Merge Driver, Knowledge Graph (graph.json), Graphify MCP Server, Graphify Pipeline (detect to export), GSD Graphify Integration, Pattern 13: Confidence Tagging on Inferred Data (+1 more)

### Community 24 - "Brownfield Detection Tool"
Cohesion: 0.39
Nodes (8): bool, Path, str, _find_code_files(), _has_package_file(), main(), Walk root up to MAX_DEPTH; return set of extensions found., _validate_root()

### Community 25 - "Spec Validator Tool"
Cohesion: 0.42
Nodes (8): str, _duplicate_brownfield_bullets(), main(), _normalize_bullet(), parse_frontmatter(), Parse YAML-like front-matter between --- markers., Extract bullet lines from a section until the next ## header., _section_bullets()

### Community 26 - "Phase 2 Decisions"
Cohesion: 0.54
Nodes (8): Spec Approval Gate Decisions (D-08/D-09), Phase 2 Context, Phase 1: Tooling Foundation, Phase 2: Spec Phase (Greenfield), Q&A Structure Decisions (D-01/D-02), Research Sub-tasks Decisions (D-03–D-05), SPEC.md Format Decisions (D-06/D-07), Phase 2 Discussion Log

### Community 28 - "Approved Scenarios & Sources"
Cohesion: 0.50
Nodes (5): Evaluator C: Voice and Consistency, Approved Fixtures Pattern, Lex Lerumph Augmented Coding Patterns, External Source URL List, Pattern 31: Approved Scenarios for AI-Generated Behaviour Tests

### Community 29 - "Install Profiles & Surface"
Cohesion: 0.50
Nodes (4): Importable Rule Libraries (ArchTests), Skill Surface Budget Module, Recipe Descriptors, Pattern 15: Install-Time Profile + Surface Toggle

### Community 30 - "OpenSpec Current-vs-Proposed"
Cohesion: 1.00
Nodes (3): OpenSpec, Archive/Merge Deltas, Current-vs-Proposed Separation

## Ambiguous Edges - Review These
- `Three Regulation Categories` → `Fitness Functions`  [AMBIGUOUS]
  research/external-sources/reviews/03-harness-engineering-review.md · relation: part_of
- `mise-en-place Cookbook Layer` → `Graphify Framework`  [AMBIGUOUS]
  research/prototype/planning/codebase/INTEGRATIONS.md · relation: conceptually_related_to
- `Phase 3 Research` → `OpenSpec (current vs proposed model)`  [AMBIGUOUS]
  research/prototype/planning/phases/03-brownfield-codebase-onboarding/03-RESEARCH.md · relation: cites
- `BROWNFIELD_SECTIONS (Already Built / To Build)` → `OpenSpec (current vs proposed model)`  [AMBIGUOUS]
  research/prototype/planning/phases/03-brownfield-codebase-onboarding/03-RESEARCH.md · relation: conceptually_related_to
- `GSD Pi` → `Package Legitimacy Gate (Slopsquatting Defense)`  [AMBIGUOUS]
  research/follow-up/A-gsd2.md · relation: references

## Knowledge Gaps
- **73 isolated node(s):** `Path`, `CompletedProcess`, `str`, `bool`, `str` (+68 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Three Regulation Categories` and `Fitness Functions`?**
  _Edge tagged AMBIGUOUS (relation: part_of) - confidence is low._
- **What is the exact relationship between `mise-en-place Cookbook Layer` and `Graphify Framework`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Phase 3 Research` and `OpenSpec (current vs proposed model)`?**
  _Edge tagged AMBIGUOUS (relation: cites) - confidence is low._
- **What is the exact relationship between `BROWNFIELD_SECTIONS (Already Built / To Build)` and `OpenSpec (current vs proposed model)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `GSD Pi` and `Package Legitimacy Gate (Slopsquatting Defense)`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `Harness Engineering` connect `Harness Engineering` to `Decision Gates & Self-Healing`, `Spec Kit & Test-as-Spec`, `Frameworks & Patterns Index`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `GSD (Get Shit Done)` connect `Thin Orchestrator & Verifier` to `Brownfield Mapping Gates`, `OpenRewrite LST & Recipes`, `Decision Gates & Self-Healing`, `BMAD & TLC Auto-Sizing`, `Prototype Learnings & Contracts`, `Graphify Knowledge Graph`, `Install Profiles & Surface`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._