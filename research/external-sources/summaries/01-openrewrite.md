# Source Summary — OpenRewrite

> URL: https://docs.openrewrite.org/
> Fetched: 2026-05-24

## 1. What it is (1-paragraph)

OpenRewrite is an open-source "automated refactoring ecosystem" for source code, aimed at letting teams eliminate technical debt and run framework/library migrations at scale (https://docs.openrewrite.org/). It ships an auto-refactoring engine plus a catalog of prepackaged, open-source **recipes** (framework migrations, security fixes, style fixes) and build-tool plugins (Maven, Gradle) that run those recipes against a repository. The engine works by parsing code into **Lossless Semantic Trees (LSTs)**, applying transformations via **Visitors** wired into **Recipes**, then printing the LST back to source while preserving original formatting (https://docs.openrewrite.org/). Originally Java-centric, it now spans many languages; a commercial layer (Moderne) extends it to mass refactoring across many repos.

## 2. Core abstractions (LSTs, recipes, visitors, etc.)

- **Lossless Semantic Tree (LST)** — A tree representation of source that is both **type-attributed** (each node knows the resolved type of references, even cross-file) and **format-preserving** (whitespace and local style are kept on the tree so output round-trips cleanly) (https://docs.openrewrite.org/concepts-and-explanations/lossless-semantic-trees). LSTs are built per run, held in memory, mutated, then printed back.
- **Tree / Marker** — Every LST node implements `Tree` with a stable unique ID, an `accept()` callback for visitors, `print()` methods, and a `Markers` bag for attaching metadata (e.g. search hits, resolution results) without changing structure (https://docs.openrewrite.org/concepts-and-explanations/visitors).
- **Visitor (`TreeVisitor<T, P>`)** — Where logic lives. Depth-first traversal driven by `visit(T, P)`; each language has isomorphic (`JavaIsoVisitor`, type-preserving) and non-isomorphic (`JavaVisitor`, allows swapping node types) variants. Visitors carry a **Cursor** (stack of ancestors + message map) so they can reason about context and pass messages without global state (https://docs.openrewrite.org/concepts-and-explanations/visitors).
- **Recipe** — A configured, named, validated transformation. Two flavors: **imperative** (Java class extending `Recipe`, exposes a `getVisitor()`) and **declarative** (YAML that composes other recipes via `recipeList`) (https://docs.openrewrite.org/concepts-and-explanations/recipes).
- **ScanningRecipe** — Two-phase recipe (scan → edit, with optional generate) using a custom **accumulator** so the recipe can see the whole project before deciding what to change or generate (https://docs.openrewrite.org/concepts-and-explanations/recipes).
- **ExecutionContext** — Thread-safe shared state object passed through the pipeline; carries config, error handlers, and inter-recipe messages (https://docs.openrewrite.org/concepts-and-explanations/recipes).
- **Preconditions** — Recipe-as-filter: lightweight search recipes that gate whether a given recipe is allowed to edit a file (https://docs.openrewrite.org/reference/yaml-format-reference).
- **Styles** — Declarative formatting/style configs that recipes consult so generated/changed code matches local conventions (https://docs.openrewrite.org/reference/yaml-format-reference).
- **Result** — Per-file diff object exposing `getBefore()`, `getAfter()`, the list of recipes that made each change, and a git-style `diff()` (https://docs.openrewrite.org/concepts-and-explanations/recipes).

## 3. Workflow / how teams use it

- Add the **rewrite-maven-plugin** or **rewrite-gradle-plugin** to the project (https://docs.openrewrite.org/running-recipes/getting-started).
- Discover available recipes with `mvn rewrite:discover` / `gradle rewriteDiscover` (https://docs.openrewrite.org/running-recipes/getting-started).
- Mark one or more recipes as **active** in plugin config, optionally pulling in third-party recipe modules (e.g. `rewrite-spring`) via Maven deps or the `rewrite-recipe-bom` (https://docs.openrewrite.org/running-recipes/getting-started).
- For composed/parametrized transformations, author a `rewrite.yml` at repo root (or `META-INF/rewrite/*.yml` inside a distributable JAR) declaring a recipe of `type: specs.openrewrite.org/v1beta/recipe` with a `recipeList:` (https://docs.openrewrite.org/reference/yaml-format-reference).
- Run `mvn rewrite:run` / `gradle rewriteRun`; review diff with normal git tooling; commit (https://docs.openrewrite.org/running-recipes/getting-started).
- Moderne (commercial) runs the same recipe catalog across thousands of repos and supports building LSTs in pieces so they need not fit in memory (https://docs.openrewrite.org/concepts-and-explanations/lossless-semantic-trees).

## 4. Concepts directly relevant to spec-driven AI coding frameworks

- **Lossless Semantic Tree** — Tree representation that keeps both types and original formatting. Matters because AI agents editing code at scale need precise, type-aware targeting and must not reformat unrelated lines [inference].
- **Markers** — Per-node metadata bag for search hits and resolution data (https://docs.openrewrite.org/concepts-and-explanations/visitors). Matters because an agent can annotate code with findings/intents that survive transformations without mutating the code itself [inference].
- **Recipe (imperative + declarative)** — Named, validated, parameterized, composable transformation (https://docs.openrewrite.org/concepts-and-explanations/recipes). Matters because spec-driven workflows can treat each spec/intent as a reusable, testable, composable unit instead of an ad-hoc prompt [inference].
- **Recipe composition via `recipeList`** — Declarative YAML lets you build large migrations by ordering small recipes (https://docs.openrewrite.org/concepts-and-explanations/recipes). Matters because high-level AI specs can decompose into ordered, traceable sub-operations [inference].
- **Preconditions** — Lightweight recipes that decide whether a heavier recipe may run on a file (https://docs.openrewrite.org/reference/yaml-format-reference). Matters because AI agents need cheap, deterministic gating ("only touch test files that import JUnit 4") before invoking expensive model calls [inference].
- **ScanningRecipe (scan → generate → edit)** — Two/three-phase pipeline with an accumulator that surveys the whole codebase before changing anything (https://docs.openrewrite.org/concepts-and-explanations/recipes). Matters because LLM-driven edits frequently need cross-file context before deciding what to change [inference].
- **Execution cycles** — The pipeline re-runs until no recipe makes changes, up to a cap, so recipes can react to each other's output (https://docs.openrewrite.org/concepts-and-explanations/recipes). Matters because agentic systems can converge multi-pass edits without bespoke control loops [inference].
- **Execution context + cursor messages** — Standard channels for sharing state across visitors safely (https://docs.openrewrite.org/concepts-and-explanations/visitors, https://docs.openrewrite.org/concepts-and-explanations/recipes). Matters because multi-step AI plans need a defined memory contract instead of relying on chat scrollback [inference].
- **Result set with diff + provenance** — Each Result reports which recipes changed each file (https://docs.openrewrite.org/concepts-and-explanations/recipes). Matters because audit/explanation of AI-driven changes is a first-class need [inference].
- **Recipe descriptors / `@Option`** — Self-describing metadata (display name, description, options, estimated effort) used for catalogs and docs (https://docs.openrewrite.org/concepts-and-explanations/recipes, https://docs.openrewrite.org/reference/yaml-format-reference). Matters because an AI orchestrator can plan over a discoverable, typed catalog of capabilities [inference].

## 5. Concrete mechanisms worth stealing for an AI coding framework

- **Lossless Semantic Tree | Parse code into a typed, format-preserving tree, mutate the tree, then print back. Type info travels with each node; whitespace and local style are tree-resident, so output round-trips exactly (https://docs.openrewrite.org/concepts-and-explanations/lossless-semantic-trees). | Have the AI propose edits against an LST-like IR instead of raw text. The framework would print back, guaranteeing formatting preservation and giving the model accurate type context for grounding (no hallucinated APIs). [inference]**
- **Declarative recipe composition (YAML `recipeList`) | A recipe can be just a YAML doc that orders other recipes and passes parameters, with no Java code (https://docs.openrewrite.org/concepts-and-explanations/recipes, https://docs.openrewrite.org/reference/yaml-format-reference). | Define "specs" as a YAML/JSON DAG that composes lower-level deterministic skills and LLM-powered skills uniformly. Both kinds expose the same options/validation surface so they can be reordered, tested, and shared. [inference]**
- **Preconditions as filters | Cheap search recipes attached to a transformation that decide which files are eligible; failed preconditions skip the recipe for that file (https://docs.openrewrite.org/reference/yaml-format-reference). | Require every AI editing step to ship with a deterministic precondition (glob, type query, regex). The orchestrator runs preconditions first to scope what the model sees, slashing token cost and reducing scope creep. [inference]**
- **ScanningRecipe with accumulator | Three-phase scan → generate → edit, where scanners populate a typed accumulator the edit phase reads (https://docs.openrewrite.org/concepts-and-explanations/recipes). | Standardize a "survey before edit" pattern for AI agents: a scan pass produces a structured project memo (deps used, patterns found), the edit pass consumes only that memo, not the whole repo. [inference]**
- **Execution cycles with `causesAnotherCycle` | The pipeline re-runs recipes until quiescence, capped (default 3), and recipes self-declare whether they may need another cycle (https://docs.openrewrite.org/concepts-and-explanations/recipes). | Adopt cycle-based convergence for AI edits (e.g. typecheck/format/test pass after each round) with an explicit cycle cap and a per-step "may-need-another-cycle" flag. [inference]**
- **Isomorphic vs non-isomorphic visitor distinction | Two visitor flavors: one guarantees the node type is preserved (compiler enforces), the other permits structural replacement (https://docs.openrewrite.org/concepts-and-explanations/visitors). | Mirror in AI tooling: "safe edits" (rename, retype, reformat — provably structure-preserving) vs "structural edits" (replace function with class). Different review gates per class. [inference]**
- **Markers (metadata on AST nodes) | `Markers` bag attached to every Tree node carries search hits, resolution data, and arbitrary metadata without altering structure (https://docs.openrewrite.org/concepts-and-explanations/visitors). | Let agents annotate code IR with rationale, confidence, source-of-truth links, and review status as markers — surfaced in PR review but invisible to runtime. [inference]**
- **Recipe descriptors (`@Option`, displayName, description, estimatedEffortPerOccurrence, tags) | Recipes self-document their parameters and expected effort saved (https://docs.openrewrite.org/concepts-and-explanations/recipes, https://docs.openrewrite.org/reference/yaml-format-reference). | Require every AI skill to publish a typed manifest so a planner LLM can do tool-selection on metadata alone, and so leadership can prioritize by `estimatedEffortPerOccurrence`. [inference]**
- **Result set with per-file `recipesThatMadeChanges` | Each file diff records which recipes contributed to the change (https://docs.openrewrite.org/concepts-and-explanations/recipes). | Persist per-hunk attribution to the AI step (skill ID, prompt hash, model version, spec ID) so every line in a PR can be traced back to a spec. [inference]**
- **Distribution via `META-INF/rewrite/*.yml` JARs | Recipes ship as packaged artifacts; consumers pull them in via dependency management (https://docs.openrewrite.org/reference/yaml-format-reference, https://docs.openrewrite.org/running-recipes/getting-started). | Treat AI "specs" as versioned, packaged artifacts (npm / OCI / pypi) with semver and a BOM, not as in-repo prompts. Enables a shared catalog. [inference]**

## 6. Notable quotes

- "OpenRewrite works by making changes to Lossless Semantic Trees (LSTs) that represent your source code and printing the modified trees back into source code." — https://docs.openrewrite.org/
- "Type-attributed. Each LST is imbued with type information... Format-preserving. Whitespace before and after LSTs are preserved in the tree so the tree can be printed out to reconstitute the original source code without clobbering formatting." — https://docs.openrewrite.org/concepts-and-explanations/lossless-semantic-trees
- "Making your recipes immutable... is a strongly recommended best practice. Any mutable state should be local to the visitor, a fresh instance of which should be returned from each invocation of `getVisitor()`." — https://docs.openrewrite.org/concepts-and-explanations/recipes
- "If a file does not satisfy the precondition, the recipe list is skipped for that file entirely. When multiple recipes are used as preconditions, all of them must make a change to the file for it to be considered to meet the precondition." — https://docs.openrewrite.org/reference/yaml-format-reference
- "The recipes in the execution pipeline may produce changes that in turn cause another recipe to do further work. As a result, the pipeline may perform multiple passes (or cycles) over all the recipes in the pipeline again until either no changes are made in a pass or some maximum number of passes is reached (by default 3)." — https://docs.openrewrite.org/concepts-and-explanations/recipes

## 7. Pages fetched

- Degree 0:
  - https://docs.openrewrite.org/ (HTTP 200)
- Degree 1:
  - https://docs.openrewrite.org/concepts-and-explanations/lossless-semantic-trees (HTTP 200)
  - https://docs.openrewrite.org/concepts-and-explanations/visitors (HTTP 200)
  - https://docs.openrewrite.org/concepts-and-explanations/recipes (HTTP 200)
  - https://docs.openrewrite.org/running-recipes/getting-started (HTTP 200)
- Degree 2:
  - https://docs.openrewrite.org/reference/yaml-format-reference (HTTP 200)

## 8. Pages attempted but failed

- None. All five fetches succeeded; deeper crawling stopped intentionally once the core abstractions, authoring model, declarative composition, and execution pipeline were covered (per the "stop fetching once you have enough" constraint).

## 9. Confidence

HIGH. Every claim in sections 1–3 and 6 is sourced directly from the fetched docs and the URL is cited. The "concepts relevant to AI coding" and "mechanisms worth stealing" sections are explicitly marked `[inference]` where the adaptation is mine rather than the source's; the underlying OpenRewrite mechanisms they reference are all sourced. The summary is bounded by what the five fetched pages assert; areas like Moderne's incremental LSTs, language-specific visitors beyond Java, and Refaster template recipes are mentioned only briefly because they were not deeply fetched.
