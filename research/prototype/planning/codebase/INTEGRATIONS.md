# External Integrations

**Analysis Date:** 2026-05-20

## APIs & External Services

**AI Coding Frameworks (Researched, Not Integrated):**
The following are subjects of documentation research, not active integrations in this codebase:
- GSD (TÂCHES / gsd-build) — studied in `research/frameworks/gsd.md`
- TLC Spec-Driven (Felipe Rodrigues / tech-leads-club) — studied in `research/frameworks/tlc-spec-driven.md`
- Graphify (Safi Shamsi) — studied in `research/frameworks/graphify.md`
- GitHub Spec Kit, OpenSpec, Task Master, BMAD-METHOD — studied in `research/frameworks/adjacent-frameworks.md`

**Active External Services:**
- None — this repository has no application code that calls external APIs

## Data Storage

**Databases:**
- None

**File Storage:**
- Local filesystem only — all artifacts are markdown files committed to Git
  - Research artifacts: `research/`
  - Planning artifacts: `.planning/`
  - Framework-internal state: `.cursor/`

**Caching:**
- Research cache: `research/.research-cache/` — local markdown files from research sweeps
  - `01-gsd-findings.md`, `02-tlc-findings.md`, `03-adjacent-findings.md`
  - Not an external cache service; plain file storage

## Authentication & Identity

**Auth Provider:**
- None — no authentication system implemented or required

## Monitoring & Observability

**Error Tracking:**
- None

**Logs:**
- GSD framework emits local state logs to `.planning/` artifacts (e.g., `STATE.md`, `PLAN.md`) during workflow execution — no external log service

## CI/CD & Deployment

**Hosting:**
- Not applicable — no deployed application

**CI Pipeline:**
- None — no CI configuration files detected (no `.github/`, no `.gitlab-ci.yml`, no `Makefile` with deploy targets)

## Environment Configuration

**Required env vars:**
- None

**Secrets location:**
- No secrets present in this repository

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## GSD Framework Internal Dependencies

The GSD framework installed at `.cursor/get-shit-done/` ships its own pre-built CommonJS runtime. Key internal components:

| Component | Path | Purpose |
|-----------|------|---------|
| GSD CLI | `.cursor/get-shit-done/bin/gsd-tools.cjs` | Main orchestration binary |
| State engine | `.cursor/get-shit-done/bin/lib/state.cjs` | Phase/workstream state management |
| Model catalog | `.cursor/get-shit-done/bin/shared/model-catalog.json` | AI model definitions for agent dispatch |
| Skills | `.cursor/skills/` (69 dirs) | Pluggable workflow commands |
| Agents | `.cursor/agents/` (35 files) | Subagent prompt configs |

These are framework-internal; no external network calls are made by the project itself.

---

*Integration audit: 2026-05-20*
