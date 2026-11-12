# Static verification and repair review

## Scope
The author implemented and reviewed bounded checks for generated static HTML. This is not an independent security or code review.

## Evidence
- `python3 -m unittest discover -s tests -q`: 39 tests passed. They include a real process exit after a pending record, recovery without a model call, and preservation of conflicting user files.
- `node artifacts/calculator-test/browser-check.mjs`: isolated Chromium checks passed for calculator arithmetic, interaction scenarios, native browser keyboard input, accessibility roles, contrast, and two viewports.
- A real Pi repair test supplied an intentionally incomplete document. The second call repaired it. The structural report passed and correctly marked browser verification as false.
- The generator refuses to overwrite an existing prototype or verification record. Tests cover this behavior.

## Limitations
- Structural checks do not prove that HTML or JavaScript is secure, functional, accessible, or free of network behavior. Obfuscated code can evade simple checks.
- The one automatic repair is based on static findings. Browser failures are not yet routed back to the model.
- A complete pending record can restore a matching interrupted build without another model call. A partial output that differs from the record, a corrupt pending record, or a conflicting user file blocks recovery. The generator does not overwrite it.
- The calculator has no screen-reader validation. There is no automatic deployment or configured release target.

## Next action
Decide whether Chromium and Bubblewrap can be optional dependencies for browser verification. Integrate bounded browser checks and repair after that decision. Keep real deployment disabled until its target and recovery rules are configured.
