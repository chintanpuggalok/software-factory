# Runtime adapters

The coordinator must not depend on Pi-specific code. The planning workflow calls
a runtime adapter with one small contract.

## Contract

An adapter provides `name` and two methods:

```python
run_text(workspace, prompt, *, confirmed, timeout) -> CompletedProcess
run_read_only(workspace, prompt, *, confirmed, timeout) -> CompletedProcess
```

Requirements for each method:

- Resolve the workspace first. Reject a missing directory or an empty prompt.
- Refuse to run unless `confirmed` is true. Confirmation is an attestation about
  spending. It is not billing verification.
- Run one non-interactive request in the workspace.
- Disable tools, skills, context files, and network access where the harness
  permits it. Planning output must not depend on repository writes.
- Return `returncode`, `stdout`, and `stderr`. Nonzero or empty output is an error
  for the caller.
- Apply a timeout. Do not retry inside the adapter.

## Adding an adapter

1. Create a class with the contract above in `runtime_adapter.py`.
2. Add the name to `IMPLEMENTED` only after a real call succeeds.
3. Keep unimplemented names in `DECLARED`. They must fail closed with a clear
   message before any subprocess starts.
4. Record the adapter name in saved state. Refuse to resume a run under a
   different adapter.
5. Test: missing workspace, empty prompt, no confirmation, nonzero exit, empty
   output, timeout, and the exact command shape with a fake process.
6. Test one real read-only call only after the user authorizes spending. State
   that billing limits are not enforced.

## Command shape by harness

| Harness | Non-interactive text | Tool restriction |
|---|---|---|
| Pi | `pi --print ... --no-tools --no-skills --no-context-files -- <prompt>` | Flags exist and are tested. |
| Codex | Not implemented | Design an equivalent restricted invocation. Do not assume flags. |
| Claude | Not implemented | Design an equivalent restricted invocation. Do not assume flags. |

Do not copy Pi flags into another harness. Verify its documented behavior first.

## Parity checklist for a new adapter

- Same substage order and audit verdict contract.
- Same spend confirmation and refusal behavior.
- Same output size limits and history limit.
- Same saved-state compatibility rule.
- Same reporting: state the adapter, the call count, and that no dollar cap is
  enforced.

Untested adapters must never be described as supported.
