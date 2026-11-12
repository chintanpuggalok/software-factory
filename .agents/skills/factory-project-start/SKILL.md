---
name: factory-project-start
description: Start or resume a product project for the factory. Use at the start of substantive product work or when planning begins in a new repository.
---

# Start the project

1. Find the project root and read applicable AGENTS.md files. Do not assume the current directory is the root.
2. Read CONTEXT.md, PLAN.md, decisions.md, and linked research or docs when present. Report stale or contradictory context. Do not invent a resolution.
3. If continuity files are missing and the work is substantive, create a short set:
   - AGENTS.md: project rules.
   - CONTEXT.md: confirmed requirements, constraints, current state, and open choices.
   - PLAN.md: one active milestone, next action, acceptance criteria, and blockers.
   - decisions.md: confirmed decisions and rationale.
   Add docs/, research/, artifacts/, or out/ only when the work needs them. Do not scaffold for a trivial task.
4. Separate confirmed facts, proposals, assumptions, and open decisions. Do not treat a proposal as approval.
5. Check that the location is writable before writing. Preserve existing work and conventions.
6. Hand the goal, confirmed decisions, artifact paths, open questions, and next action to `factory-route`.

Do not install dependencies, spend, delegate, or start expensive jobs because a plan mentions them.
