---
name: factory-plan
description: Plan a bounded product implementation. Use after scope is defined or when a complex change needs an implementation plan.
---

# Plan the work

1. Read the approved spec, architecture and scale targets, applicable project rules, and design brief when needed. Load only technical context needed for this plan.
2. Split the work into the smallest useful release and bounded changes. Identify dependencies and risks.
3. Define verification, independent acceptance scenarios, and the evidence needed to ship.
4. Mark consequential decisions that need authorization. Set one spending ceiling per delegated task. Do not cap the delegate's tool calls. Propose cheap delegation only for bounded work with clear permissions.
5. Record the plan and next action. Obtain authorization for new paid dependencies, schema or API breaks, spend above the approved limit, or workflow changes.

Complete the plan before implementation. Send the output to `audit-plan`. Advance only after `PASS: evidence`. At the stage change, hand `factory-build` the goal, confirmed decisions, artifact paths, open questions, and next action. Continue into authorized implementation without waiting for a new prompt.
