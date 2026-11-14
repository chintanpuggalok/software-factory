import http.client
import json
import subprocess
import sys

server = subprocess.Popen([sys.executable, '-u', '-c',
    "from http.server import ThreadingHTTPServer; from calculator import Handler; "
    "s=ThreadingHTTPServer(('127.0.0.1',0),Handler); print(s.server_port,flush=True); s.serve_forever()"],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
try:
    port = int(server.stdout.readline().strip())
    def request(path, body, method='POST', headers=None):
        conn = http.client.HTTPConnection('127.0.0.1', port, timeout=3)
        try:
            conn.request(method, path, body, headers or {'Content-Type': 'application/json'})
            response = conn.getresponse()
            return response.status, json.loads(response.read())
        finally:
            conn.close()

    cases = [('/add', {'a': -12.5, 'b': 2.75}, -9.75),
             ('/subtract', {'a': 3, 'b': 8}, -5),
             ('/multiply', {'a': -7, 'b': -4}, 28),
             ('/divide', {'a': 7, 'b': 2}, 3.5)]
    for path, body, result in cases:
        actual = request(path, json.dumps(body))
        assert actual == (200, {'result': result}), (path, actual)
        print('PASS', path, actual)
    for path, body, status in [('/divide', '{"a":1,"b":0}', 400),
                               ('/add', '{"a":true,"b":1}', 400),
                               ('/add', 'invalid', 400),
                               ('/add', '{"a":1}', 400),
                               ('/unknown', '{"a":1,"b":2}', 404)]:
        actual = request(path, body)
        assert actual[0] == status and 'error' in actual[1], (path, actual)
        print('PASS', path, status, actual[1])
    status, body = request('/add', '', method='GET')
    assert status == 405 and 'error' in body
    print('PASS GET 405', body)
finally:
    server.terminate()
    try:
        server.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server.kill()
        server.wait()
