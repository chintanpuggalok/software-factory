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
- A user-wide preference index exists outside this repository. An isolated local Pi install discovered all 27 package skills. GitHub installation and cross-project preference loading remain untested.
- An experimental workflow can plan and generate one static HTML prototype. A calculator test passed model-audited planning, fake-DOM checks, and selected isolated Chromium checks. Browser checks found contrast defects that were repaired manually. The coordinator does not deploy.
- Skills now use one audit verdict contract. Every stage skill names its audit and advances only on PASS. An audit removed three overlapping skills and merged their unique content into route, taste, and learn.
- Execution now goes through a selectable runtime adapter. Only `pi` is implemented. Codex and Claude fail closed. See `docs/runtime-adapters.md`.
- A Pi extension provides `/factory-status`, `/factory-simulate`, `/factory-plan`, `/factory-build`, and `/factory-resume`. The CLI is optional. The extension and its ten core tests were exercised without model calls. It draws a bounded stage widget from coordinator progress lines.
- An independent static review with `opencode-go/deepseek-v4.1-flash` accepted the gate-plumbing findings now applied. A live model smoke test of the new verdict contract was blocked by a provider usage limit.
- Existing skill approval instructions predate the autonomous goal and require review. The goal does not authorize new spending, installations, or delegation.

## Confirmed expansion
- Build an autonomous orchestration engine that can complete and improve projects.
- Run end to end without routine human approval. Continue after milestones. Stop only for a genuine blocker or required decision.
- Use the existing subscription. The user accepts overage charges. Do not add paid services without authorization.
- Add task-specific playbook routing and engineering rigor inspired by pstack.

## Proposed approach
- The user approved a local Pi-based coordinator and accepts subscription overages. The adapter cannot verify billing or enforce a dollar limit. External-effect recovery remains unimplemented. See `artifacts/pi-planning-smoke.md`.

## Open decisions
- The detailed orchestration design, usage metering, delegation permissions, and deployment targets.
- Cross-project installation and preference discovery need validation. Confirm privacy and conflict behavior in other agent environments.
- Access to the applicable ASD-STE100 standard and controlled vocabulary, and a method to verify compliance.

See `PLAN.md`, `decisions.md`, and `research/factory-inspirations.md`.
