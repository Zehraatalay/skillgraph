from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.schemas.match_type import MatchType
from agents.schemas.matched_evidence import MatchedEvidence
from agents.schemas.matching import SkillMatch
from agents.services.evidence_aggregator import EvidenceAggregator


def make_evidence(
    skill: str,
    source: EvidenceSource,
    reference: str,
) -> SkillEvidence:
    return SkillEvidence(
        skill=skill,
        source=source,
        evidence_type=(
            EvidenceType.SELF_REPORTED
            if source == EvidenceSource.CV
            else EvidenceType.IMPLEMENTATION
        ),
        reference=reference,
    )


def test_aggregates_multiple_evidence_sources():
    cv = make_evidence(
        "Python",
        EvidenceSource.CV,
        "Technical skills: Python",
    )

    github = make_evidence(
        "Python Dataclasses",
        EvidenceSource.GITHUB,
        "src/board.py",
    )

    skill_match = SkillMatch(
        skill="Python",
        matched=True,
        matched_evidence=[
            MatchedEvidence(
                evidence=cv,
                match_type=MatchType.EXACT,
            ),
            MatchedEvidence(
                evidence=github,
                match_type=MatchType.HIERARCHICAL,
            ),
        ],
    )

    summary = EvidenceAggregator().aggregate(skill_match)

    assert summary.total_evidence == 2
    assert summary.cv_evidence_count == 1
    assert summary.github_evidence_count == 1

    assert summary.exact_count == 1
    assert summary.hierarchical_count == 1

    assert len(summary.unique_references) == 2


def test_deduplicates_identical_evidence():
    github = make_evidence(
        "Python Dataclasses",
        EvidenceSource.GITHUB,
        "src/board.py",
    )

    matched = MatchedEvidence(
        evidence=github,
        match_type=MatchType.HIERARCHICAL,
    )

    skill_match = SkillMatch(
        skill="Python",
        matched=True,
        matched_evidence=[matched, matched],
    )

    summary = EvidenceAggregator().aggregate(skill_match)

    assert summary.total_evidence == 1
    assert summary.github_evidence_count == 1
    assert summary.hierarchical_count == 1


def test_handles_unmatched_skill():
    skill_match = SkillMatch(
        skill="Docker",
        matched=False,
    )

    summary = EvidenceAggregator().aggregate(skill_match)

    assert summary.total_evidence == 0
    assert summary.cv_evidence_count == 0
    assert summary.github_evidence_count == 0
    assert summary.unique_references == []
