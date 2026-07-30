from __future__ import annotations

import json
import random
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.jobs.dataset_blueprint import (
    DATASET_VERSION,
    EMPLOYMENT_BY_SENIORITY,
    GENERATION_SEED,
    LOCATION_OPTIONS,
    ROLE_DISTRIBUTION,
    SENIORITY_DISTRIBUTION,
    WORKPLACE_OPTIONS,
)
from app.jobs.schemas import (
    JobDatasetMetadata,
    JobPosting,
)
from app.jobs.technology_stacks import (
    TechnologyStack,
    get_stacks_for_role,
)


BACKEND_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIRECTORY = (
    BACKEND_ROOT
    / "data"
    / "curated_jobs"
)

JOBS_OUTPUT_FILE = (
    OUTPUT_DIRECTORY
    / "job_postings.json"
)

METADATA_OUTPUT_FILE = (
    OUTPUT_DIRECTORY
    / "dataset_metadata.json"
)


GENERAL_RESPONSIBILITIES = (
    "Design, implement, test, and maintain software features aligned with product requirements.",
    "Collaborate with engineers, designers, and stakeholders during planning, development, and review.",
    "Write readable and maintainable code supported by automated tests and technical documentation.",
    "Investigate defects, improve performance, and contribute to the long-term reliability of the product.",
    "Participate in code reviews and apply engineering standards across the development lifecycle.",
    "Contribute to continuous integration, delivery, and deployment workflows where appropriate.",
    "Translate technical requirements into practical implementation plans and incremental deliverables.",
    "Monitor application behavior and identify opportunities for reliability and usability improvements.",
)


ROLE_RESPONSIBILITIES = {
    "backend": (
        "Develop APIs, backend services, integrations, and persistence layers for product features."
    ),
    "frontend": (
        "Implement responsive interfaces and reusable components from product and design specifications."
    ),
    "full_stack": (
        "Deliver complete product features spanning interfaces, APIs, integrations, and data persistence."
    ),
    "machine_learning": (
        "Prepare datasets, evaluate experiments, and integrate selected machine learning models into applications."
    ),
    "ai_engineering": (
        "Implement AI workflows combining language models, retrieval, structured data, and application services."
    ),
    "data_engineering": (
        "Build ingestion, transformation, orchestration, and data-quality workflows."
    ),
    "data_science": (
        "Perform analysis, experimentation, visualization, and predictive modeling for measurable use cases."
    ),
    "devops": (
        "Automate infrastructure, deployment, monitoring, and operational workflows across environments."
    ),
    "mobile": (
        "Develop mobile features, platform integrations, automated tests, and performance improvements."
    ),
    "unity_game": (
        "Implement gameplay systems, interfaces, tools, and performance improvements in Unity."
    ),
}


PREFERRED_QUALIFICATION_TEMPLATES = (
    "Experience contributing to collaborative software projects or open-source repositories.",
    "Familiarity with cloud platforms, containerization, or automated delivery workflows.",
    "Evidence of personal, academic, freelance, or professional projects related to the role.",
    "Understanding of secure software development and common application security concerns.",
    "Experience working with issue tracking, code review, and version control workflows.",
    "Ability to explain technical decisions through documentation and clear implementation choices.",
)


SENIORITY_MINIMUMS = {
    "intern": (
        "Currently pursuing or recently completed a degree or structured training in a relevant technical field.",
        "Foundational programming knowledge demonstrated through coursework, projects, or repositories.",
        "Willingness to learn unfamiliar tools and receive feedback through code review.",
    ),
    "junior": (
        "Practical development experience demonstrated through academic, personal, freelance, or professional projects.",
        "Working knowledge of version control and collaborative development practices.",
        "Ability to implement scoped features with guidance and communicate technical blockers.",
    ),
    "mid": (
        "Professional or equivalent project experience delivering maintainable software systems.",
        "Ability to independently design and implement moderately complex technical features.",
        "Experience reviewing code, diagnosing production issues, and improving engineering practices.",
    ),
}


SENIORITY_SUMMARY_CONTEXT = {
    "intern": (
        "The position is designed for an early-career candidate "
        "who wants structured technical experience and regular mentorship."
    ),
    "junior": (
        "The role is suitable for an early-career engineer who can "
        "demonstrate practical project work and strong technical fundamentals."
    ),
    "mid": (
        "The position requires an engineer who can own scoped technical "
        "areas and contribute independently to design and delivery decisions."
    ),
}


