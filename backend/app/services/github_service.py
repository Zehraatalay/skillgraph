from typing import Any

from app.repositories.github_repository import GitHubRepository


class GitHubService:
    def __init__(self) -> None:
        self._repository = GitHubRepository()

    def get_analysis_preview(
        self,
        username: str,
    ) -> dict[str, Any]:
        normalized_username = username.strip()

        if not normalized_username:
            raise ValueError("GitHub username cannot be empty.")

        user = self._repository.get_user(normalized_username)
        repositories = self._repository.get_user_repositories(
            normalized_username
        )

        owned_repositories = [
            repository
            for repository in repositories
            if not repository.get("fork", False)
        ]

        return {
            "user": user,
            "repositories": owned_repositories,
            "repository_count": len(owned_repositories),
        }

    def close(self) -> None:
        self._repository.close()