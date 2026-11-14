# Verification audit

PASS: `python3 -m unittest -v test_calculator` exited 0. See `test-output.log`. It checks all operations, malformed and invalid inputs, zero division, size, content type, route, and method errors over local HTTP.

A separate `python3 calculator.py` process served the four documented curl requests. It also returned HTTP 400 for zero division, a boolean operand, and malformed JSON. See `process-output.log`. The process check exited 0. An additional independent request script asserted all four results and three HTTP 400 responses, and exited 0.

The service binds to loopback. It has no authentication and is not intended for remote use. There are no external service bindings or installed dependencies. No UI exists. Browser and accessibility checks do not apply. The author performed the checks and audit. No independent holdout reviewer was available.

Next action: hand off local run instructions. Deployment is outside the authorized scope.
