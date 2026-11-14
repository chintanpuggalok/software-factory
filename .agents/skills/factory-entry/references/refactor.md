# Refactor playbook

1. Define the behavior that must stay unchanged. Record a baseline.
2. Add characterization tests or an equivalence check when practical. A clean build alone does not prove equivalent behavior.
3. Define the target structure. Remove excess complexity within scope. Do not add speculative abstractions.
4. Change the structure in small steps. Run behavior checks after each step.
5. Check the result on the affected surface. Report gaps and intentional changes.
6. Send the change to `audit-build` and `audit-verify`. Advance only after `PASS: evidence`.
