# Complete idea and stages: review draft

## Confirmed goal
Build an autonomous software factory. It takes a product idea through production and improves the project within its authorized scope. It runs without routine approval. It pauses for external access, configuration, or other genuine blockers. Use existing prepaid access only. Do not add paid services or enable overages.

## Proposed product cycle
1. Intake: capture the idea, outcome, limits, and release target.
2. Research and spec: investigate the market and users. Define scope and acceptance criteria. Mark unknowns.
3. Design: use context-relevant taste and study relevant market leaders. Choose familiar flows when they fit. Check accessibility and states.
4. Architecture: record users, traffic, concurrency, data, budget, availability, and recovery assumptions. Select a design that fits the evidence.
5. Plan: route the task to a playbook. Split work into bounded changes. Define tests and dependencies.
6. Build: implement changes and tests. Delegate only when authorized and beneficial.
7. Verify and audit: run tests and user scenarios. Inspect UI where applicable. Record failures and evidence. Repair and repeat.
8. Release: check release evidence and rollback. Deploy to the configured target within authorized scope. Check production health.
9. Learn: capture useful corrections and confirmed taste. Separate hypotheses from confirmed preferences. Improve skills or rules only within authorized scope.

The stage-specific audits check outputs. They do not by themselves guarantee independent review or correctness.

## Proposed engine
A Pi-based local coordinator reads the project state. It selects a playbook and starts a bounded stage. It records inputs, actions, evidence, status, and the next step. It advances after checks pass. It resumes after interruption. The exact Pi integration and state format are not approved.

## Proposed build milestones
1. Resolve architecture, runtime, and execution permissions. Define the prepaid-only control and its limits.
2. Build the local state and routing core. Test restart and failure handling.
3. Connect existing stage skills and audits. Test an idea-to-plan walkthrough.
4. Add bounded implementation and verification. Test on an isolated sample project.
5. Add a simulated release and recovery checks. Verify gate ordering and failure handling.
6. Enable a real release only when the target, access, rollback, and scope are configured. Run a product walkthrough.
7. Add memory and improvement loops. Measure quality, latency, and actual cost before adding more autonomy or parallelism.

These milestones are proposals, not an approved implementation plan.

## Review findings
- The current skills ask for approvals that conflict with the confirmed autonomy goal. Update them only as part of an agreed implementation plan.
- The repo README describes the current skills, not the target engine. Keep current status and intended direction separate.
- Prepaid-only operation needs provider-specific evidence. If the system cannot tell whether a call can incur overage, it must not claim a spending cap is enforced.
- An autonomous task can encounter destructive changes, third-party terms, secrets, or production failures. Project scope, release targets, recovery, and access controls must be defined.
- Model-generated self-review is not independent evidence. Use tests and independent scenarios where practical; label missing checks.
- Taste and product choices cannot always be inferred. Mark assumptions and use defaults only when the user has authorized that choice.
- A continuously improving system must not silently change permissions, budgets, evaluation rules, or goals.
- A single-threaded first version reduces coordination complexity but is a proposal, not proof of lower total cost.

## Status and decision
The architecture, state format, provider controls, and deployment targets are not yet approved. The current repo contains draft skills, not an orchestration engine. Next: review the product cycle and milestones with the user, then decide the architecture and boundaries.
