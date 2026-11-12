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
- Added a runtime adapter layer. `pi` and `opencode` are implemented. `codex` and `claude` fail closed until implemented. Planning, static build, and browser repair all reuse the selected adapter, and the static build refuses a saved plan from a different runtime. Live probes verified a plain response, permitted file reads with tool activity on stderr, and a denied read under the deny-all agent; a mismatched parent directory exposed a PWD location bug, now fixed and tested. See `artifacts/opencode-adapter-review.md`.
- Audited each skill for need and usage. Removed three overlapping skills: `factory-autonomous`, `factory-preferences`, and `factory-eval`. Their unique content moved to `factory-route`, `factory-taste`, and `factory-learn`.
- Added `factory-project-start` so the package does not depend on a global startup skill. An isolated Pi install now discovers 27 skills with no diagnostics. See `artifacts/skill-necessity-audit.md`.
- Added a Pi extension so the factory runs from `/factory-*` commands without a CLI. Twelve Node tests pass. The extension draws a live stage widget above the prompt. `/factory` takes subcommands (status, plan, build, simulate, resume, help); the entry skill was renamed to `factory-entry` because skills shadow extension commands. The extension ran `/factory-status` and `/factory-simulate` in Pi print mode. A plan without `--yes` refused before any model call.
- The extension now passes `--runtime` through on plan and build runs, validates it against the implemented set, and shows the selection in the widget. The fix also restored plan mode: `/factory plan` had been running the deterministic simulator while promising model calls. 17 extension tests and 92 Python tests pass. See `artifacts/extension-runtime-passthrough.md`.
- Live five-stage planning and a static build passed with the current default model. Fixes: strict verdict parsing, one `REVISE` regeneration, durable `docs/factory/<stage>.md` artifacts, newest-first history budget, and longer output and timeout limits. 92 Python and 14 extension tests pass. See `artifacts/live-run-review.md`.
- The first review is in `artifacts/skill-review.md`. It predates the stage-specific audits.

## Next action
Define a deployment target and release contract, then decide the metering design for autonomous runs.

## Blockers
The OpenCode free usage limit is per provider and both free pools ran dry at times; the adapter is proven for real calls on `opencode-go/longcat-2.5-free`. Full product correctness, checklist acceptance, and screen-reader behavior remain unverified. Static snippets do not verify market-share rankings. No dollar cap is enforced; the user accepts overages. Recovery for external effects and a real deployment target remain open. Cross-project preference loading is untested. Access to the applicable ASD-STE100 standard and compliance verification are needed.
