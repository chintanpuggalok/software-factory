# Browser acceptance review

## Scope
The author implemented a bounded browser acceptance contract. This was not an independent review.

## Evidence
- The calculator contract in `calculator-test/acceptance.json` has 13 actions. An isolated Chromium run passed all 13.
- An integrated coordinator run resumed a saved five-stage plan, reused a hash-matched prototype, ran the contract, and wrote browser evidence. It exited successfully.
- The tests cover a passing browser contract, a failing assertion, invalid contracts, a missing browser, sandbox network isolation, bounded repair, and preservation of the original file.
- Browser repair was tested with a real Pi call against an intentionally broken page. The initial browser check failed, the repaired candidate passed, and the original remained unchanged.

## Limits
- The contract supports a small set of clicks, keys, resets, and DOM text or existence checks. It does not prove full product correctness, screen-reader behavior, visual quality, or security.
- The model must not be allowed to redefine the acceptance contract merely to pass a failure. Contract generation and review are not automated here.
- Bubblewrap and Chromium are optional. If unavailable, browser verification is unavailable, not passed.
- Real deployment, browser screenshots in the generic verifier, and external-effect recovery are not implemented.
