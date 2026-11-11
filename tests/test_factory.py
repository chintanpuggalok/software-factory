import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "factory.py"


class FactoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.workspace = Path(self.tmp.name)
        self.state = self.workspace / '.factory' / 'state.json'

    def invoke(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), str(self.workspace), '--goal', 'sample', *args],
                              text=True, capture_output=True)

    def test_simulated_end_to_end(self):
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads(self.state.read_text())
        self.assertEqual(len(state['stages']), 8)
        self.assertTrue(all(x['status'] == x['audit'] == 'passed' for x in state['stages']))
        self.assertIn('Simulated release', state['stages'][-1]['evidence'])

    def test_failure_blocks_and_resume(self):
        result = self.invoke('--fail-stage', 'verify')
        self.assertEqual(result.returncode, 1)
        state = json.loads(self.state.read_text())
        self.assertEqual(state['stages'][6]['status'], 'failed')
        self.assertEqual(state['stages'][7]['status'], 'pending')
        self.assertEqual(self.invoke().returncode, 0)
        self.assertEqual(json.loads(self.state.read_text())['stages'][7]['status'], 'passed')

    def test_interrupted_simulation_resumes(self):
        self.invoke('--fail-stage', 'build')
        state = json.loads(self.state.read_text())
        state['stages'][5] = {'name': 'build', 'status': 'running'}
        self.state.write_text(json.dumps(state))
        self.assertEqual(self.invoke().returncode, 0)

    def test_tampered_pass_does_not_advance(self):
        self.invoke('--fail-stage', 'build')
        state = json.loads(self.state.read_text())
        state['stages'][0].pop('audit')
        self.state.write_text(json.dumps(state))
        result = self.invoke()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(self.state.read_text())['stages'][7]['status'], 'pending')

    def test_pi_is_blocked_without_model_call(self):
        result = self.invoke('--mode', 'pi')
        self.assertEqual(result.returncode, 2)
        self.assertIn('no Pi call was made', result.stderr)
        self.assertFalse(self.state.exists())

    def test_changed_goal_is_rejected(self):
        self.invoke()
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.workspace), '--goal', 'other'],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)


if __name__ == '__main__':
    unittest.main()
