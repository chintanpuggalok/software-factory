# Local calculator API

Requires Python 3. No packages are required.

Start the server from this directory:

```sh
python3 calculator.py
```

The server listens on `127.0.0.1:8000`. Press Ctrl+C to stop it. In another terminal, call each API:

```sh
curl -sS -H 'Content-Type: application/json' -d '{"a":6,"b":3}' http://127.0.0.1:8000/add
curl -sS -H 'Content-Type: application/json' -d '{"a":6,"b":3}' http://127.0.0.1:8000/subtract
curl -sS -H 'Content-Type: application/json' -d '{"a":6,"b":3}' http://127.0.0.1:8000/multiply
curl -sS -H 'Content-Type: application/json' -d '{"a":6,"b":3}' http://127.0.0.1:8000/divide
```

Each response is JSON, for example `{"result": 9.0}`. The operands must be finite JSON numbers. The body must contain exactly `a` and `b`. Calculations use Python floating-point arithmetic. Non-finite results are rejected.

Invalid input and division by zero return HTTP 400 with a JSON `error`. Unknown POST paths return 404. A wrong content type returns 415. Bodies larger than 4096 bytes return 413. GET returns 405. The server is for local use only.

Run the tests:

```sh
python3 -m unittest -v test_calculator
```
