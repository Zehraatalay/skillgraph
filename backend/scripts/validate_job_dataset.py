from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from app.jobs.dataset_blueprint import (
    ROLE_DISTRIBUTION,
    SENIORITY_DISTRIBUTION,
)
from app.jobs.schemas import (
    JobDatasetMetadata,
    JobPosting,
)
from app.jobs.technology_stacks import (
    TECHNOLOGY_STACKS,
)


BACKEND_ROOT = Path(__file__).resolve().parent.parent

DATA_DIRECTORY = (
    BACKEND_ROOT
    / "data"
    / "curated_jobs"
)

JOBS_FILE = (
    DATA_DIRECTORY
    / "job_postings.json"
)

METADATA_FILE = (
    DATA_DIRECTORY
    / "dataset_metadata.json"
)


STACKS_BY_ID = {
    stack["stack_id"]: stack
    for stack in TECHNOLOGY_STACKS
}


def load_json(
    path: Path,
) -> Any:
    if not path.exists():
        raise FileNotFoundError(
            f"Required file not found: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def validate_unique_job_ids(
    jobs: list[JobPosting],
) -> None:
    job_ids = [
        job.job_id
        for job in jobs
    ]

    duplicate_ids = [
        job_id
        for job_id, count in Counter(
            job_ids
        ).items()
        if count > 1
    ]

    if duplicate_ids:
        raise ValueError(
            "Duplicate job IDs found: "
            f"{duplicate_ids}"
        )


def validate_unique_skill_lists(
    jobs: list[JobPosting],
) -> None:
    for job in jobs:
        required_names = [
            skill.name
            for skill in (
                job.required_skills
            )
        ]

        preferred_names = [
            skill.name
            for skill in (
                job.preferred_skills
            )
        ]

        if len(required_names) != len(
            set(required_names)
        ):
            raise ValueError(
                "Duplicate required skill "
                f"in {job.job_id}."
            )

        if len(preferred_names) != len(
            set(preferred_names)
        ):
            raise ValueError(
                "Duplicate preferred skill "
                f"in {job.job_id}."
            )

        overlap = (
            set(required_names)
            & set(preferred_names)
        )

        if overlap:
            raise ValueError(
                f"Job {job.job_id} contains skills "
                "as both required and preferred: "
                f"{sorted(overlap)}"
            )


def validate_stack_consistency(
    jobs: list[JobPosting],
) -> None:
    for job in jobs:
        stack = STACKS_BY_ID.get(
            job.technology_stack_id
        )

        if stack is None:
            raise ValueError(
                "Unknown technology stack "
                f"'{job.technology_stack_id}' "
                f"in job {job.job_id}."
            )

        if stack["role_family"] != (
            job.role_family.value
        ):
            raise ValueError(
                f"Role and stack mismatch in {job.job_id}. "
                f"Role: {job.role_family.value}, "
                f"stack role: {stack['role_family']}."
            )

        allowed_skills = (
            set(stack["required_skills"])
            | set(stack["preferred_skills"])
        )

        job_skills = {
            skill.name
            for skill in (
                job.required_skills
                + job.preferred_skills
            )
        }

        invalid_skills = (
            job_skills
            - allowed_skills
        )

        if invalid_skills:
            raise ValueError(
                f"Job {job.job_id} contains skills "
                "outside its technology stack: "
                f"{sorted(invalid_skills)}"
            )


def validate_distributions(
    jobs: list[JobPosting],
) -> None:
    actual_roles = Counter(
        job.role_family.value
        for job in jobs
    )

    actual_seniorities = Counter(
        job.seniority.value
        for job in jobs
    )

    if dict(actual_roles) != (
        ROLE_DISTRIBUTION
    ):
        raise ValueError(
            "Role distribution mismatch.\n"
            f"Expected: {ROLE_DISTRIBUTION}\n"
            f"Actual: {dict(actual_roles)}"
        )

    if dict(actual_seniorities) != (
        SENIORITY_DISTRIBUTION
    ):
        raise ValueError(
            "Seniority distribution mismatch.\n"
            f"Expected: {SENIORITY_DISTRIBUTION}\n"
            f"Actual: {dict(actual_seniorities)}"
        )


def validate_metadata(
    metadata: JobDatasetMetadata,
    jobs: list[JobPosting],
) -> None:
    if metadata.job_count != len(jobs):
        raise ValueError(
            "Metadata job_count does not "
            "match actual job count."
        )

    if not metadata.generated:
        raise ValueError(
            "Metadata generated flag "
            "must be true."
        )

    actual_role_distribution = dict(
        sorted(
            Counter(
                job.role_family.value
                for job in jobs
            ).items()
        )
    )

    actual_stack_distribution = dict(
        sorted(
            Counter(
                job.technology_stack_id
                for job in jobs
            ).items()
        )
    )

    actual_seniority_distribution = dict(
        sorted(
            Counter(
                job.seniority.value
                for job in jobs
            ).items()
        )
    )

    if metadata.role_distribution != (
        actual_role_distribution
    ):
        raise ValueError(
            "Metadata role distribution "
            "does not match job data."
        )

    if (
        metadata.technology_stack_distribution
        != actual_stack_distribution
    ):
        raise ValueError(
            "Metadata technology stack "
            "distribution does not match job data."
        )

    if (
        metadata.seniority_distribution
        != actual_seniority_distribution
    ):
        raise ValueError(
            "Metadata seniority distribution "
            "does not match job data."
        )


def main() -> None:
    raw_jobs = load_json(
        JOBS_FILE
    )

    raw_metadata = load_json(
        METADATA_FILE
    )

    if not isinstance(raw_jobs, list):
        raise ValueError(
            "job_postings.json must "
            "contain a JSON array."
        )

    jobs = [
        JobPosting.model_validate(
            job
        )
        for job in raw_jobs
    ]

    metadata = (
        JobDatasetMetadata.model_validate(
            raw_metadata
        )
    )

    if len(jobs) != 200:
        raise ValueError(
            "Dataset must contain exactly "
            f"200 jobs, got {len(jobs)}."
        )

    validate_unique_job_ids(
        jobs
    )

    validate_unique_skill_lists(
        jobs
    )

    validate_stack_consistency(
        jobs
    )

    validate_distributions(
        jobs
    )

    validate_metadata(
        metadata,
        jobs,
    )

    unique_required_skills = {
        skill.name
        for job in jobs
        for skill in job.required_skills
    }

    unique_preferred_skills = {
        skill.name
        for job in jobs
        for skill in job.preferred_skills
    }

    used_stacks = {
        job.technology_stack_id
        for job in jobs
    }

    print(
        "Dataset validation passed."
    )

    print(
        f"Validated jobs: {len(jobs)}"
    )

    print(
        "Technology stacks used: "
        f"{len(used_stacks)}"
    )

    print(
        "Unique required skills: "
        f"{len(unique_required_skills)}"
    )

    print(
        "Unique preferred skills: "
        f"{len(unique_preferred_skills)}"
    )


if __name__ == "__main__":
    main()