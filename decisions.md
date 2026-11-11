# Decisions

## Confirmed
- The factory project is `/home/chint/projects/software_factory`.
- Begin with minimal skills for the product cycle. Use ASD-STE100 for factory instructions and artifacts.
- Audit each stage with a separate skill. Keep skills project-local until finalized.
- Use `danyuchn/asd-ste100-skill` locally. Define architecture and scale targets for each app.
- Use subagents only when they provide a clear benefit and delegation is authorized.
- Chintan values high-quality UI and UX.
- The factory should run end to end without routine approval. It should stop for external blockers.
- Use existing prepaid access. Do not add paid services or enable overage charges.

## Proposals, not approved
- Use independent acceptance scenarios and browser-based design review.
- Use bounded lower-cost agents where the cost and permissions justify them.
- Keep user-wide taste separate from project-specific decisions.
- Use the local Pi orchestration architecture in `artifacts/orchestrator-proposal.md`. Architecture approval is pending.
