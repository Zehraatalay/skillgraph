from pydantic import BaseModel, Field, HttpUrl


class RepositoryMatchRequest(BaseModel):
    repository_url: HttpUrl
    limit: int = Field(default=10, ge=1, le=50)


class JobMatchResult(BaseModel):
    job_id: str
    title: str
    role_family: str
    seniority: str
    technology_stack_id: str
    score: float

    matched_required_skills: list[str]
    matched_preferred_skills: list[str]

    missing_required_skills: list[str]
    missing_preferred_skills: list[str]


class RepositoryMatchResponse(BaseModel):
    repository_url: str
    repository: str
    detected_skills: list[str]
    detected_skill_count: int
    total_jobs_evaluated: int
    matches: list[JobMatchResult]

class DeveloperMatchRequest(BaseModel):
    username: str = Field(min_length=1, max_length=39, pattern=r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
    limit: int = Field(default=10, ge=1, le=50)


class DeveloperMatchResponse(BaseModel):
    username: str
    detected_skills: list[str]
    detected_skill_count: int
    total_jobs_evaluated: int
    matches: list[JobMatchResult]
