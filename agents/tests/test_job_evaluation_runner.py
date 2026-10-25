from agents.evaluation.golden_jobs import GOLDEN_CASES
from agents.evaluation.runner import JobEvaluationRunner


class FakeExtractor:
    def __init__(self, responses):
        self.responses = responses

    def extract(self, job):
        return self.responses[job.id]


def test_runner_perfect_predictions():
    responses = {case.job.id: case.expected for case in GOLDEN_CASES}

    runner = JobEvaluationRunner(FakeExtractor(responses))

    results = runner.run_all(GOLDEN_CASES)

    assert len(results) == len(GOLDEN_CASES)

    for result in results:
        assert result.precision == 1.0
        assert result.recall == 1.0
        assert result.f1 == 1.0
        assert result.missing == []
        assert result.unexpected == []


def test_runner_detects_missing_requirement():
    case = GOLDEN_CASES[0]

    incomplete = case.expected.model_copy(deep=True)

    incomplete.requirement_groups = incomplete.requirement_groups[:-1]

    runner = JobEvaluationRunner(FakeExtractor({case.job.id: incomplete}))

    result = runner.run_case(case)

    assert result.recall < 1.0
    assert len(result.missing) == 1
    assert result.unexpected == []


def test_evaluates_stored_predictions():
    responses = {case.job.id: case.expected for case in GOLDEN_CASES}

    runner = JobEvaluationRunner(FakeExtractor({}))

    results = runner.evaluate_predictions(
        GOLDEN_CASES,
        responses,
    )

    assert len(results) == len(GOLDEN_CASES)

    for result in results:
        assert result.f1 == 1.0


def test_evaluate_predictions_does_not_replace_extractor():
    extractor = FakeExtractor({})

    runner = JobEvaluationRunner(extractor)

    predictions = {case.job.id: case.expected for case in GOLDEN_CASES}

    runner.evaluate_predictions(
        GOLDEN_CASES,
        predictions,
    )

    assert runner.extractor is extractor


def test_extract_predictions_requires_extractor():
    import pytest

    runner = JobEvaluationRunner()

    with pytest.raises(
        RuntimeError,
        match="Extractor is not configured",
    ):
        runner.extract_predictions(GOLDEN_CASES)
