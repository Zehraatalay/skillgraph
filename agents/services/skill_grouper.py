from agents.schemas.evidence import SkillEvidence
from agents.schemas.skill_group import SkillGroup
from agents.services.skill_normalizer import SkillNormalizer


class SkillGrouper:
    def __init__(
        self,
        normalizer: SkillNormalizer | None = None,
    ):
        self.normalizer = normalizer or SkillNormalizer()

    def group(
        self,
        evidence: list[SkillEvidence],
    ) -> list[SkillGroup]:

        grouped: dict[str, list[SkillEvidence]] = {}

        for item in evidence:
            normalized_name = self.normalizer.normalize(item.skill)

            grouped.setdefault(
                normalized_name,
                [],
            ).append(item)

        return [
            SkillGroup(
                name=name,
                evidence=items,
            )
            for name, items in grouped.items()
        ]
