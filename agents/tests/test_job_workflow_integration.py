from agents.graph.workflow import build_workflow
from agents.schemas.cv import CVAnalysis
from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.schemas.github import GitHubAnalysis
from agents.schemas.grouped_job_analysis import GroupedJobAnalysis
from agents.schemas.requirement_group import RequirementGroup


class FakeCVExtractor:
    def extract(self, text):
        return CVAnalysis(
            skills=[
                SkillEvidence(
                    skill="Python",
                    source=EvidenceSource.CV,
                    evidence_type=EvidenceType.SELF_REPORTED,
                )
            ],
        )


class FakeGitHubAnalyzer:
    def analyze_user(self, username):
        return GitHubAnalysis(
            username=username,
            repositories=[],
        )


class FakeJobExtractor:
    def extract(self, job):
        return GroupedJobAnalysis(
            job_id=job.id,
            requirement_groups=[
                RequirementGroup(
                    skills=["Python"],
                    operator="all",
                    priority="required",
                    evidence="Python is required.",
                )
            ],
        )


def test_complete_job_workflow():
    graph = build_workflow(
        cv_extractor=FakeCVExtractor(),
        github_analyzer=FakeGitHubAnalyzer(),
        job_extractor=FakeJobExtractor(),
    )

    result = graph.invoke(
        {
            "cv_text": "Python developer",
            "github_username": None,
            "job_postings": [
                {
                    "id": "job-001",
                    "title": "Python Developer",
                    "description": "Python is required.",
                }
            ],
        }
    )

    assert result["candidate_profile"] is not None

    assert len(result["job_analyses"]) == 1

    assert len(result["results"]) == 1

    match = result["results"][0]

    assert match["job_id"] == "job-001"

    assert match["summary"]["required"]["coverage"] == 1.0

    assert match["summary"]["required"]["satisfied"] == 1


def test_workflow_multiple_jobs():
    graph = build_workflow(
        cv_extractor=FakeCVExtractor(),
        github_analyzer=FakeGitHubAnalyzer(),
        job_extractor=FakeJobExtractor(),
    )

    result = graph.invoke(
        {
            "cv_text": "Python developer",
            "github_username": None,
            "job_postings": [
                {
                    "id": "job-001",
                    "title": "Python Developer",
                    "description": "Python is required.",
                },
                {
                    "id": "job-002",
                    "title": "ML Engineer",
                    "description": "Python is required.",
                },
            ],
        }
    )

    assert len(result["job_analyses"]) == 2
    assert len(result["results"]) == 2

    assert [match["job_id"] for match in result["results"]] == [
        "job-001",
        "job-002",
    ]


def test_workflow_without_job_extractor():
    graph = build_workflow(
        cv_extractor=FakeCVExtractor(),
        github_analyzer=FakeGitHubAnalyzer(),
    )

    result = graph.invoke(
        {
            "cv_text": "Python developer",
            "github_username": None,
        }
    )

    assert result["candidate_profile"] is not None
    assert "job_analyses" not in result
    assert "results" not in result
