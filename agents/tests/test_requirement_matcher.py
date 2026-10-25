from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.schemas.requirement_group import RequirementGroup
from agents.services.requirement_matcher import RequirementMatcher


def evidence(skill):
    return SkillEvidence(
        skill=skill,
        source=EvidenceSource.CV,
        evidence_type=EvidenceType.SELF_REPORTED,
    )


def group(skills, operator="all"):
    return RequirementGroup(
        skills=skills,
        operator=operator,
        priority="required",
        evidence="Example requirement",
    )


def test_all_group_fully_satisfied():
    result = RequirementMatcher().match(
        group(["NumPy", "Pandas"]),
        [evidence("NumPy"), evidence("Pandas")],
    )

    assert result.satisfied is True
    assert result.coverage == 1.0


def test_all_group_partially_satisfied():
    result = RequirementMatcher().match(
        group(["NumPy", "Pandas"]),
        [evidence("NumPy")],
    )

    assert result.satisfied is False
    assert result.coverage == 0.5


def test_all_group_not_satisfied():
    result = RequirementMatcher().match(
        group(["NumPy", "Pandas"]),
        [],
    )

    assert result.satisfied is False
    assert result.coverage == 0.0


def test_any_group_satisfied_by_one_skill():
    result = RequirementMatcher().match(
        group(
            ["PyTorch", "TensorFlow"],
            operator="any",
        ),
        [evidence("PyTorch")],
    )

    assert result.satisfied is True
    assert result.coverage == 1.0


def test_any_group_not_satisfied():
    result = RequirementMatcher().match(
        group(
            ["PyTorch", "TensorFlow"],
            operator="any",
        ),
        [],
    )

    assert result.satisfied is False
    assert result.coverage == 0.0


def test_any_group_with_both_skills():
    result = RequirementMatcher().match(
        group(
            ["PyTorch", "TensorFlow"],
            operator="any",
        ),
        [
            evidence("PyTorch"),
            evidence("TensorFlow"),
        ],
    )

    assert result.satisfied is True
    assert result.coverage == 1.0
