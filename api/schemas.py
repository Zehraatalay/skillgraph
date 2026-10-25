from pydantic import BaseModel, Field, model_validator


class JobPostingInput(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    company: str = Field(min_length=1)
    description: str = Field(min_length=1)


class AnalyzeRequest(BaseModel):
    cv_text: str | None = None
    github_username: str | None = None
    job_postings: list[JobPostingInput] = Field(
        min_length=1,
    )

    @model_validator(mode="after")
    def validate_candidate_input(self):
        has_cv = bool(self.cv_text and self.cv_text.strip())

        has_github = bool(self.github_username and self.github_username.strip())

        if not has_cv and not has_github:
            raise ValueError(
                "At least one of cv_text or github_username must be provided"
            )

        return self


class AnalyzeResponse(BaseModel):
    candidate_profile: dict
    job_analyses: list[dict]
    results: list[dict]
