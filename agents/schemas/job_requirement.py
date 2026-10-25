from enum import Enum

from pydantic import BaseModel, Field


class RequirementPriority(str, Enum):
    REQUIRED = "required"
    PREFERRED = "preferred"


class JobRequirement(BaseModel):
    skill: str = Field(min_length=1)

    priority: RequirementPriority

    evidence: str = Field(min_length=1)
