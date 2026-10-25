import pytest

from agents.evaluation.store import EvaluationStore
from agents.schemas.grouped_job_analysis import GroupedJobAnalysis
from agents.schemas.requirement_group import RequirementGroup


def test_save_and_load_predictions(tmp_path):
    store = EvaluationStore(tmp_path)

    predictions = {
        "job-001": GroupedJobAnalysis(
            job_id="job-001",
            requirement_groups=[
                RequirementGroup(
                    skills=["Python"],
                    priority="required",
                    evidence="Python is required.",
                )
            ],
        )
    }

    path = store.save(
        "baseline",
        predictions,
    )

    assert path.exists()

    loaded = store.load("baseline")

    assert loaded == predictions


def test_save_empty_predictions(tmp_path):
    store = EvaluationStore(tmp_path)

    store.save("empty", {})

    assert store.load("empty") == {}


@pytest.mark.parametrize(
    "invalid_name",
    [
        "",
        "../secret",
        "test/name",
        "test.name",
        "test name",
    ],
)
def test_rejects_invalid_name(tmp_path, invalid_name):
    store = EvaluationStore(tmp_path)

    with pytest.raises(ValueError):
        store.save(invalid_name, {})

    with pytest.raises(ValueError):
        store.load(invalid_name)


def test_missing_evaluation_file(tmp_path):
    store = EvaluationStore(tmp_path)

    with pytest.raises(FileNotFoundError):
        store.load("missing")
