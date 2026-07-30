from __future__ import annotations

import os
from urllib.parse import urlparse

import httpx

from app.github.parser import (
    extract_skills_from_files,
    is_supported_file,
)


GITHUB_API_URL = "https://api.github.com"
GITHUB_API_VERSION = "2026-03-10"
MAX_ANALYZED_FILES = 30
MAX_FILE_SIZE = 500_000


class GitHubRepositoryError(Exception):
    pass


def parse_github_url(
    repository_url: str,
) -> tuple[str, str]:
    parsed = urlparse(repository_url.strip())

    if parsed.netloc.lower() not in {
        "github.com",
        "www.github.com",
    }:
        raise ValueError(
            "Geçerli bir GitHub repository URL'si girilmelidir."
        )

    parts = [
        part
        for part in parsed.path.strip("/").split("/")
        if part
    ]

    if len(parts) < 2:
        raise ValueError(
            "Repository URL'sinde owner ve repository adı bulunmalıdır."
        )

    owner = parts[0]
    repository = parts[1].removesuffix(".git")

    return owner, repository


def _github_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
        "User-Agent": "SkillGraph",
    }

    token = os.getenv("GITHUB_TOKEN")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


async def _github_get(
    client: httpx.AsyncClient,
    endpoint: str,
) -> object:
    response = await client.get(
        f"{GITHUB_API_URL}{endpoint}",
        headers=_github_headers(),
    )

    if response.status_code == 404:
        raise GitHubRepositoryError(
            "Repository veya GitHub kaynağı bulunamadı."
        )

    if response.status_code in {403, 429}:
        raise GitHubRepositoryError(
            "GitHub API istek limiti aşıldı."
        )

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise GitHubRepositoryError(
            f"GitHub API hatası: {response.status_code}"
        ) from exc

    return response.json()


async def _fetch_raw_file(
    client: httpx.AsyncClient,
    owner: str,
    repository: str,
    path: str,
) -> str:
    response = await client.get(
        (
            f"{GITHUB_API_URL}/repos/"
            f"{owner}/{repository}/contents/{path}"
        ),
        headers={
            **_github_headers(),
            "Accept": "application/vnd.github.raw+json",
        },
    )

    if response.status_code != 200:
        return ""

    return response.text


async def analyze_repository(
    repository_url: str,
) -> dict[str, object]:
    owner, repository = parse_github_url(
        repository_url
    )

    files: dict[str, str] = {}

    async with httpx.AsyncClient(
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        repository_data = await _github_get(
            client,
            f"/repos/{owner}/{repository}",
        )

        if not isinstance(repository_data, dict):
            raise GitHubRepositoryError(
                "Repository bilgileri okunamadı."
            )

        default_branch = repository_data.get(
            "default_branch",
            "main",
        )

        tree_data = await _github_get(
            client,
            (
                f"/repos/{owner}/{repository}"
                f"/git/trees/{default_branch}"
                "?recursive=1"
            ),
        )

        if not isinstance(tree_data, dict):
            raise GitHubRepositoryError(
                "Repository dosya ağacı okunamadı."
            )

        tree_items = tree_data.get("tree", [])

        if not isinstance(tree_items, list):
            raise GitHubRepositoryError(
                "Repository dosya listesi okunamadı."
            )

        supported_items: list[dict[str, object]] = []

        for item in tree_items:
            if not isinstance(item, dict):
                continue

            path = item.get("path")
            item_type = item.get("type")
            size = item.get("size", 0)

            if (
                item_type == "blob"
                and isinstance(path, str)
                and isinstance(size, int)
                and size <= MAX_FILE_SIZE
                and is_supported_file(path)
            ):
                supported_items.append(item)

        supported_items = supported_items[
            :MAX_ANALYZED_FILES
        ]

        for item in supported_items:
            path = item["path"]

            if not isinstance(path, str):
                continue

            content = await _fetch_raw_file(
                client=client,
                owner=owner,
                repository=repository,
                path=path,
            )

            if content.strip():
                files[path] = content

    skills = extract_skills_from_files(files)

    return {
        "owner": owner,
        "repository": repository,
        "repository_url": repository_url,
        "analyzed_files": sorted(files),
        "skills": skills,
        "skill_count": len(skills),
    }