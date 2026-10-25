from agents.schemas.evidence import SkillEvidence
from agents.schemas.matching import (
    RequirementMatch,
    SkillMatch,
)
from agents.schemas.requirement_group import (
    RequirementGroup,
    RequirementOperator,
)
from agents.schemas.support_level import SupportLevel
from agents.services.skill_matcher import SkillMatcher


class RequirementMatcher:
    def __init__(
        self,
        skill_matcher: SkillMatcher | None = None,
    ):
        self.skill_matcher = skill_matcher or SkillMatcher()

    @staticmethod
    def _support_score(skill_match: SkillMatch) -> float:
        if skill_match.matched:
            return 1.0

        if skill_match.support_level == SupportLevel.PARTIAL:
            return 0.5

        return 0.0

    def build_result(
        self,
        requirement: RequirementGroup,
        skill_matches: list[SkillMatch],
    ) -> RequirementMatch:
        if not skill_matches:
            raise ValueError("Requirement group must contain at least one skill.")

        scores = [self._support_score(skill_match) for skill_match in skill_matches]

        if requirement.operator == RequirementOperator.ALL:
            coverage = sum(scores) / len(scores)
            satisfied = all(skill_match.matched for skill_match in skill_matches)

        elif requirement.operator == RequirementOperator.ANY:
            coverage = max(scores)
            satisfied = any(skill_match.matched for skill_match in skill_matches)

        else:
            raise ValueError(f"Unsupported operator: {requirement.operator}")

        return RequirementMatch(
            skills=skill_matches,
            operator=requirement.operator,
            priority=requirement.priority,
            satisfied=satisfied,
            coverage=coverage,
            evidence_text=requirement.evidence,
        )

    def match(
        self,
        requirement: RequirementGroup,
        candidate_evidence: list[SkillEvidence],
    ) -> RequirementMatch:
        skill_matches = [
            self.skill_matcher.match(
                skill,
                candidate_evidence,
            )
            for skill in requirement.skills
        ]

        return self.build_result(
            requirement=requirement,
            skill_matches=skill_matches,
        )
