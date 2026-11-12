# Runtime adapters

The Pi extension and the optional CLI both call the Python coordinator. The
coordinator must not depend on Pi-specific code. The planning workflow calls a
runtime adapter with one small contract.

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
   different adapter. The static build re-checks the saved runtime name.
5. Test: missing workspace, empty prompt, no confirmation, nonzero exit, empty
   output, timeout, and the exact command shape with a fake process.
6. Test one real read-only call only after the user authorizes spending. State
   that billing limits are not enforced.

## Command shape by harness

| Harness | Non-interactive text | Tool restriction |
|---|---|---|
| Pi | `pi --print ... --no-tools --no-skills --no-context-files -- <prompt>` | Flags exist and are tested. |
| OpenCode | `opencode run --standalone --agent <factory agent> [--model <m>] --archived --title factory -- <prompt>` | Injected agent permissions deny every action; the read-only agent allows only file reads. |
| Codex | Not implemented | Design an equivalent restricted invocation. Do not assume flags. |
| Claude | Not implemented | Design an equivalent restricted invocation. Do not assume flags. |

Do not copy Pi flags into another harness. Verify its documented behavior first.

## OpenCode adapter notes

`opencode_adapter.py` verifies this shape against OpenCode V2. Per call it:

1. Creates one temporary configuration directory and writes `opencode.json`
   with two agents. `factory-planner` denies every permission action, so no
   tool, skill, subagent, question, or web request can run. `factory-readonly`
   allows only file reads and keeps deny rules for `.env` files. Both agents
   get a minimal system prompt that replaces the provider base prompt.
2. Sets `XDG_CONFIG_HOME` to that directory. The user's global plugins, MCP
   servers, skills, agents, and instruction files do not apply. Provider
   authentication lives outside the config directory and keeps working.
3. Sets `OPENCODE_DISABLE_PROJECT_CONFIG=1`, which skips the project
   `opencode.json` and project `AGENTS.md` discovery.
4. Runs `opencode run --standalone ...` with a private server, so the shared
   background service does not load the ambient configuration.

Verified against a live OpenCode CLI: the injected agents resolve, the command
shape parses, stdout contains only the response text, the run header and
errors go to stderr, and the confirmation gate refuses before any process
starts. Live completions through `factory.py` verified a plain response,
permitted file reads with tool activity on stderr, and a denied file read
under the deny-all `factory-planner` agent, which refused in plain text and
leaked no contents. OpenCode resolves its project location from the `PWD`
environment variable rather than the process cwd, so the adapter pins `PWD`
to the workspace; a rerun with a mismatched parent directory confirmed this.

Environment: `FACTORY_OPENCODE_MODEL` optionally pins `--model
provider/model`. Without it the harness default model is used. Each call
saves an archived session named `factory` in the user's OpenCode database;
OpenCode has no no-session mode. The adapter kills the process group on
timeout, because the private server is a child process.

## Parity checklist for a new adapter

- Same substage order and audit verdict contract.
- Same spend confirmation and refusal behavior.
- Same output size limits and history limit.
- Same saved-state compatibility rule.
- Same reporting: state the adapter, the call count, and that no dollar cap is
  enforced.

Untested adapters must never be described as supported.
