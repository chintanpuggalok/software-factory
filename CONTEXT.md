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
- A live five-stage plan passed with the current default model, and a live static build passed structural and browser checks. The run found and fixed verdict markup, revision retry, durable artifacts, history budget, and timeout defects. The coordinator does not deploy. See `artifacts/live-run-review.md`.
- Skills now use one audit verdict contract. Every stage skill names its audit and advances only on PASS. An audit removed three overlapping skills and merged their unique content into route, taste, and learn.
- Execution now goes through a selectable runtime adapter. `pi` and `opencode` are implemented. The OpenCode adapter isolates each call with a private server, an injected restricted agent, and disabled project config. Live runs verified a plain response, permitted file reads with tool activity on stderr, and a denied read under the deny-all agent. A rerun with a mismatched parent directory exposed a PWD location bug, now fixed and tested. Codex and Claude fail closed. See `docs/runtime-adapters.md`.
- A Pi extension provides `/factory` with subcommands: status, plan, build, simulate, resume, help. It also registers `/factory-status`. A skill named `factory` was renamed to `factory-entry` because Pi lets a skill shadow an extension command. Plan and build runs accept `--runtime=pi|opencode`, and plan mode passes the pi-plan arguments it once dropped. The CLI is optional. The extension and its seventeen core tests were exercised without model calls, including one real fail-closed spawn. It draws a bounded stage widget from coordinator progress lines.
- An independent static review with `opencode-go/deepseek-v4.1-flash` accepted the gate-plumbing findings now applied. The live verdict contract now passes with the current default model.
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
