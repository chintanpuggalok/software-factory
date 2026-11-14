# Bug playbook

1. Reproduce the reported failure on the affected surface. Record the result. Mark an inconclusive reproduction as unverified.
2. Rank up to three root-cause hypotheses with the cheapest falsifying check for each. Run those checks before editing code.
3. Add a failing regression test when practical. Otherwise record why and define another check.
4. Apply the smallest fix that the evidence supports. Revert any failed fix before trying the next hypothesis. Never stack unverified fixes.
5. Rerun the reproduction and affected checks. Report the cause, change, and results. Send the change to `audit-build`, then `audit-verify` when behavior changed. Advance only after `PASS: evidence`.
