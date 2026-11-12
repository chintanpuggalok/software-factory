---
name: factory-security
description: Review security and privacy risks for a change. Use before release or when a change crosses a trust boundary.
---

# Review security

1. Identify assets, trust boundaries, credentials, and exposed interfaces. Do not read or disclose secrets.
2. Check authentication, authorization, input handling, dependency risks, data protection, and logging where relevant.
3. Cite evidence for each finding. Mark checks that could not run and assumptions that remain unverified.
4. Fix issues only within authorized scope. Re-run relevant checks. Block release when required security evidence is missing or a critical issue remains.

Do not claim a full security audit or safe production system without evidence. Send the findings or a justified not-applicable record to `audit-build` or `audit-release`. Continue only after `PASS: evidence`.
