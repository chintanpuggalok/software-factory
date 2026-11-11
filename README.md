# Software Factory

A human-directed workflow for turning a product idea into a release. It uses small agent skills, stage audits, project memory, and explicit approval gates.

**Status: early draft.** The repository contains instructions and review checklists. It is not an autonomous orchestration engine. The skills, their routing, and the complete workflow have not been validated on a product.

## Mental map

```text
Idea → Spec → Design → Architecture → Plan → Build → Verify → Release
  │      │       │          │           │       │       │         │
  └──────┴───────┴──────────┴───────────┴───────┴───────┴─────────┘
                      Stage-specific audits
                              │
                  Taste and project memory
```

The stages can overlap when the work permits. The user decides product scope, design direction, material technical choices, and required approvals.

| Area | Current implementation |
|---|---|
| Idea and spec | Skills ask about the user and problem, propose scope, and record decisions. |
| UI and UX | The design skill starts from minimalist, Apple-inspired taste. It calls for research on up to three market leaders in the relevant segment and favors familiar flows when they fit. |
| Architecture and scale | A skill asks for traffic, users, concurrency, data, growth, availability, and budget. It marks unknown values and requests approval for material decisions. |
| Build and checks | Skills describe bounded implementation, tests, independent user scenarios when feasible, and browser-based visual review when available. |
| Stage audits | Ten small audit skills give each stage a focused checklist. A self-audit is not independent review. |
| Release | The release skill calls for audits before and after deployment. A pre-deployment audit pass does not grant deployment approval. |
| Taste and memory | A local index records confirmed taste separately from hypotheses. Project context, plans, and decisions carry knowledge between sessions. |
| Cost and delegation | The instructions prefer direct work unless authorized delegation offers a clear benefit. They do not select a model or enforce a budget. |
| Clear language | The repository includes an MIT-licensed upstream ASD-STE100-inspired skill. It does not include the official dictionary or certify compliance. |

These are **instructions**, not proof that agents will follow them or that the checks will run.

## What remains untested?

**Live routing** means whether a real agent session discovers the right skills and loads them at the right time. A file can have valid frontmatter and still not be selected when needed. We have not yet verified discovery after the latest changes, automatic selection, audit invocation, or context use.

**A product walkthrough** means trying the entire flow on a real, small product: capture an idea, agree on scope and design, set scale targets, build, test, review, and prepare a release. We have not run that end-to-end exercise. It would show whether the handoffs preserve decisions, whether approvals stop work at the right places, and whether the output meets the acceptance criteria.

A walkthrough does not require a production deployment. Deployment, spending, installation, delegation, and merging require the applicable approvals.

## Comparison with pstack

This compares the draft with [Poteto's pstack](https://github.com/cursor/plugins/tree/main/pstack), not with gstack or Noodle. The pstack description below is based on its [README at commit `c742dd6`](https://github.com/cursor/plugins/blob/c742dd61706fbacc1b95f1a20b7b988cf096ce6c/pstack/README.md). We have not benchmarked either system.

| Dimension | This factory | pstack |
|---|---|---|
| Main focus | A user-led path from raw product idea through design and release. | Engineering rigor: better, verifiable code and less unnecessary output. |
| Routing | Stage skills and handoffs are instructions. Automatic routing is untested. | `poteto-mode` selects task-specific playbooks and invokes skills. |
| Design taste | Explicit minimalist baseline, competitor-flow research, and a taste index. | Includes experience-first principles and specialized workflows; it is not centered on this user's taste profile. |
| Architecture | An explicit architecture and scale-target stage. | An `architect` skill and engineering principles address design before implementation. |
| Review | One small checklist per factory stage. Independent review is conditional. | Includes specialized review and multi-model workflows, including `interrogate`. |
| Memory | Project files and a draft taste index. Cross-project memory is unresolved. | Includes `reflect`, `correct`, and other skills for improving workflows and encoding lessons. |
| Parallel work | Allowed only with authorization and a clear benefit. No model router is implemented here. | Provides model routing and parallel workflows such as `arena` and `swarm`. |
| Maturity | Draft instructions; no product walkthrough yet. | A broader published skill stack with many playbooks and harness integrations. |

The approaches are complementary. This project focuses on the product journey and the user's decisions. pstack offers deeper engineering playbooks. Neither description proves quality, cost savings, or safety.

## Use in Pi

Pi discovers project skills under `.agents/skills/` when the project is in scope. Open Pi in this project and run `/reload` after changing the skills. Inspect Pi's skill list or startup diagnostics. Invoke a stage directly, for example `/skill:factory-idea`, when you need to force selection.

These instructions are project-local. They do not make the skills available in other projects. The project rules refer to optional global `project-start`, `pi-subagents`, and autoresearch guidance that is not included here. Other users must provide equivalent rules or adapt those references. Cross-project distribution, shared taste storage, and compatibility with other agents remain open decisions.

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
