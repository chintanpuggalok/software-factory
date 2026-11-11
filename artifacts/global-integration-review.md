# Global integration review

## Scope
Reviewed the global project rules, the `project-start` skill, Pi settings, the `pi-subagents` skill, and the `autoresearch-create` skill. Reviewed the factory rules and selected factory skills. No subagents or experiments ran.

## Findings

1. **Project startup fits the factory.** Global `project-start` loads project rules, context, plan, and relevant decisions before substantive work. Factory skills use those artifacts. Run startup once per project chat, not once per factory stage. Global startup requirements still apply even if selective loading would read less.
2. **Subagent policy mostly fits.** Both require authorization and a clear benefit. The global subagent skill warns against hard tool or tight usage budgets for workers that can edit files. The factory build skill asks for a cost limit but does not explain that distinction. A spending budget is not necessarily an enforceable tool budget. Align the wording before delegation.
3. **Startup instructions cost context.** Project startup, factory skill descriptions, audit skill descriptions, and the STE skill description can all contribute. The stage skill rule does not override global startup or skills that apply to the task. Actual token cost is not measured.
4. **Automatic discovery is not global distribution.** Factory skills are in this project's `.agents/skills/`. Another unrelated project will not automatically inherit them. This matches the decision to keep them local until finalized. Shared taste storage remains unresolved.
5. **Stage audits are not tool-enforced.** Loading an audit and respecting its result depends on agent behavior. The audit skills do not provide independent review unless a separate reviewer is authorized and used.
6. **STE mode is not verified compliance.** The installed skill lacks the official dictionary. Its rewrite guidance cannot supersede higher-priority rules or permission gates. Meaning and safety requirements must remain unchanged.
7. **Autoresearch has a different scope.** Its skill starts a repeated experiment loop and uses git operations. Do not trigger it merely because the factory wants lower cost or better quality. A specific request and applicable approvals are needed.
8. **Release wording needs a precise gate.** The release audit covers both pre-release and post-deployment checks. Pre-release must not require evidence that can exist only after deployment. Run a separate post-deployment audit for production health.

## Validation
Static review only. No Pi startup diagnostics, live routing, budget enforcement, external STE linter, or end-to-end workflow was tested. The session's last advertised skill list predates the newly created audit and architecture skills. Run `/reload`, then verify the new skill list.

## Follow-up
The factory rules now refer to global startup, subagent, and autoresearch guidance. The build skill separates spending budgets from hard tool limits. The release skill has pre-deployment and post-deployment audits. A pre-deployment pass does not grant deployment approval.

The author checked the 21 skill frontmatters, local skill references, STE support files, and release gate order. This was not an independent review. Live routing, actual budget enforcement, and a product walkthrough remain untested.

## Next action
Run a bounded product walkthrough. Check discovery, stage handoffs, and context use.
