# DeepSeek skill review

## Scope and method
A read-only reviewer used `opencode-go/deepseek-v4.1-flash` through Pi subagents. It reviewed the 28 skill files, route playbooks, project instructions, and selected coordinator code. It did not use the OpenCode CLI, run tests, or independently verify live agent behavior. The parent ran 52 local tests successfully. The review is a static analysis, not an end-to-end execution test.

## Findings accepted for follow-up
1. **Audit invocation is implicit.** Most stage skills do not name the matching audit. Project rules require an audit, but isolated skill use can miss that rule. Add explicit stage-to-audit handoffs and test them.
2. **Audit verdict handling is ambiguous.** Skills describe `pass`, `revise`, and `blocked`; project rules explicitly forbid advance only for `blocked`. The coordinator accepts exactly `PASS`. Define one contract and prevent advance on unresolved revisions.
3. **Autonomy thresholds are unclear.** Some skills say to ask for required decisions without explaining when a reversible choice can proceed. Preserve higher-priority authorization rules while defining a clear pre-stop check.
4. **Security evidence is not explicit in release audit.** The release skill invokes security review, but the release audit does not explicitly check its evidence or a justified not-applicable result.
5. **Artifacts and audit evidence lack a consistent contract.** Skills do not consistently name output locations, and a passing model audit retains `PASS` without its reasoning. Specify durable project-local records and evidence while avoiding rigid paths for every project.
6. **Routing is incomplete.** The router mixes work types and lifecycle stages, does not explicitly route cold resume to recovery, and omits several stage names. Test actual selection and handoffs.
7. **Research criteria are ambiguous.** Clarify that missing market-share evidence is recorded as unverified, not silently treated as a verified ranking. Keep required evidence gates explicit.
8. **Release evidence is underspecified.** Define target-appropriate health and rollback evidence without inventing endpoints, metrics, or permissions.
9. **Skill changes need review.** Evaluate changed skills and their evidence before adopting them. Use independent review only when authorized.
10. **Autonomous execution remains partial.** The simulator and Pi planning path do not yet execute all stage audits, product-specific checks, and deployment. Do not treat simulated evidence as a real audit.

## Claims needing care
- Strict ASD-STE100 compliance remains unverified without the official dictionary. This does not by itself justify changing the user's selected writing requirement to a weaker mode.
- A planned spending budget and a prohibition on tight tool limits are not necessarily contradictory. No hard per-agent dollar cap is currently enforced.
- A fixed retry count is a proposal, not automatically the right behavior. It must account for authorized budget, failure type, and safe recovery.
- The reviewer identified punctuation and length concerns in existing instructions. Validate them against the applicable standard before claiming formal compliance.

## Next action
Review these findings with the user. Obtain agreement before changing material workflow contracts or adding dependencies. Then repair the accepted items and run structural and live routing tests.
