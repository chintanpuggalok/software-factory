# Factory project rules

- Start substantive work with `factory-project-start`. Do not repeat startup at each stage. The package is self-contained for startup, routing, stage work, audits, and writing. Optional external delegation or autoresearch guidance is not required.
- Use the project-local `asd-ste100` skill for factory instructions and artifacts. Apply the structural rules. Treat dictionary-dependent rules as required only when the official standard is available. Preserve meaning and requirements. Do not claim compliance without the official standard and dictionary.
- Start or resume with `factory`. It creates or restores state, then delegates. Use `factory-route` when the next step is unclear. Use one factory skill for the active stage. Load the matching stage audit skill when the output is ready. Load other skills only when their specific task is needed.
- Audit every stage before handoff. Use `PASS: evidence`, `REVISE: findings`, or `BLOCKED: reason`. Advance only on PASS. Fix issues within authorized scope and rerun the audit. Preserve the verdict and evidence.
- Keep artifacts under the product project. Default locations are `docs/factory/spec.md`, `docs/factory/design.md`, `docs/factory/architecture.md`, and `docs/factory/plan.md`. Store run state in `.factory/state.json` and each audit verdict beside the artifact it checks. If the project has its own convention, reuse it and state which path you used.
- Continue authorized work through implementation, verification, review, and handoff. A milestone or progress report is not a stop condition.
- Make reversible choices within scope. Record assumptions. Do not ask the user to say continue.
- Before stopping, identify the unfinished acceptance criterion and the next action. Check available tools and try safe alternatives within scope. Fix and recheck failures when possible.
- Stop only for unavailable external access, required authorization, a consequential user decision, or an unresolved external or tool blocker. State what you tried, the blocker, and the smallest input needed. Never bypass safety gates or expand scope.
- Read project context and linked records selectively. Stop when the active task has enough information.
- At stage changes, pass the goal, confirmed decisions, relevant artifact paths, open questions, and next action. Include verification evidence when relevant. Do not pass the full conversation.
- Keep current decisions concise. Link to historical evidence instead of copying it into entry points.
- Use `factory-recover` after interruption or failure. Use `factory-learn` after completed work, repeated failure, or a workflow change. It includes the bounded evaluation method.
- Treat taste hypotheses as unconfirmed. Do not assume permission to spend, install, delegate, merge, or deploy.
- Use subagents only with authorization and when a specific benefit exceeds the cost and coordination overhead. Otherwise work directly. Follow your harness's delegation rules when available. When delegating, set one spending ceiling per task and do not cap the delegate's tool calls.
- Use experiment loops only when the user requests one. Follow your harness's rules when available.
