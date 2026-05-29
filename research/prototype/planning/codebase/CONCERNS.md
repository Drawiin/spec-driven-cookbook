# Codebase Concerns

**Analysis Date:** 2026-05-20

## Tech Debt

**Empty `mise-en-place/` directory:**
- Issue: The `mise-en-place/` directory exists and was likely intended to hold synthesis/distillation artifacts drawn from the research dossier (analogous to a "prep" stage before implementation). Its `README.md` is completely empty (0 bytes).
- Files: `mise-en-place/README.md`
- Impact: Readers following the implied project structure find a dead end. Any workflow that assumes `mise-en-place/` is populated will fail silently.
- Fix approach: Either populate `mise-en-place/README.md` with its purpose and link to its expected contents, or delete the directory if it is no longer part of the project plan.

**Truncated root README.md:**
- Issue: `README.md` is 4 lines and cuts off mid-sentence at the "Core philosofy" heading. It contains significant typos ("jusr", "IA agentes", "applu", "sued to", "eve nfastwr") and does not describe the project, its structure, or how to navigate it.
- Files: `README.md`
- Impact: First-time contributors cannot orient themselves. The project intent is only discoverable through the research dossier, which requires knowing it exists.
- Fix approach: Rewrite `README.md` to describe the project goal, directory structure (`research/`, `mise-en-place/`), and how to navigate the dossier. Fix typos. Link to `research/SUMMARY.md` as the entry point.

**Untracked `.cursor/` and `.planning/` directories:**
- Issue: Both `.cursor/` and `.planning/` are untracked by git (visible in `git status`). The `.cursor/` directory contains GSD agent definitions and tooling; `.planning/` contains codebase analysis documents. Neither is committed nor gitignored.
- Files: `.cursor/`, `.planning/`
- Impact: Planning artifacts and agent tooling are invisible to collaborators and not backed up in version history. Any team member cloning the repo gets neither.
- Fix approach: Decide intentionality: if `.cursor/` and `.planning/` are project-level artifacts (rather than personal tooling), commit them. If personal/tooling-only, add to `.gitignore`.

## Known Bugs

**No known runtime bugs** — this is a documentation-only project with no executable code.

## Security Considerations

**Missing `.gitignore` — research cache not excluded:**
- Risk: The `research/.research-cache/` directory is explicitly flagged in its own `README.md` as internal-only and recommended for gitignore. No `.gitignore` file exists in the repository.
- Files: `research/.research-cache/README.md`
- Current mitigation: The cache files are currently untracked but not gitignored. They can be accidentally committed.
- Recommendations: Create a `.gitignore` at the project root and add `research/.research-cache/` to it. Consider also gitignoring `.cursor/` and `.planning/` if they are personal-tooling-only.

**No secrets or credentials present** — this is a documentation-only project with no API keys, tokens, or credentials.

## Performance Bottlenecks

**Not applicable** — no executable code or runtime system is present.

## Fragile Areas

**Research dossier has no single source-of-truth marker:**
- Files: `research/SUMMARY.md`, `research/frameworks/*.md`, `research/topics/*.md`, `research/.research-cache/*.md`
- Why fragile: The cache README declares cache files as "canonical source-of-truth for all writing and validation sub-agents," but the dossier README states "post-validation framework files" are the source of truth. There are two competing source-of-truth claims with no reconciliation.
- Safe modification: Treat `research/frameworks/*.md` and `research/topics/*.md` as the authoritative public dossier. The `.research-cache/` files are raw inputs, not outputs.
- Test coverage: N/A (documentation project).

**Unverified claims embedded in research content:**
- Files: `research/SUMMARY.md` (Section 7), `research/frameworks/graphify.md`, `research/frameworks/adjacent-frameworks.md`
- Why fragile: Section 7 of `SUMMARY.md` lists 18 unverified items, including star counts (e.g., Graphify reported ~49k in cache vs 3.7k+ on live landing page), unconfirmed MCP tool names for Graphify, BMAD Story Automator v6.6+, GSD plan-checker 8 dimensions, and OpenSpec model version strings ("Opus 4.5", "GPT 5.2") that may not exist. These items are flagged inline but could mislead future design decisions if read without consulting Section 7.
- Safe modification: Before acting on any claim in the frameworks or topics files, cross-reference with Section 7 of `SUMMARY.md` and re-verify against live sources.
- Test coverage: N/A.

**One research source was auth-gated and excluded:**
- Files: `research/SUMMARY.md` (Section 8)
- Why fragile: A Cursor OAuth URL was listed as a research source but was inaccessible. Whatever it would have contributed is missing from the dossier. This is noted but easy to forget when building on the research.
- Safe modification: Note this gap explicitly before designing any Cursor-specific patterns.

## Scaling Limits

**Not applicable** — no runtime system is present to scale.

## Dependencies at Risk

**No package manager or external dependencies present** — this is a pure documentation project with no `package.json`, `requirements.txt`, or equivalent.

## Missing Critical Features

**No `.gitignore`:**
- Problem: The repository has no `.gitignore`. The research cache README explicitly recommends adding `research/.research-cache/` to `.gitignore`.
- Blocks: Safe collaboration — without `.gitignore`, the cache, `.cursor/`, and `.planning/` are at risk of accidental commit.

**No project structure documentation:**
- Problem: There is no document explaining the purpose of each top-level directory (`research/`, `mise-en-place/`, `.planning/`), their relationship, or the intended workflow from research → synthesis → implementation.
- Blocks: Onboarding any contributor beyond the original author requires reading every file to infer structure.

**`mise-en-place/` is empty with no stated purpose:**
- Problem: The directory name implies a synthesis or preparation stage (culinary "mise en place" = everything in its place before cooking), but there is no content or explanation of what should go here.
- Blocks: It is unclear whether this is a planned phase not yet started, an abandoned direction, or a placeholder awaiting content.

## Test Coverage Gaps

**No tests of any kind** — this is a documentation-only project. There are no scripts, no validators, and no linters configured. No test runner is present or applicable.

**No link-checking:**
- What's not tested: Internal cross-links between `SUMMARY.md`, `frameworks/*.md`, and `topics/*.md` are not validated.
- Files: `research/SUMMARY.md` (contains ~30 internal markdown links)
- Risk: Broken internal links degrade navigation silently. Moving or renaming files would break links without any automated warning.
- Priority: Low (documentation-only project, small file count).

---

*Concerns audit: 2026-05-20*
