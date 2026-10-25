from enum import Enum

from pydantic import BaseModel, Field

from agents.schemas.evidence_summary import EvidenceSummary


class SupportLevel(str, Enum):
    NONE = "none"
    SELF_REPORTED = "self_reported"
    IMPLEMENTATION_BACKED = "implementation_backed"
    TESTED = "tested"


class SkillSupport(BaseModel):
    skill: str = Field(min_length=1)
    level: SupportLevel

    cv_evidence_count: int = Field(ge=0)
    github_evidence_count: int = Field(ge=0)

    evidence_summary: EvidenceSummary | None = None
