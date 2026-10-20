from pydantic import BaseModel, Field


class SourceFile(BaseModel):
    path: str
    content: str
    size: int = Field(ge=0)


class RepositoryContext(BaseModel):
    owner: str
    repository: str
    files: list[SourceFile]
    skipped_files: int = 0
    total_characters: int = 0


class SkillEvidence(BaseModel):
    skill: str
    file: str
    explanation: str


class RepositoryAnalysis(BaseModel):
    summary: str
    skills: list[SkillEvidence] = Field(default_factory=list)
