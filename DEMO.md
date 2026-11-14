# Software Factory: calculator API demo

This demo records one real agent-led run. It does not establish production readiness or prove that every project will complete without intervention.

## Prerequisites

- Pi with a working model and the factory extension loaded.
- Python 3 for this example.
- Permission to use the selected model. Usage may incur charges. The agent-led path does not enforce a dollar limit.

The run below used the **local development version** of the factory. In that version, `/factory <goal>` starts an agent turn in interactive Pi. Do not assume an older installed package has the same behavior. Reload Pi after updating the extension. The agent-led command does not run in Pi print mode.

## Start a factory run

Create or open a project directory. Start Pi from that directory:

```sh
mkdir -p calculator-api
cd calculator-api
pi
```

In interactive Pi, enter a goal with explicit boundaries:

```text
/factory Build a simple local calculator backend with four HTTP APIs: add, subtract, multiply and divide between two operands. Implement and test it end to end in this project. Document how to run and call each API. Handle invalid input and division by zero. No dependency installation, paid services, or deployment.
```

The factory should start an agent turn, inspect project instructions, select an appropriate workflow, implement the authorized scope, and run checks and audits. It may ask for a decision or stop when blocked. Review its changes and evidence. A factory verdict is not an independent guarantee.

Use `/factory` or `/factory resume` to resume work. Use `/factory status` to inspect saved coordinator status. `/factory help` lists commands. The advanced `plan`, `build`, and `simulate` commands use the separate coordinator. The agent-led run uses the current Pi model and session.

## What happened in this run

- The goal above ran in an interactive Pi subprocess in a fresh project directory.
- The agent created a Python standard-library HTTP service, documentation, tests, and local factory records. It recorded build and verification self-audits as PASS.
- The run recorded completion after approximately 166 seconds. The harness closed the idle terminal afterward. It did not install dependencies or deploy.
- A separate supervisor-written client started the handler in another process and checked all four operations, zero division, malformed and missing input, a boolean operand, an unknown path, and an unsupported method. Those checks and the generated three-test suite passed. The separate client was written after the build. It is not an independent reviewer or a pre-build holdout.

The generated service and test client are in [`artifacts/calculator-api-factory-test/`](artifacts/calculator-api-factory-test/). The review is in [`docs/factory/subprocess-review.md`](artifacts/calculator-api-factory-test/docs/factory/subprocess-review.md). The raw test output is in [`docs/factory/independent-check.log`](artifacts/calculator-api-factory-test/docs/factory/independent-check.log).

## Try the generated calculator

From the repository root:

```sh
cd artifacts/calculator-api-factory-test
python3 calculator.py
```

In another terminal, send JSON operands to any endpoint:

```sh
curl -sS -H 'Content-Type: application/json' -d '{"a":6,"b":3}' http://127.0.0.1:8000/add
curl -sS -H 'Content-Type: application/json' -d '{"a":6,"b":3}' http://127.0.0.1:8000/subtract
curl -sS -H 'Content-Type: application/json' -d '{"a":6,"b":3}' http://127.0.0.1:8000/multiply
curl -sS -H 'Content-Type: application/json' -d '{"a":6,"b":3}' http://127.0.0.1:8000/divide
```

The expected results are `9.0`, `3.0`, `18.0`, and `2.0`. Stop the server with Ctrl+C. Run the tests with:

```sh
python3 -B -m unittest -v test_calculator
python3 -B independent_check.py
```

The server binds to loopback, has no authentication, and uses floating-point arithmetic. It is a local demonstration, not a production service. Load, remote security, deployment, and arbitrary product workflows were not validated.
