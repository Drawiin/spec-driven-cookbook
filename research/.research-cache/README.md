# Research Cache

Raw research-findings reports produced by the planning-phase sub-agents on 2026-05-19.

These files are the canonical source-of-truth for all writing and validation sub-agents.
They are NOT part of the public dossier — they are internal working documents.

## Files

| File | Content | Agent ID |
|---|---|---|
| `01-gsd-findings.md` | GSD / gsd-build/get-shit-done deep dive | ccfe45b2-f665-4a68-84af-cfcdab6d008b |
| `02-tlc-findings.md` | TLC `tlc-spec-driven` skill v2.0.0 deep dive | 59e11448-8800-4db7-9f3c-6117bbff20b1 |
| `03-adjacent-findings.md` | Graphify, Spec Kit, OpenSpec, Task Master, BMAD-METHOD | ff83e72c-049d-4a6f-8820-ed0a9f107a05 |

## Gitignore policy

This entire `.research-cache/` directory should be gitignored if the team decides the raw
findings are internal-only. The public dossier (the `frameworks/` and `topics/` MD files
plus `SUMMARY.md`) is what gets committed.

Add to `.gitignore`:
```
research/.research-cache/
```
