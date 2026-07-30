from __future__ import annotations

from typing import Final


DATASET_VERSION: Final[str] = "1.0.0"
GENERATION_SEED: Final[int] = 42


ROLE_DISTRIBUTION: Final[
    dict[str, int]
] = {
    "backend": 30,
    "frontend": 28,
    "full_stack": 26,
    "machine_learning": 22,
    "ai_engineering": 20,
    "data_engineering": 20,
    "data_science": 16,
    "devops": 16,
    "mobile": 12,
    "unity_game": 10,
}


SENIORITY_DISTRIBUTION: Final[
    dict[str, int]
] = {
    "intern": 30,
    "junior": 110,
    "mid": 60,
}


WORKPLACE_OPTIONS: Final[
    tuple[str, ...]
] = (
    "remote",
    "hybrid",
    "on_site",
)


LOCATION_OPTIONS: Final[
    tuple[str, ...]
] = (
    "Remote",
    "Ankara, Türkiye",
    "İstanbul, Türkiye",
    "İzmir, Türkiye",
    "Türkiye",
    "Europe",
)


EMPLOYMENT_BY_SENIORITY: Final[
    dict[str, tuple[str, ...]]
] = {
    "intern": (
        "internship",
        "part_time",
    ),
    "junior": (
        "full_time",
        "full_time",
        "full_time",
        "contract",
    ),
    "mid": (
        "full_time",
        "full_time",
        "contract",
    ),
}


ROLE_TITLES: Final[
    dict[str, dict[str, tuple[str, ...]]]
] = {
    "backend": {
        "intern": (
            "Backend Developer Intern",
            "Python Backend Engineering Intern",
            "Software Engineering Intern - Backend",
        ),
        "junior": (
            "Junior Backend Developer",
            "Junior Python Backend Engineer",
            "Backend Software Engineer",
            "API Developer",
            "Junior Java Backend Developer",
            "Junior .NET Backend Developer",
        ),
        "mid": (
            "Backend Software Engineer",
            "Python Backend Engineer",
            "Java Backend Engineer",
            ".NET Backend Engineer",
            "Backend Platform Engineer",
        ),
    },
    "frontend": {
        "intern": (
            "Frontend Developer Intern",
            "Web Development Intern",
            "Frontend Engineering Intern",
        ),
        "junior": (
            "Junior Frontend Developer",
            "Junior React Developer",
            "Junior Vue Developer",
            "Frontend Software Engineer",
            "Web UI Developer",
        ),
        "mid": (
            "Frontend Software Engineer",
            "React Frontend Engineer",
            "Vue Frontend Engineer",
            "Web Application Engineer",
        ),
    },
    "full_stack": {
        "intern": (
            "Full Stack Developer Intern",
            "Software Engineering Intern - Full Stack",
        ),
        "junior": (
            "Junior Full Stack Developer",
            "Full Stack Software Engineer",
            "Junior Web Application Developer",
            "React and Node.js Developer",
            "Python Full Stack Developer",
        ),
        "mid": (
            "Full Stack Software Engineer",
            "Full Stack Web Engineer",
            "Product Software Engineer",
            "Application Development Engineer",
        ),
    },
    "machine_learning": {
        "intern": (
            "Machine Learning Intern",
            "Applied Machine Learning Intern",
            "ML Engineering Intern",
        ),
        "junior": (
            "Junior Machine Learning Engineer",
            "Machine Learning Engineer",
            "Applied ML Engineer",
            "Computer Vision Engineer",
            "NLP Engineer",
        ),
        "mid": (
            "Machine Learning Engineer",
            "Applied Machine Learning Engineer",
            "ML Platform Engineer",
            "Computer Vision Engineer",
        ),
    },
    "ai_engineering": {
        "intern": (
            "AI Engineering Intern",
            "Generative AI Intern",
        ),
        "junior": (
            "Junior AI Engineer",
            "AI Application Engineer",
            "Generative AI Engineer",
            "LLM Application Developer",
            "AI Software Engineer",
        ),
        "mid": (
            "AI Engineer",
            "Generative AI Engineer",
            "LLM Systems Engineer",
            "AI Platform Engineer",
        ),
    },
    "data_engineering": {
        "intern": (
            "Data Engineering Intern",
            "Data Platform Intern",
        ),
        "junior": (
            "Junior Data Engineer",
            "Data Pipeline Developer",
            "Analytics Data Engineer",
            "Junior ETL Developer",
        ),
        "mid": (
            "Data Engineer",
            "Data Platform Engineer",
            "ETL Engineer",
            "Cloud Data Engineer",
        ),
    },
    "data_science": {
        "intern": (
            "Data Science Intern",
            "Analytics Intern",
        ),
        "junior": (
            "Junior Data Scientist",
            "Data Scientist",
            "Product Data Analyst",
            "Junior Analytics Engineer",
        ),
        "mid": (
            "Data Scientist",
            "Applied Data Scientist",
            "Product Data Scientist",
        ),
    },
    "devops": {
        "intern": (
            "DevOps Intern",
            "Cloud Engineering Intern",
        ),
        "junior": (
            "Junior DevOps Engineer",
            "Junior Cloud Engineer",
            "Platform Engineering Associate",
            "Infrastructure Automation Engineer",
        ),
        "mid": (
            "DevOps Engineer",
            "Cloud Platform Engineer",
            "Site Reliability Engineer",
            "Platform Engineer",
        ),
    },
    "mobile": {
        "intern": (
            "Mobile Development Intern",
            "Android Development Intern",
        ),
        "junior": (
            "Junior Mobile Developer",
            "Junior Android Developer",
            "Junior iOS Developer",
            "Flutter Developer",
            "React Native Developer",
        ),
        "mid": (
            "Mobile Software Engineer",
            "Android Engineer",
            "iOS Engineer",
            "Cross-Platform Mobile Engineer",
        ),
    },
    "unity_game": {
        "intern": (
            "Unity Game Developer Intern",
            "Game Development Intern",
        ),
        "junior": (
            "Junior Unity Developer",
            "Unity Game Developer",
            "Gameplay Programmer",
            "Junior C# Game Developer",
        ),
        "mid": (
            "Unity Software Engineer",
            "Gameplay Engineer",
            "Unity Game Developer",
        ),
    },
}


def validate_blueprint() -> None:
    role_total = sum(
        ROLE_DISTRIBUTION.values()
    )

    seniority_total = sum(
        SENIORITY_DISTRIBUTION.values()
    )

    if role_total != 200:
        raise ValueError(
            "Role distribution must contain "
            f"exactly 200 jobs, got {role_total}."
        )

    if seniority_total != 200:
        raise ValueError(
            "Seniority distribution must contain "
            "exactly 200 jobs, "
            f"got {seniority_total}."
        )

    missing_role_titles = (
        set(ROLE_DISTRIBUTION)
        - set(ROLE_TITLES)
    )

    if missing_role_titles:
        raise ValueError(
            "Missing title definitions for roles: "
            f"{sorted(missing_role_titles)}"
        )

    required_seniority_levels = (
        set(SENIORITY_DISTRIBUTION)
    )

    for role_name, title_groups in (
        ROLE_TITLES.items()
    ):
        missing_levels = (
            required_seniority_levels
            - set(title_groups)
        )

        if missing_levels:
            raise ValueError(
                f"Role '{role_name}' is missing "
                "title definitions for: "
                f"{sorted(missing_levels)}"
            )


validate_blueprint()