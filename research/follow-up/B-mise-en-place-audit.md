# mise-en-place Audit — Coverage Against 32-Pattern Dossier

> Audited: 2026-05-27  
> Inputs: mise-en-place/README.md, mise-en-place/*/SKILL.md, root README.md, research/topics/patterns-worth-stealing.md

## 1. Current mise-en-place surface

**Validators:** `tool-validate-spec` (SPEC.md approved + section headers + brownfield dedup), `tool-env-check` (runtime prerequisites).

**Detectors:** `tool-detect-brownfield` (JSON brownfield/greenfield + map-need signal).

**Scanners:** `tool-scan-map-secrets` (fail-closed secret patterns in `.planning/codebase/*.md`; no SKILL.md — README + script only).

**Scaffolders / artifact I/O:** `tool-planning-scaffold` (idempotent `.planning/` tree, read/write-artifact, format-file).

**Context assemblers:** `tool-context-builder` (four-section markdown packet to stdout).

**Workflow skills (SKILL.md only, no Python):** `spec-phase` (Q&A → SPEC.md → approval gate), `map-codebase` (four parallel mapper sub-agents → seven map files → secret + completeness gates).

**Contract tests:** pytest on all Python tools + `spec-phase`/`map-codebase` SKILL structure.

**House contract:** Each tool has `SKILL.md` (agent reads) + stdlib Python script; exit 0 = success, exit 1 = failure with stderr/stdout detail. Workflow skills orchestrate via Shell + Task sub-agents.

## 2. Stated design principles vs implementation

| Principle | Assessment | Evidence |
|---|---|---|
| Orchestrators + specialized workers | **PARTIALLY-IMPLEMENTED** | `map-codebase` spawns four parallel `Task` mappers; `spec-phase` spawns research sub-agents. No plan/execute orchestrator yet. |
| Self-healing | **PARTIALLY-IMPLEMENTED** | Fail-closed gates: `validate_spec.py`, `scan_map_secrets.py`, map completeness (>20 lines × 7 files). No diagnose-into-PLAN repair loop. |
| Humans are lazy | **PARTIALLY-IMPLEMENTED** | `spec-phase` structured Q&A (3-turn probes), mandatory brownfield confirm gate, explicit approve/edit/abort. |
| Context rot | **STATED-BUT-NOT-IMPLEMENTED** | Root README defines 0–40/40–60/60–80/80–100% zones; no mise-en-place tool enforces per-file budgets or compaction. |
| SPEC-driven (RESEARCH→SPEC→PLAN→TASK) | **PARTIALLY-IMPLEMENTED** | RESEARCH + SPEC covered (`spec-phase`, `.planning/research/`). PLAN/TASK referenced (`/plan-phase`) but not built in mise-en-place. |
| Worker as black-box | **PARTIALLY-IMPLEMENTED** | Python tools: exit code + pointer to stderr/stdout. `map-codebase`: "orchestrator receives confirmations only, not full document bodies." No formal SUCCESS/FAILURE + artifact-path contract across all workers. |

## 3. Coverage matrix

| Pattern # | Pattern name | Status | Evidence (for IMPL/PARTIAL) or rationale (for SHOULD/DEFER/REJECT) |
|---|---|---|---|
| 1 | Compound Init Handlers | **PARTIAL** | Each phase re-runs `planning_scaffold`, `detect_brownfield`, `context_builder` separately in SKILL steps. No single JSON init blob or tempfile spill. |
| 2 | Two-Stage Namespace Routing Meta-Skills | **REJECT** | ~8 tools total; no 86-skill eager-listing cost. Premature GSD infrastructure. |
| 3 | Per-File Token Budgets with Health Zones | **SHOULD-ADOPT** | Root README states context-rot zones; no enforcement on `.planning/SPEC.md`, map files, or `STATE.md`. |
| 4 | ID-Based, Ageable Persistent Memory | **PARTIAL** | `planning_scaffold.py` creates stub `STATE.md`; no `AD-/B-/L-` IDs, archive, or deferred-ideas section. |
| 5 | Auto-Sized Pipeline with Hard Escape Valves | **DEFER** | Only `spec-phase` exists; no quick/full tiering or execute inline-step threshold. Needed when plan-phase lands. |
| 6 | Sub-Agent Context Contract | **PARTIAL** | Research sub-agents have output file format; map-codebase limits orchestrator to confirmations. Missing fixed must-receive/must-NOT-receive lists and standard output schema (Status/Files/Gate). |
| 7 | Wave-Based Parallelism with State Lockfile | **REJECT** | `map-codebase` parallel mappers only; no waves, `STATE.md.lock`, or hook-once-per-wave. GSD execute complexity before plan/execute exist. |
| 8 | Diagnose-into-PLAN Self-Healing | **SHOULD-ADOPT** | Core philosophy ("Self-healing") but no verify/debugger/plan repair path in mise-en-place. |
| 9 | Three-Role Model Config | **REJECT** | Model routing is Cursor/runtime concern; adding config layer duplicates host IDE without improving spec-phase results. |
| 10 | Asymmetric Decision Coverage Gates | **DEFER** | `spec-phase` cites D-01…D-09 as workflow rules, not numbered user decisions with plan-time blocking / verify-time warning gates. Relevant at plan-phase. |
| 11 | Test-as-Spec and SPEC_DEVIATION Markers | **DEFER** | No execute/implement workflow. Contract tests cover SKILL structure, not RED/GREEN immutability. |
| 12 | Parallel-Safety as a Property of Tests | **DEFER** | `TESTING.md` is a map output template; no `[P]` parallel-safe task marking or parallelism assessment enforcement. |
| 13 | Confidence Tagging on Inferred Data | **PARTIAL** | `spec-phase` Step 2 brownfield: tag Already Built as `[observed]`, `[inferred]`, `[unverified]`. Not embedded in map file data model or graph relations. |
| 14 | Package Legitimacy Gate (Slopsquatting) | **DEFER** | No dependency-install workflow or slopcheck integration. Relevant when execute-phase adds packages. |
| 15 | Install-Time Profile + Runtime Surface Toggle | **REJECT** | Eight stdlib tools don't need profiles/clusters/`requires:` closure — classic GSD surface-budget machinery. |
| 16 | Constitution as Governance Artifact | **DEFER** | `CONVENTIONS.md` from map is closest analog; no separate governance artifact or consult-every-phase rule. |
| 17 | Current-vs-Proposed Spec Separation | **PARTIAL** | Brownfield `## Already Built` / `## To Build` separates inventory from delta; no `changes/<name>/` delta folder or archive-merge. |
| 18 | Conditional Skill Delegation with One-Shot Nudges | **DEFER** | No optional external skill probes or once-per-session install nudges. |
| 19 | Git Merge Driver for Shared Artifacts | **DEFER** | No concurrent multi-agent writes to shared artifacts yet; premature until execute parallelism exists. |
| 20 | Lossless Semantic Tree (LST) Substrate | **REJECT** | Per-language IR investment contradicts stdlib-only, minimal-toolkit goals; text-level editing assumed throughout. |
| 21 | Authored Composition of Typed Transformations (Recipe DAG) | **REJECT** | YAML skill DAG + planner tool-selection is GSD/OpenRewrite complexity; mise-en-place is intentionally flat SKILL + script. |
| 22 | Precondition Scope Filter | **SHOULD-ADOPT** | No deterministic glob/AST precondition on AI editing skills; whole-repo reads in mapper prompts are unscoped. |
| 23 | Isomorphic vs Non-Isomorphic Edits (Tiered Review) | **DEFER** | No edit classification or tiered review gates; needs execute/review workflow first. |
| 24 | Self-Describing Skill Manifest with Estimated Effort | **PARTIAL** | SKILL frontmatter has `name` + `description` only; no parameters, tags, or `estimatedEffortPerOccurrence` for planner selection. |
| 25 | Frozen Baseline with Ratchet Semantics | **DEFER** | No arch/constraint verifiers or violation store; relevant for legacy brownfield rule adoption later. |
| 26 | Diagram-as-Executable-Spec | **DEFER** | No diagram→rule pipeline; `ARCHITECTURE.md` is prose-only map output. |
| 27 | Importable Spec Packs | **DEFER** | No external constraint pack mechanism; org standards would be copy-paste into map today. |
| 28 | Named Architectural Primitives Vocabulary | **DEFER** | Map templates use free-form `## Layers` / `## Key Patterns`; no layered/onion/slices DSL. |
| 29 | Guides + Sensors Taxonomy | **PARTIAL** | Implicit: SKILL.md = guide, `tool-*` validators = sensors. Not declared per control; unverifiable specs not flagged. |
| 30 | Computational vs Inferential Control Labelling | **PARTIAL** | Python tools are computational; workflow skills inferential — axis exists but unlabeled in manifests. |
| 31 | Approved Scenarios for AI-Generated Behaviour Tests | **PARTIAL** | `test_spec_phase_contract.py` / `test_map_codebase_contract.py` assert SKILL invariants by structure (diff-reviewable fixtures), not full approved-scenarios runner. |
| 32 | Reuse-Awareness Pre-Check | **SHOULD-ADOPT** | Brownfield map exists but no pre-generation symbol/API reuse query before building new components. Natural fit before execute-phase. |

## 4. Top 5 SHOULD-ADOPT recommendations (highest leverage first)

**1. Pattern 8 — Diagnose-into-PLAN Self-Healing |** Design `plan-phase`/`verify-phase` so failures spawn a repair PLAN in the same phase directory, re-invoked via the same execute command — no "fix mode." **Home:** `mise-en-place/verify-phase/SKILL.md` + `tool-write-repair-plan/` (stdlib script writing `.planning/phases/NN/repair-PLAN.md`). **Composes:** `tool-validate-spec` gate before plan; repair plans consumed by future execute orchestrator. **Cost:** M (design now, implement with plan/execute).

**2. Pattern 6 — Sub-Agent Context Contract |** Publish a shared `mise-en-place/contracts/sub-agent.md` referenced by `map-codebase`, `spec-phase` research, and future executors: fixed must-receive / must-NOT-receive lists + output schema (Status, Files, Gate, Deviations, Issues). **Home:** contract doc + pytest contract test per workflow skill. **Composes:** tightens existing parallel mappers and research spawns; enables safe parallelism later. **Cost:** S.

**3. Pattern 1 — Compound Init Handlers |** Build `tool-phase-init/phase_init.py` returning JSON: scaffold status, brownfield detection, env check, spec status, map completeness, context snapshot path — one Shell call at workflow entry. **Home:** `mise-en-place/tool-phase-init/`. **Composes:** replaces repeated Step-1 shell sequences in `spec-phase` and future `plan-phase`. **Cost:** S.

**4. Pattern 22 — Precondition Scope Filter |** Add required `precondition` field to every workflow SKILL frontmatter (glob list or ripgrep query); `tool-check-precondition/` exits 1 if no files match before spawning heavy sub-agents. **Home:** `mise-en-place/tool-check-precondition/`. **Composes:** runs after `tool-phase-init`, before `map-codebase` mappers or future executors. **Cost:** S.

**5. Pattern 3 — Per-File Token Budgets with Health Zones |** Build `tool-context-health/context_health.py` estimating token counts for `.planning/*` artifacts; warn at 40–60%, block expansion at 80% per root README zones. **Home:** `mise-en-place/tool-context-health/`. **Composes:** invoked at end of `spec-phase`, start of `plan-phase`, and after map writes. **Cost:** M.

## 5. Explicit REJECT list with rationale

| Pattern | Why GSD-bloat | mise-en-place instead |
|---|---|---|
| 2 — Two-Stage Namespace Routing | Solves 86-skill token tax; eight tools don't need routers | Flat README inventory + direct skill mention |
| 7 — Wave Parallelism + State Lockfile | Execute-orchestration infra (lockfiles, hook batching) before plan/execute exist | Sequential phases; `map-codebase` parallelism only |
| 9 — Three-Role Model Config | Duplicates Cursor model selection; extra config surface | Host IDE handles models |
| 15 — Install Profiles + Surface Toggle | Profile/cluster machinery for a stdlib toolkit copied into repos | All tools always available; pytest optional dev-only |
| 20 — LST Substrate | Per-language IR = massive scope vs stdlib-only house style | Text edits + deterministic validators |
| 21 — Recipe DAG | YAML composition layer + planner tool-selection over DAG | Linear workflow skills + explicit Shell steps |

## 6. Gaps in the dossier (patterns mise-en-place needs but dossier doesn't have)

| Name | Description | Dossier fit |
|---|---|---|
| Single-script-per-tool + SKILL.md contract | Stdlib Python, exit 0/1, agent reads SKILL for invocation — the house style | Group D extensibility or new "Tool contract" pattern |
| Fail-closed secret scan between mapper writes and downstream reads | `scan_map_secrets.py` exit 1 blocks spec Q&A; manual grep insufficient | Group C verification |
| Approved-status gate as hard precondition | `validate_spec.py` requires `status: approved` before plan | Group C gates (asymmetric with Pattern 10) |
| Brownfield map completeness gate | Seven canonical files, each >20 lines, before Q&A | Group B orchestration / brownfield onboarding |
| Orchestrator summaries-only sub-agent returns | Map orchestrator never ingests full doc bodies | Pattern 6 extension |

## 7. Overall assessment

mise-en-place is a focused **pre-planning layer**: brownfield detection, parallel codebase mapping, structured spec Q&A, and hard gates (approval, secrets, completeness) are solid and already ahead of the dossier on fail-closed map security and brownfield SPEC shape. It has **not** started plan, execute, verify, or context-rot enforcement — so roughly **40% of stated philosophy is implemented**, concentrated in the SPEC slice. Most urgent builds: **compound phase init (1)**, **formal sub-agent contracts (6)**, and **design diagnose-into-PLAN (8)** before adding plan-phase. Already ahead on: stdlib-only tool contract, secret gate on map artifacts, brownfield Already Built/To Build + confidence tags, and contract-tested workflow SKILLs.

## 8. Audit confidence

**MEDIUM** — Read in full: root README, mise-en-place README, patterns-worth-stealing.md, all eight SKILL.md files (seven present; `tool-scan-map-secrets` has no SKILL.md), `spec-phase`/`map-codebase` SKILL bodies end-to-end. Skimmed: all seven Python scripts (headers + key logic), contract test files (headers + assertions). Did not read topic deep-dives except where patterns required disambiguation. No `plan-phase` exists in repo (referenced but unbuilt).

---

> **Note from parent agent (2026-05-27):** The audit subagent ran in read-only (`explore`) mode by my mistake and produced this content but could not write the file itself. The content above is reproduced verbatim from the subagent's transcript; no edits were made.
