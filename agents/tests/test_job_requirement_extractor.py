import pytest

from agents.schemas.job import JobPosting
from agents.schemas.job_analysis import JobAnalysis
from agents.schemas.job_requirement import (
    JobRequirement,
    RequirementPriority,
)
from agents.services.job_requirement_extractor import (
    JobRequirementExtractor,
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
        assert schema is JobAnalysis
        assert method == "json_schema"

        return FakeStructuredLLM(self.response)


def make_job():
    return JobPosting(
        id="job-001",
        title="Junior ML Engineer",
        description=(
            "Strong Python skills are required. Familiarity with PyTorch is a plus."
        ),
    )


def test_extracts_valid_job_requirements():
    job = make_job()

    response = JobAnalysis(
        job_id="job-001",
        requirements=[
            JobRequirement(
                skill="Python",
                priority=RequirementPriority.REQUIRED,
                evidence="Strong Python skills are required",
            ),
            JobRequirement(
                skill="PyTorch",
                priority=RequirementPriority.PREFERRED,
                evidence="Familiarity with PyTorch is a plus",
            ),
        ],
    )

    extractor = JobRequirementExtractor(FakeLLM(response))

    result = extractor.extract(job)

    assert len(result.requirements) == 2

    assert result.requirements[0].priority == RequirementPriority.REQUIRED

    assert result.requirements[1].priority == RequirementPriority.PREFERRED


def test_rejects_fabricated_evidence():
    job = make_job()

    response = JobAnalysis(
        job_id="job-001",
        requirements=[
            JobRequirement(
                skill="Kubernetes",
                priority=RequirementPriority.REQUIRED,
                evidence="Kubernetes experience is required",
            )
        ],
    )

    extractor = JobRequirementExtractor(FakeLLM(response))

    with pytest.raises(
        ValueError,
        match="evidence not found",
    ):
        extractor.extract(job)


def test_rejects_mismatched_job_id():
    job = make_job()

    response = JobAnalysis(
        job_id="different-job",
        requirements=[],
    )

    extractor = JobRequirementExtractor(FakeLLM(response))

    with pytest.raises(
        ValueError,
        match="ID does not match",
    ):
        extractor.extract(job)


def test_rejects_unexpected_response():
    job = make_job()

    extractor = JobRequirementExtractor(FakeLLM({"requirements": []}))

    with pytest.raises(
        TypeError,
        match="Unexpected job requirement extraction response",
    ):
        extractor.extract(job)


def test_handles_empty_requirements():
    job = make_job()

    response = JobAnalysis(
        job_id="job-001",
        requirements=[],
    )

    extractor = JobRequirementExtractor(FakeLLM(response))

    result = extractor.extract(job)

    assert result.requirements == []
