# Refactor playbook

1. Define the behavior that must remain unchanged. Record a baseline.
2. Add characterization tests or an equivalence check when practical. A successful build alone is not proof of equivalent behavior.
3. Define the target structure. Remove unnecessary complexity within scope. Do not add speculative abstractions.
4. Change the structure in small steps. Run the behavior checks after each relevant step.
5. Verify the result on the affected surface. Report behavior gaps and any intentional changes.
