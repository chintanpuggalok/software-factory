import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pi_static


class StaticTests(unittest.TestCase):
    def setup_plan(self, folder):
        path = Path(folder) / '.factory'
        path.mkdir()
        stages = [{'name': n, 'output': 'draft', 'audit': 'PASS'} for n in
                  ('idea', 'spec', 'design', 'architecture', 'plan')]
        (path / 'pi-plan.json').write_text(json.dumps({'goal': 'goal', 'stages': stages}))

    def test_saved_runtime_mismatch_blocks_build(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / '.factory'
            path.mkdir()
            stages = [{'name': n, 'output': 'draft', 'audit': 'PASS'} for n in
                      ('idea', 'spec', 'design', 'architecture', 'plan')]
            (path / 'pi-plan.json').write_text(json.dumps(
                {'goal': 'goal', 'runtime': 'pi', 'stages': stages}))
            called = []
            with self.assertRaisesRegex(ValueError, 'different runtime'):
                pi_static.generate(folder, 'goal', subscription_confirmed=True,
                                   invoke_fn=lambda *args: called.append(True),
                                   expected_runtime='opencode')
            self.assertEqual(called, [])

    def test_saved_runtime_missing_stays_compatible(self):
        with tempfile.TemporaryDirectory() as folder:
            self.setup_plan(folder)
            document = '<html><head><title>ok</title></head><body>ok</body></html>'
            path = pi_static.generate(folder, 'goal', subscription_confirmed=True,
                                      invoke_fn=lambda *args: document, expected_runtime='opencode')
            self.assertEqual(path.read_text(), document)

    def test_writes_one_document_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as folder:
            self.setup_plan(folder)
            document = '<html><head><title>Test</title></head><body>test</body></html>'
            fake = lambda workspace, prompt, confirmed: document
            path = pi_static.generate(folder, 'goal', subscription_confirmed=True, invoke_fn=fake)
            self.assertEqual(path.read_text(), document)
            report = json.loads((path.parent / 'verification.json').read_text())
            self.assertEqual(report['status'], 'passed')
            self.assertFalse(report['browser_verified'])
            def no_call(*args):
                self.fail('Completed build must not call Pi again')
            self.assertEqual(pi_static.generate(folder, 'goal', subscription_confirmed=True, invoke_fn=no_call), path)
            self.assertEqual(path.read_text(), document)

    def test_rejects_invalid_output(self):
        with tempfile.TemporaryDirectory() as folder:
            self.setup_plan(folder)
            with self.assertRaises(ValueError):
                pi_static.generate(folder, 'goal', subscription_confirmed=True,
                                   invoke_fn=lambda *args: 'not html')

    def test_repairs_once_and_records_only_verified_output(self):
        with tempfile.TemporaryDirectory() as folder:
            self.setup_plan(folder)
            outputs = iter(['<html>bad</html>', '<html><head><title>ok</title></head><body>ok</body></html>'])
            path = pi_static.generate(folder, 'goal', subscription_confirmed=True,
                                      invoke_fn=lambda *args: next(outputs))
            self.assertIn('<title>ok</title>', path.read_text())

    def test_two_bad_outputs_do_not_create_artifact(self):
        with tempfile.TemporaryDirectory() as folder:
            self.setup_plan(folder)
            with self.assertRaisesRegex(ValueError, 'after one repair'):
                pi_static.generate(folder, 'goal', subscription_confirmed=True,
                                   invoke_fn=lambda *args: '<html>bad</html>')
            self.assertFalse((Path(folder) / '.factory-build/index.html').exists())

    def test_existing_report_blocks_before_model_call(self):
        with tempfile.TemporaryDirectory() as folder:
            self.setup_plan(folder)
            out = Path(folder) / '.factory-build'
            out.mkdir()
            (out / 'verification.json').write_text('{}')
            called = []
            with self.assertRaises(FileExistsError):
                pi_static.generate(folder, 'goal', subscription_confirmed=True,
                                   invoke_fn=lambda *args: called.append(True))
            self.assertEqual(called, [])

    def test_interrupted_build_recovers_without_model_call(self):
        with tempfile.TemporaryDirectory() as folder:
            self.setup_plan(folder)
            out = Path(folder) / '.factory-build'
            out.mkdir()
            document = '<html><head><title>ok</title></head><body>ok</body></html>'
            record = {'goal_sha256': hashlib.sha256(b'goal').hexdigest(),
                      'sha256': hashlib.sha256(document.encode()).hexdigest(), 'document': document}
            (out / 'pending.json').write_text(json.dumps(record))
            (out / 'index.html').write_text(document)
            def no_call(*args):
                self.fail('Recovery must not call Pi')
            path = pi_static.generate(folder, 'goal', subscription_confirmed=True, invoke_fn=no_call)
            self.assertEqual(path.read_text(), document)
            self.assertFalse((out / 'pending.json').exists())
            self.assertEqual(json.loads((out / 'verification.json').read_text())['status'], 'passed')

    def test_real_process_exit_after_pending_record_recovers(self):
        with tempfile.TemporaryDirectory() as folder:
            self.setup_plan(folder)
            script = '''\
import os, sys
import pi_static
original = pi_static._recover
def interrupt(folder, goal):
    if (folder / 'pending.json').exists():
        os._exit(17)
    return original(folder, goal)
pi_static._recover = interrupt
pi_static.generate(sys.argv[1], 'goal', subscription_confirmed=True,
                   invoke_fn=lambda *args: '<html><head><title>ok</title></head><body>ok</body></html>')
'''
            result = subprocess.run([sys.executable, '-c', script, folder], capture_output=True, text=True)
            self.assertEqual(result.returncode, 17, result.stderr)
            def no_call(*args):
                self.fail('Recovery must not call Pi')
            path = pi_static.generate(folder, 'goal', subscription_confirmed=True, invoke_fn=no_call)
            self.assertTrue(path.is_file())
            self.assertTrue((path.parent / 'verification.json').is_file())
            self.assertFalse((path.parent / 'pending.json').exists())

    def test_corrupt_pending_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            self.setup_plan(folder)
            out = Path(folder) / '.factory-build'
            out.mkdir()
            (out / 'pending.json').write_text('{invalid')
            with self.assertRaises(json.JSONDecodeError):
                pi_static.generate(folder, 'goal', subscription_confirmed=True)
            self.assertEqual((out / 'pending.json').read_text(), '{invalid')

    def test_conflicting_existing_file_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            self.setup_plan(folder)
            out = Path(folder) / '.factory-build'
            out.mkdir()
            document = '<html><head><title>ok</title></head><body>ok</body></html>'
            record = {'goal_sha256': hashlib.sha256(b'goal').hexdigest(),
                      'sha256': hashlib.sha256(document.encode()).hexdigest(), 'document': document}
            (out / 'pending.json').write_text(json.dumps(record))
            (out / 'index.html').write_text('user changes')
            with self.assertRaisesRegex(ValueError, 'differs'):
                pi_static.generate(folder, 'goal', subscription_confirmed=True)
            self.assertEqual((out / 'index.html').read_text(), 'user changes')

    def test_requires_matching_plan_and_attestation(self):
        with tempfile.TemporaryDirectory() as folder:
            self.setup_plan(folder)
            with self.assertRaises(ValueError):
                pi_static.generate(folder, 'different', subscription_confirmed=True)
            with self.assertRaises(ValueError):
                pi_static.generate(folder, 'goal')


if __name__ == '__main__':
    unittest.main()
