import unittest
from app.ai.schemas import RepositoryContext, SourceFile
from app.ai.analyzer import FileAssessment, ProposedSkill, analyze_repository, redact


class FakeClient:
    model = 'fake'
    def analyze(self, prompt, schema):
        return FileAssessment(skills=[
            ProposedSkill(name='PyTorch', quote='import torch', explanation='import'),
            ProposedSkill(name='Invented', quote='not present anywhere', explanation='hallucination'),
        ])


class AnalyzerTests(unittest.TestCase):
    def test_rejects_nonexistent_quotes(self):
        context = RepositoryContext(owner='x', repository='y', files=[SourceFile(path='model.py', content='import torch\n', size=13)])
        result = analyze_repository(context, FakeClient())
        self.assertEqual([s.name for s in result.skills], ['PyTorch'])
        self.assertEqual(result.rejected_evidence, 1)

    def test_redacts_simple_secret_assignments(self):
        self.assertNotIn('abc123', redact('API_KEY = abc123\nimport torch'))


if __name__ == '__main__':
    unittest.main()
