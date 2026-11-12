# Software Factory

A draft software factory for turning product ideas into verified releases. It aims for engineering rigor: evidence-based decisions, small changes, meaningful tests, and minimal unnecessary output. Its goal is autonomous execution within authorized boundaries.

Inspired by [Poteto's pstack](https://github.com/cursor/plugins/tree/main/pstack), particularly its engineering principles and task-specific playbooks. This project adapts those ideas to a product-to-release workflow with design taste and scale planning.

**Status: prototype.** An experimental Pi workflow runs planning stages with model tools disabled. It can generate a single static HTML prototype, run limited structural and isolated browser checks, and request bounded repairs. A calculator prototype passed selected Chromium checks. The coordinator does not deploy automatically. Market-share claims remain unverified.

## Mental map

```text
Idea → Spec → Design → Architecture → Plan → Build → Verify → Release
  │      │       │          │           │       │       │         │
  └──────┴───────┴──────────┴───────────┴───────┴───────┴─────────┘
                      Stage-specific audits
                              │
                  Taste and project memory
```

The stages can overlap when the work permits. The goal is to work autonomously within authorized scope. Current skills still contain approval prompts that need review against that goal.

| Area | Current implementation |
|---|---|
| Idea and spec | Skills ask about the user and problem, propose scope, and record decisions. |
| UI and UX | The design skill starts from minimalist, Apple-inspired taste. It calls for research on up to three market leaders in the relevant segment and favors familiar flows when they fit. |
| Architecture and scale | A skill asks for traffic, users, concurrency, data, growth, availability, and budget. It marks unknown values and requests approval for material decisions. |
| Build and checks | Skills describe bounded implementation, tests, independent user scenarios when feasible, and browser-based visual review when available. |
| Stage audits | Ten small audit skills give each stage a focused checklist. A self-audit is not independent review. |
| Release | The release skill calls for audits before and after deployment. A pre-deployment audit pass does not grant deployment approval. |
| Taste and memory | A project index and an optional user-wide preference skill separate confirmed preferences from hypotheses. Cross-project preference loading is not yet tested. |
| Routing and recovery | Draft skills select a task-specific route and describe safe recovery. They do not enforce transitions or restart processes. |
| Security and evaluation | Draft skills describe security checks and reproducible workflow tests. Their coverage and automatic execution are untested. |
| Learning | A draft skill captures lessons and suggests tests or workflow changes within authorized scope. |
| Cost and delegation | The instructions prefer direct work unless authorized delegation offers a clear benefit. They do not select a model or enforce a budget. |
| Clear language | The repository includes an MIT-licensed upstream ASD-STE100-inspired skill. It does not include the official dictionary or certify compliance. |

These are **instructions**, not proof that agents will follow them or that the checks will run.

## Run the simulator

```sh
python3 factory.py /path/to/existing/test-project --goal "Example product"
python3 -m unittest discover -s tests -v
```

The simulator creates `.factory/state.json` in the target directory. It does not write product code or make external calls. Repeat the same command to resume a simulated run. `--fail-stage verify` simulates a failed audit. `--mode pi` makes one read-only Pi request only when the user passes `--subscription-confirmed`. The flag is an attestation, not billing verification. No dollar limit is enforced. Do not use simulator results as production evidence.

## Experimental Pi planning

```sh
python3 factory.py /path/to/existing/test-project --mode pi-plan --subscription-confirmed --goal "Your product idea" --research-query "public market search terms"
```

This makes up to ten Pi process calls for idea, spec, design, architecture, and plan. Add `--build-static` to generate a new `.factory-build/index.html`. The build uses one Pi call, may use one static repair call, and may use one browser repair call. It does not overwrite an existing prototype. A matching interrupted build can recover from its pending record. A `verification.json` records structural checks and a hash.

After generation, the coordinator attempts an isolated browser check using Node.js, Chromium, and Bubblewrap. If any are unavailable, it reports browser verification as unavailable and does not claim a pass. The check covers page load, uncaught JavaScript errors, and horizontal overflow at two viewport sizes. A browser failure can trigger one Pi repair, saved separately without overwriting the original.

To add product-specific checks, pass `--acceptance-file /path/to/acceptance.json` with `--build-static`. See `artifacts/calculator-test/acceptance.json` for an example. The contract supports bounded clicks, keys, resets, and DOM text or existence assertions. Keep acceptance criteria independent of the implementation; do not weaken them to pass a failure. These checks are not a complete functional test, security audit, or accessibility audit. Generated HTML is untrusted and is not deployed.

The subprocesses have tools disabled. The optional research query is sent to Wikipedia; do not include secrets. `--reference-url` accepts up to three URLs from the configured public hosts. It returns static HTML only. Search snippets and page data are untrusted leads, not verified market-share evidence. Each audit uses a fresh Pi process, but it is not an independent human review or deterministic proof. Planning outputs are stored under the target project's `.factory/` directory. A failed audit stops the run. The adapter cannot verify billing or enforce a dollar cap.

## What remains untested?

**Live routing** means whether a real agent session discovers the right skills and loads them at the right time. Pi listed the original stage skills after reload. We have not verified discovery of the latest additions, automatic selection, audit invocation, or context use.

**A product walkthrough** means trying the entire flow on a real, small product: capture an idea, agree on scope and design, set scale targets, build, test, review, and prepare a release. We have not run that end-to-end exercise. It would show whether the handoffs preserve decisions, whether approvals stop work at the right places, and whether the output meets the acceptance criteria.

A walkthrough does not require a production deployment. Deployment, spending, installation, delegation, and merging require the applicable approvals.

## Comparison with pstack

This compares the draft with [Poteto's pstack](https://github.com/cursor/plugins/tree/main/pstack), not with gstack or Noodle. The pstack description below is based on its [README at commit `c742dd6`](https://github.com/cursor/plugins/blob/c742dd61706fbacc1b95f1a20b7b988cf096ce6c/pstack/README.md). We have not benchmarked either system.

| Dimension | This factory | pstack |
|---|---|---|
| Main focus | Product-to-release work with engineering rigor, user taste, and an autonomous execution goal. | Engineering rigor: better, verifiable code and less unnecessary output. |
| Routing | Draft routing skill and bug, feature, and refactor playbooks. Automatic routing is untested. | `poteto-mode` selects task-specific playbooks and invokes skills. |
| Design taste | Explicit minimalist baseline, competitor-flow research, and a taste index. | Includes experience-first principles and specialized workflows; it is not centered on this user's taste profile. |
| Architecture | A draft skill covers scale, contracts, data ownership, interfaces, alternatives, and failure modes. | An `architect` skill and engineering principles address design before implementation. |
| Review | One small checklist per factory stage. Independent review is conditional. | Includes specialized review and multi-model workflows, including `interrogate`. |
| Memory | Project files and an optional user-wide preference index. Cross-project preference loading is untested. | Includes `reflect`, `correct`, and other skills for improving workflows and encoding lessons. |
| Autonomous execution | A simulator exercises stage gates and recovery. A separate read-only Pi call was tested. Full workflow execution is not implemented. | Provides autonomous-run and orchestration playbooks, subject to harness capabilities. |
| Parallel work | Allowed only with authorization and a clear benefit. No model router is implemented here. | Provides model routing and parallel workflows such as `arena` and `swarm`. |
| Maturity | Draft instructions; no product walkthrough yet. | A broader published skill stack with many playbooks and harness integrations. |

The approaches are complementary. This project combines the product journey, user taste, and engineering rigor. pstack offers deeper engineering playbooks. Neither description proves quality, cost savings, or safety.

## Use in Pi

Pi discovers project skills under `.agents/skills/` when the project is in scope. Open Pi in this project and run `/reload` after changing the skills. Inspect Pi's skill list or startup diagnostics. Invoke a stage directly, for example `/skill:factory-idea`, when you need to force selection.

### Install for other projects

A Pi user can review this repository and install its skills from GitHub:

```sh
pi install git:github.com/chintanpuggalok/software-factory
```

For a new project, choose a location and start Pi there:

```sh
mkdir -p /path/to/my-project
cd /path/to/my-project
pi
```

If you have a separate `project-start` skill installed, run `/skill:project-start` first. Then run `/skill:factory-idea` and describe your idea. Without `project-start`, ask Pi to load the project instructions and context before starting.

Run `/reload` in an active session after installation. Installing the skills does not start an autonomous factory. The coordinator is still a prototype.

Pi loads the package skills globally, but does not create or automatically load a personal preference index. Run `/skill:factory-preferences` to manage preferences. To load relevant preferences at project startup, add a short instruction to your own global agent rules after reviewing it. Keep your index at `~/.pi/agent/preferences/index.md`; do not commit personal preferences to a public repository.

This package contains all factory skills, not just preference memory. A project-local copy can create name collisions. The project rules refer to optional global `project-start`, `pi-subagents`, and autoresearch guidance that is not included here. Other users must provide equivalent rules or adapt those references. A local package install and skill discovery passed in an isolated Pi configuration. GitHub installation and cross-project preference loading have not been tested.

Start with a small idea. Review the decisions and artifacts at each stage. Do not interpret an agent's audit result as permission to spend, merge, or deploy.

## Project files

- `CONTEXT.md`: confirmed goals and current state.
- `PLAN.md`: active milestone and blockers.
- `decisions.md`: confirmed decisions and proposals.
- `taste/index.md`: factory-local taste baseline.
- `research/`: source-based evaluations.
- `artifacts/`: review notes and validation evidence.
- `.agents/skills/`: draft factory and audit skills.

## Third-party material

`.agents/skills/asd-ste100/` contains material from [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill), pinned to commit `a4905d922500dd7530ca8a0eb9e4940494255709`. Its MIT license is included in that directory. The upstream linter is present but has not been run here. The official [ASD-STE100 standard](https://www.asd-ste100.org/) is not included, and compliance has not been verified.
