# Research & Knowledge Base

This folder is the **source material** for the spec-driven cookbook. Everything the
project has learned — external framework studies, cross-cutting analyses, external
source incorporation, and the archived v1 prototype — lives here. The next version of
the framework will be designed *from* this base.

> The framework implementation itself is intentionally **not** in this folder. The v1
> prototype has been archived under `prototype/` as a learning artifact; a new, simpler
> workflow is yet to be designed.

---

## Start Here

| If you want to… | Read |
|---|---|
| Understand the whole research sweep | [`SUMMARY.md`](SUMMARY.md) — the dossier entry point |
| See the patterns worth reusing | [`topics/patterns-worth-stealing.md`](topics/patterns-worth-stealing.md) — 32 ranked patterns |
| Learn what the v1 prototype taught us | [`prototype/LEARNINGS.md`](prototype/LEARNINGS.md) |
| Query the whole base structurally | the Graphify index in [`../graphify-out/GRAPH_REPORT.md`](../graphify-out/GRAPH_REPORT.md) |

---

## Layout

```
research/
├── SUMMARY.md            # dossier entry point (frameworks, comparison, top patterns)
├── SOURCES.md            # external source URLs incorporated into the dossier
├── frameworks/           # deep dives: GSD, TLC spec-driven, Graphify, adjacent frameworks
├── topics/               # cross-cutting analyses
│   ├── patterns-worth-stealing.md       # 32 transferable patterns, ranked
│   ├── context-engineering.md
│   ├── workflow-and-orchestration.md
│   ├── self-healing-and-verification.md
│   ├── local-storage-and-artifacts.md
│   ├── auxiliary-tooling.md
│   └── multi-runtime-support.md
├── external-sources/     # 2026-05-24 incorporation pipeline
│   ├── summaries/        #   one structured summary per external URL
│   ├── reviews/          #   alignment review per source vs the dossier
│   ├── evaluations/      #   source-fidelity / structure / voice checks
│   └── INCORPORATION-REPORT.md
├── follow-up/            # targeted follow-up audits
│   ├── A-gsd2.md         #   GSD-2 / GSD Pi notes
│   ├── B-mise-en-place-audit.md   # self-audit of the v1 prototype (~40% implemented)
│   ├── C-worker-contract.md       # worker-contract design for the next version
│   └── SUMMARY.md
├── .research-cache/      # raw research sub-agent output (provenance)
└── prototype/            # ARCHIVED v1 ("mise-en-place")
    ├── LEARNINGS.md      #   distilled takeaways from building + auditing v1
    ├── mise-en-place/    #   the prototype implementation (stdlib Python tools + SKILLs)
    └── planning/         #   the v1 build journey (ROADMAP, REQUIREMENTS, phases, codebase maps)
```

---

## Frameworks Studied

GSD, TLC Spec-Driven, Graphify, GitHub Spec Kit, OpenSpec, Task Master, BMAD-METHOD.
See [`SUMMARY.md`](SUMMARY.md) §2–3 for the at-a-glance comparison.

## Querying This Base with Graphify

The entire `research/` tree is indexed into a knowledge graph (`../graphify-out/`) so the
next design phase can query relationships ("what depends on the worker contract?",
"shortest path from context-rot to self-healing") instead of grepping prose. The
committed artifacts are `graph.json`, `GRAPH_REPORT.md`, and `graph.html`; regenerate
with `graphify` (see root `README.md`).
