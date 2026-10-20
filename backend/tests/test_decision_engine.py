import unittest
from app.ai.decision_engine import decide_skill


class DecisionEngineTests(unittest.TestCase):
    def test_rejects_linear_layer_as_regression(self):
        self.assertEqual(decide_skill('Linear Regression', 'nn.Linear(512, 256)', 'code_reference', 'uncertain')[0], 'reject')

    def test_rejects_linear_layer_as_linear_algebra(self):
        self.assertEqual(decide_skill('Linear Algebra', 'nn.Linear(512, 256)', 'code_reference', 'uncertain')[0], 'reject')

    def test_rejects_requires_grad_as_gradient_descent(self):
        self.assertEqual(decide_skill('Gradient Descent', 'p.requires_grad = True', 'code_reference', 'uncertain')[0], 'reject')

    def test_accepts_recognized_code_construct(self):
        self.assertEqual(decide_skill('Convolutional Neural Networks', 'nn.Conv2d(', 'code_reference', 'supported')[0], 'accept')

    def test_does_not_accept_dependencies_as_mastery(self):
        self.assertEqual(decide_skill('PyTorch', 'torch', 'dependency', 'verified_usage')[0], 'needs_review')

    def test_uncertain_code_requires_review(self):
        self.assertEqual(decide_skill('Transfer Learning', 'weights = weights', 'code_reference', 'uncertain')[0], 'needs_review')

    def test_documentation_requires_review(self):
        self.assertEqual(decide_skill('PyTorch', 'Uses PyTorch for training', 'documentation', 'uncertain')[0], 'needs_review')


if __name__ == '__main__':
    unittest.main()
