from agents.schemas.candidate import CandidateProfile
from agents.schemas.grouped_job_analysis import GroupedJobAnalysis
from agents.schemas.job_requirement import RequirementPriority
from agents.schemas.matching import JobMatchResult, RequirementMatch
from agents.services.requirement_matcher import RequirementMatcher


class JobMatcher:
    def __init__(
        self,
        requirement_matcher: RequirementMatcher | None = None,
    ):
        self.requirement_matcher = requirement_matcher or RequirementMatcher()

    @staticmethod
    def _average_coverage(
        requirements: list[RequirementMatch],
    ) -> float:
        if not requirements:
            return 1.0

        return sum(requirement.coverage for requirement in requirements) / len(
            requirements
        )

    def match(
        self,
        candidate: CandidateProfile,
        job: GroupedJobAnalysis,
    ) -> JobMatchResult:
        requirement_matches = [
            self.requirement_matcher.match(
                requirement,
                candidate.skills,
            )
            for requirement in job.requirement_groups
        ]

        required_matches = [
            requirement
            for requirement in requirement_matches
            if requirement.priority == RequirementPriority.REQUIRED
        ]

        preferred_matches = [
            requirement
            for requirement in requirement_matches
            if requirement.priority == RequirementPriority.PREFERRED
        ]

        return JobMatchResult(
            job_id=job.job_id,
            requirements=requirement_matches,
            required_coverage=self._average_coverage(required_matches),
            preferred_coverage=self._average_coverage(preferred_matches),
        )
