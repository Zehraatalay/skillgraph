import pytest

from agents.nodes.github_analysis import analyze_github
from agents.schemas.github import (
    GitHubAnalysis,
    RepositoryAnalysis,
)


class FakeGitHubAnalyzer:
    def analyze(self, username):
        return GitHubAnalysis(
            username=username,
            repositories=[
                RepositoryAnalysis(
                    repository_name="match3-ai-lab",
                    repository_url=("https://github.com/test/match3-ai-lab"),
                    skills=[],
                    analyzed_files=["src/engine.py"],
                )
            ],
        )


def test_analyzes_github_and_returns_json_dict():
    result = analyze_github(
        {"github_username": "testuser"},
        analyzer=FakeGitHubAnalyzer(),
    )

    assert isinstance(result["github_analysis"], dict)

    assert result["github_analysis"]["username"] == "testuser"

    assert (
        result["github_analysis"]["repositories"][0]["repository_name"]
        == "match3-ai-lab"
    )


def test_skips_github_when_username_missing():
    result = analyze_github(
        {"github_username": None},
    )

    assert result == {"github_analysis": None}


def test_rejects_missing_analyzer():
    with pytest.raises(
        RuntimeError,
        match="GitHubAnalyzer is not configured",
    ):
        analyze_github(
            {"github_username": "testuser"},
        )


def test_rejects_invalid_analyzer_result():
    class InvalidAnalyzer:
        def analyze(self, username):
            return {"username": username}

    with pytest.raises(
        TypeError,
        match="GitHubAnalyzer must return GitHubAnalysis",
    ):
        analyze_github(
            {"github_username": "testuser"},
            analyzer=InvalidAnalyzer(),
        )
