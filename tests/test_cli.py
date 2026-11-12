import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import factory


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
