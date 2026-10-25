from enum import Enum

from pydantic import BaseModel


class EvidenceSource(str, Enum):
    CV = "cv"
    GITHUB = "github"


class EvidenceType(str, Enum):
    SELF_REPORTED = "self_reported"
    IMPLEMENTATION = "implementation"
    TESTED = "tested"


class SkillEvidence(BaseModel):
    skill: str
    source: EvidenceSource
    evidence_type: EvidenceType
    description: str | None = None
    reference: str | None = None
    code_snippet: str | None = None
