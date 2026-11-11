# Context

## Confirmed
- Build a reusable software factory that takes Chintan's ideas to production quickly.
- Product specifications, features, and UI/UX quality matter. The factory should make authorized decisions without routine approval.
- Design taste is context-dependent. The baseline is minimalism and Apple-inspired design.
- Study up to three market leaders in the relevant segment. Use familiar flows as inspiration, adapted to the product.
- Use ASD-STE100 for factory instructions and artifacts. Formal compliance is not yet verified.
- Audit each stage before handoff with a stage-specific audit skill. Keep skills project-local until finalized.
- Define technical architecture and explicit scale targets before material technical decisions.
- Use subagents only when explicitly authorized and when they provide a clear net benefit. Develop durable technical and design taste memory.

## Current state
- Skill drafts are under `.agents/skills/`. Stage-specific audit skills replace the shared audit skill.
- The project-local `asd-ste100` skill is pinned to upstream commit `a4905d922500dd7530ca8a0eb9e4940494255709`. Its linter has not been executed.
- Pi lists the original stage skills after reload. Automatic routing and a product walkthrough remain untested.
- Added draft skills for routing, recovery, security, evaluation, and learning. See `research/starred-factories.md`.
- A user-wide preference index exists outside this repository. An isolated local Pi install discovered all 28 package skills. GitHub installation and cross-project preference loading remain untested.
- Existing skill approval instructions predate the autonomous goal and require review. The goal does not authorize new spending, installations, or delegation.

## Confirmed expansion
- Build an autonomous orchestration engine that can complete and improve projects.
- Run end to end without routine human approval. Stop when external configuration or access blocks progress.
- Use existing prepaid access. Do not add paid services or enable overage charges.
- Add task-specific playbook routing and engineering rigor inspired by pstack.

## Proposed approach
- Start with a local Pi orchestration loop. See `artifacts/orchestrator-proposal.md` and `artifacts/complete-idea-review.md`. The architecture needs user agreement.

## Open decisions
- Orchestration architecture, runtime, prepaid-only enforcement, delegation permissions, and deployment targets.
- Cross-project installation and preference discovery need validation. Confirm privacy and conflict behavior in other agent environments.
- Access to the applicable ASD-STE100 standard and controlled vocabulary, and a method to verify compliance.

See `PLAN.md`, `decisions.md`, and `research/factory-inspirations.md`.
