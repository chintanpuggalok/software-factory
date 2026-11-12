# Calculator workflow test

## Goal
Build a responsive calculator web app with arithmetic, keyboard input, accessible controls, and division-by-zero handling.

## Result
The first run passed idea and spec, then blocked at design. Search snippets did not describe competitor interfaces. The audit prompt also omitted prior stage outputs.

The revised run inspected static HTML from Calculator.net and Desmos. It passed the five model-audited planning stages. The Desmos page returned only a loading shell. Neither page establishes market share or proves a visual interaction flow.

A no-tools Pi generator wrote `.factory-build/index.html` from the saved plan. The coordinator now supports this bounded build with `--build-static`. A separate run from a saved plan confirmed that the integrated command creates a file. It did not deploy the app.

## Verification
- `python3 -m unittest discover -s tests -q`: 37 tests passed, including tests that a failed plan does not build, a passed plan continues, and an interrupted build can recover safely.
- `node artifacts/calculator-test/smoke.js artifacts/calculator-test/.factory-build/index.html`: arithmetic, precision, keyboard sequence, clear, and division-by-zero smoke checks passed in a fake DOM.
- `node artifacts/calculator-test/browser-check.mjs`: isolated Chromium checks passed for arithmetic, keyboard and click input, accessibility roles, text contrast, and mobile/desktop overflow. Screenshots are in `screenshots/`.
- The first browser pass found ten low-contrast text elements. The author darkened those colors and reran the checks successfully. This was a manual repair, not an autonomous repair.
- Screen-reader behavior and the complete acceptance criteria remain untested.
- Model audits are not independent proof. The generated app is untrusted prototype code and has not had a security audit.

## Next action
Add automatic verification and safe recovery to the build stage. Test screen-reader behavior and the remaining acceptance criteria before release.
