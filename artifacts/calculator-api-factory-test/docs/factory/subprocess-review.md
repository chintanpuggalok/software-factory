# Subprocess evaluation

PASS: The interactive Pi subprocess received the requested goal through `/factory`. It created a local calculator HTTP service, documentation, tests, project state, and self-audits. The run recorded `phase: complete` in `.factory/entry.json`. The harness stopped the TUI after the completed run became idle. Elapsed time was 166.3 seconds. No deployment or dependency installation was requested.

A separate supervisor-created client script, `independent_check.py`, started the generated HTTP handler in a separate process on an ephemeral loopback port. It checked all four operations with distinct operands. It also checked division by zero, boolean operands, malformed JSON, missing operands, an unknown path, and GET. All checks passed. The generated unittest suite also passed. Raw output: `docs/factory/independent-check.log`. This is a separate test implementation, not an independent reviewer or hidden pre-build holdout.

Limitations: This verifies one small local backend, not arbitrary products or production readiness. The service binds to loopback and has no authentication. The generated server uses floating-point arithmetic. The test does not evaluate deployment, sustained load, or hostile remote clients. The local terminal transcript is not included in the published demo.
