from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.schemas.match_type import MatchType
from agents.schemas.matched_evidence import MatchedEvidence
from agents.schemas.matching import SkillMatch


def test_evidence_is_derived_from_matched_evidence():
    evidence = SkillEvidence(
        skill="Python",
        source=EvidenceSource.CV,
        evidence_type=EvidenceType.SELF_REPORTED,
        reference="CV technical skills",
    )

    skill_match = SkillMatch(
        skill="Python",
        matched=True,
        matched_evidence=[
            MatchedEvidence(
                evidence=evidence,
                match_type=MatchType.EXACT,
            )
        ],
    )

    assert skill_match.evidence == [evidence]


def test_empty_matched_evidence_produces_empty_evidence():
    skill_match = SkillMatch(
        skill="Docker",
        matched=False,
    )

    assert skill_match.evidence == []
