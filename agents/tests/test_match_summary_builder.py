import pytest

from agents.schemas.candidate import CandidateProfile
from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.schemas.grouped_job_analysis import GroupedJobAnalysis
from agents.schemas.requirement_group import RequirementGroup
from agents.services.job_matcher import JobMatcher
from agents.services.match_summary_builder import MatchSummaryBuilder


def evidence(skill):
    return SkillEvidence(
        skill=skill,
        source=EvidenceSource.CV,
        evidence_type=EvidenceType.SELF_REPORTED,
    )


def requirement(
    skills,
    priority="required",
    operator="all",
):
    return RequirementGroup(
        skills=skills,
        priority=priority,
        operator=operator,
        evidence="Example requirement",
    )


def summarize(candidate_skills, requirements):
    candidate = CandidateProfile(skills=[evidence(skill) for skill in candidate_skills])

    job = GroupedJobAnalysis(
        job_id="job-001",
        requirement_groups=requirements,
    )

    match_result = JobMatcher().match(candidate, job)

    return MatchSummaryBuilder().build(match_result)


def test_summary_full_match():
    result = summarize(
        ["Python", "SQL"],
        [
            requirement(["Python"]),
            requirement(["SQL"]),
        ],
    )

    assert result.required.total == 2
    assert result.required.satisfied == 2
    assert result.required.partial == 0
    assert result.required.missing == 0
    assert result.required.coverage == 1.0


def test_summary_partial_and_missing():
    result = summarize(
        ["Python", "NumPy"],
        [
            requirement(["Python"]),
            requirement(["NumPy", "Pandas"]),
            requirement(["Docker"]),
        ],
    )

    assert result.required.total == 3
    assert result.required.satisfied == 1
    assert result.required.partial == 1
    assert result.required.missing == 1
    assert result.required.coverage == pytest.approx(0.5)


def test_summary_separates_priorities():
    result = summarize(
        ["Python"],
        [
            requirement(["Python"]),
            requirement(
                ["Docker"],
                priority="preferred",
            ),
        ],
    )

    assert result.required.coverage == 1.0
    assert result.preferred.coverage == 0.0
    assert result.preferred.missing == 1


def test_summary_empty_categories():
    result = summarize([], [])

    assert result.required.total == 0
    assert result.required.coverage is None
    assert result.preferred.total == 0
    assert result.preferred.coverage is None


def test_summary_any_group():
    result = summarize(
        ["PyTorch"],
        [
            requirement(
                ["PyTorch", "TensorFlow"],
                operator="any",
            ),
        ],
    )

    assert result.required.satisfied == 1
    assert result.required.partial == 0
    assert result.required.coverage == 1.0
