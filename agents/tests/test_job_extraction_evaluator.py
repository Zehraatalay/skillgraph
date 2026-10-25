import pytest

from agents.schemas.grouped_job_analysis import GroupedJobAnalysis
from agents.schemas.job import JobPosting
from agents.schemas.job_evaluation import JobEvaluationCase
from agents.schemas.requirement_group import RequirementGroup
from agents.services.job_extraction_evaluator import (
    JobExtractionEvaluator,
)


def make_group(
    skills,
    operator="all",
    priority="required",
):
    return RequirementGroup(
        skills=skills,
        operator=operator,
        priority=priority,
        evidence="Example requirement",
    )


def make_case(expected_groups):
    return JobEvaluationCase(
        name="test-case",
        job=JobPosting(
            id="job-001",
            title="ML Engineer",
            description="Example requirement",
        ),
        expected=GroupedJobAnalysis(
            job_id="job-001",
            requirement_groups=expected_groups,
        ),
    )


def make_prediction(groups):
    return GroupedJobAnalysis(
        job_id="job-001",
        requirement_groups=groups,
    )


def test_perfect_match():
    groups = [
        make_group(["Python"]),
        make_group(
            ["PyTorch", "TensorFlow"],
            operator="any",
            priority="preferred",
        ),
    ]

    result = JobExtractionEvaluator().evaluate(
        make_case(groups),
        make_prediction(groups),
    )

    assert result.precision == 1.0
    assert result.recall == 1.0
    assert result.f1 == 1.0


def test_missing_requirement():
    expected = [
        make_group(["Python"]),
        make_group(["SQL"]),
    ]

    predicted = [
        make_group(["Python"]),
    ]

    result = JobExtractionEvaluator().evaluate(
        make_case(expected),
        make_prediction(predicted),
    )

    assert result.matched_count == 1
    assert result.missing_count == 1
    assert result.precision == 1.0
    assert result.recall == 0.5


def test_unexpected_requirement():
    expected = [
        make_group(["Python"]),
    ]

    predicted = [
        make_group(["Python"]),
        make_group(["Kubernetes"]),
    ]

    result = JobExtractionEvaluator().evaluate(
        make_case(expected),
        make_prediction(predicted),
    )

    assert result.unexpected_count == 1
    assert result.precision == 0.5
    assert result.recall == 1.0


def test_wrong_operator_is_not_match():
    expected = [
        make_group(
            ["PyTorch", "TensorFlow"],
            operator="any",
        ),
    ]

    predicted = [
        make_group(
            ["PyTorch", "TensorFlow"],
            operator="all",
        ),
    ]

    result = JobExtractionEvaluator().evaluate(
        make_case(expected),
        make_prediction(predicted),
    )

    assert result.matched_count == 0


def test_wrong_priority_is_not_match():
    expected = [
        make_group(["Python"], priority="required"),
    ]

    predicted = [
        make_group(["Python"], priority="preferred"),
    ]

    result = JobExtractionEvaluator().evaluate(
        make_case(expected),
        make_prediction(predicted),
    )

    assert result.matched_count == 0


def test_skill_order_does_not_matter():
    expected = [
        make_group(["NumPy", "Pandas"]),
    ]

    predicted = [
        make_group(["Pandas", "NumPy"]),
    ]

    result = JobExtractionEvaluator().evaluate(
        make_case(expected),
        make_prediction(predicted),
    )

    assert result.matched_count == 1


def test_empty_expected_and_predicted():
    result = JobExtractionEvaluator().evaluate(
        make_case([]),
        make_prediction([]),
    )

    assert result.precision == 1.0
    assert result.recall == 1.0
    assert result.f1 == 1.0


def test_rejects_wrong_job_id():
    predicted = GroupedJobAnalysis(
        job_id="wrong-id",
        requirement_groups=[],
    )

    with pytest.raises(
        ValueError,
        match="job ID",
    ):
        JobExtractionEvaluator().evaluate(
            make_case([]),
            predicted,
        )


def test_case_insensitive_skill_matching():
    expected = [
        make_group(["Statistical Analysis"]),
    ]

    predicted = [
        make_group(["statistical analysis"]),
    ]

    result = JobExtractionEvaluator().evaluate(
        make_case(expected),
        make_prediction(predicted),
    )

    assert result.matched_count == 1
    assert result.f1 == 1.0


def test_rag_alias_matching():
    expected = [
        make_group(["RAG"]),
    ]

    predicted = [
        make_group(["retrieval-augmented generation (RAG)"]),
    ]

    result = JobExtractionEvaluator().evaluate(
        make_case(expected),
        make_prediction(predicted),
    )

    assert result.matched_count == 1
    assert result.f1 == 1.0


def test_group_skill_order_and_case_insensitive():
    expected = [
        make_group(
            ["REST APIs", "FastAPI"],
            priority="preferred",
        ),
    ]

    predicted = [
        make_group(
            ["fastapi", "rest apis"],
            priority="preferred",
        ),
    ]

    result = JobExtractionEvaluator().evaluate(
        make_case(expected),
        make_prediction(predicted),
    )

    assert result.matched_count == 1