PREFERRED_SKILL_COUNTS = {
    "intern": 2,
    "junior": 3,
    "mid": 4,
}


def allocate_role_seniority_pairs() -> list[tuple[str, str]]:
    roles: list[str] = []

    for role_family, count in ROLE_DISTRIBUTION.items():
        roles.extend(
            [role_family] * count
        )

    seniorities: list[str] = []

    for seniority, count in SENIORITY_DISTRIBUTION.items():
        seniorities.extend(
            [seniority] * count
        )

    random.shuffle(roles)
    random.shuffle(seniorities)

    return list(
        zip(
            roles,
            seniorities,
            strict=True,
        )
    )


def choose_stack(
    role_family: str,
) -> TechnologyStack:
    stacks = get_stacks_for_role(
        role_family
    )

    if not stacks:
        raise ValueError(
            f"No technology stack found for role: {role_family}"
        )

    return random.choice(stacks)


def choose_stack_skills(
    stack: TechnologyStack,
    seniority: str,
) -> tuple[list[str], list[str]]:
    base_required = list(
        stack["required_skills"]
    )

    base_preferred = list(
        stack["preferred_skills"]
    )

    if seniority == "intern":
        required_skills = base_required[:4]

        preferred_candidates = (
            base_required[4:]
            + base_preferred
        )

    elif seniority == "junior":
        required_skills = list(
            base_required
        )

        preferred_candidates = list(
            base_preferred
        )

    elif seniority == "mid":
        required_skills = list(
            base_required
        )

        preferred_candidates = list(
            base_preferred
        )

        if preferred_candidates:
            promoted_skill = random.choice(
                preferred_candidates
            )

            required_skills.append(
                promoted_skill
            )

            preferred_candidates.remove(
                promoted_skill
            )

    else:
        raise ValueError(
            f"Unsupported seniority level: {seniority}"
        )

    preferred_count = min(
        PREFERRED_SKILL_COUNTS[seniority],
        len(preferred_candidates),
    )

    preferred_skills = random.sample(
        preferred_candidates,
        k=preferred_count,
    )

    return (
        required_skills,
        preferred_skills,
    )


def build_weighted_skills(
    skill_names: list[str],
    *,
    required: bool,
) -> list[dict[str, Any]]:
    weighted_skills: list[
        dict[str, Any]
    ] = []

    for index, skill_name in enumerate(
        skill_names
    ):
        if required:
            weight = max(
                0.70,
                1.0 - index * 0.05,
            )
        else:
            weight = max(
                0.35,
                0.60 - index * 0.05,
            )

        weighted_skills.append(
            {
                "name": skill_name,
                "weight": round(
                    weight,
                    2,
                ),
                "evidence_type": (
                    "repository"
                ),
            }
        )

    return weighted_skills


def build_title(
    stack: TechnologyStack,
    seniority: str,
) -> str:
    base_title = random.choice(
        stack["title_options"]
    )

    if seniority == "intern":
        return f"{base_title} Intern"

    if seniority == "junior":
        return f"Junior {base_title}"

    return base_title


def build_summary(
    stack: TechnologyStack,
    title: str,
    seniority: str,
) -> str:
    return (
        f"We are looking for a {title} to join our engineering team. "
        f"{stack['summary_focus']} "
        f"{SENIORITY_SUMMARY_CONTEXT[seniority]}"
    )


def build_responsibilities(
    role_family: str,
    stack: TechnologyStack,
) -> list[str]:
    responsibilities = random.sample(
        GENERAL_RESPONSIBILITIES,
        k=4,
    )

    responsibilities.append(
        ROLE_RESPONSIBILITIES[
            role_family
        ]
    )

    responsibilities.append(
        "Contribute to technical work based on the "
        f"{stack['display_name']} technology stack."
    )

    return responsibilities


def build_minimum_qualifications(
    seniority: str,
    required_skills: list[str],
) -> list[str]:
    qualifications = list(
        SENIORITY_MINIMUMS[
            seniority
        ]
    )

    highlighted_skills = ", ".join(
        required_skills[:3]
    )

    qualifications.append(
        "Demonstrated experience with "
        f"{highlighted_skills} through "
        "repositories, coursework, or "
        "software projects."
    )

    return qualifications


