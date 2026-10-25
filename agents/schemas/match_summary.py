from pydantic import BaseModel, Field


class RequirementSummary(BaseModel):
    total: int = Field(ge=0)
    satisfied: int = Field(ge=0)
    partial: int = Field(ge=0)
    missing: int = Field(ge=0)

    coverage: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )


class JobMatchSummary(BaseModel):
    job_id: str = Field(min_length=1)

    required: RequirementSummary
    preferred: RequirementSummary
