import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pi_adapter
import pi_workflow


class PlanningTests(unittest.TestCase):
    def test_runs_and_resumes_without_new_calls(self):
        calls = []
        def fake(workspace, prompt, confirmed):
            calls.append(prompt)
            return 'PASS' if 'Return exactly one verdict' in prompt else 'Draft with assumptions'
        with tempfile.TemporaryDirectory() as folder:
            state, blocker = pi_workflow.run_plan(folder, 'test goal', subscription_confirmed=True, invoke_fn=fake)
            self.assertIsNone(blocker)
            self.assertEqual(len(state['stages']), 5)
            self.assertEqual(len(calls), 10)
            pi_workflow.run_plan(folder, 'test goal', subscription_confirmed=True, invoke_fn=fake)
            self.assertEqual(len(calls), 10)

    def test_failed_audit_does_not_advance(self):
        def fake(workspace, prompt, confirmed):
            return 'BLOCKED' if 'Return exactly one verdict' in prompt else 'draft'
        with tempfile.TemporaryDirectory() as folder:
            state, blocker = pi_workflow.run_plan(folder, 'goal', subscription_confirmed=True, invoke_fn=fake)
            self.assertEqual(state['stages'], [])
            self.assertIn('idea', blocker)
            saved = json.loads((Path(folder) / '.factory/pi-plan.json').read_text())
            self.assertEqual(saved['stages'], [])
            self.assertEqual(saved['blocked']['stage'], 'idea')
            self.assertEqual(saved['blocked']['output'], 'draft')

    def test_without_attestation_no_call(self):
        with tempfile.TemporaryDirectory() as folder, patch('pi_adapter.subprocess.run') as run:
            with self.assertRaises(pi_adapter.PrepaidUnavailable):
                pi_workflow.run_plan(folder, 'goal')
            run.assert_not_called()

    def test_rejects_invalid_saved_state(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / '.factory'
            path.mkdir()
            (path / 'pi-plan.json').write_text(json.dumps({'version': 1, 'goal': 'goal', 'stages': [{'name': 'spec', 'output': 'x', 'audit': 'PASS'}]}))
            with self.assertRaises(ValueError):
                pi_workflow.run_plan(folder, 'goal', subscription_confirmed=True)

    def test_audit_receives_prior_stage_context(self):
        prompts = []
        def fake(workspace, prompt, confirmed):
            prompts.append(prompt)
            return 'PASS' if 'Return exactly one verdict' in prompt else 'stage evidence'
        with tempfile.TemporaryDirectory() as folder:
            pi_workflow.run_plan(folder, 'goal', subscription_confirmed=True,
                                 invoke_fn=fake, max_new_stages=2)
            self.assertIn('Prior stages:', prompts[3])
            self.assertIn('stage evidence', prompts[3])

    def test_research_runs_once_for_design_and_is_persisted(self):
        calls = []
        def fake(workspace, prompt, confirmed):
            return 'PASS' if 'Return exactly one verdict' in prompt else 'draft'
        def research(query):
            calls.append(query)
            return {'query': query, 'results': [], 'limitation': 'not evidence'}
        with tempfile.TemporaryDirectory() as folder:
            state, blocker = pi_workflow.run_plan(folder, 'goal', subscription_confirmed=True,
                invoke_fn=fake, research_query='public query', research_fn=research)
            self.assertIsNone(blocker)
            self.assertEqual(calls, ['public query'])
            self.assertEqual(state['research']['query'], 'public query')
            pi_workflow.run_plan(folder, 'goal', subscription_confirmed=True,
                invoke_fn=fake, research_query='public query', research_fn=research)
            self.assertEqual(calls, ['public query'])

    def test_no_tools_command(self):
        with tempfile.TemporaryDirectory() as folder, \
                patch('pi_adapter.shutil.which', return_value='/fake/pi'), \
                patch('pi_adapter.subprocess.run') as run:
            pi_adapter.run_text(folder, 'test', subscription_confirmed=True)
            command = run.call_args.args[0]
            self.assertIn('--no-tools', command)
            self.assertIn('--no-context-files', command)
            self.assertIn('--no-mcp', command)


if __name__ == '__main__':
    unittest.main()
