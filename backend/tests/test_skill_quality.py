import unittest
from app.ai.skill_quality import normalize_skill, category_for, assess_evidence
from app.ai.analyzer import analyze_repository, FileAssessment, ProposedSkill
from app.ai.schemas import RepositoryContext, SourceFile


class SkillQualityTests(unittest.TestCase):
    def test_cnn_aliases(self):
        self.assertEqual(normalize_skill('Convolutional Neural Network (CNN)'), 'Convolutional Neural Networks')
        self.assertEqual(normalize_skill('Convolutional Neural Networks (CNNs)'), 'Convolutional Neural Networks')

    def test_categories(self):
        self.assertEqual(category_for('Transfer Learning'), 'ml_technique')
        self.assertEqual(category_for('PyTorch'), 'framework')

    def test_linear_layer_is_not_regression(self):
        level, _ = assess_evidence('Linear Regression', 'self.fc = nn.Linear(128, 10)', 'code_reference')
        self.assertEqual(level, 'uncertain')

    def test_cnn_construct_supported_not_verified(self):
        level, _ = assess_evidence('Convolutional Neural Networks', 'self.conv = nn.Conv2d(3, 32, 3)', 'code_reference')
        self.assertEqual(level, 'supported')

    def test_generic_math_not_algorithm_proof(self):
        level, _ = assess_evidence('Linear Algebra', 'x = x.reshape(-1, 128)', 'code_reference')
        self.assertEqual(level, 'uncertain')

    def test_aliases_deduplicated_per_file(self):
        class FakeClient:
            model = 'fake'
            def analyze(self, prompt, schema):
                return FileAssessment(skills=[
                    ProposedSkill(name='CNN', quote='self.conv = nn.Conv2d(3, 32, 3)', explanation='conv'),
                    ProposedSkill(name='Convolutional Neural Network (CNN)', quote='self.conv = nn.Conv2d(3, 32, 3)', explanation='conv'),
                ])
        code = 'self.conv = nn.Conv2d(3, 32, 3)'
        context = RepositoryContext(owner='x', repository='y', files=[SourceFile(path='model.py', content=code, size=len(code))])
        result = analyze_repository(context, FakeClient())
        self.assertEqual(len(result.skills), 1)
        self.assertEqual(result.rejected_evidence, 1)
        self.assertEqual(result.skills[0].confidence, 'supported')


if __name__ == '__main__':
    unittest.main()
