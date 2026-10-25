from agents.nodes.candidate_profile import build_candidate_profile
from agents.schemas.cv import CVAnalysis
from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.schemas.github import GitHubAnalysis, RepositoryAnalysis


def test_candidate_profile_from_cv():
    cv_analysis = CVAnalysis(
        skills=[
            SkillEvidence(
                skill="Python",
                source=EvidenceSource.CV,
                evidence_type=EvidenceType.SELF_REPORTED,
                reference="Python",
            )
        ],
        education=["Computer Engineering"],
        projects=["Sales Forecasting"],
    )

    state = {
        "cv_analysis": cv_analysis.model_dump(mode="json"),
        "github_analysis": None,
    }

    result = build_candidate_profile(state)

    profile = result["candidate_profile"]

    assert profile["skills"][0]["skill"] == "Python"
    assert profile["education"] == ["Computer Engineering"]
    assert profile["projects"] == ["Sales Forecasting"]


def test_candidate_profile_from_github():
    github_analysis = GitHubAnalysis(
        username="exampleuser",
        repositories=[
            RepositoryAnalysis(
                repository_name="ml-project",
                skills=[
                    SkillEvidence(
                        skill="Python",
                        source=EvidenceSource.GITHUB,
                        evidence_type=EvidenceType.IMPLEMENTATION,
                        reference="src/model.py",
                    )
                ],
            )
        ],
    )

    state = {
        "cv_analysis": None,
        "github_analysis": github_analysis.model_dump(mode="json"),
    }

    result = build_candidate_profile(state)

    profile = result["candidate_profile"]

    assert profile["skills"][0]["source"] == "github"
    assert profile["projects"] == ["ml-project"]


def test_candidate_profile_preserves_multiple_evidence():
    cv_analysis = CVAnalysis(
        skills=[
            SkillEvidence(
                skill="Python",
                source=EvidenceSource.CV,
                evidence_type=EvidenceType.SELF_REPORTED,
                reference="Python",
            )
        ]
    )

    github_analysis = GitHubAnalysis(
        username="exampleuser",
        repositories=[
            RepositoryAnalysis(
                repository_name="python-project",
                skills=[
                    SkillEvidence(
                        skill="Python",
                        source=EvidenceSource.GITHUB,
                        evidence_type=EvidenceType.IMPLEMENTATION,
                        reference="src/main.py",
                    )
                ],
            )
        ],
    )

    state = {
        "cv_analysis": cv_analysis.model_dump(mode="json"),
        "github_analysis": github_analysis.model_dump(mode="json"),
    }

    result = build_candidate_profile(state)

    skills = result["candidate_profile"]["skills"]

    assert len(skills) == 2

    assert skills[0]["source"] == "cv"
    assert skills[1]["source"] == "github"


def test_empty_candidate_profile():
    state = {
        "cv_analysis": None,
        "github_analysis": None,
    }

    result = build_candidate_profile(state)

    assert result["candidate_profile"] == {
        "skills": [],
        "education": [],
        "experience": [],
        "projects": [],
    }
