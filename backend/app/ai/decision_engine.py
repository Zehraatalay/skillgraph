"""Conservative, deterministic decisions for code-derived skill candidates.

A decision of accept means usable *evidence*, not verified developer mastery.
"""
import re
from typing import Literal

Decision = Literal['accept', 'reject', 'needs_review']


def decide_skill(name: str, quote: str, evidence_type: str, confidence: str) -> tuple[Decision, str]:
    """Make a conservative decision using the exact verified quote only."""
    if name == 'Linear Regression' and re.search(r'\b(?:nn\.)?Linear\s*\(', quote):
        return 'reject', 'nn.Linear is a neural network layer, not a regression estimator.'
    if name == 'Linear Algebra' and re.search(r'\b(?:nn\.)?Linear\s*\(', quote):
        return 'reject', 'Neural network linear layers do not establish linear algebra proficiency.'
    if name == 'Gradient Descent' and re.search(r'\brequires_grad\s*=\s*(?:True|False)\b', quote):
        return 'reject', 'Autograd configuration alone does not establish an optimizer or gradient descent.'
    if evidence_type == 'documentation':
        return 'needs_review', 'Documentation claims need corroborating code evidence.'
    if evidence_type in {'dependency', 'import'}:
        return 'needs_review', 'Declared dependency/import alone does not establish developer proficiency.'
    if confidence == 'supported' and evidence_type == 'code_reference':
        return 'accept', 'Recognizable code construct; evidence accepted, not proof of mastery.'
    return 'needs_review', 'No sufficiently specific code evidence for automatic acceptance.'
