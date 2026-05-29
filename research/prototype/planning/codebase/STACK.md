# Technology Stack

**Analysis Date:** 2026-05-20

## Languages

**Primary:**
- Markdown — all documentation, research, and planning artifacts (`.md` files throughout `research/`, `mise-en-place/`, `.planning/`)

**Secondary:**
- CommonJS JavaScript — GSD framework runtime scripts (`.cjs` files in `.cursor/get-shit-done/bin/`) — framework-internal only, not authored by this project
- JSON — GSD manifests and model catalogs (`.cursor/get-shit-done/bin/shared/model-catalog.json`, `.cursor/gsd-file-manifest.json`)

## Runtime

**Environment:**
- macOS darwin 24.6.0
- Shell: zsh

**Package Manager:**
- None — no application dependencies managed by this project
- GSD framework is installed as a pre-built binary bundle (`.cjs` files), not via npm/pip/cargo

## Frameworks

**AI Workflow:**
- GSD (Get-Shit-Done) v1.42.3 — meta-prompting and context engineering framework
  - Installed at: `.cursor/get-shit-done/`
  - Skills: 60+ skill modules at `.cursor/skills/`
  - Agents: 33+ agent configs at `.cursor/agents/`
  - Profile: `full` (all skills enabled, as set in `.cursor/.gsd-profile`)

**Testing:**
- Not applicable — no application code to test

**Build/Dev:**
- Not applicable — no build pipeline

## Key Dependencies

**Critical:**
- GSD v1.42.3 — AI workflow orchestration system; provides all planning, phasing, research, and execution commands
  - Manifest: `.cursor/gsd-file-manifest.json`
  - State: `.cursor/gsd-install-state.json`

**Infrastructure:**
- Cursor IDE — primary authoring and AI development environment; required to run GSD skills and agents
- Git — version control (repo at `/Users/viniciusguimaraes/personal-projects/spec-driven-cookbook`)

## Configuration

**Environment:**
- No application environment variables required
- No `.env` files present

**GSD Config:**
- Profile: `.cursor/.gsd-profile` (value: `full`)
- Install state: `.cursor/gsd-install-state.json`
- File integrity manifest: `.cursor/gsd-file-manifest.json`
- Skills directory: `.cursor/skills/` (69 skill modules)
- Agents directory: `.cursor/agents/` (35 agent configs)

**Build:**
- No build configuration — this is a documentation-only repository

## Platform Requirements

**Development:**
- macOS or compatible Unix environment
- Cursor IDE with GSD framework installed
- Git for version control
- No Node.js, Python, or other runtime required by the project itself

**Production:**
- Not applicable — no deployed application

---

*Stack analysis: 2026-05-20*
