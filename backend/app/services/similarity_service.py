from typing import Any

from app.repositories.graph_repository import GraphRepository


class SimilarityService:
    def __init__(self) -> None:
        self._graph = GraphRepository()

    def get_similar_developers(
        self,
        username: str,
        limit: int = 5,
    ) -> dict[str, Any]:
        normalized_username = username.strip()

        if not normalized_username:
            raise ValueError(
                "GitHub username cannot be empty."
            )

        if not self._graph.developer_exists(
            normalized_username
        ):
            raise ValueError(
                "No analyzed graph data was found "
                "for this developer."
            )

        rows = self._graph.get_similar_developers(
            developer_login=normalized_username,
            limit=limit,
        )

        similar_developers: list[dict[str, Any]] = []

        for row in rows:
            similar_developers.append(
                {
                    "login": row["login"],
                    "name": row.get("name"),
                    "avatar_url": row.get("avatar_url"),
                    "html_url": row.get("html_url"),
                    "similarity_score": round(
                        float(row["similarity_score"]),
                        2,
                    ),
                    "shared_technology_count": int(
                        row["shared_technology_count"]
                    ),
                    "shared_technologies": sorted(
                        row["shared_technologies"]
                    ),
                    "candidate_technologies": sorted(
                        row["candidate_technologies"]
                    ),
                }
            )

        return {
            "developer_login": normalized_username,
            "similar_developer_count": len(
                similar_developers
            ),
            "similar_developers": similar_developers,
        }

    def close(self) -> None:
        self._graph.close()