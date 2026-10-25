from enum import Enum

from pydantic import BaseModel, Field, model_validator

from agents.schemas.job_requirement import RequirementPriority


class RequirementOperator(str, Enum):
    ALL = "all"
    ANY = "any"


class RequirementGroup(BaseModel):
    skills: list[str] = Field(min_length=1)

    operator: RequirementOperator = RequirementOperator.ALL

    priority: RequirementPriority

    evidence: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_skills(self):
        cleaned_skills = [skill.strip() for skill in self.skills]

        if any(not skill for skill in cleaned_skills):
            raise ValueError("Requirement skills cannot be empty")

        normalized_skills = [skill.casefold() for skill in cleaned_skills]

        if len(normalized_skills) != len(set(normalized_skills)):
            raise ValueError("Duplicate skills in requirement group")

        self.skills = cleaned_skills

        return self
