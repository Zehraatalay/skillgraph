import pytest

from agents.schemas.grouped_job_analysis import GroupedJobAnalysis
from agents.schemas.job import JobPosting
from agents.schemas.requirement_group import RequirementGroup
from agents.services.grouped_job_requirement_extractor import (
    GroupedJobRequirementExtractor,
)


class FakeStructuredLLM:
    def __init__(self, response):
        self.response = response

    def invoke(self, messages):
        return self.response


class FakeLLM:
    def __init__(self, response):
        self.response = response

    def with_structured_output(self, schema, method):
        assert schema is GroupedJobAnalysis
        assert method == "json_schema"

        return FakeStructuredLLM(self.response)


def make_job():
    return JobPosting(
        id="job-001",
        title="ML Engineer",
        description=(
            "Experience with Python and SQL is required. "
            "Familiarity with PyTorch or TensorFlow is a plus."
        ),
    )


def make_valid_response():
    return GroupedJobAnalysis(
        job_id="job-001",
        requirement_groups=[
            RequirementGroup(
                skills=["Python", "SQL"],
                operator="all",
                priority="required",
                evidence=("Experience with Python and SQL is required."),
            ),
            RequirementGroup(
                skills=["PyTorch", "TensorFlow"],
                operator="any",
                priority="preferred",
                evidence=("Familiarity with PyTorch or TensorFlow is a plus."),
            ),
        ],
    )


def test_extracts_grouped_requirements():
    extractor = GroupedJobRequirementExtractor(FakeLLM(make_valid_response()))

    result = extractor.extract(make_job())

    assert len(result.requirement_groups) == 2

    assert result.requirement_groups[0].operator.value == "all"
    assert result.requirement_groups[1].operator.value == "any"


def test_preserves_required_preferred():
    extractor = GroupedJobRequirementExtractor(FakeLLM(make_valid_response()))

    result = extractor.extract(make_job())

    assert result.requirement_groups[0].priority.value == "required"
    assert result.requirement_groups[1].priority.value == "preferred"


def test_rejects_fabricated_evidence():
    response = GroupedJobAnalysis(
        job_id="job-001",
        requirement_groups=[
            RequirementGroup(
                skills=["Kubernetes"],
                operator="all",
                priority="required",
                evidence="Kubernetes is required.",
            )
        ],
    )

    extractor = GroupedJobRequirementExtractor(FakeLLM(response))

    with pytest.raises(
        ValueError,
        match="evidence not found",
    ):
        extractor.extract(make_job())


def test_rejects_mismatched_job_id():
    response = GroupedJobAnalysis(
        job_id="wrong-id",
        requirement_groups=[],
    )

    extractor = GroupedJobRequirementExtractor(FakeLLM(response))

    with pytest.raises(
        ValueError,
        match="ID does not match",
    ):
        extractor.extract(make_job())


def test_rejects_unexpected_response():
    extractor = GroupedJobRequirementExtractor(FakeLLM({"requirement_groups": []}))

    with pytest.raises(
        TypeError,
        match="Unexpected grouped job extraction response",
    ):
        extractor.extract(make_job())


def test_handles_empty_requirements():
    response = GroupedJobAnalysis(
        job_id="job-001",
        requirement_groups=[],
    )

    extractor = GroupedJobRequirementExtractor(FakeLLM(response))

    result = extractor.extract(make_job())

    assert result.requirement_groups == []
