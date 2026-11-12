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
            return 'PASS' if 'Return only one line' in prompt else 'Draft with assumptions'
        with tempfile.TemporaryDirectory() as folder:
            state, blocker = pi_workflow.run_plan(folder, 'test goal', subscription_confirmed=True, invoke_fn=fake)
            self.assertIsNone(blocker)
            self.assertEqual(len(state['stages']), 5)
            self.assertEqual(len(calls), 10)
            pi_workflow.run_plan(folder, 'test goal', subscription_confirmed=True, invoke_fn=fake)
            self.assertEqual(len(calls), 10)

    def test_failed_audit_does_not_advance(self):
        def fake(workspace, prompt, confirmed):
            return 'BLOCKED' if 'Return only one line' in prompt else 'draft'
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
            return 'PASS' if 'Return only one line' in prompt else 'stage evidence'
        with tempfile.TemporaryDirectory() as folder:
            pi_workflow.run_plan(folder, 'goal', subscription_confirmed=True,
                                 invoke_fn=fake, max_new_stages=2)
            self.assertIn('Prior stages:', prompts[3])
            self.assertIn('stage evidence', prompts[3])

    def test_research_runs_once_for_design_and_is_persisted(self):
        calls = []
        def fake(workspace, prompt, confirmed):
            return 'PASS' if 'Return only one line' in prompt else 'draft'
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


class VerdictTests(unittest.TestCase):
    def test_accepts_one_verdict_line(self):
        self.assertEqual(pi_workflow.parse_verdict('PASS: ok'), 'PASS: ok')
        self.assertEqual(pi_workflow.parse_verdict('\nPASS\n'), 'PASS: audit passed')
        self.assertEqual(pi_workflow.parse_verdict('REVISE: missing tests'), 'REVISE: missing tests')
        self.assertEqual(pi_workflow.parse_verdict('BLOCKED: no access'), 'BLOCKED: no access')

    def test_rejects_tool_markup_and_missing_reason(self):
        self.assertIsNone(pi_workflow.parse_verdict('<calls>\n<invoke name="bash">'))
        self.assertIsNone(pi_workflow.parse_verdict('REVISE'))
        self.assertIsNone(pi_workflow.parse_verdict('I think it is fine'))
        self.assertIsNone(pi_workflow.parse_verdict(''))

    def test_invalid_verdict_gets_one_correction(self):
        replies = iter(['draft', '<calls>\n<invoke name="bash">', 'PASS: corrected'])
        calls = []
        def fake(workspace, prompt, confirmed):
            calls.append(prompt)
            return next(replies)
        with tempfile.TemporaryDirectory() as folder:
            state, blocker = pi_workflow.run_plan(folder, 'goal', subscription_confirmed=True,
                                                  invoke_fn=fake, max_new_stages=1)
            self.assertIsNone(blocker)
            self.assertEqual(len(calls), 3)
            self.assertIn('not a valid verdict', calls[2])
            self.assertTrue(state['stages'][0]['audit'].startswith('PASS'))

    def test_two_invalid_verdicts_block(self):
        def fake(workspace, prompt, confirmed):
            return 'draft' if 'Return only one line' not in prompt else '<calls>'
        with tempfile.TemporaryDirectory() as folder:
            state, blocker = pi_workflow.run_plan(folder, 'goal', subscription_confirmed=True,
                                                  invoke_fn=fake, max_new_stages=1)
            self.assertIn('invalid audit verdict', blocker)
            self.assertEqual(state['stages'], [])


class ArtifactTests(unittest.TestCase):
    def test_passed_stage_writes_artifact_once(self):
        def fake(workspace, prompt, confirmed):
            return 'PASS: ok' if 'Return only one line' in prompt else 'draft evidence'
        with tempfile.TemporaryDirectory() as folder:
            state, blocker = pi_workflow.run_plan(folder, 'goal', subscription_confirmed=True,
                                                  invoke_fn=fake, max_new_stages=1)
            self.assertIsNone(blocker)
            path = Path(folder) / 'docs/factory/idea.md'
            self.assertTrue(path.is_file())
            self.assertIn('Verdict: PASS: ok', path.read_text())
            self.assertEqual(state['stages'][0]['artifact'], 'docs/factory/idea.md')
            path.write_text('user edit')
            pi_workflow.run_plan(folder, 'goal', subscription_confirmed=True,
                                 invoke_fn=fake, max_new_stages=1)
            self.assertEqual(path.read_text(), 'user edit')

    def test_existing_artifact_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'docs/factory/spec.md'
            target.parent.mkdir(parents=True)
            target.write_text('existing')
            path, created = pi_workflow.persist_artifact(folder, 'spec', 'PASS: ok', 'new')
            self.assertFalse(created)
            self.assertEqual(path.read_text(), 'existing')


class RevisionTests(unittest.TestCase):
    def test_revise_triggers_one_regeneration(self):
        replies = iter(['draft', 'REVISE: add evidence', 'revised draft', 'PASS: fixed'])
        prompts = []
        def fake(workspace, prompt, confirmed):
            prompts.append(prompt)
            return next(replies)
        with tempfile.TemporaryDirectory() as folder:
            state, blocker = pi_workflow.run_plan(folder, 'goal', subscription_confirmed=True,
                                                  invoke_fn=fake, max_new_stages=1)
            self.assertIsNone(blocker)
            self.assertIn('did not pass the audit', prompts[2])
            self.assertIn('REVISE: add evidence', prompts[2])
            self.assertTrue(state['stages'][0]['audit'].startswith('PASS'))

    def test_second_revise_blocks(self):
        def fake(workspace, prompt, confirmed):
            if 'Return only one line' in prompt:
                return 'REVISE: still missing evidence'
            return 'draft'
        with tempfile.TemporaryDirectory() as folder:
            state, blocker = pi_workflow.run_plan(folder, 'goal', subscription_confirmed=True,
                                                  invoke_fn=fake, max_new_stages=1)
            self.assertIn('still missing evidence', blocker)
            self.assertEqual(state['stages'], [])

    def test_history_gives_newest_stage_full_text(self):
        stages = [{'name': 'idea', 'audit': 'PASS: a', 'output': 'i' * 30000, 'artifact': 'a'},
                  {'name': 'spec', 'audit': 'PASS: b', 'output': 's' * 30000, 'artifact': 'b'}]
        history = pi_workflow.build_history(stages)
        self.assertIn('s' * 20000, history)
        self.assertIn('truncated', history)
