from typing import Any

import requests

from app.core.config import get_settings


class GitHubAPIError(Exception):
    """Raised when a GitHub API request fails."""


class GitHubRepository:
    def __init__(self) -> None:
        settings = get_settings()

        self._base_url = settings.github_api_url.rstrip("/")
        self._session = requests.Session()

        self._session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {settings.github_token}",
                "X-GitHub-Api-Version": settings.github_api_version,
                "User-Agent": "SkillGraph",
            }
        )

    def _get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        try:
            response = self._session.get(
                f"{self._base_url}{endpoint}",
                params=params,
                timeout=20,
            )
        except requests.RequestException as exc:
            raise GitHubAPIError(
                "GitHub API request could not be completed."
            ) from exc

        if response.status_code == 404:
            raise GitHubAPIError("GitHub user or resource was not found.")

        if response.status_code == 401:
            raise GitHubAPIError(
                "GitHub token is missing, invalid or expired."
            )

        if response.status_code == 403:
            remaining = response.headers.get("X-RateLimit-Remaining")

            if remaining == "0":
                raise GitHubAPIError(
                    "GitHub API rate limit has been exceeded."
                )

            raise GitHubAPIError(
                "GitHub API denied access to this resource."
            )

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise GitHubAPIError(
                f"GitHub API returned HTTP {response.status_code}."
            ) from exc

        return response.json()

    def get_user(self, username: str) -> dict[str, Any]:
        return self._get(f"/users/{username}")

    def get_user_repositories(
        self,
        username: str,
    ) -> list[dict[str, Any]]:
        repositories: list[dict[str, Any]] = []
        page = 1

        while True:
            page_data = self._get(
                f"/users/{username}/repos",
                params={
                    "type": "owner",
                    "sort": "updated",
                    "direction": "desc",
                    "per_page": 100,
                    "page": page,
                },
            )

            if not page_data:
                break

            repositories.extend(page_data)

            if len(page_data) < 100:
                break

            page += 1

        return repositories

    def get_repository_languages(
        self,
        owner: str,
        repository_name: str,
    ) -> dict[str, int]:
        result = self._get(
            f"/repos/{owner}/{repository_name}/languages"
        )

        return {
            language: int(byte_count)
            for language, byte_count in result.items()
        }

    def close(self) -> None:
        self._session.close()