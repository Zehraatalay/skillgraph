from pydantic import BaseModel, Field

from agents.schemas.evidence import SkillEvidence


class CVAnalysis(BaseModel):
    skills: list[SkillEvidence] = Field(default_factory=list)

    education: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)