---
name: audit-build
description: Audit implementation before verification. Use when a build change is ready for review.
---

# Audit the build

Read the actual diff, approved scope, and raw test output. Do not trust prose claims without file or command evidence. Check scope, pure-core boundary separation, error handling, security risks, tests, and unresolved defects. Cite evidence for findings. Report `PASS: evidence`, `REVISE: findings`, or `BLOCKED: reason`. State the next action. Record the verdict with the stage output. Do not claim independent review when the author performs the audit.
