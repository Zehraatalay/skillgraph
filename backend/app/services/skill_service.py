import math
from typing import Any

from app.repositories.graph_repository import GraphRepository


class SkillService:
    def __init__(self) -> None:
        self._graph = GraphRepository()

    @staticmethod
    def _determine_level(score: float) -> str:
        if score >= 80:
            return "Advanced"

        if score >= 60:
            return "Upper Intermediate"

        if score >= 40:
            return "Intermediate"

        if score >= 20:
            return "Beginner"

        return "Emerging"

    def get_developer_skill_profile(
        self,
        username: str,
    ) -> dict[str, Any]:
        normalized_username = username.strip()

        if not normalized_username:
            raise ValueError("GitHub username cannot be empty.")

        statistics = (
            self._graph.get_developer_technology_statistics(
                normalized_username
            )
        )

        if not statistics:
            raise ValueError(
                "No analyzed graph data was found for this developer."
            )

        maximum_bytes = max(
            int(item["total_bytes"])
            for item in statistics
        )

        maximum_stars = max(
            int(item["total_stars"])
            for item in statistics
        )

        skills: list[dict[str, Any]] = []

        for item in statistics:
            repository_count = int(item["repository_count"])
            total_bytes = int(item["total_bytes"])
            total_stars = int(item["total_stars"])

            repository_component = min(
                repository_count / 5,
                1,
            ) * 35

            byte_component = 0.0

            if maximum_bytes > 0:
                byte_component = (
                    math.log1p(total_bytes)
                    / math.log1p(maximum_bytes)
                ) * 45

            star_component = 0.0

            if maximum_stars > 0:
                star_component = (
                    math.log1p(total_stars)
                    / math.log1p(maximum_stars)
                ) * 20

            score = round(
                repository_component
                + byte_component
                + star_component,
                2,
            )

            skills.append(
                {
                    "technology": item["technology"],
                    "score": score,
                    "level": self._determine_level(score),
                    "repository_count": repository_count,
                    "total_bytes": total_bytes,
                    "total_stars": total_stars,
                    "repositories": item["repositories"],
                }
            )

        skills.sort(
            key=lambda skill: skill["score"],
            reverse=True,
        )

        return {
            "developer_login": normalized_username,
            "technology_count": len(skills),
            "skills": skills,
        }

    def close(self) -> None:
        self._graph.close()