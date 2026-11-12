# Bug playbook

1. Reproduce the reported failure on the affected surface. Record the result.
2. Form possible causes. Use evidence to eliminate causes. Confirm the root cause when possible.
3. Add a failing regression test when practical. If not, record why and define another check.
4. Make the smallest fix supported by evidence. Re-run the original reproduction and affected checks.
5. Report the cause, change, and results. Send the change to `audit-build`, then `audit-verify` when behavior changed. Advance only after `PASS: evidence`. Hand over the goal, decisions, artifact paths, evidence, and next action.

Mark an inconclusive reproduction as unverified.
