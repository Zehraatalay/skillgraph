from typing import ClassVar

from agents.schemas.match_type import MatchType
from agents.services.skill_normalizer import SkillNormalizer


class SkillRelationshipResolver:
    PARENT_SKILLS: ClassVar[dict[str, set[str]]] = {
        # Python
        "Python Dataclasses": {"Python"},
        "Python Type Hinting": {"Python"},
        # NumPy
        "NumPy Boolean Indexing": {"NumPy"},
        "NumPy Array Creation": {"NumPy"},
        "NumPy Array Manipulation": {"NumPy"},
        "NumPy Array Iteration": {"NumPy"},
        "NumPy Array Validation": {"NumPy"},
        "NumPy Array Initialization": {"NumPy"},
        "NumPy Random Number Generation": {"NumPy"},
        # Gymnasium
        "Gymnasium Environment API": {"Gymnasium"},
        "Gymnasium Spaces": {"Gymnasium"},
        "Gymnasium Environment Design": {"Gymnasium"},
        # PyTorch
        "PyTorch Neural Network Training": {"PyTorch"},
        # Pandas
        "Pandas DataFrame Manipulation": {"Pandas"},
        # FastAPI
        "FastAPI Endpoint Development": {"FastAPI"},
        # Docker
        "Docker Containerization": {"Docker"},
        # SQL
        "SQL Window Functions": {"SQL"},
    }

    def __init__(
        self,
        normalizer: SkillNormalizer | None = None,
    ):
        self.normalizer = normalizer or SkillNormalizer()

        self.parent_skills = {
            self._key(child): {self._key(parent) for parent in parents}
            for child, parents in self.PARENT_SKILLS.items()
        }

    def _key(self, skill: str) -> str:
        return self.normalizer.normalize(skill).casefold()

    def resolve(
        self,
        candidate_skill: str,
        required_skill: str,
    ) -> MatchType | None:

        candidate_key = self._key(candidate_skill)
        required_key = self._key(required_skill)

        if candidate_key == required_key:
            if candidate_skill.strip().casefold() == required_skill.strip().casefold():
                return MatchType.EXACT

            return MatchType.ALIAS

        if required_key in self.parent_skills.get(
            candidate_key,
            set(),
        ):
            return MatchType.HIERARCHICAL

        return None

    def matches(
        self,
        candidate_skill: str,
        required_skill: str,
    ) -> bool:
        return self.resolve(candidate_skill, required_skill) is not None
