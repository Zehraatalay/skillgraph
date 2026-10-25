from pydantic import BaseModel, Field

from agents.schemas.evidence import SkillEvidence


class GitHubEvidenceExtraction(BaseModel):
    skills: list[SkillEvidence] = Field(default_factory=list)
