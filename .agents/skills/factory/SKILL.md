---
name: factory
description: Start or resume the software factory with one call. Use when the user gives a product goal, says "factory", or returns to continue earlier work.
---

# Run the factory

This is the single entry point. It creates or restores project state, then hands work to one stage skill.

1. Read `.factory/entry.json` and `.factory/pi-plan.json` when present. Read project continuity files.
2. Use the supplied goal. If no goal was supplied, restore the saved goal. Ask once only when neither exists.
3. Ensure continuity files exist. Follow `factory-project-start` when they are missing or stale.
4. Choose the next action:
   - No goal or no plan: start with `factory-idea` and continue through `factory-spec`, `factory-design`, `factory-architecture`, and `factory-plan`.
   - A blocked stage or interrupted run: use `factory-recover`.
   - Complete plan with no prototype evidence: use `factory-build`.
   - Prototype verified: report the state and propose the next improvement.
5. Write or update `.factory/entry.json` with the goal, phase, and update time. Keep it short. Do not store secrets.
6. Run the selected skill and its audit. Continue authorized work without a new prompt. Stop only for a real blocker or a consequential decision.
7. End with one short status: goal, phase, audit verdicts, and next action.

Do not start a new goal when a saved goal exists. Use `factory-route` when the correct stage is unclear. Do not treat a saved goal as permission to spend, install, delegate, merge, or deploy.
