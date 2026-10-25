from pydantic import BaseModel, Field

from agents.schemas.support_level import SupportLevel


class SemanticMatchDecision(BaseModel):
    requirement_id: str | None = None

    required_skill: str

    support_level: SupportLevel

    supporting_evidence_indices: list[int] = Field(default_factory=list)

    reasoning: str


class SemanticMatchBatch(BaseModel):
    decisions: list[SemanticMatchDecision] = Field(default_factory=list)
