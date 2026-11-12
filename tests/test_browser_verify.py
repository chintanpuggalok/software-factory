import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import browser_verify


class BrowserVerifyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.page = Path(self.tmp.name) / 'index.html'
        self.page.write_text('<html><body>test</body></html>')

    def test_acceptance_contract_requires_assertion(self):
        with self.assertRaises(ValueError):
            browser_verify.validate_acceptance({'version': 1, 'actions': [{'action': 'key', 'key': '1'}]})

    def test_acceptance_contract_rejects_arbitrary_code_and_fields(self):
        with self.assertRaises(ValueError):
            browser_verify.validate_acceptance({'version': 1, 'actions': [{'action': 'eval', 'code': '1'}]})
        with self.assertRaises(ValueError):
            browser_verify.validate_acceptance({'version': 1, 'actions': [{'action': 'expect_exists', 'selector': 'body', 'extra': 'x'}]})

    def test_missing_dependencies_are_not_a_pass(self):
        with patch('browser_verify.shutil.which', return_value=None), patch('browser_verify.find_chromium', return_value=None):
            self.assertEqual(browser_verify.probe(self.page)['status'], 'unavailable')

    def test_page_failure_is_reported(self):
        result = subprocess.CompletedProcess([], 0, json.dumps({'status':'failed','script_errors':['bad']}), '')
        with patch('browser_verify.shutil.which', return_value='/bin/fake'), \
             patch('browser_verify.find_chromium', return_value='/bin/fake'), \
             patch('browser_verify.subprocess.run', return_value=result):
            report = browser_verify.probe(self.page)
            self.assertEqual(report['status'], 'failed')
            self.assertEqual(report['script_errors'], ['bad'])

    def test_infrastructure_failure_does_not_pass(self):
        result = subprocess.CompletedProcess([], 1, '', 'sandbox failed')
        with patch('browser_verify.shutil.which', return_value='/bin/fake'), \
             patch('browser_verify.find_chromium', return_value='/bin/fake'), \
             patch('browser_verify.subprocess.run', return_value=result):
            report = browser_verify.probe(self.page)
            self.assertEqual(report['status'], 'unavailable')

    def test_timeout_is_a_failure(self):
        with patch('browser_verify.shutil.which', return_value='/bin/fake'), \
             patch('browser_verify.find_chromium', return_value='/bin/fake'), \
             patch('browser_verify.subprocess.run', side_effect=subprocess.TimeoutExpired('node', 30)):
            self.assertEqual(browser_verify.probe(self.page)['status'], 'failed')


if __name__ == '__main__':
    unittest.main()
