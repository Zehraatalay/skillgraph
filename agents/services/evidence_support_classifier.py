from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
)
from agents.schemas.evidence_support import (
    SkillSupport,
    SupportLevel,
)
from agents.schemas.matching import SkillMatch
from agents.services.evidence_aggregator import (
    EvidenceAggregator,
)


class EvidenceSupportClassifier:
    def __init__(
        self,
        aggregator: EvidenceAggregator | None = None,
    ):
        self.aggregator = aggregator or EvidenceAggregator()

    def classify(
        self,
        skill_match: SkillMatch,
    ) -> SkillSupport:

        summary = self.aggregator.aggregate(skill_match)

        evidence_items = skill_match.evidence + skill_match.partial_evidence

        cv_count = sum(
            evidence.source == EvidenceSource.CV for evidence in evidence_items
        )

        github_count = sum(
            evidence.source == EvidenceSource.GITHUB for evidence in evidence_items
        )

        if any(
            evidence.source == EvidenceSource.GITHUB
            and evidence.evidence_type == EvidenceType.TESTED
            for evidence in evidence_items
        ):
            level = SupportLevel.TESTED

        elif any(
            evidence.source == EvidenceSource.GITHUB
            and evidence.evidence_type == EvidenceType.IMPLEMENTATION
            for evidence in evidence_items
        ):
            level = SupportLevel.IMPLEMENTATION_BACKED

        elif cv_count > 0:
            level = SupportLevel.SELF_REPORTED

        else:
            level = SupportLevel.NONE

        return SkillSupport(
            skill=skill_match.skill,
            level=level,
            cv_evidence_count=cv_count,
            github_evidence_count=github_count,
            evidence_summary=summary,
        )
