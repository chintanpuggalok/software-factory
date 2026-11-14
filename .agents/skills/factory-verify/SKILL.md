---
name: factory-verify
description: Check implementation behavior, interface quality, and trust boundaries before release. Use after build work.
---

# Check behavior, interface, and security

1. Read the spec, design brief, plan, taste index, and `git diff` surface.
2. Run unit, integration, and end-to-end checks (including local `cf dev` or `wrangler dev` checks for Cloudflare apps) when available. Record commands, exit codes, and results.
3. Check the pre-build user scenarios independently of implementation details. Report when holdout separation is unavailable.
4. For UI changes, inspect the running interface in a browser when available. Check core flows, screen sizes, accessibility, loading, empty, and error states, and zero console or network errors. Report when browser inspection is unavailable.
5. For trust boundaries, check authentication, authorization, input parsing, secrets isolation, Cloudflare binding permissions, dependencies, and logging. Never read or disclose secrets.
6. Repair defects within authorized scope and rerun affected checks.

Do not mark a failed or unrun check as passed. Send the evidence to `audit-verify`. Advance only after `PASS: evidence`. Pass `factory-release` the goal, decisions, artifact paths, check results, and next action.
