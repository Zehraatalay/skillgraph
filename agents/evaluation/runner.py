from dataclasses import dataclass

from agents.schemas.job_evaluation import JobEvaluationCase
from agents.services.job_extraction_evaluator import (
    JobExtractionEvaluator,
)


@dataclass
class CaseEvaluation:
    name: str
    precision: float
    recall: float
    f1: float
    missing: list[str]
    unexpected: list[str]


class JobEvaluationRunner:
    def __init__(self, extractor=None):
        self.extractor = extractor
        self.evaluator = JobExtractionEvaluator()

    def _key(self, group):
        return self.evaluator._group_key(group)

    def _describe(self, group):
        return f"{group.skills} [{group.operator.value}, {group.priority.value}]"

    def extract_predictions(
        self,
        cases: list[JobEvaluationCase],
    ) -> dict:
        if self.extractor is None:
            raise RuntimeError("Extractor is not configured")

        return {case.job.id: self.extractor.extract(case.job) for case in cases}

    def evaluate_case(
        self,
        case: JobEvaluationCase,
        predicted,
    ) -> CaseEvaluation:
        result = self.evaluator.evaluate(
            case=case,
            predicted=predicted,
        )

        expected_by_key = {
            self._key(group): group for group in case.expected.requirement_groups
        }

        predicted_by_key = {
            self._key(group): group for group in predicted.requirement_groups
        }

        missing_keys = expected_by_key.keys() - predicted_by_key.keys()

        unexpected_keys = predicted_by_key.keys() - expected_by_key.keys()

        missing = [
            self._describe(expected_by_key[key])
            for key in expected_by_key
            if key in missing_keys
        ]

        unexpected = [
            self._describe(predicted_by_key[key])
            for key in predicted_by_key
            if key in unexpected_keys
        ]

        return CaseEvaluation(
            name=case.name,
            precision=result.precision,
            recall=result.recall,
            f1=result.f1,
            missing=missing,
            unexpected=unexpected,
        )

    def evaluate_predictions(
        self,
        cases: list[JobEvaluationCase],
        predictions: dict,
    ) -> list[CaseEvaluation]:
        return [
            self.evaluate_case(
                case,
                predictions[case.job.id],
            )
            for case in cases
        ]

    def run_case(
        self,
        case: JobEvaluationCase,
    ) -> CaseEvaluation:
        if self.extractor is None:
            raise RuntimeError("Extractor is not configured")

        predicted = self.extractor.extract(case.job)

        return self.evaluate_case(case, predicted)

    def run_all(
        self,
        cases: list[JobEvaluationCase],
    ) -> list[CaseEvaluation]:
        return [self.run_case(case) for case in cases]
