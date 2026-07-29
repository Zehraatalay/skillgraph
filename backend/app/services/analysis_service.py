from typing import Any

from app.repositories.github_repository import GitHubRepository
from app.repositories.graph_repository import GraphRepository


class AnalysisService:
    def __init__(self) -> None:
        self._github = GitHubRepository()
        self._graph = GraphRepository()

    def analyze_developer(
        self,
        username: str,
    ) -> dict[str, Any]:
        normalized_username = username.strip()

        if not normalized_username:
            raise ValueError("GitHub username cannot be empty.")

        self._graph.create_constraints()

        user = self._github.get_user(normalized_username)
        repositories = self._github.get_user_repositories(
            normalized_username
        )

        owned_repositories = [
            repository
            for repository in repositories
            if not repository.get("fork", False)
        ]

        self._graph.save_developer(user)

        for repository in owned_repositories:
            self._graph.save_repository(
                developer_login=user["login"],
                repository=repository,
            )

            languages = self._github.get_repository_languages(
                owner=user["login"],
                repository_name=repository["name"],
            )

            for language_name, byte_count in languages.items():
                self._graph.save_technology(
                    repository_id=repository["id"],
                    technology_name=language_name,
                    byte_count=byte_count,
                )

            for topic_name in repository.get("topics", []):
                normalized_topic = topic_name.strip().lower()

                if normalized_topic:
                    self._graph.save_topic(
                        repository_id=repository["id"],
                        topic_name=normalized_topic,
                    )

        summary = self._graph.get_developer_graph_summary(
            user["login"]
        )

        if summary is None:
            raise RuntimeError(
                "Developer was analyzed but graph summary "
                "could not be created."
            )

        summary["technologies"] = [
            technology
            for technology in summary["technologies"]
            if technology is not None
        ]

        summary["topics"] = [
            topic
            for topic in summary["topics"]
            if topic is not None
        ]

        return {
            "message": "Developer analysis completed successfully.",
            "developer": summary,
        }

    def close(self) -> None:
        self._github.close()
        self._graph.close()