# Initial skill review

## Validation
- Checked nine skills for frontmatter, matching names, descriptions, and local skill references.
- Confirmed that the factory-local taste index exists.
- Did not run Pi discovery, token measurements, market research, or a product walkthrough.

## Findings
- **High: untested routing and handoffs.** Skill names in prose do not enforce loading or stage transitions. Test with a real idea after `/reload`.
- **High: independent evaluation is conditional.** Holdout separation requires separate access controls or a separate evaluator. The skill explicitly reports when independence is absent.
- **Medium: taste portability is unresolved.** The index is factory-local; product projects cannot assume access to shared memory. Agree on storage and privacy before cross-project use.
- **Medium: competitor ranking may be unavailable.** The design skill asks before treating unverified candidates as market leaders. Test whether this blocks work unnecessarily.
- **Medium: token savings are unmeasured.** Short files and selective loading do not guarantee context savings. Measure a real session against a baseline.
- **Medium: ASD-STE100 compliance is not established.** Instructions are intended to be explicit, but no controlled-vocabulary or formal compliance audit was performed.
- **Low: repeated handoff instructions add words.** Consider moving them to shared rules only after testing portability outside this project.

## Next action
Review the skills and walk a real idea through them. Check stage routing, handoff size, approval gates, and taste retrieval.
