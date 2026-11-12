---
name: factory-build
description: Implement an approved product plan. Use when authorized implementation work is ready.
---

# Build the change

1. Read the approved scope, plan, design brief, and applicable project rules.
2. Implement bounded changes. Add or update tests for changed behavior.
3. Use subagents only when delegation is authorized and provides a clear benefit. If your harness provides delegation guidance, follow it. Give each agent a bounded task, relevant context, and one spending ceiling. Do not cap the delegate's tool calls. Do not delegate secrets.
4. Run relevant checks. Record results and remaining risks. Preserve unrelated work.
5. Send the change to `audit-build`. Advance only after `PASS: evidence`. At each stage change, hand over the goal, confirmed decisions, artifact paths, open questions, and next action. Include check results. Load `factory-verify` or `factory-visual-review` only when that stage starts.

Do not install dependencies, spend, merge, or deploy without required approval. Do not claim unrun checks passed.
