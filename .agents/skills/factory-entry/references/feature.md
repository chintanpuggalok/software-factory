# Feature playbook

1. Read the affected code and acceptance criteria. Identify the users and flows.
2. Define the data model, interfaces, and module boundaries before a non-trivial change. Compare feasible options.
3. Split work into bounded changes. Identify shared state and dependencies. Delegate only with user authorization and clear benefit.
4. Implement the smallest useful change. Add tests for expected behavior and key failures.
5. Check the feature on the affected surface. Record results and gaps.
6. Send the change to `audit-build` and `audit-verify`. Advance only after `PASS: evidence`.
