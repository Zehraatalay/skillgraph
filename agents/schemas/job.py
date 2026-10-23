from pydantic import BaseModel, Field


class JobPosting(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)

    company: str | None = None
    url: str | None = None

    requirements: list[str] = Field(default_factory=list)