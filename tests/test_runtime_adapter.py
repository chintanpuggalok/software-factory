import subprocess
import tempfile
import unittest
from unittest.mock import patch

import runtime_adapter


class RuntimeSelectionTests(unittest.TestCase):
    def test_pi_is_default(self):
        self.assertEqual(runtime_adapter.get_runtime().name, 'pi')

    def test_environment_can_select_runtime(self):
        with patch.dict('os.environ', {'FACTORY_RUNTIME': 'codex'}):
            self.assertEqual(runtime_adapter.get_runtime().name, 'codex')

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


if __name__ == '__main__':
    unittest.main()
