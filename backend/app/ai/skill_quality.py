"""Conservative skill taxonomy and deterministic evidence checks.

These rules do not constitute full semantic verification of algorithms.
"""
import re
from pathlib import PurePosixPath

ALIASES = {
    'convolutional neural network (cnn)': 'Convolutional Neural Networks',
    'convolutional neural networks (cnns)': 'Convolutional Neural Networks',
    'cnn': 'Convolutional Neural Networks',
    'cnns': 'Convolutional Neural Networks',
    'convolutional neural networks': 'Convolutional Neural Networks',
    'transfer learning': 'Transfer Learning',
    'batch normalization': 'Batch Normalization',
    'activation functions': 'Activation Functions',
    'gradient descent': 'Gradient Descent',
    'linear regression': 'Linear Regression',
    'linear algebra': 'Linear Algebra',
    'pytorch': 'PyTorch',
    'torch': 'PyTorch',
    'torchvision': 'TorchVision',
    'opencv-python': 'OpenCV',
    'opencv': 'OpenCV',
    'scikit-learn': 'Scikit-learn',
    'sklearn': 'Scikit-learn',
}

CATEGORIES = {
    'Convolutional Neural Networks': 'model_architecture',
    'Transfer Learning': 'ml_technique',
    'Batch Normalization': 'neural_network_component',
    'Activation Functions': 'neural_network_component',
    'Gradient Descent': 'optimization_concept',
    'Linear Regression': 'ml_algorithm',
    'Linear Algebra': 'foundational_concept',
    'PyTorch': 'framework',
    'TorchVision': 'library',
    'OpenCV': 'library',
    'Scikit-learn': 'library',
}

# Only explicit evidence in the quoted substring counts; never infer from filenames.
PATTERNS = {
    'Convolutional Neural Networks': r'\b(?:nn\.Conv[123]d|Conv[123]D|Conv2d|Conv1d|Conv3d)\b',
    'Batch Normalization': r'\b(?:nn\.BatchNorm[123]d|BatchNorm[123]d)\b',
    'Activation Functions': r'\b(?:nn\.(?:ReLU|GELU|Sigmoid|Tanh|LeakyReLU)|F\.(?:relu|gelu|sigmoid|tanh))\b',
    'Transfer Learning': r'\b(?:pretrained\s*=\s*True|weights\s*=\s*(?!None\b)[\w.]+|requires_grad\s*=\s*False|load_state_dict\s*\()',
    'Gradient Descent': r'\b(?:torch\.optim\.SGD|optim\.SGD|SGD\s*\()',
    'Linear Regression': r'\b(?:LinearRegression\s*\(|linear_model\.LinearRegression\s*\()',
}


def normalize_skill(name: str) -> str:
    cleaned = ' '.join(name.strip().split())
    return ALIASES.get(cleaned.casefold(), cleaned)


def category_for(name: str) -> str:
    return CATEGORIES.get(name, 'other')


def assess_evidence(name: str, quote: str, evidence_type: str) -> tuple[str, str]:
    """Return (confidence tier, rationale), without claiming algorithm proof."""
    if evidence_type == 'dependency':
        return 'verified_usage', 'Dependency declaration verified; runtime usage is not established.'
    if evidence_type == 'import':
        return 'verified_usage', 'Import statement verified; algorithm implementation is not established.'
    if evidence_type == 'documentation':
        return 'uncertain', 'Documentation is a claim, not implementation evidence.'
    if name == 'Linear Regression' and re.search(r'\b(?:nn\.)?Linear\s*\(', quote):
        return 'uncertain', 'A neural-network Linear layer is not linear regression.'
    pattern = PATTERNS.get(name)
    if pattern and re.search(pattern, quote, flags=re.IGNORECASE):
        return 'supported', 'Recognizable code construct; full semantic verification is still required.'
    return 'uncertain', 'Quote exists, but no specific implementation pattern was confirmed.'
