---
name: factory-build
description: Implement an approved product plan. Use when authorized implementation work is ready.
---

# Build the change

1. Read the approved scope, plan, architecture, design brief, and project rules.
2. Apply low-level principles: pure core domain logic, imperative I/O shell at module edges, guard clauses for flat control flow, strict boundary types, and structured errors. Never swallow errors silently.
3. For Cloudflare projects, load `workers-best-practices`, `cloudflare-app-bootstrap`, and `workers-development`. Use the `cf` CLI unless the project has a Wrangler config file (`wrangler.jsonc`, `wrangler.json`, or `wrangler.toml`).
4. When the user authorizes delegation and parallel work helps, delegate bounded Cloudflare service, UI, or test tasks to subagents with one spending ceiling per task. Never delegate secrets.
5. Add or update behavior tests at module boundaries. Run relevant checks and preserve unrelated work.
6. Send the change to `audit-build`. Advance only after `PASS: evidence`. Pass `factory-verify` the goal, decisions, artifact paths, check results, and next action.

Do not install dependencies, spend, merge, or deploy without authorization. Do not claim unrun checks passed.
