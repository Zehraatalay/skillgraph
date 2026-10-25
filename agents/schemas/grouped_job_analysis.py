from pydantic import BaseModel, Field

from agents.schemas.requirement_group import RequirementGroup


class GroupedJobAnalysis(BaseModel):
    job_id: str = Field(min_length=1)

    requirement_groups: list[RequirementGroup] = Field(default_factory=list)
