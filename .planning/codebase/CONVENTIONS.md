# Coding Conventions

**Analysis Date:** 2026-05-20

> **Pre-implementation note:** This project has no source code yet. The repository contains research markdown documents and GSD framework tooling. Conventions documented here apply to the existing markdown artifact layer. Conventions for the eventual implementation language must be established when code is first written.

---

## Project State

The repository is in the research/ideation phase. All content is markdown:

- `README.md` — project vision (rough draft, single paragraph)
- `mise-en-place/README.md` — placeholder (1 line)
- `research/SUMMARY.md` — hub document for research dossier
- `research/frameworks/*.md` — per-framework deep dives (4 files)
- `research/topics/*.md` — cross-cutting topic analyses (7 files)
- `research/.research-cache/*.md` — raw research cache (4 files)

No `package.json`, lockfile, linting config, or build tooling exists.

---

## Markdown Document Conventions

### Document Header Pattern

All research documents follow this header pattern:

```markdown
# [Title — Plain Noun Phrase]

> [One-line descriptor]
> Source: [URL or file reference]
> [Date or production context]

---
```

Block-quote headers carry metadata (source URLs, dates, cross-links). The `---` horizontal rule always follows the header block and separates it from body content.

### Section Numbering

Top-level sections use numbered H2 headings:

```markdown
## 1. Section Title
## 2. Section Title
## 3. Section Title
```

### Cross-References

Internal links use relative paths with descriptive anchor text:

```markdown
[frameworks/gsd.md](frameworks/gsd.md)
[../topics/patterns-worth-stealing.md](../topics/patterns-worth-stealing.md)
```

Always use relative markdown links — never absolute paths or bare filenames.

### Tables

Comparison and summary information uses pipe tables with a header separator row:

```markdown
| Column A | Column B | Column C |
|---|---|---|
| value    | value    | value    |
```

Tables are preferred over bullet lists for structured comparisons.

### Bullet Lists for Detail

Structured detail under a named item uses bullet sub-lists:

```markdown
- **Origin:** [source]
- **Problem it solves:** [description]
- **How it works:** [description]
- **Transferability:** HIGH/MEDIUM/LOW
```

Bold keys + plain values are the standard for labeled property lists.

### Code Blocks

Code examples use fenced blocks with language tags:

```markdown
```bash
command --flag value
```

```typescript
interface Foo { ... }
```
```

Shell commands use `bash`; conceptual code uses the appropriate language.

### File Path References

File paths appear in backticks inline: `` `.planning/STATE.md` ``, `` `src/services/user.ts` ``.

Never quote file paths with quotes or angle brackets.

---

## Naming Conventions

### Files

- Research deep-dives: `lowercase-kebab-case.md` (e.g., `tlc-spec-driven.md`, `adjacent-frameworks.md`)
- Topic analyses: `lowercase-kebab-case.md` (e.g., `patterns-worth-stealing.md`, `context-engineering.md`)
- Planning codebase docs: `UPPERCASE.md` (e.g., `CONVENTIONS.md`, `STACK.md`)
- Hub/summary docs: `UPPERCASE.md` (e.g., `SUMMARY.md`, `README.md`)

### Directories

- Lowercase, descriptive: `research/`, `frameworks/`, `topics/`, `mise-en-place/`
- GSD tooling directories use existing GSD conventions (`mise-en-place/` is the GSD project staging area)

---

## Error Handling

**Not applicable** — no source code. Establish when the implementation language is chosen.

---

## Logging

**Not applicable** — no source code.

---

## Comments

**Not applicable** — no source code. For markdown, use HTML comments `<!-- ... -->` for frontmatter metadata (e.g., GSD uses `<!-- refreshed: YYYY-MM-DD -->` in codebase docs).

---

## Module / Document Design

**Separation of concerns** in the research layer:
- Each framework gets its own deep-dive file in `research/frameworks/`
- Cross-cutting patterns go to `research/topics/`
- Raw cache stays in `research/.research-cache/`
- No content is duplicated — files cross-link to each other

---

## Conventions To Establish

When implementation begins, the following must be decided and added to this document:

- Primary language and runtime
- File naming for source files (kebab-case vs camelCase vs snake_case)
- Import order and path aliasing
- Error handling strategy (exceptions vs result types vs error callbacks)
- Logging library and structured log format
- Linting rules (`eslint`, `biome`, `ruff`, etc.) and formatter config

---

*Convention analysis: 2026-05-20*
