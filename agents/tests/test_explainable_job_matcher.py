from agents.schemas.candidate import CandidateProfile
from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.schemas.evidence_support import SupportLevel
from agents.schemas.grouped_job_analysis import GroupedJobAnalysis
from agents.schemas.requirement_group import RequirementGroup
from agents.services.explainable_job_matcher import (
    ExplainableJobMatcher,
)


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


def test_explainable_match_preserves_job_id():
    candidate = CandidateProfile()

    job = GroupedJobAnalysis(
        job_id="job-001",
        requirement_groups=[],
    )

    result = ExplainableJobMatcher().match(
        candidate,
        job,
    )

    assert result.job_id == "job-001"
    assert result.match_result.job_id == "job-001"
    assert result.summary.job_id == "job-001"


def test_explainable_match_classifies_cv_evidence():
    candidate = CandidateProfile(
        skills=[
            evidence("Python"),
        ]
    )

    job = GroupedJobAnalysis(
        job_id="job-001",
        requirement_groups=[
            requirement(["Python"]),
        ],
    )

    result = ExplainableJobMatcher().match(
        candidate,
        job,
    )

    explained = result.explained_requirements[0]

    assert explained.requirement.satisfied is True

    support = explained.skill_support[0]

    assert support.skill == "Python"
    assert support.level == SupportLevel.SELF_REPORTED
    assert support.cv_evidence_count == 1
    assert support.github_evidence_count == 0


def test_explainable_match_classifies_github_evidence():
    candidate = CandidateProfile(
        skills=[
            evidence("Python"),
            evidence(
                "Python",
                source=EvidenceSource.GITHUB,
                evidence_type=EvidenceType.IMPLEMENTATION,
            ),
        ]
    )

    job = GroupedJobAnalysis(
        job_id="job-001",
        requirement_groups=[
            requirement(["Python"]),
        ],
    )

    result = ExplainableJobMatcher().match(
        candidate,
        job,
    )

    support = result.explained_requirements[0].skill_support[0]

    assert support.level == SupportLevel.IMPLEMENTATION_BACKED
    assert support.cv_evidence_count == 1
    assert support.github_evidence_count == 1


def test_explainable_match_partial_requirement():
    candidate = CandidateProfile(
        skills=[
            evidence("NumPy"),
        ]
    )

    job = GroupedJobAnalysis(
        job_id="job-001",
        requirement_groups=[
            requirement(["NumPy", "Pandas"]),
        ],
    )

    result = ExplainableJobMatcher().match(
        candidate,
        job,
    )

    explained = result.explained_requirements[0]

    assert explained.requirement.satisfied is False
    assert explained.requirement.coverage == 0.5

    assert explained.skill_support[0].level == (SupportLevel.SELF_REPORTED)

    assert explained.skill_support[1].level == (SupportLevel.NONE)

    assert result.summary.required.partial == 1


def test_explainable_match_any_requirement():
    candidate = CandidateProfile(
        skills=[
            evidence("PyTorch"),
        ]
    )

    job = GroupedJobAnalysis(
        job_id="job-001",
        requirement_groups=[
            requirement(
                ["PyTorch", "TensorFlow"],
                operator="any",
                priority="preferred",
            ),
        ],
    )

    result = ExplainableJobMatcher().match(
        candidate,
        job,
    )

    explained = result.explained_requirements[0]

    assert explained.requirement.satisfied is True
    assert explained.requirement.coverage == 1.0

    assert explained.skill_support[0].level == (SupportLevel.SELF_REPORTED)

    assert explained.skill_support[1].level == (SupportLevel.NONE)

    assert result.summary.preferred.satisfied == 1


def test_explainable_match_empty_requirements():
    result = ExplainableJobMatcher().match(
        CandidateProfile(),
        GroupedJobAnalysis(
            job_id="job-001",
            requirement_groups=[],
        ),
    )

    assert result.explained_requirements == []

    assert result.summary.required.coverage is None
    assert result.summary.preferred.coverage is None
