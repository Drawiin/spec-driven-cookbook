# Source Summary — The Role of Developer Skills in agentic coding (Martin Fowler memo #13)

> URL: https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html
> Fetched: 2026-05-24

## 1. Thesis

Agentic coding assistants (Cursor, Windsurf, Cline) have advanced impressively through IDE integration — running tests, fixing lint errors, doing web research, even reading browser previews — but in real sessions on non-trivial codebases the author still intervenes, corrects and steers "all the time," and sometimes throws the changes away. Experienced developer skills remain essential to catch AI missteps across three impact radiuses (time-to-commit, team flow, long-term maintainability), and those are precisely the skills the industry must preserve and train for, since AI will not autonomously write 90% of code in a year for non-trivial work.

## 2. Author & date / position in the exploring-gen-ai series

- Author: Birgitta Böckeler (Thoughtworks). [inference based on series authorship; not stated verbatim on this page]
- Position: Memo #13 in the "Exploring Gen AI" series. Previous: #12 "What role does LLM reasoning play for software tasks?". Next: #14 "Guiding an LLM for Robust Java ByteBuffer Code". Latest in series at time of fetch: "Humans and Agents in Software Engineering Loops" (dated Mar 04). The page itself does not display a publication date.

## 3. Core arguments

- Agentic IDE tooling has genuinely leapt forward, especially for editing existing codebases, not just greenfield demos.
- Even successful agentic sessions require constant human steering; missteps have non-negligible probability regardless of prompt rigor or context providers.
- LLMs "frequently don't listen to the letter of the prompt," and reliability degrades as sessions/context windows grow.
- AI failures fall on a 3-tier impact radius: (a) time-to-commit, (b) team flow in the iteration, (c) long-term maintainability. Bigger radius = longer feedback loop = more dangerous.
- The maintainability tier is where 20+ years of experience matters most — exactly the tier most invisible to less-experienced reviewers.
- Therefore safeguards are needed at individual, team, and organizational levels; pretending AI removes the need for craft creates compounding debt.
- Forecast: AI writing 90% of code autonomously within a year is implausible; AI *assisting* in 90% is plausible for some teams/codebases.

## 4. Skills the memo emphasizes (and why)

- **Critical review of generated code** | rare for the author to find nothing to fix | reviews every AI commit candidate before accepting.
- **Knowing when to stop / "artisanal coding" fallback** | sessions can spiral; experience tells you when to bail | "stop AI coding sessions when you feel overwhelmed... revise prompt and start new session, or fall back to manual implementation."
- **Pattern recognition for misdiagnosis** | prevents rabbit holes | spotted that a Docker build issue was `node_modules` built for wrong architecture, not a Docker arch setting.
- **Incremental / vertical-slice thinking** | counters AI's tendency to "go broad" | during frontend migration AI tried to convert all components at once instead of one component end-to-end.
- **Root-cause analysis** | counters AI's brute-force fixes | AI raised Docker memory limits instead of asking why memory usage was so high.
- **Developer-workflow / DX judgment** | AI breaks team ergonomics | introduced two start commands instead of one; broke hot reload; over-complicated builds.
- **Requirements discipline / attention** | catches under-specified prompts early | AI jumps to wrong conclusions when functional requirements are vague.
- **Test design taste** | counters AI's verbose, duplicative tests | "more tests are not necessarily better" — duplicated assertions make suites brittle.
- **Modularity / reuse awareness** | counters AI duplication | AI re-implements a UI component that already exists; uses inline CSS instead of classes/variables.
- **Restraint against over-engineering** | counters verbose/over-built output | AI built an elaborate JSON-display web component beyond what was needed.
- **Architectural awareness (e.g., DI chains)** | counters brittle designs | AI added a redundant constructor parameter when the value was already obtainable from an already-injected dependency: `value = service_a.get_value(); ServiceB(service_a, value=value)`.

## 5. Concepts directly relevant to spec-driven AI coding frameworks

