# Active milestone: build and test the local coordinator

## Goal
Build a Pi-based coordinator with durable project-local state. Test an end-to-end run against a simulated release.

## Acceptance criteria
- State transitions, evidence, audit gates, and restart recovery are tested.
- A simulated product run reaches a simulated release. Failure cases do not advance.
- Model calls require explicit subscription attestation. Report that billing and usage limits are not enforced.
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
- Implemented a local simulator, Pi adapter, no-tools planning loop, bounded Wikipedia search, and MIT license. Eighteen tests pass. A real sample passed five model-audited planning stages. See `artifacts/pi-planning-smoke.md`.
- The calculator test passed planning and generated a static prototype. Fake-DOM and isolated Chromium checks passed after manual contrast fixes. The generator is now available through `--build-static`. See `artifacts/calculator-test/review.md`.
- Strengthened continuation and recovery instructions after an early stop. Three static instruction checks pass. Live agent behavior is not yet validated.
- Added limited static checks, one repair attempt, and pending-record recovery. Tests include a real process interruption. See `artifacts/static-verification-review.md`.
- Added optional isolated Chromium checks, one browser-repair attempt, and a bounded acceptance contract. An integrated calculator run passed 13 acceptance actions. See `artifacts/browser-acceptance-review.md`.
- Applied the accepted findings from an independent static review. Every stage skill now names its audit, all ten audits share one verdict contract, release requires security evidence, artifact paths are defined, routing covers resume and all stages, and playbooks name their audits. See `artifacts/deepseek-skill-review.md`.
- Added a runtime adapter layer. `pi` and `opencode` are implemented. `codex` and `claude` fail closed until implemented. Planning, static build, and browser repair all reuse the selected adapter, and the static build refuses a saved plan from a different runtime. 82 Python tests and 12 extension tests pass. See `artifacts/opencode-adapter-review.md`.
- Audited each skill for need and usage. Removed three overlapping skills: `factory-autonomous`, `factory-preferences`, and `factory-eval`. Their unique content moved to `factory-route`, `factory-taste`, and `factory-learn`.
- Added `factory-project-start` so the package does not depend on a global startup skill. An isolated Pi install now discovers 27 skills with no diagnostics. See `artifacts/skill-necessity-audit.md`.
- Added a Pi extension so the factory runs from `/factory-*` commands without a CLI. Twelve Node tests pass. The extension draws a live stage widget above the prompt and `/factory` creates or restores state. The extension ran `/factory-status` and `/factory-simulate` in Pi print mode. A plan without `--yes` refused before any model call.
- Live five-stage planning and a static build passed with the current default model. Fixes: strict verdict parsing, one `REVISE` regeneration, durable `docs/factory/<stage>.md` artifacts, newest-first history budget, and longer output and timeout limits. 91 Python and 12 extension tests pass. See `artifacts/live-run-review.md`.
- The first review is in `artifacts/skill-review.md`. It predates the stage-specific audits.

## Next action
Repeat the planner probe (deny-all agent, tempting file-read prompt) when the OpenCode free quota resets or another provider is connected, and observe the refusal output. Then define a deployment target and release contract.

## Blockers
The OpenCode adapter has insufficient provider balance, so it is unproven for real calls. Full product correctness, checklist acceptance, and screen-reader behavior remain unverified. Static snippets do not verify market-share rankings. No dollar cap is enforced; the user accepts overages. Recovery for external effects and a real deployment target remain open. Cross-project preference loading is untested. Access to the applicable ASD-STE100 standard and compliance verification are needed.
