from pydantic import BaseModel, Field, HttpUrl


class RepositoryAnalysisRequest(BaseModel):
    repository_url: HttpUrl


class RepositoryAnalysisResponse(BaseModel):
    owner: str
    repository: str
    repository_url: str
    analyzed_files: list[str]
    skills: list[str]
    skill_count: int = Field(ge=0) 