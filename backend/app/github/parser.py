from __future__ import annotations

import re

from app.jobs.skill_registry import (
    SKILL_REGISTRY,
    normalize_skill_text,
)


def _contains_keyword(
    text: str,
    keyword: str,
) -> bool:
    """
    Check whether a keyword occurs as a complete term.

    Prevents false matches such as:
    - py inside pytorch
    - sql inside postgresql
    - git inside github
    - ai inside api
    """

    normalized_keyword = normalize_skill_text(
        keyword
    )

    if not normalized_keyword:
        return False

    pattern = (
        r"(?<![a-z0-9])"
        + re.escape(normalized_keyword)
        + r"(?![a-z0-9])"
    )

    return (
        re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )
        is not None
    )


def extract_skills(
    text: str,
) -> list[str]:
    """
    Extract canonical skills from free text.

    Returns a sorted list of unique canonical skill names.
    """

    normalized_text = normalize_skill_text(
        text
    )

    found_skills: set[str] = set()

    for skill in SKILL_REGISTRY:
        searchable_terms = (
            skill.name,
            *skill.aliases,
            *skill.github_keywords,
        )

        for term in searchable_terms:
            if _contains_keyword(
                normalized_text,
                term,
            ):
                found_skills.add(
                    skill.name
                )
                break

    return sorted(found_skills)

SUPPORTED_FILE_NAMES = {
    "readme.md",
    "requirements.txt",
    "pyproject.toml",
    "pipfile",
    "package.json",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "pubspec.yaml",
}


def is_supported_file(
    file_path: str,
) -> bool:
    normalized_path = file_path.strip().lower()

    file_name = normalized_path.rsplit(
        "/",
        maxsplit=1,
    )[-1]

    if file_name in SUPPORTED_FILE_NAMES:
        return True

    if normalized_path.startswith(
        ".github/workflows/"
    ):
        return (
            file_name.endswith(".yml")
            or file_name.endswith(".yaml")
        )

    return False


def extract_skills_from_file(
    file_path: str,
    content: str,
) -> list[str]:
    """
    Extract skills from a supported repository file.
    """

    if not is_supported_file(file_path):
        return []

    return extract_skills(content)


def extract_skills_from_files(
    files: dict[str, str],
) -> list[str]:
    """
    Extract unique skills from multiple repository files.

    Example:
        {
            "README.md": "...",
            "requirements.txt": "...",
            "Dockerfile": "...",
        }
    """

    found_skills: set[str] = set()

    for file_path, content in files.items():
        file_skills = extract_skills_from_file(
            file_path=file_path,
            content=content,
        )

        found_skills.update(file_skills)

    return sorted(found_skills)