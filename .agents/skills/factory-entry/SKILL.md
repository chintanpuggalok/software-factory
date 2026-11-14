---
name: factory-entry
description: Single entry point to start, resume, route, or recover any factory task with one call.
---

# Run the factory

1. Find the project root. Read `AGENTS.md`, `CONTEXT.md`, `PLAN.md`, `decisions.md`, `.factory/entry.json`, and `.factory/pi-plan.json` when present.
2. Use the supplied goal. When the user supplies no goal, restore the saved goal. Ask once only when neither exists.
3. Record the goal, authorized scope, release target (defaulting to Cloudflare), constraints, and checkable completion criteria. For substantive work with missing continuity files, create short `AGENTS.md`, `CONTEXT.md`, `PLAN.md`, and `decisions.md` files.
4. When earlier state fails or interrupts a run, inspect durable state and in-flight effects first. Do not repeat unsafe external effects. Limit one stage to two attempts. Try another safe approach within scope when a check fails.
5. Size the route to task complexity:
   - Bounded bug, small feature, or refactor (1–2 files, clear scope): read the matching playbook in `references/`, then run `factory-build` and `factory-verify`.
   - New product or complex multi-component feature: run `factory-idea`, `factory-spec`, `factory-design`, `factory-architecture`, and `factory-plan`.
   - Ready plan or authorized change: run `factory-build`.
   - Pre-release evidence: run `factory-verify`, `factory-state-gate`, `untangle`, or `factory-release`.
6. Write `.factory/entry.json` with the goal, phase, and update time. Never store secrets.
7. Run the selected skill and its audit. Continue authorized work until the completion criteria pass. Run `factory-learn` after completion and end with one short status.

Do not start a new goal when a saved goal exists. Do not treat a saved goal as permission to spend, install, delegate, merge, or deploy.
