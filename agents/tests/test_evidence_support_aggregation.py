from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.schemas.evidence_support import SupportLevel
from agents.services.evidence_support_classifier import (
    EvidenceSupportClassifier,
)
from agents.services.skill_matcher import SkillMatcher


def test_classifier_includes_evidence_summary():
    evidence = [
        SkillEvidence(
            skill="Python",
            source=EvidenceSource.CV,
            evidence_type=EvidenceType.SELF_REPORTED,
            reference="Technical skills: Python",
        ),
        SkillEvidence(
            skill="Python Dataclasses",
            source=EvidenceSource.GITHUB,
            evidence_type=EvidenceType.IMPLEMENTATION,
            reference="src/board.py",
        ),
    ]

    skill_match = SkillMatcher().match(
        required_skill="Python",
        candidate_evidence=evidence,
    )

    support = EvidenceSupportClassifier().classify(skill_match)

    assert support.skill == "Python"
    assert support.level == SupportLevel.IMPLEMENTATION_BACKED

    assert support.cv_evidence_count == 1
    assert support.github_evidence_count == 1

    assert support.evidence_summary is not None

    assert support.evidence_summary.total_evidence == 2
    assert support.evidence_summary.exact_count == 1
    assert support.evidence_summary.hierarchical_count == 1
