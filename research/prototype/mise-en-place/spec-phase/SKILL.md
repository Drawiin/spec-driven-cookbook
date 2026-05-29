---
name: spec-phase
description: "Structured deep-questioning flow → .planning/SPEC.md → explicit approval gate"
---

<cursor_skill_adapter>
## A. Skill Invocation
- This skill is invoked when the user mentions `spec-phase` or describes starting a new project spec.
- Treat all user text after the skill mention as `{{GSD_ARGS}}`.
- If no arguments are present, treat `{{GSD_ARGS}}` as empty.

## B. User Prompting
When the workflow needs user input, prompt the user conversationally:
- Present options as a numbered list in your response text
- Ask the user to reply with their choice
- For multi-select, ask for comma-separated numbers

## C. Tool Usage
Use these Cursor tools when executing GSD workflows:
- `Shell` for running commands (terminal operations)
- `StrReplace` for editing existing files
- `Read`, `Write`, `Glob`, `Grep`, `Task`, `WebSearch`, `WebFetch`, `TodoWrite` as needed

## D. Subagent Spawning
When the workflow needs to spawn a subagent:
- Use `Task(subagent_type="generalPurpose", ...)`
- Do NOT pass the `model` parameter — use the Cursor default model
</cursor_skill_adapter>

<objective>
Take a developer from any starting point — empty or existing repo — to an explicitly approved SPEC.md, using a structured Q&A that covers five mandatory categories, supports optional research sub-tasks, and enforces an in-flow approval gate before planning can begin. Brownfield repos run detection and codebase mapping before Q&A.
</objective>

<process>

## Step 1: Startup

Per D-09, PROJ-01, SPEC-05 — all context comes from local files; no session history is assumed.

1. Run scaffolding:

```shell
python3 mise-en-place/tool-planning-scaffold/planning_scaffold.py scaffold
```

This creates `.planning/`, `.planning/phases/`, and `.planning/codebase/` idempotently. Note: `planning_scaffold.py` does **not** create `.planning/research/` (`PLANNING_DIRS` omits it).

2. Create the research output directory:

```shell
mkdir -p .planning/research
```

3. Read `.planning/SPEC.md` if it exists. If found, present its `status` value and ask:

> An existing spec was found (status: \<status\>). What would you like to do?
> (1) Continue editing from the last completed section
> (2) Start fresh — discard and restart
> (3) Abort

- **(3) Abort:** stop immediately.
- **(1) Continue:** resume Q&A from the first incomplete category.
- **(2) Start fresh:** overwrite with a new session.

### Step 1.4: Brownfield Detection (runs after scaffold, before Step 2 Q&A)

Runs on **every** Step 1 branch (Start fresh, Continue with existing SPEC.md) before Step 2 opens.

**Continue path policies:**
- **Continue** on a brownfield repo with a **greenfield-format** SPEC (no `project_type: brownfield`, no `## Already Built` / `## To Build`): re-run Step 1.4 detection and mapping before Q&A — do not skip to Step 2.
- **Continue** on a brownfield repo with an **existing brownfield-format** SPEC: still run detection; if the map is stale (`codebase_map_commit` in SPEC frontmatter ≠ `git rev-parse HEAD` when git is available) or **partial** (fewer than seven canonical files each with >20 lines), re-run `map-codebase` before Q&A.

**Procedure:**

```shell
python3 mise-en-place/tool-detect-brownfield/detect_brownfield.py
```

1. Parse JSON from stdout. If stdout is not valid JSON: print `ERROR: detect_brownfield returned invalid JSON` to stderr; **STOP** — do not proceed to Step 2 Q&A.
2. If `is_brownfield` is false → skip mapping; continue to Step 2 greenfield Q&A.
3. If `is_brownfield` is true:
   - Set internal brownfield mode and `project_type: brownfield` intent immediately (not deferred to Step 4).
   - **Completeness check:** Canonical files: `STACK.md`, `ARCHITECTURE.md`, `CONVENTIONS.md`, `STRUCTURE.md`, `TESTING.md`, `INTEGRATIONS.md`, `CONCERNS.md`. Map is complete only when all seven exist and each has >20 lines.
   - If `needs_codebase_map` is true **or** map is incomplete (including stub `STACK.md` when `has_codebase_map` is true): execute `map-codebase/SKILL.md` workflow. Do not trust `has_codebase_map` JSON alone.
   - If map exists and appears complete: offer `map-codebase` check_existing Refresh / Update / Skip; on Skip verify `codebase_map_commit` matches HEAD or warn stale.
   - After mapping, re-verify completeness; if still incomplete, fail with retry per `map-codebase` — do not open Q&A.
   - Read one-line summaries from all seven map files (summaries only — do not dump full contents).
   - Present 3–5 bullets of detected capabilities; **require** user confirm/correct — mandatory gate before Q&A.
   - Continue to Step 2 with brownfield mode active.

All inputs from local files and tool stdout only (SPEC-05 clean context).

## Step 2: Q&A Flow — Five-Category Spine

Per D-01, D-02, SPEC-01 — always cover all five categories in this exact order:

1. **Problem**
2. **Who it's for**
3. **Constraints**
4. **Success Criteria**
5. **Out-of-scope**

For each category: open with a focused starting question. After each answer, evaluate whether it is specific enough to write a concrete spec section (specific = names facts, conditions, or numbers; vague = abstract generalities or "it depends").

