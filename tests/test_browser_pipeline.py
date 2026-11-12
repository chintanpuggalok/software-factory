import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import browser_pipeline
import pi_static


class BrowserPipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        stage_names = ('idea', 'spec', 'design', 'architecture', 'plan')
        stages = [{'name': n, 'output': 'plan', 'audit': 'PASS'} for n in stage_names]
        (self.root / '.factory').mkdir()
        (self.root / '.factory/pi-plan.json').write_text(json.dumps({'goal': 'goal', 'stages': stages}))
        self.document = '<html><head><title>Original</title></head><body>ok</body></html>'
        self.original = pi_static.generate(self.root, 'goal', subscription_confirmed=True,
                                           invoke_fn=lambda *args: self.document)

    @staticmethod
    def report(path, status):
        return {'status': status, 'sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest()}

    def test_passed_browser_does_not_call_model(self):
        def no_call(*args):
            self.fail('Pi must not be called')
        result = browser_pipeline.verify_and_repair(self.root, 'goal', self.original,
            subscription_confirmed=True, probe_fn=lambda p: self.report(p, 'passed'), invoke_fn=no_call)
        self.assertEqual(result['browser']['status'], 'passed')
        self.assertFalse(result['repair_attempted'])

    def test_unavailable_is_not_pass_and_does_not_repair(self):
        def no_call(*args):
            self.fail('Pi must not be called')
        result = browser_pipeline.verify_and_repair(self.root, 'goal', self.original,
            subscription_confirmed=True, probe_fn=lambda p: self.report(p, 'unavailable'), invoke_fn=no_call)
        self.assertEqual(result['browser']['status'], 'unavailable')
        self.assertFalse(result['repair_attempted'])

    def test_failed_browser_repairs_once_without_overwriting_original(self):
        def probe(path):
            return self.report(path, 'failed' if Path(path) == self.original else 'passed')
        repaired = '<html><head><title>Fixed</title></head><body>ok</body></html>'
        calls = []
        def invoke(*args):
            calls.append(1)
            return repaired
        result = browser_pipeline.verify_and_repair(self.root, 'goal', self.original,
            subscription_confirmed=True, probe_fn=probe, invoke_fn=invoke)
        self.assertEqual(result['browser']['status'], 'passed')
        self.assertEqual(self.original.read_text(), self.document)
        self.assertEqual(Path(result['artifact']).read_text(), repaired)
        result = browser_pipeline.verify_and_repair(self.root, 'goal', self.original,
            subscription_confirmed=True, probe_fn=probe, invoke_fn=invoke)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result['browser']['status'], 'passed')

    def test_modified_original_is_not_reused(self):
        self.original.write_text('user edit')
        with self.assertRaises(ValueError):
            browser_pipeline.verify_and_repair(self.root, 'goal', self.original,
                subscription_confirmed=True, probe_fn=lambda p: self.report(p, 'passed'))
        self.assertEqual(self.original.read_text(), 'user edit')


if __name__ == '__main__':
    unittest.main()
