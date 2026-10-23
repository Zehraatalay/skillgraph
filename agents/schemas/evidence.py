from enum import Enum

from pydantic import BaseModel, Field


class EvidenceSource(str, Enum):
    CV = "cv"
    GITHUB = "github"


class EvidenceType(str, Enum):
    SELF_REPORTED = "self_reported"
    IMPLEMENTATION = "implementation"
    TESTED = "tested"


class SkillEvidence(BaseModel):
    skill: str = Field(min_length=1)
    source: EvidenceSource
    evidence_type: EvidenceType

    description: str | None = None
    reference: str | None = None