from agents.schemas.job_requirement import RequirementPriority
from agents.schemas.match_summary import (
    JobMatchSummary,
    RequirementSummary,
)
from agents.schemas.matching import JobMatchResult, RequirementMatch


class MatchSummaryBuilder:
    @staticmethod
    def _summarize(
        requirements: list[RequirementMatch],
    ) -> RequirementSummary:
        total = len(requirements)

        if total == 0:
            return RequirementSummary(
                total=0,
                satisfied=0,
                partial=0,
                missing=0,
                coverage=None,
            )

        satisfied = sum(requirement.satisfied for requirement in requirements)

        partial = sum(
            not requirement.satisfied and requirement.coverage > 0
            for requirement in requirements
        )

        missing = sum(
            not requirement.satisfied and requirement.coverage == 0
            for requirement in requirements
        )

        coverage = sum(requirement.coverage for requirement in requirements) / total

        return RequirementSummary(
            total=total,
            satisfied=satisfied,
            partial=partial,
            missing=missing,
            coverage=coverage,
        )

    def build(
        self,
        result: JobMatchResult,
    ) -> JobMatchSummary:
        required = [
            requirement
            for requirement in result.requirements
            if requirement.priority == RequirementPriority.REQUIRED
        ]

        preferred = [
            requirement
            for requirement in result.requirements
            if requirement.priority == RequirementPriority.PREFERRED
        ]

        return JobMatchSummary(
            job_id=result.job_id,
            required=self._summarize(required),
            preferred=self._summarize(preferred),
        )
