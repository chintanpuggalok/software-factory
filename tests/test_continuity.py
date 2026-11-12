import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ContinuityInstructionTests(unittest.TestCase):
    def test_normal_work_continues_after_stage(self):
        text = (ROOT / '.agents/skills/factory-autonomous/SKILL.md').read_text()
        self.assertIn('Continue to the next authorized task', text)
        self.assertIn('Do not stop at a milestone', text)

    def test_failure_has_safe_recovery(self):
        text = (ROOT / '.agents/skills/factory-recover/SKILL.md').read_text()
        self.assertIn('Try another safe approach within scope', text)
        self.assertIn('Do not repeat unsafe external effects', text)

    def test_authorization_boundary_is_preserved(self):
        text = (ROOT / 'AGENTS.md').read_text()
        self.assertIn('required authorization', text)
        self.assertIn('Never bypass safety gates or expand scope', text)


if __name__ == '__main__':
    unittest.main()
