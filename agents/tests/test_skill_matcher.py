from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.services.skill_matcher import SkillMatcher


def make_evidence(
    skill,
    source=EvidenceSource.CV,
    evidence_type=EvidenceType.SELF_REPORTED,
):
    return SkillEvidence(
        skill=skill,
        source=source,
        evidence_type=evidence_type,
    )


def test_exact_skill_match():
    result = SkillMatcher().match(
        "Python",
        [make_evidence("Python")],
    )

    assert result.matched is True
    assert len(result.evidence) == 1


def test_case_insensitive_match():
    result = SkillMatcher().match(
        "python",
        [make_evidence("Python")],
    )

    assert result.matched is True


def test_alias_match():
    result = SkillMatcher().match(
        "RAG",
        [make_evidence("retrieval-augmented generation (RAG)")],
    )

    assert result.matched is True


def test_different_skills_do_not_match():
    result = SkillMatcher().match(
        "PyTorch",
        [make_evidence("TensorFlow")],
    )

    assert result.matched is False
    assert result.evidence == []


def test_preserves_multiple_evidence():
    cv_evidence = make_evidence("Python")

    github_evidence = make_evidence(
        "Python",
        source=EvidenceSource.GITHUB,
        evidence_type=EvidenceType.IMPLEMENTATION,
    )

    result = SkillMatcher().match(
        "Python",
        [cv_evidence, github_evidence],
    )

    assert result.matched is True
    assert len(result.evidence) == 2


def test_empty_candidate_evidence():
    result = SkillMatcher().match(
        "Python",
        [],
    )

    assert result.matched is False
