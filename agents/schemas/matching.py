from typing import Literal

from pydantic import BaseModel, Field, computed_field

from agents.schemas.evidence import SkillEvidence
from agents.schemas.job_requirement import RequirementPriority
from agents.schemas.matched_evidence import MatchedEvidence
from agents.schemas.requirement_group import RequirementOperator
from agents.schemas.support_level import SupportLevel


class SkillMatch(BaseModel):
    skill: str

    matched: bool

    matched_evidence: list[MatchedEvidence] = Field(default_factory=list)

    support_level: SupportLevel = SupportLevel.NONE

    partial_evidence: list[SkillEvidence] = Field(default_factory=list)

    @computed_field
    @property
    def evidence(self) -> list[SkillEvidence]:
        return [item.evidence for item in self.matched_evidence]


class RequirementMatch(BaseModel):
    skills: list[SkillMatch]

    operator: RequirementOperator

    priority: RequirementPriority

    satisfied: bool

    coverage: float = Field(
        ge=0.0,
        le=1.0,
    )

    evidence_text: str


class JobMatchResult(BaseModel):
    job_id: str

    requirements: list[RequirementMatch] = Field(default_factory=list)

    required_coverage: float = Field(
        ge=0.0,
        le=1.0,
    )

    preferred_coverage: float = Field(
        ge=0.0,
        le=1.0,
    )
    semantic_status: Literal[
        "not_requested",
        "completed",
        "failed",
    ] = "not_requested"
