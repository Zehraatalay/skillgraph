from agents.schemas.evidence import EvidenceSource
from agents.schemas.evidence_summary import EvidenceSummary
from agents.schemas.match_type import MatchType
from agents.schemas.matching import SkillMatch


class EvidenceAggregator:
    def aggregate(
        self,
        skill_match: SkillMatch,
    ) -> EvidenceSummary:

        unique_matches = {}

        for item in skill_match.matched_evidence:
            evidence = item.evidence

            key = (
                evidence.skill,
                evidence.source,
                evidence.evidence_type,
                evidence.reference,
                evidence.code_snippet,
                evidence.description,
            )

            unique_matches.setdefault(key, item)

        matches = list(unique_matches.values())

        references = list(
            dict.fromkeys(
                item.evidence.reference for item in matches if item.evidence.reference
            )
        )

        return EvidenceSummary(
            total_evidence=len(matches),
            cv_evidence_count=sum(
                item.evidence.source == EvidenceSource.CV for item in matches
            ),
            github_evidence_count=sum(
                item.evidence.source == EvidenceSource.GITHUB for item in matches
            ),
            exact_count=sum(item.match_type == MatchType.EXACT for item in matches),
            alias_count=sum(item.match_type == MatchType.ALIAS for item in matches),
            hierarchical_count=sum(
                item.match_type == MatchType.HIERARCHICAL for item in matches
            ),
            unique_references=references,
        )
