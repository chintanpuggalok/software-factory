---
name: factory-recover
description: Recover a factory task after interruption or failure. Use when work must resume or a stage fails.
---

# Recover the task

1. Read the last durable state, authorized scope, and available evidence. Inspect the current work before changing it.
2. Identify completed work, in-flight effects, failed checks, and unknown outcomes. Do not repeat an external action until its outcome is known.
3. Record the failure, retry limit, and next safe action. Preserve unrelated work.
4. Retry only when the cause and scope permit it. Re-run the affected checks. Try another safe approach within scope when it can resolve the failure.
5. Resume the remaining authorized work after recovery. Do not wait for a new prompt.

If recovery is blocked, report what was tried and the smallest input needed. Do not repeat unsafe external effects. Do not claim automatic restart or exactly-once execution.
