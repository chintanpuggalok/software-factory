---
name: factory-architecture
description: Define technical architecture and scale targets. Use after product scope is clear and before material technical decisions.
---

# Define the architecture

1. Read the scope, relevant technical preferences, and affected systems. Record existing contracts and constraints.
2. Identify expected users, peak concurrency, traffic, data volume, growth, availability, and budget. Mark unknown values. Do not invent targets.
3. Model the domain, data ownership, state transitions, interfaces, and module boundaries. Identify invalid states and failure modes.
4. Compare at least two materially different designs when the decision is non-trivial. Assess complexity, scale, cost, security, operations, and recovery. Prefer the smallest design that meets the requirements.
5. Record the chosen design, alternatives, trade-offs, assumptions, limits, and evidence. State when the design must change.
6. Obtain agreement for consequential decisions that block progress. Do not treat an assumption as a user decision.

Do not install services or spend money. Send the output to `audit-architecture`. Advance only after `PASS: evidence`.
