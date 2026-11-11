---
name: factory-release
description: Prepare and verify a release. Use when implementation and reviews are ready for a production decision.
---

# Prepare the release

1. Summarize the change, test results, visual review, known risks, and rollback path. Mark missing evidence.
2. Check the project's release and security requirements.
3. Run `audit-release` before deployment. Record pending approvals. Resolve blocking findings.
4. Request required approval before merge, external spend, or production deployment.
5. After approval, perform the authorized release. Verify production health and report the evidence.
6. Run `audit-release` again after deployment. Record the outcome and useful lessons. If blocked, state the blocker and next action.

Do not claim deployment or production health without evidence. Do not bypass a failed gate.
