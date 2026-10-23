from typing import TypedDict

from agents.schemas.candidate import CandidateProfile
from agents.schemas.cv import CVAnalysis
from agents.schemas.github import GitHubAnalysis
from agents.schemas.job import JobPosting


class SkillGraphState(TypedDict):
    # User inputs
    cv_text: str | None
    github_username: str | None
    preferences_text: str | None

    job_postings: list[JobPosting]

    # Intermediate analysis
    cv_analysis: CVAnalysis | None
    github_analysis: GitHubAnalysis | None
    candidate_profile: CandidateProfile | None

    # Final output
    results: list[dict]