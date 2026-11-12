# Factory project rules

- Follow global project startup rules before factory work. Do not repeat startup at each stage.
- Use the project-local `asd-ste100` skill in strict mode for factory instructions and artifacts. Preserve meaning and requirements. Do not claim compliance without the official standard and dictionary.
- Route tasks with `factory-route`. Use one factory skill for the active stage. Load the matching stage audit skill when the output is ready. Load other skills only when their specific task is needed.
- Audit every stage before handoff. Fix issues within authorized scope. Recheck fixes. Do not advance when the audit reports blocked.
- Continue authorized work through implementation, verification, review, and handoff. A milestone or progress report is not a stop condition.
- Make reversible choices within scope. Record assumptions. Do not ask the user to say continue.
- Before stopping, identify the unfinished acceptance criterion and the next action. Check available tools and try safe alternatives within scope. Fix and recheck failures when possible.
- Stop only when completion needs unavailable external access, required authorization, a consequential user decision, or an unresolved external or tool blocker. State what was tried, the blocker, and the smallest input needed. Never bypass safety gates or expand scope.
- Read project context and linked records selectively. Stop when the active task has enough information.
- At stage changes, pass the goal, confirmed decisions, relevant artifact paths, open questions, and next action. Include verification evidence when relevant. Do not pass the full conversation.
- Keep current decisions concise. Link to historical evidence instead of copying it into entry points.
- Use `factory-recover` after interruption or failure. Use `factory-eval` to test changed skills. Use `factory-learn` after completed work or repeated failure.
- Treat taste hypotheses as unconfirmed. Do not assume permission to spend, install, delegate, merge, or deploy.
- Use subagents only with authorization and when a specific benefit exceeds the cost and coordination overhead. Otherwise work directly. Follow the global `pi-subagents` skill when delegating.
- Use autoresearch only when the user requests an experiment loop. Follow the global autoresearch skill and all approval gates.
