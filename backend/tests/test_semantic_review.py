import unittest
from types import SimpleNamespace
from app.ai.semantic_review import deterministic_context, review_skill


class SemanticReviewTests(unittest.TestCase):
    def test_resnet_is_cnn(self):
        d, _ = deterministic_context('Convolutional Neural Networks', 'self.backbone = resnet18(weights = weights)', '')
        self.assertEqual(d, 'accept')

    def test_transfer_variable_without_definition_not_accepted(self):
        d, _ = deterministic_context('Transfer Learning', 'resnet18(weights = weights)', 'weights = None\nresnet18(weights = weights)')
        self.assertEqual(d, 'needs_review')

    def test_transfer_explicit_pretrained_enum(self):
        source = 'weights = ResNet18_Weights.DEFAULT if pretrained else None\nself.backbone = resnet18(weights = weights)'
        d, _ = deterministic_context('Transfer Learning', 'self.backbone = resnet18(weights = weights)', source)
        self.assertEqual(d, 'accept')

    def test_rejected_cannot_be_promoted(self):
        skill = SimpleNamespace(name='Linear Regression', quote='nn.Linear(1, 2)', decision='reject', decision_reason='wrong', evidence_type='code_reference')
        self.assertEqual(review_skill(skill, 'LinearRegression()')[0], 'reject')

    def test_unknown_skill_not_promoted(self):
        skill = SimpleNamespace(name='Gradient Descent', quote='p.requires_grad = True', decision='needs_review', decision_reason='unknown', evidence_type='code_reference')
        self.assertEqual(review_skill(skill, 'p.requires_grad = True')[0], 'needs_review')

    def test_llm_cannot_override_without_rule(self):
        skill = SimpleNamespace(name='Gradient Descent', quote='p.requires_grad = True', decision='needs_review', decision_reason='unknown', evidence_type='code_reference')
        class FakeClient:
            def analyze(self, prompt, schema):
                return schema(supports_claim=True, evidence_quote='p.requires_grad = True', rationale='yes')
        decision, _, evidence = review_skill(skill, 'p.requires_grad = True', client=FakeClient(), use_llm=True)
        self.assertEqual(decision, 'needs_review')
        self.assertEqual(evidence, 'p.requires_grad = True')


if __name__ == '__main__':
    unittest.main()
