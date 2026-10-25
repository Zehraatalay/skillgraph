import pytest
from pydantic import ValidationError

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


def test_cv_analysis_defaults():
    analysis = CVAnalysis()

    assert analysis.skills == []
    assert analysis.education == []
    assert analysis.experience == []
    assert analysis.projects == []


def test_github_analysis():
    repository = RepositoryAnalysis(
        repository_name="match3-ai-lab",
        analyzed_files=["src/match3_ai/games/match3/board.py"],
    )

    analysis = GitHubAnalysis(
        username="exampleuser",
        repositories=[repository],
    )

    assert analysis.username == "exampleuser"
    assert len(analysis.repositories) == 1
    assert analysis.repositories[0].repository_name == ("match3-ai-lab")


def test_evidence_validation():
    evidence = SkillEvidence(
        skill="Python",
        source="github",
        evidence_type="implementation",
        reference="repo/src/main.py",
    )

    assert evidence.skill == "Python"
    assert evidence.source.value == "github"


def test_invalid_evidence_type():
    with pytest.raises(ValidationError):
        SkillEvidence(
            skill="Python",
            source="github",
            evidence_type="unverified",
        )


def test_empty_repository_name():
    with pytest.raises(ValidationError):
        RepositoryAnalysis(repository_name="")


def test_github_evidence_with_code_snippet():
    evidence = SkillEvidence(
        skill="NumPy",
        source=EvidenceSource.GITHUB,
        evidence_type=EvidenceType.IMPLEMENTATION,
        reference="src/engine.py",
        code_snippet="self.rng = np.random.default_rng(seed)",
    )

    assert evidence.skill == "NumPy"

    assert evidence.code_snippet == ("self.rng = np.random.default_rng(seed)")

    assert evidence.source == EvidenceSource.GITHUB
