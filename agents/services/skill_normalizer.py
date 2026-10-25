import re
from typing import ClassVar


class SkillNormalizer:
    SKILL_ALIASES: ClassVar[dict[str, str]] = {
        "oop": "Object-Oriented Programming",
        "object-oriented programming": "Object-Oriented Programming",
        "sklearn": "scikit-learn",
        "scikit learn": "scikit-learn",
        "scikit-learn": "scikit-learn",
        "retrieval-augmented generation (rag)": "RAG",
        "retrieval-augmented generation": "RAG",
        "rag": "RAG",
        "data analysis": "Data Analytics",
        "data analytics": "Data Analytics",
    }

    def normalize(self, skill: str) -> str:
        if not isinstance(skill, str):
            raise TypeError("Skill name must be a string")

        cleaned = re.sub(r"\s+", " ", skill).strip()

        if not cleaned:
            raise ValueError("Skill name cannot be empty")

        normalized_key = cleaned.casefold()

        return self.SKILL_ALIASES.get(
            normalized_key,
            cleaned,
        )
