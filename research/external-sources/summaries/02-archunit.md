# Source Summary — ArchUnit

> URL: https://www.archunit.org/
> Fetched: 2026-05-24

## 1. What it is (1-paragraph)

ArchUnit is a free, extensible Java library for unit-testing the architecture of a Java codebase using ordinary unit-test frameworks (JUnit 4/5, TestNG, anything that runs Java). It imports compiled bytecode into a graph of `JavaClass`, `JavaMethod`, `JavaField`, `JavaAccess`, etc. objects and lets developers express architectural rules — package dependencies, layer access, naming, annotation presence, slice acyclicity, modularization, custom predicates — as fluent-API `ArchRule`s that are evaluated against that graph and produce per-violation assertion failures (with class + line number) when broken (https://www.archunit.org/userguide/html/000_Index.html). A .NET/C# port exists (https://archunitnet.readthedocs.io/en/latest/).

## 2. Core abstractions

- **`ClassFileImporter` → `JavaClasses`**: imports bytecode from packages, paths, JARs, or full classpath into an in-memory graph; supports `ImportOption`s like `DO_NOT_INCLUDE_TESTS`, `DO_NOT_INCLUDE_JARS`.
- **Core domain model**: `JavaClass`, `JavaMethod`, `JavaField`, `JavaConstructor`, `JavaAccess` (subdivided into `JavaFieldAccess`, `JavaMethodCall`, `JavaConstructorCall`) — mirrors the Reflection API plus dependency/access edges (`getAccessesFromSelf`, `getAccessesToSelf`).
- **Lang API (rule DSL)**: fluent `ArchRuleDefinition.classes().that(<predicate>).should(<condition>)` plus `noClasses()`, `methods()`, `fields()`, `members()`, `codeUnits()`, `constructors()` and their `no*` negations. Generic shape: `classes that ${PREDICATE} should ${CONDITION}` built from composable `DescribedPredicate` and `ArchCondition` (https://www.archunit.org/userguide/html/000_Index.html §7).
- **Library API — predefined complex rules**:
  - **Layered architecture**: `layeredArchitecture().layer("X").definedBy("..x..").whereLayer("X").mayOnlyBeAccessedByLayers("Y")`.
  - **Onion / Hexagonal**: `onionArchitecture().domainModels(..).domainServices(..).applicationServices(..).adapter("rest", "..adapter.rest..")` enforces Palermo's onion semantics (https://jeffreypalermo.com/2008/07/the-onion-architecture-part-1/).
  - **Slices**: `slices().matching("..myapp.(*)..").should().beFreeOfCycles()` or `.notDependOnEachOther()`; supports a custom `SliceAssignment` mapping classes to `SliceIdentifier`s for legacy packages.
  - **Modules**: `ModuleRuleDefinition.modules().definedByPackages(..)` or `.definedByAnnotation(@AppModule)` with `respectTheirAllowedDependenciesDeclaredIn(..)` and `onlyDependOnEachOtherThroughPackagesDeclaredIn("exposedPackages")` — JPMS-like enforcement.
  - **GeneralCodingRules**: no `System.out`/`System.err`, no generic exceptions, no `java.util.logging`, no field injection, etc.
  - **PlantUML-as-rules**: `adhereToPlantUmlDiagram(diagram.puml, consideringAllDependencies())` derives rules straight from a component diagram via stereotypes that encode package identifiers.
  - **`FreezingArchRule`**: wraps any rule to baseline existing violations in a `ViolationStore` (default = text files in VCS); only *new* violations fail; fixed ones auto-shrink the store. Configurable via `archunit.properties` (`freeze.store.default.path`, `allowStoreCreation`, `allowStoreUpdate`, `freeze.refreeze`).
- **JUnit integration**: `@AnalyzeClasses(packages=...)` + `@ArchTest` on static `ArchRule` fields; auto-caches `JavaClasses` per location across tests; `ArchTests.in(ServiceRules.class)` composes rule libraries.

## 3. Workflow / how teams use it

- Add the `archunit-junit5` test dependency and write architecture rules as ordinary tests inside the project's test suite (no new tool, no new language) (https://www.archunit.org/motivation).
- Co-locate rules with the code they govern, often as one or more `*ArchitectureTest` classes that aggregate rule libraries via `ArchTests.in(...)`.
- Run them in CI on every push/PR — failures appear in the same test report as regular unit tests with rule text, violating class, and line number embedded in the assertion message.
- For legacy code bases with thousands of pre-existing violations, wrap rules in `FreezingArchRule.freeze(...)` to set a baseline; commit the violation store text file to VCS; ratchet down over time (refusing regressions while gradually shrinking the store).
- Configure CI safety via `freeze.store.default.allowStoreCreation=false` and `allowStoreUpdate=false` so CI can never silently grow the baseline.
- Optionally express the target architecture as a PlantUML component diagram and let ArchUnit derive rules from the picture — the diagram itself becomes the executable spec.

## 4. Concepts directly relevant to spec-driven AI coding frameworks

- **ArchRule as executable architectural decision**: an ADR-equivalent constraint expressed in code; matters because AI agents can be given a rule set as a verifier loop rather than vague prose.
- **`FreezingArchRule` / `ViolationStore`**: explicit baseline of "known debt" with anti-regression semantics; matters because AI agents introducing changes to a legacy codebase need a way to *not* be blamed for pre-existing issues while still being blocked on *new* violations.
- **PlantUML-as-rules**: a single artifact serves as both human-readable diagram and machine-checked spec; matters because spec-driven AI workflows want the spec authored once and consumed by both humans and tooling [inference].
- **Custom `DescribedPredicate` / `ArchCondition`**: rules are first-class, composable, and self-describing (the predicate carries its own English description used in failure messages); matters because AI agents producing/consuming rules benefit from self-narrating constraints (the failure message *is* the spec).
- **Slices + cycle detection + modularization (`@AppModule`)**: declarative "what depends on what" boundaries enforced at build time; matters because spec-driven systems need a way to declare module boundaries that an AI agent must respect when generating code.
- **`@AnalyzeClasses` + `ArchTests.in(...)`**: rule libraries are *importable, parameterized contracts* — matters because cross-repo or org-wide architectural standards can be packaged and reused; AI agents could install the canonical rule pack as a constraint set [inference].
- **Layered/Onion architecture as a primitive**: idiomatic architectures are encoded as DSL methods, not free-form text; matters because AI agents can target a small named vocabulary of well-known patterns.

## 5. Concrete mechanisms worth stealing for an AI coding framework

- **Self-describing rule objects** | Each `ArchRule` carries its own English description, automatically embedded in failure messages alongside violating class + line number ("Rule '...' was violated (1 times): Method `<X>` calls `<Y>` in (`SomeService.java:14`)"). The spec *is* the assertion message. | Adaptation: every spec/rule produced or consumed by an AI agent should round-trip to a human-readable sentence and back; rule violations reported to the agent should embed the offending file:line plus the rule's prose statement — closes the loop between spec, code, and feedback. Cross-ref: "test-as-spec" — ArchUnit is essentially the canonical implementation.
- **Frozen baseline with ratchet semantics** | `FreezingArchRule` records every existing violation in a VCS-committed `ViolationStore`; CI fails only on *new* violations and auto-shrinks the store when violations are fixed. `allowStoreCreation`/`allowStoreUpdate` flags prevent silent baseline growth. | Adaptation: spec-driven AI frameworks should support "freeze on adoption" — when a new constraint is introduced, snapshot the current violations as known debt so the agent can ship code today while the constraint applies strictly to *new* output. This is exactly the analog of "decision coverage gates" with a ratchet: legacy diffs are exempt, new diffs are not.
- **Diagram-as-spec (PlantUML → ArchRule)** | A PlantUML component diagram with stereotyped components (`<<..pkg..>>`) becomes an executable rule via `adhereToPlantUmlDiagram(url, consideringAllDependencies())`. Components are mapped to package identifiers; arrows are the only allowed dependencies. | Adaptation: let an AI agent consume a single source-of-truth diagram (PlantUML, Mermaid, or similar) and *both* generate code against it *and* be evaluated against it on every commit. The diagram is the contract; the agent can't drift without the diff failing.
- **Predefined architecture primitives (layered, onion, slices, modules)** | A handful of named, composable, parameter-driven architectures cover the common cases without forcing teams to write predicates from scratch. | Adaptation: ship a curated catalog of named architectural patterns as first-class spec primitives ("this project is layered: controller → service → persistence"; "this project is onion: domain ← application ← adapters"). The AI agent then has a small, well-known vocabulary to comply with — much higher signal than free-form prose.
- **Importable, composable rule libraries (`ArchTests.in(...)`)** | Rules can be packaged in classes, imported across modules, and meta-annotated (`@AnalyzeMainClasses`) to avoid repetition. | Adaptation: spec packs become installable dependencies. An AI agent working in a repo discovers which packs are active (via config or convention) and treats them as hard constraints. Analog to lint-rule packages but with semantic, cross-file scope.
- **Self-contained verifier: no new infra, no new language** | ArchUnit runs inside the project's existing test framework — no daemon, no plugin, no DSL parser. Plain Java + an assertion. | Adaptation: spec-driven verifiers for AI-generated code should ride on whatever the project already runs in CI (`pytest`, `vitest`, `go test`, …) rather than introducing a new sidecar tool. Lowers adoption cost and keeps the agent's feedback loop in one place.
- **Bytecode-level evidence over source heuristics** | ArchUnit reads bytecode, not source, so it sees what the compiler actually produced — accurate dependency edges, no false positives from comments or string literals. | Adaptation: where possible, spec verifiers for AI-generated code should target a post-compile / post-build artifact (AST, IR, or bundle graph) rather than raw source text. AI agents are prone to "looks right" output; ground truth needs a deterministic substrate.

## 6. Notable quotes (with URL)

- "ArchUnit is a free, simple and extensible library for checking the architecture of your Java code... by analyzing given Java bytecode, importing all classes into a Java code structure." (https://www.archunit.org/)
- "Especially in an agile project, where the role of the architect might even be distributed, developers should all have a common language and understanding of the components and their relations." (https://www.archunit.org/motivation)
- "When rules are introduced in grown projects, there are often hundreds or even thousands of violations, way too many to fix immediately. The only way to tackle such extensive violations is to establish an iterative approach, which prevents the code base from further deterioration." — on `FreezingArchRule` (https://www.archunit.org/userguide/html/000_Index.html §8.6)
- "On the first run all violations of that rule will be stored as the current state. On consecutive runs only new violations will be reported." (https://www.archunit.org/userguide/html/000_Index.html §8.6.1)
- "ArchUnit can derive rules straight from PlantUML diagrams and check to make sure that all imported `JavaClasses` abide by the dependencies of the diagram." (https://www.archunit.org/userguide/html/000_Index.html §8.5)
- "ArchUnit doesn't strive to be a 'competition' for module systems like the Java Platform Module System... But ArchUnit can bring JPMS-like features to older code bases." (https://www.archunit.org/userguide/html/000_Index.html §8.3)

## 7. Pages fetched

- Degree 0:
  - https://www.archunit.org/
- Degree 1:
  - https://www.archunit.org/motivation
  - https://www.archunit.org/userguide/html/000_Index.html (single-page user guide covering Introduction, Installation, Getting Started, What to Check, Ideas and Concepts, Core API, Lang API, Library API, JUnit Support, Advanced Configuration — sections 1–10)

The official user guide is published as a single HTML page, so all "2-degree" concepts (predefined rules, freezing arch rules, writing tests, modules, slices, PlantUML, layered/onion) are already contained within the §1 user-guide fetch above. No separate deep pages were needed.

## 8. Pages attempted but failed

- None. All fetches returned HTTP 200.

## 9. Confidence: HIGH

Rationale: The official user guide (v1.4.2, the current release per the news feed) is a single comprehensive page that was fetched in full (≈1686 lines, 77 KB) and covers every load-bearing concept listed in the task brief (rules, fluent API, layered/onion architecture, slices, modules, freezing rules, PlantUML, JUnit integration, configuration). All non-obvious claims above are sourced from that guide or from the motivation page. Items marked [inference] are clearly labeled and concern adaptation suggestions, not claims about ArchUnit's behavior.
