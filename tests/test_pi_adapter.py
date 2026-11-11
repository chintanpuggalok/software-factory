import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pi_adapter


class PiAdapterTests(unittest.TestCase):
    def test_unverified_prepaid_fails_before_process(self):
        with tempfile.TemporaryDirectory() as directory, patch('pi_adapter.subprocess.run') as run:
            with self.assertRaises(pi_adapter.PrepaidUnavailable):
                pi_adapter.run_read_only(directory, 'test')
            run.assert_not_called()

    def test_command_contract_with_fake_process(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch('pi_adapter.shutil.which', return_value='/fake/pi'), \
                patch('pi_adapter.subprocess.run', return_value=subprocess.CompletedProcess([], 0, 'ok', '')) as run:
            result = pi_adapter.run_read_only(directory, '--not-a-flag', subscription_confirmed=True)
            command = run.call_args.args[0]
            self.assertEqual(command[0], '/fake/pi')
            self.assertEqual(command[-2:], ['--', '--not-a-flag'])
            self.assertIn('--no-extensions', command)
            self.assertIn('--no-mcp', command)
            self.assertEqual(command[command.index('--tools') + 1], 'read')
            self.assertEqual(run.call_args.kwargs['cwd'], Path(directory).resolve())
            self.assertEqual(result.stdout, 'ok')

    def test_invalid_workspace_does_not_start_process(self):
        with tempfile.TemporaryDirectory() as directory, patch('pi_adapter.subprocess.run') as run:
            with self.assertRaises(ValueError):
                pi_adapter.run_read_only(Path(directory) / 'missing', 'test')
            run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
