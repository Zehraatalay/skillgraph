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


def evidence(
    skill,
    source,
    evidence_type,
):
    return SkillEvidence(
        skill=skill,
        source=source,
        evidence_type=evidence_type,
    )


def classify(evidence_items):
    skill_match = SkillMatcher().match(
        required_skill="Python",
        candidate_evidence=evidence_items,
    )

    return EvidenceSupportClassifier().classify(skill_match)


def test_no_evidence():
    result = classify([])

    assert result.level == SupportLevel.NONE
    assert result.cv_evidence_count == 0
    assert result.github_evidence_count == 0


def test_self_reported():
    result = classify(
        [
            evidence(
                "Python",
                EvidenceSource.CV,
                EvidenceType.SELF_REPORTED,
            )
        ]
    )

    assert result.level == SupportLevel.SELF_REPORTED
    assert result.cv_evidence_count == 1


def test_implementation_backed():
    result = classify(
        [
            evidence(
                "Python",
                EvidenceSource.GITHUB,
                EvidenceType.IMPLEMENTATION,
            )
        ]
    )

    assert result.level == SupportLevel.IMPLEMENTATION_BACKED
    assert result.github_evidence_count == 1


def test_cv_and_github():
    result = classify(
        [
            evidence(
                "Python",
                EvidenceSource.CV,
                EvidenceType.SELF_REPORTED,
            ),
            evidence(
                "Python",
                EvidenceSource.GITHUB,
                EvidenceType.IMPLEMENTATION,
            ),
        ]
    )

    assert result.level == SupportLevel.IMPLEMENTATION_BACKED
    assert result.cv_evidence_count == 1
    assert result.github_evidence_count == 1


def test_tested_evidence():
    result = classify(
        [
            evidence(
                "Python",
                EvidenceSource.GITHUB,
                EvidenceType.TESTED,
            )
        ]
    )

    assert result.level == SupportLevel.TESTED


def test_implementation_preferred_over_self_reported():
    result = classify(
        [
            evidence(
                "Python",
                EvidenceSource.CV,
                EvidenceType.SELF_REPORTED,
            ),
            evidence(
                "Python",
                EvidenceSource.GITHUB,
                EvidenceType.IMPLEMENTATION,
            ),
        ]
    )

    assert result.level != SupportLevel.SELF_REPORTED
