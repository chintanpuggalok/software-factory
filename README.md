# Software Factory

A prototype software factory that takes a product idea through planning, a static prototype, and browser checks. It aims for engineering rigor and autonomous execution within authorized limits.

Inspired by [Poteto's pstack](https://github.com/cursor/plugins/tree/main/pstack).

**Status: prototype.** Planning, prototype generation, and selected browser checks work. Automatic task routing, unattended release, and deployment are not implemented. Market-share claims from research are not verified.

## What you get

- **27 agent skills:** 16 workflow skills, 10 stage audits, and the ASD-STE100 writing skill. The package is self-contained. No external skill is required.
- **One coordinator:** Python, project-local state, resumable stages.
- **One audit contract:** `PASS: evidence`, `REVISE: findings`, `BLOCKED: reason`. Work advances only on PASS.
- **Optional browser checks:** isolated Chromium with an acceptance contract.
- **Runtime adapters:** Pi and OpenCode today. Codex and Claude fail closed until implemented.

## Mental map

```text
Idea → Spec → Design → Architecture → Plan → Build → Verify → Release
  │      │       │          │           │       │       │         │
  └──────┴───────┴──────────┴───────────┴───────┴───────┴─────────┘
                      Stage-specific audits
                              │
                  Taste and project memory
```

Stages can overlap. Small changes skip stages. Every stage has an audit with one verdict contract.

## Install the package

Requires [Pi](https://pi.dev) and `python3`. Review the repository before installing it.

```sh
pi install git:github.com/chintanpuggalok/software-factory
```

This installs the skills and the `/factory-*` commands. Run `/reload` in an active session, then run `/factory-status` in any project.

An isolated local install confirmed that Pi discovers the extension and all 27 skills from the package. GitHub installation and cross-project preference loading are untested.

## Use in a new project

Create the project, start Pi there, and run the startup skill.

```sh
mkdir -p /path/to/my-project
cd /path/to/my-project
pi
```

Inside Pi, use one command:

```text
/factory A local checklist app for one person
```

`/factory` creates the project state, plans the product, then builds and verifies a static prototype. Later runs restore the saved goal:

```text
/factory
```

Try it without model calls first:

```text
/factory A local checklist app for one person --simulate
```

Skills-only alternative, when the extension is not installed:

```text
/skill:factory-entry A local checklist app for one person
```

The package includes its own startup skill. You do not need a global `project-start` skill.

## Use in an existing project

Open Pi in the repository root. Keep your existing conventions.

```sh
cd /path/to/existing-repo
pi
```

Inside Pi, start with one command:

```text
/factory
```

Or give a goal when the project has none saved:

```text
/factory Improve checkout error handling
```

`/factory` restores saved state and continues the next phase. `/factory-status` reports state without changing it. To work on an existing application, use the skills directly:

```text
/skill:factory-project-start
/skill:factory-route
```

- `factory-project-start` reads the existing `AGENTS.md`, `CONTEXT.md`, `PLAN.md`, `decisions.md`, and linked docs. It creates only the files that are missing and does not reorganize your work.
- `factory-route` selects the next step. Use it instead of forcing the full stage sequence.

Use the skills for existing code:

| Task | Start with |
|---|---|
| Fix a bug | `/skill:factory-route`, then the bug playbook and `factory-verify` |
| Add a feature | `/skill:factory-route`, then the feature playbook |
| Refactor | `/skill:factory-route`, then the refactor playbook |
| Review a trust boundary | `/skill:factory-security` |
| Prepare a release | `/skill:factory-release` |

The coordinator's `/factory build` generates a **single static HTML prototype** in `.factory-build/`. It does not modify an existing application or its dependencies. For an existing app, use the skills and your project's own tooling. The coordinator can still plan and record audits.

### Run one stage directly

| Command | Use when |
|---|---|
| `/skill:factory-project-start` | Starting or resuming substantive product work |
| `/skill:factory-route` | Work enters the factory, or earlier work resumes |
| `/skill:factory-idea` | Shaping a raw idea |
| `/skill:factory-spec` | Defining scope and acceptance criteria |
| `/skill:factory-design` | Choosing a visual and interaction direction |
| `/skill:factory-architecture` | Setting scale targets, interfaces, and failure modes |
| `/skill:factory-plan` | Splitting complex work |
| `/skill:factory-build` | Implementing an authorized change |
| `/skill:factory-verify` | Proving behavior |
| `/skill:factory-visual-review` | Checking a running interface |
| `/skill:factory-security` | Reviewing a trust boundary |
| `/skill:factory-release` | Preparing a release |
| `/skill:factory-recover` | Resuming after interruption or failure |
| `/skill:factory-learn` | Capturing lessons and testing workflow changes |
| `/skill:factory-taste` | Recording project or user-wide preferences |

Use one workflow skill per stage. Load the matching `audit-*` skill when the output is ready. Do not advance on `REVISE` or `BLOCKED`.

Delegation is optional. If you use subagents, follow your harness's rules. The factory rules in this package remain in force.

Preference memory is optional. Project preferences live in the product. User-wide preferences default to `~/.pi/agent/preferences/index.md`. Do not commit personal preferences to a public repository.

## Coordinator commands

The package registers a Pi extension. You do not run a CLI. `/factory` is the normal entry point. The other commands are advanced controls.

| Command | What it does | Model calls |
|---|---|---|
| `/factory` | Show status and the next step. Resumes a saved goal | None |
| `/factory <goal>` | Create or restore state, plan, then build and verify | Up to 13 |
| `/factory status` | Show the saved run, stage verdicts, and verification state | None |
| `/factory plan <goal>` | Plan only, with one audit per stage | Up to 10 |
| `/factory build` | Generate and verify one prototype from a passed plan | Up to 3 |
| `/factory simulate <goal>` | Run the eight-stage simulation | None |
| `/factory resume` | Repeat the last plan or build | Same as the last run |
| `/factory help` | Show this command list | None |

Examples:

```text
/factory A local checklist app for one person
/factory status
/factory simulate A local checklist app for one person
/factory plan A local checklist app for one person --research-query=task management software
/factory plan A local checklist app for one person --runtime=opencode
/factory build --acceptance-file=.factory/acceptance.json
```

`/factory` with no goal restores the saved goal. `/factory plan` and `/factory build` ask for confirmation in the TUI. In print or automation mode they require `--yes`. `--runtime=pi|opencode` selects the execution adapter for planning and build calls; unknown values are rejected before any call. Confirmation is an attestation about spending. No dollar limit is enforced. Codex and Claude runtimes are not implemented.

The extension writes only under the target project's `.factory/` and `.factory-build/` directories. It runs the bundled Python coordinator from the package, so it needs `python3`.

### Requirements

- Python 3.10 or later.
- Node.js 22+ for browser checks.
- Chromium and Bubblewrap (`bwrap`) for isolated browser checks. Both are optional.

### Options

```text
--yes                                  Confirm model calls without the interactive prompt
--research-query=<terms>               Send a public query to Wikipedia. Do not include secrets
--reference-url=<https url>            Inspect up to three approved public hosts, static HTML only
--acceptance-file=<path>               Browser acceptance actions for the generated prototype
--build                                Generate the prototype after a passed plan
```

### TUI

While a command runs, the extension draws a status widget above the prompt. It follows the pi-subagents pattern: a bounded box, one glyph per stage, and a single final state per row.

```text
╭────────────────────────── factory ───────────────────────────╮
│ A local checklist app for one person                         │
│ pi · 2/5 stages · up to 10 calls · no dollar limit           │
│                                                              │
│ ✓ idea          passed                                       │
│ ✓ spec          passed                                       │
│ ● design        auditing…                                    │
│ ○ architecture  pending                                      │
│ ○ plan          pending                                      │
│                                                              │
│ /factory-status for detail · ctrl+c stops the run            │
╰──────────────────────────────────────────────────────────────╯
```

| Glyph | Meaning |
|---|---|
| `○` | Pending |
| `●` | Running or auditing |
| `✓` | Audit returned `PASS: evidence` |
| `✗` | Audit returned `REVISE` or `BLOCKED` |

Rules:

- At most six stage rows. Extra stages collapse into `… +N more stages`.
- A blocker replaces the empty line with `blocked at <stage>: <verdict>`.
- After a build, one line shows `static <status> · browser <status>`.
- The widget uses the terminal width, clamped to 96 columns, and truncates long goals.
- The footer status line shows `factory: running…` during a run and clears at the end.
- The final widget stays until the next run or session end.

The widget is display only. It does not add accept, reject, or stop keys. Output is plain text with no theme colors yet.

### What build does

1. Generates one new `.factory-build/index.html`. It never overwrites an existing prototype.
2. Runs limited structural checks and adds a hash to `verification.json`.
3. Makes one repair attempt if structural checks fail.
4. Runs an isolated browser probe: page load, uncaught JavaScript errors, and horizontal overflow at mobile and desktop sizes.
5. Makes one browser repair attempt if the probe fails, saved to `.factory-build/browser-repair/` without overwriting the original.

If Chromium, Bubblewrap, or sandbox setup is unavailable, browser verification reports **unavailable**, not passed.

### Acceptance contracts

Add product-specific browser checks with a small JSON contract:

```json
{
  "version": 1,
  "actions": [
    {"action": "click", "selector": "[data-digit='2']"},
    {"action": "expect_text", "selector": "#display", "text": "2"}
  ]
}
```

Supported actions: `click`, `key`, `reset`, `expect_text`, `expect_exists`. A contract needs at least one assertion and at most 50 actions. Keep acceptance criteria independent of the implementation. Do not weaken them to pass a failure.

See `artifacts/calculator-test/acceptance.json` for a 13-action example.

### View a generated prototype

```sh
cd .factory-build
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000`.

### Run the tests

```sh
python3 -m unittest discover -s tests -v
node --test tests/test_extension_core.mjs
```

The suites cover state recovery, audit gating, planning, structural and browser verification, sandbox network isolation, extension argument parsing, and skill contracts. Browser tests skip when Chromium is unavailable.

### Optional CLI

For CI or manual runs, the same coordinator is available directly:

```sh
python3 factory.py /path/to/project --goal "Example product"
python3 factory.py /path/to/project --mode pi-plan --subscription-confirmed --goal "Example product"
```

## Runtime adapters

The Pi extension and the optional CLI both call the same Python coordinator. `--runtime` selects the execution adapter. `pi` and `opencode` are implemented; `opencode` needs the OpenCode CLI and its own authenticated provider. `codex` and `claude` fail closed before any process starts.

To add one, follow `docs/runtime-adapters.md`. Do not copy Pi flags into another harness without verifying its documented behavior.

The OpenCode adapter runs each call in a private server with an isolated configuration directory: no ambient plugins, MCP servers, skills, or instruction files, and project configuration and `AGENTS.md` discovery are disabled. OpenCode resolves its project location from `PWD`, which the adapter pins to the workspace. The OpenCode free usage limit is per provider; select any authenticated provider with `FACTORY_OPENCODE_MODEL`.

## Verified and unverified

**Verified:**

- 27 skills discovered from an isolated local package install, with no diagnostics.
- Fixed-stage planning over Pi, with one audit per stage.
- Calculator prototype passing 13 browser acceptance actions.
- Sandbox network isolation, interrupted-build recovery, and bounded repair.
- 92 Python tests and 14 extension tests.
- The coordinator emits `PROGRESS` lines on stderr. The extension turns them into a live stage widget.
- The Pi extension ran `/factory status` and `/factory simulate` in print mode without a CLI or model call.
- The OpenCode adapter shape against a live OpenCode CLI: the injected agents resolve, the command parses, the response header goes to stderr, and the confirmation gate refuses before any process starts.
- A live five-stage plan with the current default model: all stages passed, and each wrote `docs/factory/<stage>.md`.
- A live static build after that plan: structural checks passed and the isolated browser probe passed. See `artifacts/live-run-review.md`.
- Three real completions through the OpenCode adapter via `factory.py --mode pi --runtime opencode`: one plain response, permitted file reads, and a denied file read under the deny-all planner agent. Tool activity went to stderr, stdout held only the response text, and exit codes were clean. A rerun with a mismatched parent working directory caught a location bug; the adapter now pins `PWD` to the workspace and a test locks it.

**Unverified:**

- Individually provoked denials for shell, web, and subagent actions under the planner agent. They follow the same permission rules as the observed file-read denial.

- Automatic skill or playbook selection for an arbitrary request.
- A completely unattended idea-to-release run.
- Deployment and production health checks.
- Full accessibility and screen-reader behavior.
- Market-share evidence quality.
- Formal ASD-STE100 compliance, which needs the official dictionary.

Model audits are not independent proof. A self-audit is not independent review.

## Comparison with pstack

| Dimension | This factory | pstack |
|---|---|---|
| Focus | Product-to-release workflow with taste, scale planning, and browser evidence | Engineering rigor and task-specific playbooks |
| Routing | `factory-route` with bug, feature, and refactor playbooks. Automatic selection untested | `poteto-mode` selects playbooks and invokes skills |
| Design | Minimalist baseline, competitor-flow research, taste memory | Experience-first principles, not a personal taste profile |
| Evidence | One audit per stage, static and browser checks, acceptance contracts | Specialized review and multi-model workflows |
| Autonomy | Prototype coordinator; no unattended release | Autonomous-run and orchestration playbooks |
| Maturity | Prototype with a partial calculator walkthrough | Broader published stack with many integrations |

This comparison uses the [pstack README at commit `c742dd6`](https://github.com/cursor/plugins/blob/c742dd61706fbacc1b95f1a20b7b988cf096ce6c/pstack/README.md). Neither description proves quality, cost savings, or safety.

## Project files

- `AGENTS.md`: factory operating rules.
- `CONTEXT.md`: confirmed goals and current state.
- `PLAN.md`: active milestone and blockers.
- `decisions.md`: confirmed decisions and proposals.
- `docs/runtime-adapters.md`: adapter contract.
- `taste/index.md`: factory-local taste baseline.
- `research/`: source-based evaluations.
- `artifacts/`: reviews, tests, and the calculator prototype.
- `.agents/skills/`: workflow, audit, and STE skills.
- `extensions/`: the Pi extension and its testable core.

## Third-party material

`.agents/skills/asd-ste100/` contains material from [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill), pinned to commit `a4905d922500dd7530ca8a0eb9e4940494255709`. Its MIT license is included in that directory. The official [ASD-STE100 standard](https://www.asd-ste100.org/) is not included, and compliance has not been verified.

Original project material is MIT licensed. See `LICENSE`.
