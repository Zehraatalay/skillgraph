import pytest

from agents.nodes.job_matching import create_job_matching_node
from agents.schemas.candidate import CandidateProfile
from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.schemas.grouped_job_analysis import GroupedJobAnalysis
from agents.schemas.requirement_group import RequirementGroup


def candidate_data():
    return CandidateProfile(
        skills=[
            SkillEvidence(
                skill="Python",
                source=EvidenceSource.CV,
                evidence_type=EvidenceType.SELF_REPORTED,
            )
        ]
    ).model_dump(mode="json")


def job_data(job_id, skill):
    return GroupedJobAnalysis(
        job_id=job_id,
        requirement_groups=[
            RequirementGroup(
                skills=[skill],
                priority="required",
                evidence=f"{skill} is required.",
            )
        ],
    ).model_dump(mode="json")


def test_matching_node_single_job():
    node = create_job_matching_node()

    result = node(
        {
            "candidate_profile": candidate_data(),
            "job_analyses": [
                job_data("job-001", "Python"),
            ],
        }
    )

    assert len(result["results"]) == 1

    match = result["results"][0]

    assert match["job_id"] == "job-001"
    assert match["summary"]["required"]["coverage"] == 1.0


def test_matching_node_multiple_jobs():
    node = create_job_matching_node()

    result = node(
        {
            "candidate_profile": candidate_data(),
            "job_analyses": [
                job_data("job-001", "Python"),
                job_data("job-002", "Docker"),
            ],
        }
    )

    assert len(result["results"]) == 2

    assert result["results"][0]["summary"]["required"]["coverage"] == 1.0
    assert result["results"][1]["summary"]["required"]["coverage"] == 0.0


def test_matching_node_requires_candidate():
    node = create_job_matching_node()

    with pytest.raises(
        ValueError,
        match="Candidate profile is required",
    ):
        node(
            {
                "job_analyses": [
                    job_data("job-001", "Python"),
                ],
            }
        )


def test_matching_node_empty_jobs():
    node = create_job_matching_node()

    result = node(
        {
            "candidate_profile": candidate_data(),
            "job_analyses": [],
        }
    )

    assert result["results"] == []
