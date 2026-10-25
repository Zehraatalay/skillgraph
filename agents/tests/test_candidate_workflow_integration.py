from agents.graph.workflow import build_workflow
from agents.schemas.cv import CVAnalysis
from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.schemas.github import (
    GitHubAnalysis,
    RepositoryAnalysis,
)


class FakeCVExtractor:
    def extract(self, cv_text: str) -> CVAnalysis:
        return CVAnalysis(
            skills=[
                SkillEvidence(
                    skill="Python",
                    source=EvidenceSource.CV,
                    evidence_type=EvidenceType.SELF_REPORTED,
                    reference="Python",
                )
            ],
            education=["Computer Engineering"],
            experience=[],
            projects=["University Project"],
        )


class FakeGitHubAnalyzer:
    def analyze(self, username: str) -> GitHubAnalysis:
        return GitHubAnalysis(
            username=username,
            repositories=[
                RepositoryAnalysis(
                    repository_name="match3-ai-lab",
                    repository_url=("https://github.com/test/match3-ai-lab"),
                    skills=[
                        SkillEvidence(
                            skill="NumPy",
                            source=EvidenceSource.GITHUB,
                            evidence_type=EvidenceType.IMPLEMENTATION,
                            reference="src/board.py",
                            code_snippet="import numpy as np",
                        )
                    ],
                    analyzed_files=["src/board.py"],
                )
            ],
        )


def test_workflow_combines_cv_and_github_evidence():
    workflow = build_workflow(
        cv_extractor=FakeCVExtractor(),
        github_analyzer=FakeGitHubAnalyzer(),
    )

    result = workflow.invoke(
        {
            "cv_text": "Python developer",
            "github_username": "testuser",
            "preferences_text": None,
            "job_postings": [
                {
                    "id": "job-001",
                    "title": "ML Engineer",
                    "description": "Python and NumPy",
                }
            ],
            "cv_analysis": None,
            "github_analysis": None,
            "candidate_profile": None,
            "results": [],
        }
    )

    profile = result["candidate_profile"]

    assert profile is not None

    skills = profile["skills"]

    assert len(skills) == 2

    skill_names = {skill["skill"] for skill in skills}

    assert skill_names == {
        "Python",
        "NumPy",
    }

    sources = {skill["source"] for skill in skills}

    assert sources == {
        "cv",
        "github",
    }

    assert "Computer Engineering" in profile["education"]
    assert "University Project" in profile["projects"]
    assert "match3-ai-lab" in profile["projects"]
