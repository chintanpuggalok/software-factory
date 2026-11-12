# OpenCode runtime adapter review

## Scope
The author implemented and reviewed the OpenCode runtime adapter for the factory coordinator. This is a self-review, not an independent audit. Two tiny real calls on a free model were made through the adapter with the user's standing subscription authorization. Billing limits are not enforced.

## Evidence
- `python3 -m unittest discover -s tests -v`: 82 tests passed. New tests cover the OpenCode adapter (9), runtime selection (2), CLI paths (3), and saved-runtime compatibility (2).
- `node --test tests/test_extension_core.mjs`: 12 tests passed.
- `factory.py --mode pi-plan --runtime codex`: `BLOCKED: codex adapter is not implemented; use one of: pi, opencode`, exit 2, no process started.
- `factory.py --mode pi --runtime opencode` without `--subscription-confirmed`: `BLOCKED: Subscription not confirmed; no OpenCode call was made`, exit 2.
- Live OpenCode CLI checks (free, no completed model call): `opencode run --agent <unknown>` fails fast with `Agent not found`; with `XDG_CONFIG_HOME` pointed at the adapter's configuration, the injected `factory-planner` and `factory-readonly` agents resolve; with `OPENCODE_DISABLE_PROJECT_CONFIG=1`, agents defined in the project `opencode.json` are not discovered.
- Two real completions through the adapter via `factory.py --mode pi --runtime opencode --subscription-confirmed` with `FACTORY_OPENCODE_MODEL=opencode/glm-5.3-flash-free`: one plain response returned `OK` on stdout, exit 0; one with a tempting file-read request executed the permitted `read` tool, reported the file contents on stdout, and printed the tool activity (`→ Read NOTES.md`) on stderr. Both calls cleaned up their temporary configuration directories. Free-tier quota was exhausted between calls; billing limits are not enforced.
- Denial enforcement observed live on `opencode-go/longcat-2.5-free`: the deny-all `factory-planner` agent, told explicitly to read a workspace file, refused on stdout in plain text, named no file contents, ran no tool, and exited 0. The permitted-read run with the same model reported the file contents on stdout with tool activity on stderr.
- A location bug was found by rerunning with a mismatched parent working directory: OpenCode resolves its project location from the `PWD` environment variable, not the child process cwd. The adapter now sets `PWD` to the workspace. The rerun read the intended workspace file, and a unit test locks the environment contract.

## Design
- One call, one private server: `opencode run --standalone --agent <factory agent> [--model <m>] --archived --title factory -- <prompt>`.
- An injected configuration defines two agents. `factory-planner` denies every permission action. `factory-readonly` allows only file reads and keeps deny rules for `.env` files. Both get a minimal system prompt.
- `XDG_CONFIG_HOME` points at a per-call temporary directory, so ambient plugins, MCP servers, skills, agents, and global instructions do not apply. Provider authentication stays in the data directory and kept working.
- `OPENCODE_DISABLE_PROJECT_CONFIG=1` skips the project `opencode.json` and project `AGENTS.md` discovery.
- `FACTORY_OPENCODE_MODEL` optionally pins the model; otherwise the harness default applies.
- Planning, static build, and browser repair reuse the selected adapter through one invocation helper. The static build refuses a saved plan from a different runtime.

## Limitations
- The OpenCode free usage limit is per provider. `opencode/*` free models and `opencode-go/*` free models had separate budgets; both ran out at times during testing. A caller can select any authenticated provider with `FACTORY_OPENCODE_MODEL`.
- Each call saves an archived session named `factory` in the user's OpenCode database. OpenCode has no no-session mode.
- Permissions restrict tool execution, not provider traffic. The model provider itself uses the network by design.
- The extension passes `--runtime` through on plan and build runs; `FACTORY_RUNTIME` remains the selection path for direct CLI use.
- Denial enforcement is observed for file reads only. Shell, web, and subagent denials follow the same permission rules but were not individually provoked.

## Next action
Decide whether the extension should pass `--runtime` through. Then define a deployment target and release contract.
