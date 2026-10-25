import pytest
from pydantic import ValidationError

from agents.schemas.grouped_job_analysis import (
    GroupedJobAnalysis,
)
from agents.schemas.requirement_group import (
    RequirementGroup,
    RequirementOperator,
)


def test_single_required_skill():
    group = RequirementGroup(
        skills=["Python"],
        operator=RequirementOperator.ALL,
        priority="required",
        evidence="Strong Python skills are required",
    )

    assert group.skills == ["Python"]
    assert group.operator == RequirementOperator.ALL


def test_any_operator():
    group = RequirementGroup(
        skills=["PyTorch", "TensorFlow"],
        operator=RequirementOperator.ANY,
        priority="preferred",
        evidence="Familiarity with PyTorch or TensorFlow",
    )

    assert group.operator == RequirementOperator.ANY
    assert len(group.skills) == 2


def test_all_operator():
    group = RequirementGroup(
        skills=["NumPy", "Pandas"],
        operator=RequirementOperator.ALL,
        priority="required",
        evidence="Experience working with NumPy and Pandas",
    )

    assert group.operator == RequirementOperator.ALL


def test_rejects_empty_skills():
    with pytest.raises(ValidationError):
        RequirementGroup(
            skills=[],
            priority="required",
            evidence="Python required",
        )


def test_rejects_blank_skill():
    with pytest.raises(
        ValidationError,
        match="Requirement skills cannot be empty",
    ):
        RequirementGroup(
            skills=["Python", "   "],
            priority="required",
            evidence="Python required",
        )


def test_rejects_duplicate_skills():
    with pytest.raises(
        ValidationError,
        match="Duplicate skills",
    ):
        RequirementGroup(
            skills=["Python", "python"],
            priority="required",
            evidence="Python required",
        )


def test_grouped_job_analysis():
    analysis = GroupedJobAnalysis(
        job_id="job-001",
        requirement_groups=[
            RequirementGroup(
                skills=["Python"],
                priority="required",
                evidence="Python required",
            ),
            RequirementGroup(
                skills=["PyTorch", "TensorFlow"],
                operator="any",
                priority="preferred",
                evidence="PyTorch or TensorFlow preferred",
            ),
        ],
    )

    assert analysis.job_id == "job-001"
    assert len(analysis.requirement_groups) == 2
