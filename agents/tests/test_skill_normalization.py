import pytest

from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.services.skill_grouper import SkillGrouper
from agents.services.skill_normalizer import SkillNormalizer


def make_evidence(skill: str) -> SkillEvidence:
    return SkillEvidence(
        skill=skill,
        source=EvidenceSource.GITHUB,
        evidence_type=EvidenceType.IMPLEMENTATION,
        reference="src/example.py",
        code_snippet="import numpy as np",
    )


def test_preserves_specific_numpy_skills():
    normalizer = SkillNormalizer()

    assert normalizer.normalize("NumPy Boolean Indexing") == "NumPy Boolean Indexing"

    assert normalizer.normalize("NumPy Array Creation") == "NumPy Array Creation"


def test_normalizes_case_and_whitespace():
    normalizer = SkillNormalizer()

    result = normalizer.normalize("  NUMPY   ARRAY  CREATION ")

    assert result == "NUMPY ARRAY CREATION"


def test_preserves_unknown_skill():
    normalizer = SkillNormalizer()

    assert normalizer.normalize("Apache Spark") == "Apache Spark"


def test_normalizes_skill_aliases():
    normalizer = SkillNormalizer()

    assert normalizer.normalize("sklearn") == "scikit-learn"

    assert normalizer.normalize("Scikit Learn") == "scikit-learn"

    assert normalizer.normalize("OOP") == ("Object-Oriented Programming")


def test_rejects_empty_skill():
    normalizer = SkillNormalizer()

    with pytest.raises(
        ValueError,
        match="Skill name cannot be empty",
    ):
        normalizer.normalize("   ")


def test_groups_evidence_by_normalized_skill():
    grouper = SkillGrouper()

    evidence = [
        make_evidence("NumPy Array Creation"),
        make_evidence("NumPy Boolean Indexing"),
        make_evidence("Action Masking"),
    ]

    groups = grouper.group(evidence)

    assert len(groups) == 3

    groups_by_name = {group.name: group for group in groups}

    assert len(groups_by_name["NumPy Array Creation"].evidence) == 1

    assert len(groups_by_name["NumPy Boolean Indexing"].evidence) == 1

    assert len(groups_by_name["Action Masking"].evidence) == 1


def test_preserves_original_evidence():
    grouper = SkillGrouper()

    original = make_evidence("NumPy Boolean Indexing")

    groups = grouper.group([original])

    assert groups[0].name == "NumPy Boolean Indexing"

    assert groups[0].evidence[0].skill == "NumPy Boolean Indexing"


def test_handles_empty_evidence():
    grouper = SkillGrouper()

    assert grouper.group([]) == []


def test_python_dataclasses_is_not_equivalent_to_python():
    normalizer = SkillNormalizer()

    assert normalizer.normalize("Python Dataclasses") != normalizer.normalize("Python")
