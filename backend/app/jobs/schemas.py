from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RoleFamily(str, Enum):
    BACKEND = "backend"
    FRONTEND = "frontend"
    FULL_STACK = "full_stack"
    MACHINE_LEARNING = "machine_learning"
    AI_ENGINEERING = "ai_engineering"
    DATA_ENGINEERING = "data_engineering"
    DATA_SCIENCE = "data_science"
    DEVOPS = "devops"
    MOBILE = "mobile"
    UNITY_GAME = "unity_game"


class SeniorityLevel(str, Enum):
    INTERN = "intern"
    JUNIOR = "junior"
    MID = "mid"


class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    INTERNSHIP = "internship"
    CONTRACT = "contract"


class WorkplaceType(str, Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ON_SITE = "on_site"


class DatasetSourceType(str, Enum):
    CURATED_TEMPLATE = "curated_template"
    ANONYMIZED_REAL_DERIVED = "anonymized_real_derived"


class SkillRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        min_length=1,
        max_length=100,
    )

    weight: float = Field(
        ge=0.1,
        le=1.0,
    )

    evidence_type: str = Field(
        default="github",
        description=(
            "How this skill may be evidenced. "
            "Examples: github, repository, configuration, workflow."
        ),
    )

    @field_validator("name")
    @classmethod
    def normalize_skill_name(
        cls,
        value: str,
    ) -> str:
        normalized = " ".join(
            value.strip().lower().split()
        )

        if not normalized:
            raise ValueError(
                "Skill name cannot be empty."
            )

        return normalized


class JobPosting(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_id: str = Field(
        min_length=3,
        max_length=100,
    )

    title: str = Field(
        min_length=3,
        max_length=150,
    )

    role_family: RoleFamily
    technology_stack_id: str = Field(
    min_length=3,
    max_length=100,
    )

    seniority: SeniorityLevel
    employment_type: EmploymentType
    workplace_type: WorkplaceType

    location: str = Field(
        min_length=2,
        max_length=100,
    )

    summary: str = Field(
        min_length=50,
        max_length=1000,
    )

    responsibilities: list[str] = Field(
        min_length=3,
        max_length=8,
    )

    minimum_qualifications: list[str] = Field(
        min_length=2,
        max_length=8,
    )

    preferred_qualifications: list[str] = Field(
        default_factory=list,
        max_length=8,
    )

    required_skills: list[SkillRequirement] = Field(
        min_length=3,
        max_length=10,
    )

    preferred_skills: list[SkillRequirement] = Field(
        default_factory=list,
        max_length=10,
    )

    source_type: DatasetSourceType
    source_note: str = Field(
        min_length=10,
        max_length=500,
    )

    is_synthetic: bool = True
    dataset_version: str = "1.0.0"

    @field_validator(
        "responsibilities",
        "minimum_qualifications",
        "preferred_qualifications",
    )
    @classmethod
    def clean_text_list(
        cls,
        values: list[str],
    ) -> list[str]:
        cleaned_values: list[str] = []
        seen_values: set[str] = set()

        for value in values:
            cleaned = " ".join(
                value.strip().split()
            )

            if not cleaned:
                continue

            comparison_value = cleaned.casefold()

            if comparison_value in seen_values:
                continue

            seen_values.add(
                comparison_value
            )
            cleaned_values.append(
                cleaned
            )

        return cleaned_values

    @field_validator("preferred_skills")
    @classmethod
    def validate_preferred_skills(
        cls,
        preferred_skills: list[
            SkillRequirement
        ],
        validation_info,
    ) -> list[SkillRequirement]:
        required_skills = (
            validation_info.data.get(
                "required_skills",
                [],
            )
        )

        required_names = {
            skill.name
            for skill in required_skills
        }

        preferred_names = {
            skill.name
            for skill in preferred_skills
        }

        duplicate_names = (
            required_names
            & preferred_names
        )

        if duplicate_names:
            raise ValueError(
                "Skills cannot be both required "
                "and preferred: "
                f"{sorted(duplicate_names)}"
            )

        return preferred_skills


class JobDatasetMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_name: str
    version: str
    description: str

    job_count: int = Field(
        ge=0,
    )

    generated: bool

    role_distribution: dict[str, int] = (
        Field(default_factory=dict)
    )
    technology_stack_distribution: dict[str, int] = Field(
        default_factory=dict
    )
    seniority_distribution: dict[
        str,
        int
    ] = Field(default_factory=dict)

    source_distribution: dict[
        str,
        int
    ] = Field(default_factory=dict)

    generation_seed: int | None = None
    generated_at: str | None = None