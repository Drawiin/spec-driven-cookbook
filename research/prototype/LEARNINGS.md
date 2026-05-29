# Prototype v1 — Learnings ("mise-en-place")

> Status: **Archived as source material.** This prototype is no longer the active
> framework. It is preserved here for the patterns it validated and the mistakes
> worth not repeating.
> Distilled: 2026-05-29, from a five-track audit of the prototype (tooling, skill
> contracts, roadmap-vs-implementation, research-incorporation, and consistency).

---

## 1. What This Prototype Was

`mise-en-place/` was the first attempt at the spec-driven cookbook: a meta-framework
for spec-driven AI-assisted development built on a *thin orchestrator + specialized
worker* model, intended to self-replicate into tailored per-project `.cursor/` folders.

It reached roughly **40% of its stated philosophy**, concentrated in two areas that
actually worked:

- **Spec phase (greenfield)** — structured Q&A → persisted `SPEC.md` → approval gate.
- **Brownfield onboarding** — detect existing code → parallel codebase mapping →
  a spec that separates `## Already Built` from `## To Build`.

The plan, execute, self-healing, and replication layers (roadmap phases 4–8) were
**designed but never built**. The dossier and follow-up audits ran consistently
*ahead of the code*.

What lives here:

- `mise-en-place/` — the prototype implementation (stdlib Python tools + SKILL.md contracts).
- `planning/` — the GSD-style build journey (`PROJECT.md`, `ROADMAP.md`, `REQUIREMENTS.md`,
  `STATE.md`, `codebase/` maps, and per-phase `phases/` artifacts).

---

## 2. What It Got Right (patterns to keep)

These were validated in practice and are worth carrying into the next framework:

1. **Single-script + SKILL.md "house contract" per tool.** Each capability = one
   stdlib-only Python script with a clear exit-code contract (0/1) plus a SKILL.md
   describing invocation. Portable, inspectable, no install step.
2. **Fail-closed deterministic gates.** A secret scanner and a spec validator that
   *block* the workflow rather than advising. The principle was right (even though
   the secret scanner's implementation was accidentally fail-open — see §3).
3. **Brownfield delta model.** `detect → map → delta Q&A → Already Built / To Build`
   with an explicit approval gate. This separation is genuinely useful and should survive.
4. **Parallel mappers, orchestrator gets summaries only.** Four codebase-mapping
   sub-agents run in parallel; the orchestrator receives condensed results — the
   correct shape for context discipline.
5. **Spec-as-contract with a hard approval gate.** `status: approved` required before
   downstream phases. Right idea (though the gate wasn't actually wired to the validator).
6. **Confidence tagging** on inferred facts (`[observed]` / `[inferred]` / `[unverified]`).
   Borrowed from Graphify's EXTRACTED/INFERRED/AMBIGUOUS model — keep it, and push it
   into the data model rather than prose.

---

## 3. What It Got Wrong (mistakes worth not repeating)

### Correctness / safety bugs the tests let through
- **The security gate was fail-OPEN.** `scan_map_secrets` returned an empty hit list
  (exit 0) on read errors — a gate that passes when it can't read is not a gate.
- **Path traversal** in `read_artifact` (only writes were guarded), and **symlink
  traversal** in the context builder (it followed symlinks out of the repo).
- **Unbounded recursion** on negative `--depth`; full-file reads before truncation.
- **Tests guarded structure, not behavior.** Contract tests were substring checks;
  the secret-scanner had 2 tests. Several real bugs shipped green.

> Lesson: a deterministic gate is only as trustworthy as its failure mode. Default to
> fail-closed, and test the failure paths (unreadable, binary, oversized, traversal),
> not just the happy path.

### Design / discipline gaps
- **The central guarantee was unenforced.** The approval step flipped `status: approved`
  *without running the validator*. The framework's whole premise ("the spec is the
  contract") was advisory in practice.
- **Context discipline was preached, not enforced.** The full context-builder output
  was pasted into all four mapper prompts (4× token load) — the exact bloat the
  framework existed to prevent. "Minimal context packet" was stated everywhere and
  defined nowhere (no worker contract existed).
- **No deterministic completeness gate** for the codebase map — "seven files, each
  >20 lines" was prose an agent could fudge.

### Process / drift gaps
- **The framework couldn't keep its own house consistent.** After removing the GSD
  scaffolding, dead `/gsd-*` commands remained as the primary "resume" pointer, the
  codebase maps still described GSD as the installed stack, and progress trackers
  contradicted themselves (Phase 1 "1/3" vs "Complete"; STATE said both 7 and 3 plans).

> Lesson: if the framework that builds software can't keep its own planning artifacts
> coherent, it won't keep a user's project coherent either. Self-consistency is a feature.

### Scope / structure gaps
- **The dossier ran ~2 phases ahead of the code.** Research and follow-up audits kept
  proposing designs (worker contracts, context-health zones, diagnose-into-PLAN repair)
  that were never implemented. Lots of planning, comparatively little shipped surface.
- **~8 tools + multi-phase GSD scaffolding** for a still-incomplete pipeline. The
  follow-up audit explicitly flagged this as GSD-style bloat — which is the main
  motivation for the "keep the next workflow simpler" reset.

---

## 4. Headline Takeaways for the Next Framework

1. **Ship less, enforce more.** A small number of capabilities that are actually
   wired to their gates beats a large surface of advisory steps.
2. **Gates fail closed and are tested on their failure modes.**
3. **Define the worker/context contract first** (what a sub-agent receives, what it
   must NOT receive, and its fixed output shape) — it's the backbone of context discipline.
4. **Self-consistency is part of the product.** Resume pointers, status trackers, and
   codebase maps must stay true after every change; stale references are bugs.
5. **Keep the research base queryable, not just readable.** Hence the Graphify index
   over `research/` (see `research/README.md`).

---

## 5. Where the Evidence Lives

- **Validated patterns + still-open ideas:** `research/topics/patterns-worth-stealing.md`
  (32 ranked patterns), `research/follow-up/B-mise-en-place-audit.md` (self-audit,
  ~40%-implemented verdict), `research/follow-up/C-worker-contract.md` (worker-contract design).
- **The build journey:** `research/prototype/planning/` (ROADMAP, REQUIREMENTS, per-phase artifacts).
- **The implementation being critiqued:** `research/prototype/mise-en-place/`.