def build_job(
    *,
    sequence: int,
    role_family: str,
    seniority: str,
) -> JobPosting:
    stack = choose_stack(
        role_family
    )

    title = build_title(
        stack,
        seniority,
    )

    required_skills, preferred_skills = (
        choose_stack_skills(
            stack,
            seniority,
        )
    )

    role_code = role_family.replace(
        "_",
        "-",
    )

    job_id = (
        f"{role_code}-"
        f"{seniority}-"
        f"{sequence:03d}"
    )

    return JobPosting(
        job_id=job_id,
        title=title,
        role_family=role_family,
        technology_stack_id=(
            stack["stack_id"]
        ),
        seniority=seniority,
        employment_type=random.choice(
            EMPLOYMENT_BY_SENIORITY[
                seniority
            ]
        ),
        workplace_type=random.choice(
            WORKPLACE_OPTIONS
        ),
        location=random.choice(
            LOCATION_OPTIONS
        ),
        summary=build_summary(
            stack,
            title,
            seniority,
        ),
        responsibilities=(
            build_responsibilities(
                role_family,
                stack,
            )
        ),
        minimum_qualifications=(
            build_minimum_qualifications(
                seniority,
                required_skills,
            )
        ),
        preferred_qualifications=(
            random.sample(
                PREFERRED_QUALIFICATION_TEMPLATES,
                k=3,
            )
        ),
        required_skills=(
            build_weighted_skills(
                required_skills,
                required=True,
            )
        ),
        preferred_skills=(
            build_weighted_skills(
                preferred_skills,
                required=False,
            )
        ),
        source_type="curated_template",
        source_note=(
            "A curated synthetic posting generated from a "
            "role-specific and internally consistent technology stack."
        ),
        is_synthetic=True,
        dataset_version=(
            DATASET_VERSION
        ),
    )


def generate_jobs() -> list[JobPosting]:
    random.seed(
        GENERATION_SEED
    )

    role_seniority_pairs = (
        allocate_role_seniority_pairs()
    )

    jobs = [
        build_job(
            sequence=index,
            role_family=role_family,
            seniority=seniority,
        )
        for index, (
            role_family,
            seniority,
        ) in enumerate(
            role_seniority_pairs,
            start=1,
        )
    ]

    jobs.sort(
        key=lambda job: (
            job.role_family.value,
            job.technology_stack_id,
            job.seniority.value,
            job.job_id,
        )
    )

    return jobs


def create_metadata(
    jobs: list[JobPosting],
) -> JobDatasetMetadata:
    role_distribution = Counter(
        job.role_family.value
        for job in jobs
    )

    stack_distribution = Counter(
        job.technology_stack_id
        for job in jobs
    )

    seniority_distribution = Counter(
        job.seniority.value
        for job in jobs
    )

    source_distribution = Counter(
        job.source_type.value
        for job in jobs
    )

    return JobDatasetMetadata(
        dataset_name=(
            "SkillGraph Curated "
            "Developer Jobs"
        ),
        version=DATASET_VERSION,
        description=(
            "Curated software engineering job postings "
            "generated from internally consistent "
            "role-specific technology stacks."
        ),
        job_count=len(jobs),
        generated=True,
        role_distribution=dict(
            sorted(
                role_distribution.items()
            )
        ),
        technology_stack_distribution=dict(
            sorted(
                stack_distribution.items()
            )
        ),
        seniority_distribution=dict(
            sorted(
                seniority_distribution.items()
            )
        ),
        source_distribution=dict(
            sorted(
                source_distribution.items()
            )
        ),
        generation_seed=(
            GENERATION_SEED
        ),
        generated_at=(
            datetime.now(UTC)
            .replace(microsecond=0)
            .isoformat()
        ),
    )


def write_json(
    path: Path,
    content: Any,
) -> None:
    path.write_text(
        json.dumps(
            content,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    jobs = generate_jobs()

    metadata = create_metadata(
        jobs
    )

    write_json(
        JOBS_OUTPUT_FILE,
        [
            job.model_dump(
                mode="json"
            )
            for job in jobs
        ],
    )

    write_json(
        METADATA_OUTPUT_FILE,
        metadata.model_dump(
            mode="json"
        ),
    )

    print(
        f"Generated {len(jobs)} job postings."
    )

    print(
        "Technology stacks used: "
        f"{len(metadata.technology_stack_distribution)}"
    )

    print(
        f"Jobs: {JOBS_OUTPUT_FILE}"
    )

    print(
        f"Metadata: {METADATA_OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()