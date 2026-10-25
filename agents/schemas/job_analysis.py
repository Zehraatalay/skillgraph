from pydantic import BaseModel, Field

from agents.schemas.job_requirement import JobRequirement


class JobAnalysis(BaseModel):
    job_id: str = Field(min_length=1)

    requirements: list[JobRequirement] = Field(default_factory=list)
