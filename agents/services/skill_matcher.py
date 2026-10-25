from agents.schemas.evidence import SkillEvidence
from agents.schemas.matched_evidence import MatchedEvidence
from agents.schemas.matching import SkillMatch
from agents.schemas.support_level import SupportLevel
from agents.services.skill_relationship_resolver import (
    SkillRelationshipResolver,
)


class SkillMatcher:
    def __init__(
        self,
        relationship_resolver: SkillRelationshipResolver | None = None,
    ):
        self.relationship_resolver = (
            relationship_resolver or SkillRelationshipResolver()
        )

    def match(
        self,
        required_skill: str,
        candidate_evidence: list[SkillEvidence],
    ) -> SkillMatch:

        matched_evidence = []

        for evidence in candidate_evidence:
            match_type = self.relationship_resolver.resolve(
                candidate_skill=evidence.skill,
                required_skill=required_skill,
            )

            if match_type is None:
                continue

            matched_evidence.append(
                MatchedEvidence(
                    evidence=evidence,
                    match_type=match_type,
                )
            )

        return SkillMatch(
            skill=required_skill,
            matched=bool(matched_evidence),
            matched_evidence=matched_evidence,
            support_level=(
                SupportLevel.FULL if matched_evidence else SupportLevel.NONE
            ),
        )
