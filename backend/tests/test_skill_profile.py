import unittest
from app.ai.analyzer import AIAnalysis, VerifiedSkill
from app.ai.skill_profile import build_skill_profile


def finding(name, file, decision='accept', quote='nn.Conv2d(', category='model_architecture'):
    return VerifiedSkill(name=name, file=file, quote=quote, explanation='Test evidence',
                         category=category, decision=decision, decision_reason='Test decision')


class SkillProfileTests(unittest.TestCase):
    def test_groups_across_files_and_excludes_rejected(self):
        analysis = AIAnalysis(repository='Zehraatalay/stylematch', model='llama3:latest', files_analyzed=[], skills=[
            finding('Convolutional Neural Networks', 'a.py'),
            finding('Convolutional Neural Networks', 'b.py', quote='resnet18(weights=weights)'),
            finding('Linear Regression', 'a.py', decision='reject'),
            finding('Gradient Descent', 'b.py', decision='needs_review'),
        ])
        profile = build_skill_profile(analysis)
        self.assertEqual(profile.developer, 'Zehraatalay')
        self.assertEqual(len(profile.skills), 1)
        self.assertEqual(profile.skills[0].evidence_count, 2)
        self.assertEqual(profile.accepted_evidence_count, 2)
        self.assertEqual(profile.excluded_by_decision, {'needs_review': 1, 'reject': 1})
        self.assertEqual([e.file for e in profile.skills[0].evidence], ['a.py', 'b.py'])

    def test_identical_evidence_deduplicated(self):
        entry = finding('Batch Normalization', 'model.py', quote='nn.BatchNorm2d(')
        analysis = AIAnalysis(repository='dev/repo', model='test', files_analyzed=[], skills=[entry, entry])
        profile = build_skill_profile(analysis)
        self.assertEqual(profile.accepted_evidence_count, 1)

    def test_only_nonaccepted_findings_yields_empty_profile(self):
        analysis = AIAnalysis(repository='dev/repo', model='test', files_analyzed=[], skills=[
            finding('CNN', 'model.py', decision='needs_review')])
        profile = build_skill_profile(analysis)
        self.assertEqual(profile.skills, [])
        self.assertEqual(profile.excluded_findings_count, 1)

    def test_invalid_repository_rejected(self):
        analysis = AIAnalysis(repository='invalid', model='test', files_analyzed=[], skills=[])
        with self.assertRaises(ValueError):
            build_skill_profile(analysis)


if __name__ == '__main__':
    unittest.main()
