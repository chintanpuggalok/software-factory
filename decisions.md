# Decisions

## Confirmed
- Build an autonomous software factory with engineering rigor and context-specific design taste.
- Use a local Pi-based coordinator with project-local state. The user approved this architecture.
- Use existing subscription access. The user states that it will not generate extra charges and permits a $1 hard limit if needed. Do not add paid services or enable overage charges. The adapter cannot enforce the $1 limit.
- Run end to end without routine approval within authorized scope. Stop for genuine blockers.
- Use subagents only when explicitly authorized and beneficial.
- Use MIT for original project material. The bundled STE skill retains its own license.
- Use ASD-STE100 for factory instructions and artifacts. Formal compliance remains unverified.
- Use stage-specific audits. Keep skills project-local until finalized. Define architecture and scale targets for product work.
- Use the local `danyuchn/asd-ste100-skill`.
- Keep user-wide preferences outside the repository. Keep project decisions local.

## Proposals, not approved
- Use independent acceptance scenarios and browser-based design review.
- Use bounded lower-cost agents where cost and permissions justify them.

## Open
- How to verify prepaid-only model usage with the configured provider.
- Which real product and deployment target to use for a production walkthrough.
