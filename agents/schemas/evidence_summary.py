from pydantic import BaseModel, Field


class EvidenceSummary(BaseModel):
    total_evidence: int = Field(ge=0)

    cv_evidence_count: int = Field(ge=0)
    github_evidence_count: int = Field(ge=0)

    exact_count: int = Field(ge=0)
    alias_count: int = Field(ge=0)
    hierarchical_count: int = Field(ge=0)

    unique_references: list[str] = Field(default_factory=list)
