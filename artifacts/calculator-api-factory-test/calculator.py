"""Local HTTP calculator using only the Python standard library."""
import json
import math
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MAX_BODY = 4096
OPERATIONS = {
    '/add': lambda a, b: a + b,
    '/subtract': lambda a, b: a - b,
    '/multiply': lambda a, b: a * b,
    '/divide': lambda a, b: a / b,
}


def calculate(path, data):
    """Return a finite result or raise ValueError for invalid input."""
    if not isinstance(data, dict) or set(data) != {'a', 'b'}:
        raise ValueError('Body must contain only a and b.')
    values = []
    for name in ('a', 'b'):
        value = data[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError('Operands must be finite numbers.')
        try:
            value = float(value)
        except OverflowError:
            raise ValueError('Operands must be finite numbers.') from None
        if not math.isfinite(value):
            raise ValueError('Operands must be finite numbers.')
        values.append(value)
    a, b = values
    if path == '/divide' and b == 0:
        raise ValueError('Division by zero is not allowed.')
    result = OPERATIONS[path](a, b)
    if not math.isfinite(result):
        raise ValueError('Result must be finite.')
    return result


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, body):
        encoded = json.dumps(body, allow_nan=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_POST(self):
        if self.path not in OPERATIONS:
            self.respond(404, {'error': 'Unknown endpoint.'})
            return
        if self.headers.get_content_type() != 'application/json':
            self.respond(415, {'error': 'Content-Type must be application/json.'})
            return
        try:
            length = int(self.headers.get('Content-Length', ''))
        except ValueError:
            self.respond(400, {'error': 'A valid Content-Length is required.'})
            return
        if not 0 <= length <= MAX_BODY:
            self.respond(413, {'error': 'Invalid or oversized body.'})
            return
        try:
            data = json.loads(self.rfile.read(length))
        except (ValueError, UnicodeDecodeError, RecursionError):
            self.respond(400, {'error': 'Body must be valid JSON.'})
            return
        try:
            result = calculate(self.path, data)
        except ValueError as error:
            self.respond(400, {'error': str(error)})
            return
        self.respond(200, {'result': result})

    def do_GET(self):
        self.respond(405, {'error': 'Use POST.'})


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 8000), Handler)
    print('Calculator listening on http://127.0.0.1:8000', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
