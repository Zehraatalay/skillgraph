

from typing import TypedDict


class SkillGraphState(TypedDict, total=False):
    cv_text: str | None
    github_username: str | None
    preferences_text: str | None

    job_postings: list[dict]

    cv_analysis: dict | None
    github_analysis: dict | None
    candidate_profile: dict | None

    job_analyses: list[dict]
    results: list[dict]
