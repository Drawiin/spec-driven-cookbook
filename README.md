# Spec-driven cookbook

<img width="4599" height="3121" alt="image" src="https://github.com/user-attachments/assets/26a29efb-d01e-4e6a-b234-b4ff305d1755" />

"Vibe coding" is dead—or at least, coding the way we used to is. We realized that blindly delegating thinking to AI agents is not a viable strategy if we want to build great things reliably and at scale. Reliable AI systems require the same rigor we apply to writing code. 

This project explores specification-driven patterns for designing, orchestrating, and scaling AI agents. It's about building applications with quality and scalability that are sustainable in the long run. More importantly, it's about building the applications that build these applications—tools that help developers work faster without sacrificing quality, allowing them to apply their experience and human judgment where it truly matters.

# Core philosophy

- **Orchestrators + specialized workers**
  - A single orchestrator per workflow, tailored to specific needs, with reusable workers plus workflow-specific ones.
  - Ephemeral workers run with fresh context, containing only the tools, CLIs, skills, and MCP needed for a single task. 

- **Self-healing**
  - AI agents make mistakes (SLOP)—it's inherent to statistics-based models. We design guardrails and auto-correction mechanisms to catch errors before humans intervene, reducing system entropy and enabling continuous sessions without interruption or token waste.

- **Humans are lazy**
  - People struggle to express what they want precisely. Agents should never blindly execute instructions; instead, ask for clarification, run dry scenarios, research first, and help craft plans before execution. This reduces miscommunication SLOP while keeping interaction fast enough to maintain engagement.

- **Context rot**
  - LLM performance degrades as context window fills. We define zones:
    - **0–40%**: Smart zone—good results, full context usable
    - **40–60%**: Warning zone—begin compacting and saving to persistent storage
    - **60–80%**: Danger zone—avoid except for research/planning agents; performance drops, SLOP increases
    - **80–100%**: Rot zone—auto-compact immediately
- **SPEC-driven design**
  - **RESEARCH**: Thorough understanding of the problem and solution space, including edge cases and failure modes
  - **SPEC**: Well-crafted specification
  - **PLAN**: Detailed plan to achieve the SPEC, usually divided into multiple TASKs (or inline for small work), with clear dependencies and expected outputs
    - Defines which agents to spawn, which artifacts to load, validations, and handoffs
  - **TASK**: Smallest unit of work with a dependency graph; can execute in parallel if independent, and can be retried on failure without affecting the rest of the plan


# Workers

Workers behave like black-box commands: invoke with context and input, receive a simple signal (`SUCCESS`/`FAILURE`) and a pointer to detailed output (usually markdown). This keeps workflows clean while providing rich information when needed.

Examples:
- Researchers (gather and analyze information)
- Planners (devise execution strategies)
- Validators (check correctness)
- Executors (implement changes)
- Debuggers (diagnose failures)
- Reviewers (assess quality)

# References
 - [GSD (Get Shit Done)](https://github.com/gsd-build/get-shit-done): Soft meta-framework, agnostic but text-heavy; our V1 inspiration
 - [GSD-2](https://github.com/gsd-build/gsd-2): Follow-up focused on building specialized agents with the Agents SDK
