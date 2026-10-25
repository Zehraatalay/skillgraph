from agents.graph.state import SkillGraphState
from agents.schemas.candidate import CandidateProfile
from agents.schemas.grouped_job_analysis import GroupedJobAnalysis
from agents.services.explainable_job_matcher import (
    ExplainableJobMatcher,
)


def create_job_matching_node(
    matcher: ExplainableJobMatcher | None = None,
):
    matcher = matcher if matcher is not None else ExplainableJobMatcher()

    def match_jobs(state: SkillGraphState) -> dict:
        candidate_data = state.get("candidate_profile")

        if candidate_data is None:
            raise ValueError("Candidate profile is required for matching")

        candidate = CandidateProfile.model_validate(candidate_data)

        job_analyses = state.get("job_analyses") or []

        results = []

        for job_data in job_analyses:
            job = GroupedJobAnalysis.model_validate(job_data)

            result = matcher.match(
                candidate,
                job,
            )

            results.append(result.model_dump(mode="json"))

        return {
            "results": results,
        }

    return match_jobs
