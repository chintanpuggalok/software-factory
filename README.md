# Software Factory

A prototype software factory that takes a product idea through planning, a static prototype, and browser checks. It aims for engineering rigor and autonomous execution within authorized limits.

Inspired by [Poteto's pstack](https://github.com/cursor/plugins/tree/main/pstack).

**Status: prototype.** Planning, prototype generation, and selected browser checks work. Automatic task routing, unattended release, and deployment are not implemented. Market-share claims from research are not verified.

## What you get

- **25 agent skills:** 14 workflow skills plus 10 stage audits and the ASD-STE100 writing skill.
- **One coordinator:** Python, project-local state, resumable stages.
- **One audit contract:** `PASS: evidence`, `REVISE: findings`, `BLOCKED: reason`. Work advances only on PASS.
- **Optional browser checks:** isolated Chromium with an acceptance contract.
- **Runtime adapters:** Pi today. Codex and Claude fail closed until implemented.

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

## Install the skills

Requires [Pi](https://pi.dev). Review the repository before installing it.

```sh
pi install git:github.com/chintanpuggalok/software-factory
```

Then run `/reload` in an active session.

## Use the skills

### Start a new product

```sh
mkdir -p /path/to/my-project
cd /path/to/my-project
pi
```

Inside Pi:

```text
/skill:project-start      # if you have this global skill
/skill:factory-route
```

Describe the idea. `factory-route` records the goal, scope, release target, and completion criteria, then selects the next stage.

If you do not have `project-start`, ask Pi to create `AGENTS.md`, `CONTEXT.md`, and `PLAN.md` first. Project rules and current requests take precedence over skill defaults.

### Run one stage directly

| Command | Use when |
|---|---|
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

Preference memory is optional. Project preferences live in the product. User-wide preferences default to `~/.pi/agent/preferences/index.md`. Do not commit personal preferences to a public repository.

## Use the coordinator

The coordinator is a prototype CLI. It writes only under the target project's `.factory/` and `.factory-build/` directories.

### Requirements

- Python 3.10 or later.
- Pi for real model calls.
- Node.js 22+ for browser checks.
- Chromium and Bubblewrap (`bwrap`) for isolated browser checks. Both are optional.

### Simulate a full cycle

No model calls and no external effects.

```sh
python3 factory.py /path/to/test-project --goal "Example product"
python3 factory.py /path/to/test-project --goal "Example product" --fail-stage verify
```

### Plan with a real model

```sh
python3 factory.py /path/to/test-project \
  --mode pi-plan --subscription-confirmed \
  --goal "A local checklist app for one person"
```

This makes up to ten calls: one stage output and one audit for each of idea, spec, design, architecture, and plan. A failed audit stops the run and saves its verdict.

Optional:

```sh
  --research-query "public market search terms"   # sent to Wikipedia; no secrets
  --reference-url https://www.calculator.net/     # up to three approved hosts
  --build-static                                  # generate one static HTML prototype
  --acceptance-file /path/to/acceptance.json      # browser acceptance actions
  --runtime pi                                    # codex and claude are not implemented
```

`--subscription-confirmed` is an attestation, not billing verification. The coordinator does not enforce a dollar limit.

### What `--build-static` does

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
```

The suite covers state recovery, audit gating, planning, structural and browser verification, sandbox network isolation, and skill contracts. Browser tests skip when Chromium is unavailable.

## Runtime adapters

`--runtime` selects the execution adapter. Only `pi` is implemented and tested. `codex` and `claude` fail closed before any process starts.

To add one, follow `docs/runtime-adapters.md`. Do not copy Pi flags into another harness without verifying its documented behavior.

## Verified and unverified

**Verified:**

- 25 skills discovered from an isolated local package install, with no diagnostics.
- Fixed-stage planning over Pi, with one audit per stage.
- Calculator prototype passing 13 browser acceptance actions.
- Sandbox network isolation, interrupted-build recovery, and bounded repair.
- 65 automated tests.

**Unverified:**

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

## Third-party material

`.agents/skills/asd-ste100/` contains material from [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill), pinned to commit `a4905d922500dd7530ca8a0eb9e4940494255709`. Its MIT license is included in that directory. The official [ASD-STE100 standard](https://www.asd-ste100.org/) is not included, and compliance has not been verified.

Original project material is MIT licensed. See `LICENSE`.