- If vague and fewer than **3 turns** used in this category: ask one targeted follow-up probe.
- Advance when: (a) **3 turns** are spent in this category, OR (b) the answer is specific enough — the agent decides, not the user (per D-02).

**Inline research trigger (D-03b):** at any point during Q&A, if the user says "research X" or asks to look something up, immediately execute Step 3 for that topic, then resume Q&A from where it left off.

**Brownfield mode (when Step 1.4 set brownfield flag):**
- Same five-category order preserved.
- Do **not** re-ask stack, directory structure, conventions, testing approach, integrations, or concerns already covered in the seven map summaries preloaded in Step 1.4.
- **Problem** and **Success Criteria** focus on **delta** — new work only, not inventory of existing code.
- Success Criteria must reference **To Build** items only; do not mix built capabilities into new requirements.
- Tag Already Built items during confirmation: `[observed]`, `[inferred]`, or `[unverified]` as appropriate.

## Step 3: Research Sub-Tasks

Per D-03, D-04, D-05, SPEC-03 — two trigger modes, handled identically once triggered:

- **(a) User-requested:** user says "research \<topic\>" at any point during Q&A.
- **(b) Agent-suggested:** at the end of Q&A, if knowledge gaps were detected, present a numbered list of proposed research topics; ask the user to accept or skip each individually.

Before spawning any sub-agent, ensure `.planning/research/` exists (`mkdir -p .planning/research` if Step 1 was skipped).

For each accepted research topic, use the **Task tool** to spawn a `generalPurpose` sub-agent. **Do NOT pass the `model` parameter** — use the Cursor default model.

Sub-agent prompt must include:

- **Topic:** \<the research topic\>
- **Project context:** \<1–2 sentence summary from Q&A answers so far\>
- **Output file:** `.planning/research/RESEARCH-<topic-slug>.md` where topic-slug is lowercased and hyphen-separated (e.g. `stripe-pricing-model`)
- **Path override note (D-04):** CONTEXT.md D-04 originally specified a phase-specific path for research output. That path is non-portable when this skill is replicated to new projects. This skill uses `.planning/research/` instead — portable across all projects.
- **File format:**
  - `# Research: <topic>`
  - `## Summary` — 2–3 sentence executive summary
  - `## Key Findings` — bullets
  - `## Implications for Spec` — how findings shape constraints or success criteria
  - `## Sources` — URLs or descriptions
- **Instruction:** "Keep the file concise — the spec author will read this before writing the final spec."

After each sub-agent completes: Read `.planning/research/RESEARCH-<topic-slug>.md` and note key findings for incorporation into SPEC.md. Multiple research sub-tasks may run; each produces its own file. All are read before the spec is finalized.

## Step 4: SPEC.md Assembly

Per D-06, D-07, SPEC-02 — merge all Q&A answers and research findings. Use the Write tool to create `.planning/SPEC.md`:

**Front-matter** (delimited by `---` markers):

```yaml
---
status: draft
version: 1
date: YYYY-MM-DD
project_type: greenfield   # or brownfield when Step 1.4 set brownfield mode
codebase_map_commit: <git rev-parse HEAD when git available; omit if not a repo>
---
```

**Document body (greenfield):**

```markdown
# Spec: <project name from Q&A>

## Problem

## Who It's For

## Constraints

## Success Criteria

## Out of Scope
```

**Document body (brownfield)** — order matters for `validate_spec.py`:

```markdown
# Spec: <project name from Q&A>

## Already Built

## To Build

## Problem

## Who It's For

## Constraints

## Success Criteria

## Out of Scope
```

Section headers must match `validate_spec.py` `REQUIRED_SECTIONS` and `BROWNFIELD_SECTIONS` exactly (case-sensitive). Q&A category names use conversational casing ("Who it's for", "Out-of-scope") but the written SPEC.md headers must use the canonical forms above.

Each section contains concrete answers from Q&A, enriched with research findings where relevant.

**Brownfield assembly rules:**
- `## Already Built` — validated capabilities from map + user confirmation (with confidence tags).
- `## To Build` — active requirements only; every item must be a gap not already in Already Built.
- `validate_spec.py` dedup gate rejects identical bullets in both brownfield sections at Step 5 approval.

## Step 5: Approval Gate

Per D-08, D-09, SPEC-04 — present the full contents of `.planning/SPEC.md` to the developer.

Ask: **"Approve this spec? Reply with: yes / edit / abort"**

- **yes:** If `status: draft` is present in front-matter, use StrReplace on `.planning/SPEC.md` with `old_string: "status: draft"` and `new_string: "status: approved"`. If already `status: approved` (idempotent): skip the patch. Confirm: "Spec approved ✓ — run /plan-phase to begin planning." Remind: "The plan-phase will verify approval via `python3 mise-en-place/tool-validate-spec/validate_spec.py` before proceeding."
- **edit:** Ask "Which section would you like to revise? (Problem / Who it's for / Constraints / Success Criteria / Out-of-scope / Already Built / To Build)". Return to Q&A for that category. Re-assemble and re-present SPEC.md. Re-prompt approval.
- **abort:** leave status as draft. Confirm: "Spec saved as draft in `.planning/SPEC.md` — resume with /spec-phase." Exit.

</process>
