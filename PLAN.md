# Active milestone: build and test the local coordinator

## Goal
Build a Pi-based coordinator with durable project-local state. Test an end-to-end run against a simulated release.

## Acceptance criteria
- State transitions, evidence, audit gates, and restart recovery are tested.
- A simulated product run reaches a simulated release. Failure cases do not advance.
- Real model calls remain blocked when prepaid-only enforcement cannot be verified.
- Existing skill and preference boundaries remain explicit.
- A real product walkthrough and formal ASD-STE100 compliance remain separate unverified gates.

## Completed
- Drafted stage skills, added selective-loading rules, and created a factory-local taste index.
- Added architecture and scale planning. Replaced the shared audit with stage-specific audit skills.
- Installed the approved STE skill locally at a pinned upstream commit. Its linter has not run.
- Integrated global startup, delegation, and autoresearch boundaries. Added separate release audits before and after deployment.
- Checked 21 skill frontmatters, local links, STE support files, and release gate order. See `artifacts/global-integration-review.md`.
- Reviewed starred repositories. Added draft routing, recovery, security, evaluation, and learning skills. See `research/starred-factories.md`.
- Added draft task playbooks, architecture guidance, and an autonomous-run skill inspired by pstack. These instructions are not an orchestration engine.
- Added a user-wide preference index, preference skill, and Pi package manifest. An isolated local Pi installation discovered 28 skills without diagnostics. GitHub installation and cross-project preference loading remain untested.
- Completed a self-review of the project. See `artifacts/end-to-end-review.md`.
- Implemented a local deterministic simulator, read-only Pi adapter, and MIT license. Nine tests pass. One real read-only Pi prompt returned the expected text. See `artifacts/coordinator-test.md`.
- Live routing and product execution remain untested.
- The first review is in `artifacts/skill-review.md`. It predates the stage-specific audits.

## Next action
Identify a provider-supported hard spending limit. Then implement stage execution and safe recovery for external effects.

## Blockers
The adapter cannot verify billing or enforce a dollar limit. Full stage execution and a real deployment target remain open. Cross-project preference loading is untested. Access to the applicable ASD-STE100 standard and compliance verification are needed.
