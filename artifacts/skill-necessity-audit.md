# Skill necessity audit

## Method
For each skill, the author checked four questions:

1. Does it have a unique job that no other skill performs?
2. Is it referenced by a stage, playbook, route, or project rule?
3. Does removing it lose safety, evidence, or a required user decision?
4. Is it exercised by the coordinator or a tested path?

Reference counts came from a repository scan. This is a static audit, not a live routing measurement.

## Removed as unnecessary

| Skill | Evidence | Disposition |
|---|---|---|
| `factory-autonomous` | Zero inbound references. Its continuity and stop rules duplicated `AGENTS.md`. The coordinator, not the skill, runs the loop. | Goal, scope, and completion-criteria step moved to `factory-route`. Continuation rules already live in `AGENTS.md`. |
| `factory-preferences` | Overlapped `factory-taste` on promotion, scope separation, and privacy. Only three references, all replaceable. | User-wide index path, storage consent, and harness fallback moved to `factory-taste`. |
| `factory-eval` | One reference, from `AGENTS.md`. No stage invoked it. | Baseline, case set, permission-boundary case, and cost evidence moved into `factory-learn` step 4–5. |

Result: 28 skills became 25. An isolated Pi install discovered all 25 with no diagnostics.

## Kept, with reason

| Skill | Unique job that justifies it |
|---|---|
| `factory-route` | Chooses the entry point, records completion criteria, and handles resume. |
| `factory-idea` / `factory-spec` | Product shaping and acceptance criteria. Different decisions and gates. |
| `factory-design` | Visual and flow direction, taste use, and competitor evidence. |
| `factory-architecture` | Scale, data ownership, interfaces, failure modes, and cost. Separate from planning. |
| `factory-plan` | Bounded decomposition, dependencies, and authorization points. |
| `factory-build` | Authorized implementation and delegation rules. |
| `factory-verify` | Behavior evidence and independent scenario limits. |
| `factory-visual-review` | Running-interface quality and accessibility states. Not covered by tests. |
| `factory-security` | Trust boundaries, credentials, dependencies, and release blocking. Referenced by route and release. |
| `factory-release` | Release evidence, approvals, rollback, and health checks. |
| `factory-recover` | Safe resume, attempt limits, and repeated-effect protection. |
| `factory-learn` | Captures causes and validates workflow changes. Now includes evaluation. |
| `factory-taste` | Project and user-wide preferences, with hypotheses kept separate. |
| `audit-*` (10) | One gate per stage, with a single verdict contract. Each is referenced by its stage or playbook. |
| `asd-ste100` | Required writing standard and structural checks. |

## Considered and rejected for removal
- **`audit-*` skills:** they are small, but they are the only explicit gate at the point of use. Removing them would leave the audit rule in `AGENTS.md` alone, which the earlier review showed is easy to miss.
- **`factory-security`:** its checks are partially duplicated in `audit-release`, but the release audit reviews evidence. It does not perform the security review.
- **`factory-visual-review`:** browser acceptance tests prove behavior, not visual quality.

## Limits
- Reference counts show documentation wiring, not live agent selection.
- A merged skill is shorter overall but its single file is longer. The context cost of merging was not measured.
- Live model validation of the new verdict contract remains blocked by the provider usage limit.
