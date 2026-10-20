from __future__ import annotations

import json
from pathlib import Path

from app.github.service import analyze_repository
from app.jobs.skill_registry import normalize_skill, normalize_skill_text
from app.repositories.graph_repository import GraphRepository


DATASET_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "curated_jobs"
    / "job_postings.json"
)


def _load_jobs() -> list[dict]:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Job dataset bulunamadı: {DATASET_PATH}"
        )

    data = json.loads(
        DATASET_PATH.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, list):
        raise ValueError(
            "Job dataset JSON listesi olmalıdır."
        )

    return data


def _canonical(value: str) -> str:
    return normalize_skill(value) or normalize_skill_text(value)


def _normalize_skills(values) -> set[str]:
    return {_canonical(v) for v in values if isinstance(v, str) and v.strip()}


def _skill_names(
    skills: list[dict],
) -> set[str]:
    return {
        _canonical(skill["name"])
        for skill in skills
        if isinstance(skill, dict)
        and isinstance(skill.get("name"), str)
    }


def _calculate_match(
    developer_skills: set[str],
    job: dict,
) -> dict:
    required = _skill_names(
        job.get("required_skills", [])
    )

    preferred = _skill_names(
        job.get("preferred_skills", [])
    )

    matched_required = (
        developer_skills & required
    )

    matched_preferred = (
        developer_skills & preferred
    )

    missing_required = (
        required - developer_skills
    )

    missing_preferred = (
        preferred - developer_skills
    )

    required_ratio = (
        len(matched_required) / len(required)
        if required
        else 0.0
    )

    preferred_ratio = (
        len(matched_preferred) / len(preferred)
        if preferred
        else 0.0
    )

    # Required skills daha önemli.
    score = (
        required_ratio * 80
        + preferred_ratio * 20
    )

    return {
        "job_id": job["job_id"],
        "title": job["title"],
        "role_family": job["role_family"],
        "seniority": job["seniority"],
        "technology_stack_id": job[
            "technology_stack_id"
        ],
        "score": round(score, 2),
        "matched_required_skills": sorted(
            matched_required
        ),
        "matched_preferred_skills": sorted(
            matched_preferred
        ),
        "missing_required_skills": sorted(
            missing_required
        ),
        "missing_preferred_skills": sorted(
            missing_preferred
        ),
    }


async def match_repository_to_jobs(
    repository_url: str,
    limit: int,
) -> dict:
    repository_analysis = (
        await analyze_repository(
            repository_url
        )
    )

    detected_skills = _normalize_skills(repository_analysis["skills"])

    jobs = _load_jobs()

    matches = [
        _calculate_match(
            developer_skills=detected_skills,
            job=job,
        )
        for job in jobs
    ]

    matches.sort(
        key=lambda match: (
            match["score"],
            len(
                match[
                    "matched_required_skills"
                ]
            ),
            len(
                match[
                    "matched_preferred_skills"
                ]
            ),
        ),
        reverse=True,
    )

    return {
        "repository_url": repository_url,
        "repository": repository_analysis[
            "repository"
        ],
        "detected_skills": sorted(
            detected_skills
        ),
        "detected_skill_count": len(
            detected_skills
        ),
        "total_jobs_evaluated": len(jobs),
        "matches": matches[:limit],
    }

def match_developer_to_jobs(username: str, limit: int) -> dict | None:
    """Rank curated job templates against technologies persisted in Neo4j.

    No new GitHub API call is made; analyze the developer first via the
    existing analysis endpoint. The score is a skill-coverage heuristic.
    """
    graph = GraphRepository()
    try:
        if not graph.developer_exists(username):
            return None
        stats = graph.get_developer_technology_statistics(username)
    finally:
        graph.close()

    skills = _normalize_skills([row["technology"] for row in stats])
    jobs = _load_jobs()
    matches = [_calculate_match(skills, job) for job in jobs]
    matches.sort(
        key=lambda match: (
            -match["score"],
            -len(match["matched_required_skills"]),
            -len(match["matched_preferred_skills"]),
            match["job_id"],
        )
    )
    return {
        "username": username,
        "detected_skills": sorted(skills),
        "detected_skill_count": len(skills),
        "total_jobs_evaluated": len(jobs),
        "matches": matches[:limit],
    }
