# Feature playbook

1. Read the affected code and the acceptance criteria. Identify the users and relevant flows.
2. Define the data model, interfaces, and module boundaries before a non-trivial change. Compare feasible alternatives.
3. Split work into bounded changes. Identify shared state and dependencies. Delegate only when authorized and beneficial.
4. Implement the smallest useful change. Add tests for the expected behavior and important failures.
5. Verify the feature on the affected surface. Record the results and any gaps.
6. Send the change to `audit-build` and `audit-verify`. Advance only after `PASS: evidence`. Hand over the goal, decisions, artifact paths, evidence, and next action.
