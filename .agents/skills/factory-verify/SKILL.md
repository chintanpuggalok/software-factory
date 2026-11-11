---
name: factory-verify
description: Verify implementation against the spec and user scenarios. Use after implementation or before release.
---

# Verify behavior

1. Read the approved spec, plan, and change summary.
2. Run relevant unit, integration, and end-to-end checks when available. Record commands and results.
3. Check important user scenarios independently of implementation details. Keep holdout cases separate from the implementer when feasible; do not claim independence otherwise.
4. Report failures, missing coverage, and untested risks. Repair within authorized scope and repeat affected checks.

Do not mark a failed or untested requirement as passed. At the stage change, hand `factory-release` the goal, confirmed decisions, artifact paths, open questions, next action, and check results.
