# OpenCode runtime adapter review

## Scope
The author implemented and reviewed the OpenCode runtime adapter for the factory coordinator. This is a self-review, not an independent audit. One tiny real model call was made during setup checks; the account's free quota was already exhausted, so no paid call completed. Billing limits are not enforced.

## Evidence
- `python3 -m unittest discover -s tests -v`: 82 tests passed. New tests cover the OpenCode adapter (9), runtime selection (2), CLI paths (3), and saved-runtime compatibility (2).
- `node --test tests/test_extension_core.mjs`: 12 tests passed.
- `factory.py --mode pi-plan --runtime codex`: `BLOCKED: codex adapter is not implemented; use one of: pi, opencode`, exit 2, no process started.
- `factory.py --mode pi --runtime opencode` without `--subscription-confirmed`: `BLOCKED: Subscription not confirmed; no OpenCode call was made`, exit 2.
- Live OpenCode CLI checks (free, no completed model call): `opencode run --agent <unknown>` fails fast with `Agent not found`; with `XDG_CONFIG_HOME` pointed at the adapter's configuration, the injected `factory-planner` and `factory-readonly` agents resolve; with `OPENCODE_DISABLE_PROJECT_CONFIG=1`, agents defined in the project `opencode.json` are not discovered; one successful tiny call returned `OK` on stdout with the `> agent · model` header on stderr.
- The adapter ran end to end through `factory.py`: the real CLI accepted the generated configuration and command shape, the provider rejected the call (`Insufficient balance`), and the adapter passed the exit code and stderr through cleanly. No temporary configuration directories were left behind.

## Design
- One call, one private server: `opencode run --standalone --agent <factory agent> [--model <m>] --archived --title factory -- <prompt>`.
- An injected configuration defines two agents. `factory-planner` denies every permission action. `factory-readonly` allows only file reads and keeps deny rules for `.env` files. Both get a minimal system prompt.
- `XDG_CONFIG_HOME` points at a per-call temporary directory, so ambient plugins, MCP servers, skills, agents, and global instructions do not apply. Provider authentication stays in the data directory and kept working.
- `OPENCODE_DISABLE_PROJECT_CONFIG=1` skips the project `opencode.json` and project `AGENTS.md` discovery.
- `FACTORY_OPENCODE_MODEL` optionally pins the model; otherwise the harness default applies.
- Planning, static build, and browser repair reuse the selected adapter through one invocation helper. The static build refuses a saved plan from a different runtime.

## Limitations
- No successful planning call through the adapter: the OpenCode provider reported `Free usage limit reached` and the default model reported `Insufficient balance`. Denial behavior while a model attempts a denied tool, and `--format` behavior, are unobserved.
- Each call saves an archived session named `factory` in the user's OpenCode database. OpenCode has no no-session mode.
- Permissions restrict tool execution, not provider traffic. The model provider itself uses the network by design.
- The Pi extension does not pass `--runtime`; extension users select the adapter through `FACTORY_RUNTIME`.
- `OPENCODE_DISABLE_PROJECT_CONFIG` and the injected agent permissions are documented OpenCode V2 behavior verified by agent-resolution probes, not by a completed restricted run.

## Next action
Run one real read-only planning call through the adapter when provider quota or balance is available, and observe output purity when a model attempts a denied tool. Then decide whether the extension should pass `--runtime` through.
