# Context

## Confirmed
- Build a reusable software factory that takes Chintan's ideas to production quickly.
- Chintan decides product specifications and features. UI and UX quality matter.
- Design taste is context-dependent. The baseline is minimalism and Apple-inspired design.
- Study up to three market leaders in the relevant segment. Use familiar flows as inspiration, adapted to the product.
- Use ASD-STE100 for factory instructions and artifacts. Formal compliance is not yet verified.
- Audit each stage before handoff with a stage-specific audit skill. Keep skills project-local until finalized.
- Define technical architecture and explicit scale targets before material technical decisions.
- Use subagents only when explicitly authorized and when they provide a clear net benefit. Develop durable technical and design taste memory.

## Current state
- Skill drafts are under `.agents/skills/`. Stage-specific audit skills replace the shared audit skill.
- The project-local `asd-ste100` skill is pinned to upstream commit `a4905d922500dd7530ca8a0eb9e4940494255709`. Its linter has not been executed.
- Skills have not been tested in Pi or on a product.
- Skills are proposals, not approval to install tools, delegate, spend, merge, or deploy.

## Open decisions
- Spending limits, provider/model selection, delegation permissions, and deployment gates.
- Shared taste storage across projects and privacy boundaries.
- Access to the applicable ASD-STE100 standard and controlled vocabulary, and a method to verify compliance.

See `PLAN.md`, `decisions.md`, and `research/factory-inspirations.md`.
