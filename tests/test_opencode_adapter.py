import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import opencode_adapter


class FakeProcess:
    def __init__(self, stdout='ok'):
        self.pid = 4242
        self.returncode = 0
        self._stdout = stdout
        self.communicated = 0

    def communicate(self, timeout=None):
        self.communicated += 1
        return (self._stdout, '')


class OpenCodeAdapterTests(unittest.TestCase):
    def test_unconfirmed_spend_fails_before_process(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch('opencode_adapter.subprocess.Popen') as popen:
            with self.assertRaises(opencode_adapter.PrepaidUnavailable):
                opencode_adapter.run_read_only(directory, 'test')
            popen.assert_not_called()

    def test_invalid_workspace_does_not_start_process(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch('opencode_adapter.subprocess.Popen') as popen:
            with self.assertRaises(ValueError):
                opencode_adapter.run_read_only(Path(directory) / 'missing', 'test')
            popen.assert_not_called()

    def test_empty_prompt_does_not_start_process(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch('opencode_adapter.subprocess.Popen') as popen:
            with self.assertRaises(ValueError):
                opencode_adapter.run_text(directory, '   ')
            popen.assert_not_called()

    def test_read_only_command_shape_with_fake_process(self):
        captured = {}

        def fake_popen(argv, **kwargs):
            captured['argv'] = argv
            captured['cwd'] = kwargs.get('cwd')
            captured['env'] = kwargs.get('env')
            config_dir = Path(kwargs['env']['XDG_CONFIG_HOME']) / 'opencode'
            captured['config'] = json.loads((config_dir / 'opencode.json').read_text())
            return FakeProcess()

        with tempfile.TemporaryDirectory() as directory, \
                patch.dict(os.environ, {'FACTORY_OPENCODE_MODEL': ''}, clear=False), \
                patch('opencode_adapter.shutil.which', return_value='/fake/opencode'), \
                patch('opencode_adapter.subprocess.Popen', side_effect=fake_popen):
            result = opencode_adapter.run_read_only(directory, '--not-a-flag',
                                                    subscription_confirmed=True)
        argv = captured['argv']
        self.assertEqual(argv[0], '/fake/opencode')
        self.assertEqual(argv[1:3], ['run', '--standalone'])
        self.assertEqual(argv[argv.index('--agent') + 1], 'factory-readonly')
        self.assertNotIn('--model', argv)
        self.assertIn('--archived', argv)
        self.assertEqual(argv[argv.index('--title') + 1], 'factory')
        self.assertEqual(argv[-2:], ['--', '--not-a-flag'])
        self.assertEqual(captured['cwd'], Path(directory).resolve())
        self.assertEqual(captured['env']['OPENCODE_DISABLE_PROJECT_CONFIG'], '1')
        self.assertIn('"factory-readonly"', json.dumps(captured['config']))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, 'ok')
        self.assertFalse(Path(captured['env']['XDG_CONFIG_HOME']).exists(),
                         'Isolated config directory must be removed after the call')

    def test_planner_denies_every_action(self):
        captured = {}

        def fake_popen(argv, **kwargs):
            captured['argv'] = argv
            captured['env'] = kwargs.get('env')
            config_dir = Path(kwargs['env']['XDG_CONFIG_HOME']) / 'opencode'
            captured['config'] = json.loads((config_dir / 'opencode.json').read_text())
            return FakeProcess()

        with tempfile.TemporaryDirectory() as directory, \
                patch.dict(os.environ, {'FACTORY_OPENCODE_MODEL': ''}, clear=False), \
                patch('opencode_adapter.shutil.which', return_value='/fake/opencode'), \
                patch('opencode_adapter.subprocess.Popen', side_effect=fake_popen):
            opencode_adapter.run_text(directory, 'plan', subscription_confirmed=True)
        agents = captured['config']['agents']
        self.assertEqual(agents['factory-planner']['permissions'],
                         [{'action': '*', 'resource': '*', 'effect': 'deny'}])
        self.assertNotIn('--model', captured['argv'])
        self.assertEqual(captured['argv'][captured['argv'].index('--agent') + 1],
                         'factory-planner')

    def test_read_only_permissions_allow_only_file_reads(self):
        rules = opencode_adapter._permissions(read_allowed=True)
        self.assertEqual(rules[0], {'action': '*', 'resource': '*', 'effect': 'deny'})
        self.assertEqual(rules[1], {'action': 'read', 'resource': '*', 'effect': 'allow'})
        effects = [rule['effect'] for rule in rules[2:]]
        self.assertEqual(effects, ['deny', 'deny', 'allow'])
        actions = {rule['action'] for rule in rules}
        self.assertEqual(actions, {'*', 'read'})

    def test_model_environment_override(self):
        def fake_popen(argv, **kwargs):
            fake_popen.argv = argv
            return FakeProcess()

        with tempfile.TemporaryDirectory() as directory, \
                patch('opencode_adapter.shutil.which', return_value='/fake/opencode'), \
                patch('opencode_adapter.subprocess.Popen', side_effect=fake_popen):
            with patch.dict(os.environ, {'FACTORY_OPENCODE_MODEL': 'opengo/one'}, clear=False):
                opencode_adapter.run_text(directory, 'prompt', subscription_confirmed=True)
                self.assertEqual(fake_popen.argv[fake_popen.argv.index('--model') + 1], 'opengo/one')
            with patch.dict(os.environ, clear=False):
                os.environ.pop('FACTORY_OPENCODE_MODEL', None)
                opencode_adapter.run_text(directory, 'prompt', subscription_confirmed=True)
                self.assertNotIn('--model', fake_popen.argv)

    def test_timeout_kills_process_group(self):
        class TimeoutProcess:
            pid = 99
            returncode = -9

            def communicate(self, timeout=None):
                if timeout is not None:
                    raise subprocess.TimeoutExpired('opencode', 5)
                return ('', '')

            def kill(self):
                pass

        killpg = []
        with tempfile.TemporaryDirectory() as directory, \
                patch.dict(os.environ, {'FACTORY_OPENCODE_MODEL': ''}, clear=False), \
                patch('opencode_adapter.shutil.which', return_value='/fake/opencode'), \
                patch('opencode_adapter.subprocess.Popen', return_value=TimeoutProcess()), \
                patch('opencode_adapter.os.getpgid', return_value=99), \
                patch('opencode_adapter.os.killpg', side_effect=lambda pid, sig: killpg.append(pid)):
            with self.assertRaises(subprocess.TimeoutExpired):
                opencode_adapter.run_text(directory, 'prompt', subscription_confirmed=True, timeout=5)
        self.assertEqual(killpg, [99])

    def test_config_directory_is_removed_when_the_process_fails(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch.dict(os.environ, {'FACTORY_OPENCODE_MODEL': ''}, clear=False), \
                patch('opencode_adapter.shutil.which', return_value='/fake/opencode'), \
                patch('opencode_adapter.subprocess.Popen', side_effect=OSError('spawn failed')):
            with self.assertRaises(OSError):
                opencode_adapter.run_text(directory, 'prompt', subscription_confirmed=True)
        leftovers = [path for path in Path(tempfile.gettempdir()).glob('factory-opencode-*')]
        self.assertEqual(leftovers, [])


if __name__ == '__main__':
    unittest.main()
