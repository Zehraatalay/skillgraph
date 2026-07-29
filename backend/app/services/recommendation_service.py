from typing import Any

from app.services.skill_service import SkillService


TECHNOLOGY_RULES: dict[str, list[dict[str, Any]]] = {
    "Python": [
        {
            "technology": "FastAPI",
            "weight": 0.88,
            "reason": (
                "Python bilgin web API geliştirmeye uygun bir temel "
                "oluşturuyor."
            ),
        },
        {
            "technology": "Django",
            "weight": 0.72,
            "reason": (
                "Python deneyimini kapsamlı web uygulamalarına "
                "taşıyabilirsin."
            ),
        },
        {
            "technology": "Docker",
            "weight": 0.78,
            "reason": (
                "Python projelerini taşınabilir ve tekrarlanabilir "
                "ortamlarda çalıştırabilirsin."
            ),
        },
        {
            "technology": "PostgreSQL",
            "weight": 0.75,
            "reason": (
                "Python backend projelerinde ilişkisel veri yönetimini "
                "güçlendirebilirsin."
            ),
        },
        {
            "technology": "PyTest",
            "weight": 0.70,
            "reason": (
                "Python projelerinde otomatik test ve güvenilirlik "
                "becerisi kazanabilirsin."
            ),
        },
    ],
    "JavaScript": [
        {
            "technology": "TypeScript",
            "weight": 0.92,
            "reason": (
                "JavaScript deneyimini tip güvenliğiyle daha sürdürülebilir "
                "hale getirebilirsin."
            ),
        },
        {
            "technology": "Node.js",
            "weight": 0.78,
            "reason": (
                "JavaScript bilgini backend geliştirmeye taşıyabilirsin."
            ),
        },
        {
            "technology": "Vitest",
            "weight": 0.64,
            "reason": (
                "JavaScript projelerinde otomatik test yetkinliği "
                "kazanabilirsin."
            ),
        },
    ],
    "Vue": [
        {
            "technology": "Pinia",
            "weight": 0.82,
            "reason": (
                "Vue uygulamalarında merkezi ve ölçeklenebilir state "
                "yönetimi sağlayabilirsin."
            ),
        },
        {
            "technology": "Nuxt",
            "weight": 0.76,
            "reason": (
                "Vue deneyimini tam kapsamlı uygulama geliştirmeye "
                "taşıyabilirsin."
            ),
        },
        {
            "technology": "TypeScript",
            "weight": 0.86,
            "reason": (
                "Vue component ve servislerinde tip güvenliği "
                "kazanabilirsin."
            ),
        },
    ],
    "HTML": [
        {
            "technology": "CSS",
            "weight": 0.72,
            "reason": (
                "Web arayüzlerini daha kontrollü ve responsive biçimde "
                "tasarlayabilirsin."
            ),
        },
        {
            "technology": "Accessibility",
            "weight": 0.58,
            "reason": (
                "Daha erişilebilir ve semantik web arayüzleri "
                "geliştirebilirsin."
            ),
        },
    ],
    "CSS": [
        {
            "technology": "Tailwind CSS",
            "weight": 0.68,
            "reason": (
                "Arayüz geliştirme sürecini utility-first yaklaşımla "
                "hızlandırabilirsin."
            ),
        },
    ],
    "Java": [
        {
            "technology": "Spring Boot",
            "weight": 0.90,
            "reason": (
                "Java bilginle kurumsal backend ve REST API uygulamaları "
                "geliştirebilirsin."
            ),
        },
        {
            "technology": "JUnit",
            "weight": 0.66,
            "reason": (
                "Java projelerinde test otomasyonu ve kod güvenilirliği "
                "sağlayabilirsin."
            ),
        },
    ],
    "C#": [
        {
            "technology": "Unity",
            "weight": 0.88,
            "reason": (
                "C# bilgin oyun ve gerçek zamanlı simülasyon geliştirmeye "
                "uygun bir temel oluşturuyor."
            ),
        },
        {
            "technology": "ASP.NET Core",
            "weight": 0.78,
            "reason": (
                "C# deneyimini modern backend geliştirmeye "
                "taşıyabilirsin."
            ),
        },
    ],
    "Neo4j": [
        {
            "technology": "Cypher",
            "weight": 0.94,
            "reason": (
                "Neo4j graph verilerini daha etkili sorgulayabilmek için "
                "Cypher bilgisini derinleştirebilirsin."
            ),
        },
        {
            "technology": "Graph Data Science",
            "weight": 0.82,
            "reason": (
                "Graph verileri üzerinde benzerlik, sıralama ve topluluk "
                "algoritmaları çalıştırabilirsin."
            ),
        },
    ],
    "TeX": [
        {
            "technology": "LaTeX",
            "weight": 0.90,
            "reason": (
                "Teknik ve akademik doküman üretme yetkinliğini "
                "geliştirebilirsin."
            ),
        },
    ],
}


class RecommendationService:
    def __init__(self) -> None:
        self._skill_service = SkillService()

    @staticmethod
    def _determine_priority(score: float) -> str:
        if score >= 75:
            return "High"

        if score >= 50:
            return "Medium"

        return "Low"

    def get_developer_recommendations(
        self,
        username: str,
    ) -> dict[str, Any]:
        skill_profile = (
            self._skill_service.get_developer_skill_profile(username)
        )

        existing_technologies = {
            skill["technology"].casefold()
            for skill in skill_profile["skills"]
        }

        recommendation_candidates: dict[str, dict[str, Any]] = {}

        for skill in skill_profile["skills"]:
            source_technology = skill["technology"]
            source_score = float(skill["score"])

            rules = TECHNOLOGY_RULES.get(source_technology, [])

            for rule in rules:
                recommended_technology = str(rule["technology"])

                if (
                    recommended_technology.casefold()
                    in existing_technologies
                ):
                    continue

                contribution = (
                    source_score * float(rule["weight"])
                )

                candidate = recommendation_candidates.setdefault(
                    recommended_technology,
                    {
                        "technology": recommended_technology,
                        "contributions": [],
                        "based_on": [],
                        "reasons": [],
                    },
                )

                candidate["contributions"].append(contribution)

                if source_technology not in candidate["based_on"]:
                    candidate["based_on"].append(source_technology)

                reason = str(rule["reason"])

                if reason not in candidate["reasons"]:
                    candidate["reasons"].append(reason)

        recommendations: list[dict[str, Any]] = []

        for candidate in recommendation_candidates.values():
            contributions = candidate["contributions"]

            highest_contribution = max(contributions)
            supporting_bonus = min(
                max(len(contributions) - 1, 0) * 5,
                15,
            )

            score = round(
                min(highest_contribution + supporting_bonus, 100),
                2,
            )

            recommendations.append(
                {
                    "technology": candidate["technology"],
                    "score": score,
                    "priority": self._determine_priority(score),
                    "reason": " ".join(candidate["reasons"]),
                    "based_on": candidate["based_on"],
                }
            )

        recommendations.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return {
            "developer_login": skill_profile["developer_login"],
            "recommendation_count": len(recommendations),
            "recommendations": recommendations[:8],
        }

    def close(self) -> None:
        self._skill_service.close()