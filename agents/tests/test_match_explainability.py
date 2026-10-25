import pytest

from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.schemas.match_type import MatchType
from agents.services.skill_matcher import SkillMatcher
from agents.services.skill_relationship_resolver import (
    SkillRelationshipResolver,
)


@pytest.mark.parametrize(
    ("candidate", "required", "expected"),
    [
        ("Python", "Python", MatchType.EXACT),
        ("PYTHON", "python", MatchType.EXACT),
        ("sklearn", "scikit-learn", MatchType.ALIAS),
        (
            "Python Dataclasses",
            "Python",
            MatchType.HIERARCHICAL,
        ),
        (
            "NumPy Boolean Indexing",
            "NumPy",
            MatchType.HIERARCHICAL,
        ),
        ("Python", "Python Dataclasses", None),
        ("PyTorch", "TensorFlow", None),
    ],
)
def test_resolve_match_type(
    candidate,
    required,
    expected,
):
    resolver = SkillRelationshipResolver()

    assert (
        resolver.resolve(
            candidate,
            required,
        )
        == expected
    )


def make_evidence(skill: str) -> SkillEvidence:
    return SkillEvidence(
        skill=skill,
        source=EvidenceSource.GITHUB,
        evidence_type=EvidenceType.IMPLEMENTATION,
        reference="src/example.py",
    )


def test_skill_matcher_preserves_match_types():
    matcher = SkillMatcher()

    evidence = [
        make_evidence("Python"),
        make_evidence("Python Dataclasses"),
        make_evidence("Python Type Hinting"),
        make_evidence("NumPy"),
    ]

    result = matcher.match(
        required_skill="Python",
        candidate_evidence=evidence,
    )

    assert result.matched is True

    assert len(result.evidence) == 3

    assert len(result.matched_evidence) == 3

    assert [item.match_type for item in result.matched_evidence] == [
        MatchType.EXACT,
        MatchType.HIERARCHICAL,
        MatchType.HIERARCHICAL,
    ]


def test_unmatched_skill_has_no_evidence():
    matcher = SkillMatcher()

    result = matcher.match(
        required_skill="Docker",
        candidate_evidence=[
            make_evidence("Python"),
        ],
    )

    assert result.matched is False
    assert result.evidence == []
    assert result.matched_evidence == []
