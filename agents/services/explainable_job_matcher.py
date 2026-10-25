from agents.schemas.candidate import CandidateProfile
from agents.schemas.explainable_match import (
    ExplainableJobMatch,
    ExplainedRequirement,
)
from agents.schemas.grouped_job_analysis import GroupedJobAnalysis
from agents.services.evidence_support_classifier import (
    EvidenceSupportClassifier,
)
from agents.services.job_matcher import JobMatcher
from agents.services.match_summary_builder import (
    MatchSummaryBuilder,
)


class ExplainableJobMatcher:
    def __init__(
        self,
        job_matcher: JobMatcher | None = None,
        summary_builder: MatchSummaryBuilder | None = None,
        support_classifier: EvidenceSupportClassifier | None = None,
    ):
        self.job_matcher = job_matcher or JobMatcher()

        self.summary_builder = summary_builder or MatchSummaryBuilder()

        self.support_classifier = support_classifier or EvidenceSupportClassifier()

    def match(
        self,
        candidate: CandidateProfile,
        job: GroupedJobAnalysis,
    ) -> ExplainableJobMatch:
        match_result = self.job_matcher.match(
            candidate,
            job,
        )

        summary = self.summary_builder.build(match_result)

        explained_requirements = []

        for requirement_match in match_result.requirements:
            skill_support = [
                self.support_classifier.classify(skill_match)
                for skill_match in requirement_match.skills
            ]

            explained_requirements.append(
                ExplainedRequirement(
                    requirement=requirement_match,
                    skill_support=skill_support,
                )
            )

        return ExplainableJobMatch(
            job_id=job.job_id,
            match_result=match_result,
            summary=summary,
            explained_requirements=explained_requirements,
        )
