from pydantic import BaseModel, Field


class SimilarDeveloperResponse(BaseModel):
    login: str
    name: str | None = None
    avatar_url: str | None = None
    html_url: str | None = None
    similarity_score: float = Field(ge=0, le=100)
    shared_technology_count: int
    shared_technologies: list[str] = Field(default_factory=list)
    candidate_technologies: list[str] = Field(default_factory=list)


class DeveloperSimilarityResponse(BaseModel):
    developer_login: str
    similar_developer_count: int
    similar_developers: list[SimilarDeveloperResponse] = Field(
        default_factory=list
    )