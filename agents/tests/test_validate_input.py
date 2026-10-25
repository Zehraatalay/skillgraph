import pytest

from agents.nodes.validate_input import validate_input
from agents.schemas.job import JobPosting


@pytest.fixture
def valid_job():
    return JobPosting(
        id="job-001",
        title="Data Analyst",
        description="Experience with SQL and Python.",
    )


@pytest.mark.parametrize(
    "cv_text,github_username",
    [
        ("Python developer", None),
        (None, "exampleuser"),
        ("Python developer", "exampleuser"),
    ],
)
def test_valid_candidate_sources(
    valid_job,
    cv_text,
    github_username,
):
    state = {
        "cv_text": cv_text,
        "github_username": github_username,
        "preferences_text": "Interested in Data Analyst roles",
        "job_postings": [valid_job],
    }

    assert validate_input(state) == {}


@pytest.mark.parametrize(
    "cv_text,github_username",
    [
        (None, None),
        ("", ""),
        ("   ", None),
        (None, "   "),
    ],
)
def test_missing_candidate_sources(
    valid_job,
    cv_text,
    github_username,
):
    state = {
        "cv_text": cv_text,
        "github_username": github_username,
        "preferences_text": "Interested in Data Analyst roles",
        "job_postings": [valid_job],
    }

    with pytest.raises(
        ValueError,
        match="At least one candidate source",
    ):
        validate_input(state)


def test_missing_job_postings():
    state = {
        "cv_text": "Python developer",
        "github_username": None,
        "preferences_text": "Interested in Data Analyst roles",
        "job_postings": [],
    }

    with pytest.raises(
        ValueError,
        match="At least one job posting",
    ):
        validate_input(state)


@pytest.mark.parametrize(
    "preferences_text",
    [None, "", "   "],
)
def test_optional_preferences(valid_job, preferences_text):
    state = {
        "cv_text": "Python developer",
        "github_username": None,
        "preferences_text": preferences_text,
        "job_postings": [valid_job],
    }

    assert validate_input(state) == {}
