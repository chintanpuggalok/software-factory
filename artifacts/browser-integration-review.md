# Browser integration review

## Scope
The author implemented and reviewed optional browser checks and one bounded repair. This is not an independent security or accessibility audit.

## Evidence
- `python3 -m unittest discover -s tests -q`: 49 tests passed. The integration test confirmed that the isolated browser could not reach a host-local HTTP server.
- A real calculator run resumed from a saved five-stage plan, generated a prototype, and passed the generic browser probe. The probe checks page load, uncaught JavaScript errors, and horizontal overflow at two viewport sizes.
- A separate real test started with a deliberate JavaScript error. The browser failed, Pi repaired a separate candidate, and the browser recheck passed. The original file remained unchanged.
- The calculator-specific Chromium checks also passed for selected arithmetic, interactions, accessibility roles, and contrast.
- If Node, Chromium, Bubblewrap, or sandbox setup is unavailable, the workflow reports browser verification as unavailable. It does not mark the check as passed.

## Limits and risks
- Browser checks are not a security audit, full functional test, complete accessibility audit, or screen-reader test.
- Bubblewrap restricts filesystem and network access for the browser process in this Linux configuration. This is not a proof of complete sandbox security.
- The generic probe does not validate product-specific acceptance criteria or keyboard flows. The calculator-specific checks are separate.
- A repaired candidate is saved separately. Release and deployment are not implemented. No production target was used.
- The user's subscription may incur overages. The coordinator does not enforce a dollar limit.

## Next action
Define a generic acceptance-test contract and a deployment target before enabling autonomous release. Test more crash points and obtain independent security review when authorized.
