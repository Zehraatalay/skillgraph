from pydantic import BaseModel, Field


class DeveloperGraphSummaryResponse(BaseModel):
    login: str
    name: str | None = None
    repository_count: int
    technologies: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)


class DeveloperAnalysisResponse(BaseModel):
    message: str
    developer: DeveloperGraphSummaryResponse