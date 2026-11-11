---
name: factory-build
description: Implement an approved product plan. Use when authorized implementation work is ready.
---

# Build the change

1. Read the approved scope, plan, design brief, and applicable project rules.
2. Implement bounded changes. Add or update tests for changed behavior.
3. Use subagents only when delegation is authorized and provides a clear benefit. Follow the global `pi-subagents` skill. Give each agent a bounded task and relevant context. Set a spending budget when required. Do not impose a hard tool budget or tight usage budget on agents that can edit files. Do not delegate secrets.
4. Run relevant checks. Record results and remaining risks. Preserve unrelated work.
5. At each stage change, hand over the goal, confirmed decisions, artifact paths, open questions, and next action. Include check results. Load `factory-verify` or `factory-visual-review` only when that stage starts.

Do not install dependencies, spend, merge, or deploy without required approval. Do not claim unrun checks passed.
