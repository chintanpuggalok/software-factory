---
name: factory-release
description: Prepare and verify a release. Use when implementation and reviews are ready for a production decision.
---

# Prepare the release

1. Summarize the change, test results, visual review, security evidence, known risks, and rollback path. Mark missing evidence.
2. Check the project's release and security requirements. Use `factory-security` to review relevant risks. Record its findings or a justified reason that the change does not cross a trust boundary.
3. Run `audit-release` before deployment. Record pending approvals. Resolve blocking findings.
4. Request authorization before merge, new external spend, or production deployment.
5. After authorization, perform the authorized release. Verify production health against the evidence defined by the project.
6. Run `audit-release` again after deployment. Record the outcome and useful lessons. If blocked, state the blocker and next action.

Production health evidence must include the deployed revision, a target-appropriate availability or correctness check, and error or log evidence over a stated period. Execute the rollback or prove it in a non-production environment. If the target cannot supply this evidence, report the gap.

Do not claim deployment or production health without evidence. Do not bypass a failed gate.
