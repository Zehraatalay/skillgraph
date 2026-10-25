from agents.schemas.grouped_job_analysis import GroupedJobAnalysis
from agents.schemas.job_evaluation import (
    JobEvaluationCase,
    JobEvaluationResult,
)
from agents.schemas.requirement_group import RequirementGroup
from agents.services.skill_normalizer import SkillNormalizer


class JobExtractionEvaluator:
    def __init__(self):
        self.normalizer = SkillNormalizer()

    def _group_key(
        self,
        group: RequirementGroup,
    ) -> tuple:
        normalized_skills = frozenset(
            self.normalizer.normalize(skill).strip().casefold()
            for skill in group.skills
        )

        return (
            normalized_skills,
            group.operator.value,
            group.priority.value,
        )

    def evaluate(
        self,
        case: JobEvaluationCase,
        predicted: GroupedJobAnalysis,
    ) -> JobEvaluationResult:
        if predicted.job_id != case.job.id:
            raise ValueError("Predicted job ID does not match evaluation case")

        expected_keys = {
            self._group_key(group) for group in case.expected.requirement_groups
        }

        predicted_keys = {
            self._group_key(group) for group in predicted.requirement_groups
        }

        matched = len(expected_keys & predicted_keys)

        expected_count = len(expected_keys)
        predicted_count = len(predicted_keys)

        missing = expected_count - matched
        unexpected = predicted_count - matched

        if predicted_count == 0:
            precision = 1.0 if expected_count == 0 else 0.0
        else:
            precision = matched / predicted_count

        recall = matched / expected_count if expected_count > 0 else 1.0

        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall > 0
            else 0.0
        )

        return JobEvaluationResult(
            case_name=case.name,
            expected_count=expected_count,
            predicted_count=predicted_count,
            matched_count=matched,
            missing_count=missing,
            unexpected_count=unexpected,
            precision=precision,
            recall=recall,
            f1=f1,
        )
