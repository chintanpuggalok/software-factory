import subprocess
import tempfile
import unittest
from unittest.mock import patch

import runtime_adapter


class RuntimeSelectionTests(unittest.TestCase):
    def test_pi_is_default(self):
        self.assertEqual(runtime_adapter.get_runtime().name, 'pi')

    def test_environment_can_select_runtime(self):
        for name in ('codex', 'opencode'):
            with patch.dict('os.environ', {'FACTORY_RUNTIME': name}):
                self.assertEqual(runtime_adapter.get_runtime().name, name)

    def test_unknown_runtime_fails_closed(self):
        with self.assertRaises(runtime_adapter.RuntimeUnavailable):
            runtime_adapter.get_runtime('unknown')

    def test_placeholder_runtimes_refuse_before_subprocess(self):
        with patch('pi_adapter.subprocess.run') as run:
            for name in ('codex', 'claude'):
                runtime = runtime_adapter.get_runtime(name)
                self.assertFalse(runtime.available())
                with self.assertRaises(runtime_adapter.RuntimeUnavailable):
                    runtime.run_text('.', 'prompt', confirmed=True)
            run.assert_not_called()

    def test_pi_delegates_to_pi_adapter(self):
        runtime = runtime_adapter.get_runtime('pi')
        with patch('pi_adapter.run_text', return_value=subprocess.CompletedProcess([], 0, 'ok', '')) as call:
            result = runtime.run_text('/tmp', 'prompt', confirmed=True, timeout=5)
            self.assertEqual(result.stdout, 'ok')
            call.assert_called_once_with('/tmp', 'prompt', subscription_confirmed=True, timeout=5)

    def test_opencode_delegates_to_opencode_adapter(self):
        runtime = runtime_adapter.get_runtime('opencode')
        self.assertEqual(runtime.name, 'opencode')
        with patch('opencode_adapter.run_text', return_value=subprocess.CompletedProcess([], 0, 'ok', '')) as text, \
                patch('opencode_adapter.run_read_only',
                      return_value=subprocess.CompletedProcess([], 0, 'read', '')) as read_only:
            result = runtime.run_text('/tmp', 'prompt', confirmed=True, timeout=5)
            self.assertEqual(result.stdout, 'ok')
            text.assert_called_once_with('/tmp', 'prompt', subscription_confirmed=True, timeout=5)
            result = runtime.run_read_only('/tmp', 'prompt', confirmed=False, timeout=6)
            self.assertEqual(result.stdout, 'read')
            read_only.assert_called_once_with('/tmp', 'prompt', subscription_confirmed=False, timeout=6)

    def test_opencode_availability_follows_the_executable(self):
        runtime = runtime_adapter.get_runtime('opencode')
        with patch('runtime_adapter.shutil.which', return_value=None):
            self.assertFalse(runtime.available())
        with patch('runtime_adapter.shutil.which', return_value='/fake/opencode'):
            self.assertTrue(runtime.available())


if __name__ == '__main__':
    unittest.main()
