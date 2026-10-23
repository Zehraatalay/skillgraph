from pydantic import BaseModel, Field

from agents.schemas.evidence import SkillEvidence


class RepositoryAnalysis(BaseModel):
    repository_name: str = Field(min_length=1)
    repository_url: str | None = None

    skills: list[SkillEvidence] = Field(default_factory=list)

    analyzed_files: list[str] = Field(default_factory=list)


class GitHubAnalysis(BaseModel):
    username: str = Field(min_length=1)

    repositories: list[RepositoryAnalysis] = Field(
        default_factory=list
    )