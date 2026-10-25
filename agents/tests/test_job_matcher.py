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


def evidence(
    skill: str,
    source: EvidenceSource = EvidenceSource.CV,
    evidence_type: EvidenceType = EvidenceType.SELF_REPORTED,
) -> SkillEvidence:
    return SkillEvidence(
        skill=skill,
        source=source,
        evidence_type=evidence_type,
    )


def requirement(
    skills: list[str],
    operator: str = "all",
    priority: str = "required",
) -> RequirementGroup:
    return RequirementGroup(
        skills=skills,
        operator=operator,
        priority=priority,
        evidence="Example requirement",
    )


def job(
    requirements: list[RequirementGroup],
) -> GroupedJobAnalysis:
    return GroupedJobAnalysis(
        job_id="job-001",
        requirement_groups=requirements,
    )


def candidate(
    skills: list[SkillEvidence],
) -> CandidateProfile:
    return CandidateProfile(skills=skills)


def test_job_matcher_full_match():
    result = JobMatcher().match(
        candidate(
            [
                evidence("Python"),
                evidence("SQL"),
            ]
        ),
        job(
            [
                requirement(["Python"]),
                requirement(["SQL"]),
            ]
        ),
    )

    assert result.required_coverage == 1.0
    assert result.preferred_coverage == 1.0
    assert all(item.satisfied for item in result.requirements)


def test_job_matcher_partial_required_coverage():
    result = JobMatcher().match(
        candidate(
            [
                evidence("Python"),
                evidence("NumPy"),
                evidence("Git"),
            ]
        ),
        job(
            [
                requirement(["Python"]),
                requirement(["NumPy", "Pandas"]),
                requirement(["Git"]),
            ]
        ),
    )

    assert result.required_coverage == pytest.approx(5 / 6)

    assert result.requirements[1].coverage == 0.5
    assert result.requirements[1].satisfied is False


def test_job_matcher_separates_required_preferred():
    result = JobMatcher().match(
        candidate(
            [
                evidence("Python"),
                evidence("PyTorch"),
            ]
        ),
        job(
            [
                requirement(["Python"]),
                requirement(
                    ["PyTorch", "TensorFlow"],
                    operator="any",
                    priority="preferred",
                ),
                requirement(
                    ["Docker"],
                    priority="preferred",
                ),
            ]
        ),
    )

    assert result.required_coverage == 1.0
    assert result.preferred_coverage == 0.5


def test_job_matcher_no_requirements():
    result = JobMatcher().match(
        candidate([]),
        job([]),
    )

    assert result.requirements == []
    assert result.required_coverage == 1.0
    assert result.preferred_coverage == 1.0


def test_job_matcher_preserves_cv_and_github_evidence():
    cv_evidence = evidence("Python")

    github_evidence = evidence(
        "Python",
        source=EvidenceSource.GITHUB,
        evidence_type=EvidenceType.IMPLEMENTATION,
    )

    result = JobMatcher().match(
        candidate(
            [
                cv_evidence,
                github_evidence,
            ]
        ),
        job(
            [
                requirement(["Python"]),
            ]
        ),
    )

    skill_match = result.requirements[0].skills[0]

    assert skill_match.matched is True
    assert len(skill_match.evidence) == 2

    assert {item.source for item in skill_match.evidence} == {
        EvidenceSource.CV,
        EvidenceSource.GITHUB,
    }


def test_job_matcher_unmatched_requirement():
    result = JobMatcher().match(
        candidate(
            [
                evidence("Python"),
            ]
        ),
        job(
            [
                requirement(["Kubernetes"]),
            ]
        ),
    )

    assert result.required_coverage == 0.0
    assert result.requirements[0].satisfied is False
    assert result.requirements[0].skills[0].evidence == []


def test_job_matcher_preserves_job_id():
    result = JobMatcher().match(
        candidate([]),
        job([]),
    )

    assert result.job_id == "job-001"
