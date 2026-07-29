from pydantic import BaseModel, Field


class TechnologySkillResponse(BaseModel):
    technology: str
    score: float = Field(ge=0, le=100)
    level: str
    repository_count: int
    total_bytes: int
    total_stars: int
    repositories: list[str] = Field(default_factory=list)


class DeveloperSkillProfileResponse(BaseModel):
    developer_login: str
    technology_count: int
    skills: list[TechnologySkillResponse] = Field(default_factory=list)