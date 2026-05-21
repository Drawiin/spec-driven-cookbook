# Walking Skeleton — Spec Driven Cookbook

**Phase:** 1
**Generated:** 2026-05-21

## Capability Proven End-to-End

Developer runs `python3 mise-en-place/tool-env-check/env_check.py` from any project root and receives a structured pass/fail report on all runtime prerequisites (git, python3, bun/node, cursor) in under 5 seconds — no installation, no pip dependencies, no configuration required.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Language | Python 3.9+ stdlib only | No pip dependencies; works out of the box on any macOS/Linux Python 3.x install; D-01 |
| Tool structure | One standalone script per `tool-*` skill | Each script is fully self-contained; drag-and-drop to a new project satisfies TOOL-05; D-03 |
| Invocation surface | `SKILL.md` as agent contract; `Shell(python3 …)` as runtime | Cursor agents read SKILL.md and invoke the script — no install step needed; D-08 |
| Subprocess safety | Explicit `stdout=PIPE, stderr=PIPE`; `--no-pager`; no `shell=True` | Prevents subprocess injection (security) and git pager hangs (Pitfall 2 in RESEARCH.md) |
| Path safety | Resolve `--root` to absolute; assert within cwd before any read/write | Prevents path traversal via CLI args (ASVS Level 1 input validation) |
| Directory layout | `mise-en-place/tool-<name>/SKILL.md` + `<name>.py` | Tool co-located with its contract; self-contained by folder; D-02, D-04 |
| Test runner | pytest (dev-only; not shipped in `mise-en-place/`) | stdlib unittest is sufficient but pytest gives cleaner fixtures; D-01 applies to shipped scripts only |

## Stack Touched in Phase 1

- [x] Project scaffold — `mise-en-place/` directory tree with README
- [x] Invocation contract — SKILL.md in each `tool-*` skill (cursor_skill_adapter boilerplate + process block)
- [x] File I/O — `pathlib.Path` reads/writes against filesystem (context-builder tree, planning-scaffold)
- [x] External process calls — `git` subprocess via `subprocess.run()` (context-builder git summary)
- [x] CLI invocation — developer runs `python3 script.py [args]` from project root (full end-to-end path proven)
- [ ] Routing — N/A (CLI tool, no routing layer)
- [ ] Database — N/A (file-based state; no DB)

## Out of Scope (Deferred to Later Slices)

- TOOL-03 (verification scripts for lint/test gates at execution boundaries) — Phase 5 concern
- Multi-runtime support (Claude Code, Codex variants) — deferred to v2
- Shared utility module across tool scripts — intentionally avoided; breaks TOOL-05 self-containment guarantee
- pip-installable distribution — deferred to v2
- Sophisticated gitignore parsing (negation patterns, double-star globs) — `fnmatch` handles the >95% common case; full spec parsing is future work

## Subsequent Slice Plan

Each later phase adds one workflow layer on top of this tooling foundation without altering its architectural decisions:

- Phase 2: Spec phase — structured deep-questioning flow producing approved SPEC.md
- Phase 3: Brownfield onboarding — codebase mapping step before spec Q&A
- Phase 4: Plan phase — spec-to-plan decomposition with approval gate
- Phase 5: Execute phase — thin orchestrator dispatching workers in parallel waves
- Phase 6: Self-healing layer — per-task verifier + corrective re-run
- Phase 7: Replication engine (project analysis + profile)
- Phase 8: Replication engine (output + coding template)
