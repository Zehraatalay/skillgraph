from typing import Any

from app.repositories.graph_repository import GraphRepository
import math

class SimilarityService:
    def __init__(self) -> None:
        self._graph = GraphRepository()

    @staticmethod
    def _create_vector(
        technology_vector: list[dict[str, Any]],
    ) -> dict[str, float]:
        return {
            str(item["technology"]): math.log1p(
                float(item["weight"])
            )
            for item in technology_vector
        }


    @staticmethod
    def _cosine_similarity(
        first_vector: dict[str, float],
        second_vector: dict[str, float],
    ) -> float:
        all_technologies = (
            set(first_vector)
            | set(second_vector)
        )

        dot_product = sum(
            first_vector.get(technology, 0.0)
            * second_vector.get(technology, 0.0)
            for technology in all_technologies
        )

        first_magnitude = math.sqrt(
            sum(
                weight**2
                for weight in first_vector.values()
            )
        )

        second_magnitude = math.sqrt(
            sum(
                weight**2
                for weight in second_vector.values()
            )
        )

        if first_magnitude == 0 or second_magnitude == 0:
            return 0.0

        return (
            dot_product
            / (first_magnitude * second_magnitude)
        )

    @staticmethod
    def _jaccard_similarity(
        first_vector: dict[str, float],
        second_vector: dict[str, float],
    ) -> float:

        first = set(first_vector.keys())
        second = set(second_vector.keys())

        if not first and not second:
            return 0.0

        return len(first & second) / len(first | second)
    @staticmethod
    def _hybrid_similarity(
        cosine: float,
        jaccard: float,
    ) -> float:

        return (
            0.60 * cosine
            + 0.40 * jaccard
        )
    @staticmethod
    def _calculate_shared_contributions(
        target_vector: dict[str, float],
        candidate_vector: dict[str, float],
    ) -> list[dict[str, Any]]:
        shared_technologies = (
            set(target_vector)
            & set(candidate_vector)
        )

        contributions = [
            {
                "technology": technology,
                "contribution": (
                    target_vector[technology]
                    * candidate_vector[technology]
                ),
            }
            for technology in shared_technologies
        ]

        contributions.sort(
            key=lambda item: item["contribution"],
            reverse=True,
        )

        return contributions
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

        rows = (
            self._graph
            .get_developer_technology_vectors()
        )

        target_row = next(
            (
                row
                for row in rows
                if str(row["login"]).casefold()
                == normalized_username.casefold()
            ),
            None,
        )

        if target_row is None:
            return {
                "developer_login": normalized_username,
                "similar_developer_count": 0,
                "similar_developers": [],
            }

        target_vector = self._create_vector(
            target_row["technology_vector"]
        )

        similar_developers: list[dict[str, Any]] = []

        for row in rows:
            candidate_login = str(row["login"])

            if (
                candidate_login.casefold()
                == normalized_username.casefold()
            ):
                continue

            candidate_vector = self._create_vector(
                row["technology_vector"]
            )

            cosine = self._cosine_similarity(
                target_vector,
                candidate_vector,
            )

            jaccard = self._jaccard_similarity(
                target_vector,
                candidate_vector,
            )

            similarity = self._hybrid_similarity(
                cosine,
                jaccard,
            )

            shared_contributions = (
                self._calculate_shared_contributions(
                    target_vector,
                    candidate_vector,
                )
            )

            if similarity <= 0 or not shared_contributions:
                continue

            shared_technologies = [
                item["technology"]
                for item in shared_contributions
            ]

            similar_developers.append(
                {
                    "login": candidate_login,
                    "name": row.get("name"),
                    "avatar_url": row.get("avatar_url"),
                    "html_url": row.get("html_url"),
                    "similarity_score": round(
                        similarity * 100,
                        2,
                    ),
                    "cosine_score": round(
                        cosine * 100,
                        2,
                    ),

                    "jaccard_score": round(
                        jaccard * 100,
                        2,
                    ),
                    "shared_technology_count": len(
                        shared_technologies
                    ),
                    "shared_technologies": (
                        shared_technologies
                    ),
                    "candidate_technologies": sorted(
                        candidate_vector.keys()
                    ),
                }
            )

        similar_developers.sort(
            key=lambda developer: (
                developer["similarity_score"],
                developer["shared_technology_count"],
            ),
            reverse=True,
        )

        limited_developers = similar_developers[:limit]

        return {
            "developer_login": str(
                target_row["login"]
            ),
            "similar_developer_count": len(
                limited_developers
            ),
            "similar_developers": limited_developers,
        }

    def close(self) -> None:
        self._graph.close()