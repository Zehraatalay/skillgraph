from pydantic import BaseModel, Field


class TechnologyRecommendationResponse(BaseModel):
    technology: str
    score: float = Field(ge=0, le=100)
    priority: str
    reason: str
    based_on: list[str] = Field(default_factory=list)


class DeveloperRecommendationResponse(BaseModel):
    developer_login: str
    recommendation_count: int
    recommendations: list[TechnologyRecommendationResponse] = Field(
        default_factory=list
    )