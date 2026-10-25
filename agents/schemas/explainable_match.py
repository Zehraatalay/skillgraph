from pydantic import BaseModel, Field

from agents.schemas.evidence_support import SkillSupport
from agents.schemas.match_summary import JobMatchSummary
from agents.schemas.matching import (
    JobMatchResult,
    RequirementMatch,
)


class ExplainedRequirement(BaseModel):
    requirement: RequirementMatch

    skill_support: list[SkillSupport] = Field(default_factory=list)


class ExplainableJobMatch(BaseModel):
    job_id: str = Field(min_length=1)

    match_result: JobMatchResult

    summary: JobMatchSummary

    explained_requirements: list[ExplainedRequirement] = Field(default_factory=list)
