import pytest

from agents.services.skill_relationship_resolver import (
    SkillRelationshipResolver,
)


@pytest.fixture
def resolver():
    return SkillRelationshipResolver()


@pytest.mark.parametrize(
    ("candidate", "required", "expected"),
    [
        ("Python", "Python", True),
        ("PYTHON", "python", True),
        ("sklearn", "Scikit-Learn", True),
        ("Python Dataclasses", "Python", True),
        ("Python", "Python Dataclasses", False),
        ("Python Type Hinting", "Python", True),
        ("NumPy Boolean Indexing", "NumPy", True),
        ("NumPy", "NumPy Boolean Indexing", False),
        ("NumPy Array Creation", "NumPy", True),
        ("Gymnasium Environment Design", "Gymnasium", True),
        ("Gymnasium", "Gymnasium Environment Design", False),
        ("PyTorch", "TensorFlow", False),
    ],
)
def test_skill_relationships(
    resolver,
    candidate,
    required,
    expected,
):
    assert (
        resolver.matches(
            candidate,
            required,
        )
        is expected
    )


from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.services.skill_matcher import SkillMatcher


def test_skill_matcher_preserves_hierarchical_evidence():
    matcher = SkillMatcher()

    evidence = SkillEvidence(
        skill="Python Dataclasses",
        source=EvidenceSource.GITHUB,
        evidence_type=EvidenceType.IMPLEMENTATION,
        reference="src/board.py",
        code_snippet="@dataclass\nclass BoardState: ...",
    )

    result = matcher.match(
        required_skill="Python",
        candidate_evidence=[evidence],
    )

    assert result.matched is True
    assert result.evidence == [evidence]
    assert result.evidence[0].skill == "Python Dataclasses"


def test_skill_matcher_rejects_reverse_hierarchy():
    matcher = SkillMatcher()

    evidence = SkillEvidence(
        skill="Python",
        source=EvidenceSource.CV,
        evidence_type=EvidenceType.SELF_REPORTED,
        reference="Python",
    )

    result = matcher.match(
        required_skill="Python Dataclasses",
        candidate_evidence=[evidence],
    )

    assert result.matched is False
    assert result.evidence == []


import pytest

from agents.schemas.match_type import MatchType


@pytest.mark.parametrize(
    "candidate_skill, required_skill",
    [
        ("PyTorch Neural Network Training", "PyTorch"),
        ("Pandas DataFrame Manipulation", "Pandas"),
        ("FastAPI Endpoint Development", "FastAPI"),
        ("Docker Containerization", "Docker"),
        ("SQL Window Functions", "SQL"),
    ],
)
def test_new_hierarchical_relationships(
    candidate_skill,
    required_skill,
):
    resolver = SkillRelationshipResolver()

    assert (
        resolver.resolve(
            candidate_skill,
            required_skill,
        )
        == MatchType.HIERARCHICAL
    )

    assert (
        resolver.resolve(
            required_skill,
            candidate_skill,
        )
        is None
    )
