from pydantic import BaseModel, Field

from agents.schemas.evidence import SkillEvidence


class SkillGroup(BaseModel):
    name: str

    evidence: list[SkillEvidence] = Field(default_factory=list)