- **Three impact radiuses (commit / iteration / maintainability)** | a framework should classify and route AI output by which radius a defect lives in; long-radius issues need different gates than short-radius ones.
- **Steering as the unit of work** | the developer's micro-corrections *are* the value-add; specs and orchestration should make steering cheap, structured, and capturable rather than ad-hoc.
- **Prompt fidelity decay over long sessions** | "the longer a coding session gets, the more hit-and-miss it becomes" — frameworks should bound context windows, checkpoint, and re-anchor against the spec.
- **Custom rules are necessary but insufficient** | rule sets help but LLMs may ignore them; a framework should treat rules as advisory and add deterministic verification (lint, tests, hooks).
- **Vertical slicing over broad sweeps** | spec-driven planning should explicitly force incremental working slices rather than mass transformations.
- **Root-cause over brute-force** | plans should require a hypothesis/diagnosis step before fix-application steps for non-trivial errors.
- **"Go-wrong" log** | a team ritual of logging AI-induced friction; a framework can institutionalize this as structured telemetry/learnings.
- **Shift-left review (pre-commit, IDE-integrated)** | a spec framework should bake review gates at the earliest possible step, not at PR time.
- **Culture/environment shapes tool effectiveness** (Dr. Cat Hicks credit) | a framework's adoption guidance must address org pressure and psychological safety, not only mechanics. [inference: the memo explicitly thanks Hicks for this framing]

## 6. Mechanisms / practices worth stealing

- **Impact-radius triage** | classify AI defects as commit/iteration/maintainability | tag each spec/task with the radius it most affects, and require heavier gates for radius (c).
- **Vertical-slice constraint in prompts** | force one end-to-end slice before broad work | a planner step that rejects "convert all" plans and requires a "first slice" deliverable.
- **Diagnose-before-fix step** | require explicit root-cause hypothesis | for any error-driven task, the framework inserts a "what is the actual cause?" step before allowing changes.
- **Test-quality gates beyond coverage** | watch for duplicated assertions and over-generation | a reviewer agent (or lint) that flags duplicate test logic and new tests redundant with existing ones.
- **Reuse-awareness pre-check** | scan codebase for existing components before generating new ones | inject a "have we already built this?" search step before code generation.
- **DX guardrails** | preserve one-command runs, hot reload, single build flow | a framework rule set that forbids multi-command splits or hot-reload regressions without explicit approval.
- **"Artisanal fallback" trigger** | explicit stop conditions that hand control back to the developer | session-bounded budgets (steps/tokens/iterations) that auto-pause with a summary.
- **"Go-wrong" log ritual** | weekly team review of AI-induced friction | framework persists structured failure cases as durable learnings used to update rules.
- **Quality monitoring tuned for AI risks** | weight code-duplication metrics higher | bake Sonarqube/Codescene-style gates into CI templates, with duplication-sensitivity raised.
- **Custom rules as living artifact** | treat the rule set as a versioned product the team iterates on | framework provides a rules registry with provenance back to the "Go-wrong" log.

## 7. Notable quotes

- "Even in those successful sessions, I intervened, corrected and steered all the time. And often I decided to not even commit the changes." (https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html)
- "LLMs frequently don't listen to the letter of the prompt. The longer a coding session gets, the more hit-and-miss it becomes."
- "The bigger the impact radius, the longer the feedback loop for a team to catch those issues."
- "Counterintuitively for less experienced programmers, more tests are not necessarily better."
- "By no stretch of my personal imagination will we have AI that writes 90% of our code autonomously in a year. Will it assist in writing 90% of the code? Maybe."
- "Stay cautious of 'good enough' solutions that were miraculously created in a very short amount of time, but introduce long-term maintenance costs."

## 8. Pages fetched (degree 0/1/2)

- Degree 0: https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html

## 9. Pages attempted but failed

- None.

## 10. Confidence

HIGH. The memo is short, self-contained, and was fetched in full; all claims and examples are quoted or paraphrased directly from the page. The only [inference] markers cover (a) authorship attribution (series byline not shown on the fetched page) and (b) the framing that "environment shapes tool effectiveness" is the lesson Fowler/Böckeler draws from the Hicks acknowledgment — the page credits Hicks but does not spell that interpretation out in those exact words.
