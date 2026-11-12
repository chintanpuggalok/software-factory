import http.server
import tempfile
import threading
import unittest
from pathlib import Path

import browser_verify


class BrowserIntegrationTests(unittest.TestCase):
    def test_browser_runs_acceptance_and_detects_failure(self):
        if not browser_verify.find_chromium():
            self.skipTest('Chromium unavailable')
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / 'index.html'
            page.write_text('<html><head><title>test</title></head><body><button id="b" onclick="this.textContent=\'ok\'">go</button></body></html>')
            contract = {'version': 1, 'actions': [{'action': 'click', 'selector': '#b'},
                       {'action': 'expect_text', 'selector': '#b', 'text': 'ok'}]}
            report = browser_verify.probe(page, acceptance=contract)
            if report['status'] == 'unavailable':
                self.skipTest(report['reason'])
            self.assertEqual(report['status'], 'passed', report)
            contract['actions'][1]['text'] = 'wrong'
            self.assertEqual(browser_verify.probe(page, acceptance=contract)['status'], 'failed')

    def test_browser_network_isolated_from_host(self):
        if not browser_verify.find_chromium():
            self.skipTest('Chromium unavailable')
        requests = []
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                requests.append(self.path)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'ok')
            def log_message(self, *args):
                pass
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as directory:
                page = Path(directory) / 'index.html'
                page.write_text('<html><head><title>initial</title></head><body>test<script>'
                    f'fetch("http://127.0.0.1:{server.server_port}/probe").then(() => document.title="connected")'
                    '.catch(() => document.title="blocked");</script></body></html>')
                report = browser_verify.probe(page)
                if report['status'] == 'unavailable':
                    self.skipTest(report['reason'])
                self.assertEqual(report['status'], 'passed', report)
                self.assertEqual(report['title'], 'blocked')
                self.assertEqual(requests, [])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


if __name__ == '__main__':
    unittest.main()
