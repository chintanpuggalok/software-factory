import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from calculator import Handler, calculate


class CalculatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, path, body, method='POST', content_type='application/json'):
        conn = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        try:
            conn.request(method, path, body, {'Content-Type': content_type})
            response = conn.getresponse()
            self.assertEqual(response.getheader('Content-Type'), 'application/json')
            return response.status, json.loads(response.read())
        finally:
            conn.close()

    def test_arithmetic_over_http(self):
        for path, expected in [('/add', 9), ('/subtract', 3), ('/multiply', 18), ('/divide', 2)]:
            with self.subTest(path=path):
                self.assertEqual(self.request(path, '{"a":6,"b":3}'), (200, {'result': expected}))
        self.assertEqual(self.request('/add', '{"a":-1.5,"b":0.25}'), (200, {'result': -1.25}))

    def test_bad_inputs_over_http(self):
        for body in ['{', '[]', '{}', '{"a":1}', '{"a":1,"b":2,"c":3}',
                     '{"a":true,"b":2}', '{"a":"1","b":2}',
                     '{"a":NaN,"b":2}', '{"a":1e999,"b":2}',
                     '{"a":1e308,"b":1e308}']:
            with self.subTest(body=body):
                status, response = self.request('/add', body)
                self.assertEqual(status, 400)
                self.assertIn('error', response)
        status, response = self.request('/divide', '{"a":1,"b":0}')
        self.assertEqual(status, 400)
        self.assertIn('zero', response['error'])
        self.assertEqual(self.request('/add', 'x' * 4097)[0], 413)
        self.assertEqual(self.request('/add', '{}', content_type='text/plain')[0], 415)
        self.assertEqual(self.request('/unknown', '{}')[0], 404)
        self.assertEqual(self.request('/add', '', method='GET')[0], 405)

    def test_core_boundary(self):
        self.assertEqual(calculate('/subtract', {'a': 1, 'b': 4}), -3)
        with self.assertRaises(ValueError):
            calculate('/divide', {'a': 1, 'b': -0.0})
        with self.assertRaises(ValueError):
            calculate('/add', {'a': 10**1000, 'b': 1})


if __name__ == '__main__':
    unittest.main()
