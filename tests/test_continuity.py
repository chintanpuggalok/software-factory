import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / '.agents/skills'
STAGES = ('idea', 'spec', 'design', 'architecture', 'plan', 'build', 'verify',
          'visual-review', 'release', 'taste')
AUDIT_FOR = {'visual-review': 'audit-visual'}


def read(path):
    return path.read_text(encoding='utf-8')


class ContinuityInstructionTests(unittest.TestCase):
    def test_normal_work_continues_after_stage(self):
        text = read(SKILLS / 'factory-autonomous/SKILL.md')
        self.assertIn('Continue to the next authorized task', text)
        self.assertIn('Do not stop at a milestone', text)

    def test_failure_has_safe_recovery(self):
        text = read(SKILLS / 'factory-recover/SKILL.md')
        self.assertIn('Try another safe approach within scope', text)
        self.assertIn('Do not repeat unsafe external effects', text)
        self.assertIn('two attempts', text)

    def test_authorization_boundary_is_preserved(self):
        text = read(ROOT / 'AGENTS.md')
        self.assertIn('required authorization', text)
        self.assertIn('Never bypass safety gates or expand scope', text)

    def test_every_stage_skill_names_its_audit(self):
        for stage in STAGES:
            audit = AUDIT_FOR.get(stage, f'audit-{stage}')
            text = read(SKILLS / f'factory-{stage}/SKILL.md')
            self.assertIn(audit, text, f'factory-{stage} does not name {audit}')

    def test_every_audit_defines_the_verdict_contract(self):
        audits = list(SKILLS.glob('audit-*/SKILL.md'))
        self.assertEqual(len(audits), 10)
        for path in audits:
            text = read(path)
            self.assertIn('PASS: evidence', text, path)
            self.assertIn('REVISE: findings', text, path)
            self.assertIn('BLOCKED: reason', text, path)

    def test_stage_skills_do_not_advance_without_pass(self):
        for stage in ('idea', 'spec', 'design', 'architecture', 'plan', 'build',
                      'verify', 'visual-review'):
            text = read(SKILLS / f'factory-{stage}/SKILL.md')
            self.assertRegex(text, r'Advance only after `PASS', f'factory-{stage}')

    def test_artifacts_have_a_default_contract(self):
        text = read(ROOT / 'AGENTS.md')
        for value in ('docs/factory/spec.md', 'docs/factory/plan.md', '.factory/state.json'):
            self.assertIn(value, text)

    def test_release_requires_security_evidence(self):
        self.assertIn('security and privacy evidence', read(SKILLS / 'audit-release/SKILL.md'))
        self.assertIn('factory-security', read(SKILLS / 'factory-release/SKILL.md'))

    def test_no_stray_semicolons_in_stage_skills(self):
        for path in SKILLS.glob('factory-*/SKILL.md'):
            body = read(path).split('---', 2)[2]
            self.assertNotIn(';', body, path)

    def test_runtime_adapter_documented(self):
        text = read(ROOT / 'docs/runtime-adapters.md')
        for value in ('run_text', 'confirmed', 'Codex', 'Claude'):
            self.assertIn(value, text)


if __name__ == '__main__':
    unittest.main()
