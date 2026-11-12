import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import factory


class StubRuntime:
    def __init__(self, name='opencode'):
        self.name = name

    def available(self):
        return True

    def run_read_only(self, workspace, prompt, *, confirmed=False):
        return subprocess.CompletedProcess([], 0, 'out', '')


class CLITests(unittest.TestCase):
    def test_passed_plan_continues_to_static_build(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(sys, 'argv', ['factory.py', '.', '--goal', 'goal', '--mode', 'pi-plan',
                                        '--subscription-confirmed', '--build-static']), \
                patch('pi_workflow.run_plan', return_value=({'stages': []}, None)), \
                patch('pi_static.generate', return_value=Path(directory) / 'index.html') as generate, \
                patch('browser_pipeline.verify_and_repair', return_value={'artifact': 'index.html', 'browser': {'status': 'passed'}}), \
                contextlib.redirect_stdout(io.StringIO()) as stdout, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(factory.main(), 0)
            generate.assert_called_once()
            self.assertIn('prototype_path', stdout.getvalue())

    def test_opencode_runtime_plans_when_available(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(sys, 'argv', ['factory.py', directory, '--goal', 'goal', '--mode', 'pi-plan',
                                        '--runtime', 'opencode', '--subscription-confirmed']), \
                patch('runtime_adapter.get_runtime', return_value=StubRuntime('opencode')), \
                patch('pi_workflow.run_plan', return_value=({'stages': [], 'runtime': 'opencode'}, None)) as run_plan, \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(factory.main(), 0)
            self.assertEqual(run_plan.call_args.kwargs['runtime'].name, 'opencode')

    def test_declared_runtime_fails_closed_before_calls(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(sys, 'argv', ['factory.py', directory, '--goal', 'goal', '--mode', 'pi-plan',
                                        '--runtime', 'codex', '--subscription-confirmed']), \
                patch('pi_workflow.run_plan') as run_plan, \
                patch('pi_adapter.subprocess.run') as run, \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as stderr:
            self.assertEqual(factory.main(), 2)
            run_plan.assert_not_called()
            run.assert_not_called()
            self.assertIn('BLOCKED', stderr.getvalue())

    def test_direct_read_only_uses_selected_runtime(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(sys, 'argv', ['factory.py', directory, '--goal', 'prompt', '--mode', 'pi',
                                        '--runtime', 'opencode', '--subscription-confirmed']), \
                patch('runtime_adapter.get_runtime', return_value=StubRuntime('opencode')), \
                contextlib.redirect_stdout(io.StringIO()) as stdout, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(factory.main(), 0)
            self.assertEqual(stdout.getvalue(), 'out')

    def test_unavailable_browser_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(sys, 'argv', ['factory.py', '.', '--goal', 'goal', '--mode', 'pi-plan',
                                        '--subscription-confirmed', '--build-static']), \
                patch('pi_workflow.run_plan', return_value=({'stages': []}, None)), \
                patch('pi_static.generate', return_value=Path(directory) / 'index.html'), \
                patch('browser_pipeline.verify_and_repair', return_value={'artifact': 'index.html', 'browser': {'status': 'unavailable'}}), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(factory.main(), 2)

    def test_blocked_plan_never_builds(self):
        with patch.object(sys, 'argv', ['factory.py', '.', '--goal', 'goal', '--mode', 'pi-plan',
                                        '--subscription-confirmed', '--build-static']), \
                patch('pi_workflow.run_plan', return_value=({'stages': []}, 'audit failed')), \
                patch('pi_static.generate') as generate, \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(factory.main(), 1)
            generate.assert_not_called()


if __name__ == '__main__':
    unittest.main()
