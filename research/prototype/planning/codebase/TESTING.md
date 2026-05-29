# Testing Patterns

**Analysis Date:** 2026-05-20

> **Pre-implementation note:** No testing infrastructure exists. The repository contains only research markdown documents and installed GSD framework tooling. No test runner, assertion library, coverage tool, or test files have been created. This document records current state and provides a baseline for future testing decisions.

---

## Current State

| Aspect | Status |
|---|---|
| Test runner | Not present |
| Test files | None (`*.test.*`, `*.spec.*` — zero matches) |
| Coverage tooling | Not present |
| CI pipeline | Not present |
| Linting (for test quality) | Not present |
| Package manifest | Not present (`package.json` does not exist) |

---

## Test Framework

**Runner:** Not detected

**Assertion Library:** Not detected

**Run Commands:**
```bash
# No test commands available yet
```

---

## Test File Organization

**Location:** Not established

**Naming:** Not established

**Structure:** Not established

---

## Mocking

**Framework:** Not detected

**Patterns:** Not established

---

## Fixtures and Factories

**Test Data:** Not established

**Location:** Not established

---

## Coverage

**Requirements:** None enforced

**View Coverage:**
```bash
# Not available yet
```

---

## Test Types

**Unit Tests:** Not established

**Integration Tests:** Not established

**E2E Tests:** Not established

---

## Testing Strategy To Establish

When implementation begins, the following decisions must be made and documented here:

### Recommended Decision Points

**Language determines runner:**
- TypeScript/JavaScript: Vitest (preferred for modern projects), Jest, or Node's built-in `node:test`
- Python: pytest
- Go: built-in `testing` package

**Coverage target:** Establish a minimum threshold (e.g., 80% lines) and enforce it in CI before merge.

**What to test:**
- Public behavior, not implementation details
- Edge cases: empty, null, zero, boundary values
- Error paths, not only happy paths
- Regression tests for any fixed bugs (Beyoncé Rule)

**What NOT to test:**
- The unit under test via self-mocking
- Pure configuration or generated code
- Third-party library internals

**Test data strategy:**
- Prefer factories over fixtures for domain objects
- Keep test data close to the test that uses it unless shared across many tests

**Integration vs. unit boundary:**
- Unit: single function or module, all I/O mocked
- Integration: two or more real modules wired together
- E2E: full user-visible flow from entry point to output

---

## GSD-Documented Testing Conventions (Reference)

The GSD framework (installed in `.cursor/`) expects the following when generating tests via `/gsd-add-tests`:

- Tests are derived from `UAT.md` acceptance criteria
- Test naming describes behavior, not code: `it("returns empty array when input is null")` not `it("tests getItems")`
- Each test must fail when behavior breaks and pass when behavior is correct
- Tests reuse project fixtures and utilities — no invented setup unless justified
- No `.only` or skipped tests left in files

These conventions apply once test infrastructure is in place.

---

*Testing analysis: 2026-05-20*
