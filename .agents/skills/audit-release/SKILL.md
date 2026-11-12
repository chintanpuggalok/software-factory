---
name: audit-release
description: Audit release readiness and production evidence. Use before a release decision and after deployment.
---

# Audit the release

Before deployment, read the release summary and evidence. Check test results, security and privacy evidence or a justified not-applicable record, risks, rollback, and required approvals. Record approvals that are still pending. A pass means the release is ready for an approval decision, not that deployment is approved. Do not require production health evidence before deployment.

After deployment, audit production health and the release outcome. Mark missing evidence.

For each audit, cite evidence for findings. Report `PASS: evidence`, `REVISE: findings`, or `BLOCKED: reason`. State the next action. Record the verdict with the stage output. Do not claim independent review when the author performs the audit.
