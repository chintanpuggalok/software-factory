---
name: factory-autonomous
description: Guide an authorized autonomous project run. Use when the user requests end-to-end execution within a defined scope.
---

# Run the project

1. Record the goal, authorized scope, release target, constraints, and checkable completion criteria.
2. Select a bounded task with `factory-route`. Run the matching stage and audit. Record actions, evidence, and the next task.
3. Fix failures within authorized scope. Re-run the affected checks. Do not weaken the completion criteria.
4. Continue to the next authorized task after each stage. Do not stop at a milestone or ask the user to say continue. Record reversible assumptions.
5. Before stopping, identify the unmet criterion and next action. Check available tools. Try safe alternatives within scope. Use `factory-recover` after interruption.
6. Pause only for unavailable access, required authorization, a consequential user decision, or an unresolved external or tool blocker. State what was tried and the smallest input needed.
7. When the criteria pass, run `factory-learn`. Report the result and unverified risks.

Follow the user's authorized cost limits and higher-priority permissions for spending, delegation, installation, and deployment. This skill is an instruction, not a running scheduler or restart mechanism.
