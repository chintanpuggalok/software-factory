# Autonomous orchestrator proposal

Status: proposed. The user has not approved the architecture.

## Goal
Run a project from an idea to a verified release. Improve the project within the authorized scope. Stop when access, external configuration, or another external blocker prevents progress.

## Proposed first version
- Use Pi as the local agent runtime.
- Keep project state, work items, decisions, and evidence in project-local files.
- Route each task to a playbook and its stage-specific skill.
- Run one bounded work item at a time. Run its audit and required checks before advancing.
- Resume from the last recorded state after a restart. Record failures and the next action.
- Use available prepaid access only. Do not add paid services or enable overage charges.
- Run without routine approval for actions inside the authorized project scope. Do not bypass tests, security controls, or external access requirements.
- Use subagents only with explicit authorization and a clear benefit. The user has not yet authorized delegation for this implementation.

## Not yet specified
- Pi integration method and process supervision.
- Provider quota visibility and enforcement.
- Exact release targets, credentials, and rollback requirements.
- How to distinguish authorized project improvements from scope expansion.
- Recovery, concurrency, and release safety rules.

## Validation
Use a local test project and simulated release target. Test routing, restart recovery, failure gates, and evidence before enabling real deployments.
