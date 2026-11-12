# Pi planning smoke test

## Scope
The author tested the experimental Pi planning workflow with a local checklist app idea. This was not an independent review. The Pi subprocesses had tools disabled. The test did not implement or deploy the app.

## Evidence
- `python3 -m unittest discover -s tests -q` passed 14 tests. The planning tests use fake Pi responses.
- Before web research was added, a real Pi run passed idea and spec, then stopped at design for missing competitor evidence.
- With a public Wikipedia search query, a real sample run passed idea, spec, design, architecture, and plan. The audits were model judgments. The test did not independently verify market-share claims or competitor rankings.
- A separate one-stage real Pi smoke test passed idea and its model audit.
- The design audit is a separate Pi process, not a deterministic check or human review. Model output is untrusted.
- A real model call can incur subscription overages. The user explicitly accepted overages. The adapter does not enforce a dollar cap.

## Blocker
The planner can receive Wikipedia search snippets as untrusted leads. It cannot browse source pages or independently verify market-share rankings. It cannot implement or deploy products. Do not mark factual research, implementation, or release as verified.

## Next action
Add source-page verification with appropriate permissions and terms. Design a safe execution boundary for build and deployment. Test failure recovery before real external effects.
