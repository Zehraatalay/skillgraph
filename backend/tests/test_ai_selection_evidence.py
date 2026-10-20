import unittest
from app.ai.analyzer import select_analysis_files, classify_evidence, analyze_repository, FileAssessment, ProposedSkill
from app.ai.schemas import RepositoryContext, SourceFile


def context():
    paths = ['README.md', 'FinalProject/requirements.txt', 'HW1/requirements.txt', 'HW3/train.py', 'FinalProject/model_scratch.py', 'FinalProject/model_transfer.py', 'FinalProject/train_transfer.py', 'tests/test_model.py']
    return RepositoryContext(owner='test', repository='stylematch', files=[SourceFile(path=p, content='import torch\nmodel = nn.Linear(1, 2)\n', size=34) for p in paths])


class SelectionEvidenceTests(unittest.TestCase):
    def test_small_budget_includes_implementation(self):
        selected = [f.path for f in select_analysis_files(context(), 4)]
        self.assertEqual(len(selected), 4)
        self.assertIn('README.md', selected)
        self.assertIn('FinalProject/model_scratch.py', selected)
        self.assertIn('FinalProject/model_transfer.py', selected)
        self.assertFalse(any(p.startswith('tests/') for p in selected))

    def test_evidence_types(self):
        self.assertEqual(classify_evidence('requirements.txt', 'torch==2.0'), 'dependency')
        self.assertEqual(classify_evidence('README.md', 'CNN'), 'documentation')
        self.assertEqual(classify_evidence('model.py', 'import torch'), 'import')
        self.assertEqual(classify_evidence('train.py', 'kmeans_models, cluster_label = build_ktree(Xtr, K, D)'), 'code_reference')

    def test_zero_budget(self):
        self.assertEqual(select_analysis_files(context(), 0), [])

    def test_verification_does_not_claim_semantic_proof(self):
        class FakeClient:
            model = 'fake'
            def analyze(self, prompt, schema):
                return FileAssessment(skills=[ProposedSkill(name='PyTorch', quote='import torch', explanation='Import')])
        result = analyze_repository(context(), FakeClient(), max_files=2)
        self.assertTrue(all(s.verification == 'quote_verified_only' for s in result.skills))

if __name__ == '__main__':
    unittest.main()
