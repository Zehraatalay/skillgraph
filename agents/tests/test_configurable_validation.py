import pytest

from agents.nodes.validate_input import (
    create_validate_input_node,
)


def test_candidate_only_validation():
    validator = create_validate_input_node(require_job_postings=False)

    result = validator(
        {
            "cv_text": "Python developer",
            "github_username": None,
        }
    )

    assert result == {}


def test_matching_validation_requires_jobs():
    validator = create_validate_input_node(require_job_postings=True)

    with pytest.raises(
        ValueError,
        match="At least one job posting is required",
    ):
        validator(
            {
                "cv_text": "Python developer",
                "github_username": None,
            }
        )


def test_matching_validation_with_jobs():
    validator = create_validate_input_node(require_job_postings=True)

    result = validator(
        {
            "cv_text": "Python developer",
            "job_postings": [
                {
                    "id": "job-001",
                    "title": "Python Developer",
                    "description": "Python is required.",
                }
            ],
        }
    )

    assert result == {}


def test_candidate_source_still_required():
    validator = create_validate_input_node(require_job_postings=False)

    with pytest.raises(
        ValueError,
        match="At least one candidate source is required",
    ):
        validator(
            {
                "cv_text": "",
                "github_username": None,
            }
        )
