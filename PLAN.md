# Active milestone: draft and validate factory skills

## Goal
Create minimal, explicit skills for the product cycle and taste memory.

## Acceptance criteria
- Each stage has a clear trigger, inputs, steps, output, and boundary.
- User decisions and approval gates remain explicit.
- Taste records distinguish user decisions from agent hypotheses.
- Each stage has an audit with findings and a clear outcome.
- Skills use portable frontmatter and pass local structural checks.
- Factory instructions follow ASD-STE100, verified against the applicable standard.
- A real product walkthrough tests routing and handoffs before adoption.

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
- Live routing and product execution remain untested.
- The first review is in `artifacts/skill-review.md`. It predates the stage-specific audits.

## Next action
Review the proposed engine architecture with Chintan. Then test skill routing and handoffs on a bounded product idea.

## Blockers
The engine architecture, provider spending controls, delegation, and deployment targets remain open. Cross-project preference loading is untested. Access to the applicable ASD-STE100 standard and compliance verification are needed.
