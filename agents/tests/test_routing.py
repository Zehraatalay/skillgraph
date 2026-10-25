import pytest

from agents.graph.checkpointer import create_checkpointer
from agents.graph.workflow import build_workflow
from agents.schemas.github import (
    GitHubAnalysis,
    RepositoryAnalysis,
)
from agents.schemas.job import JobPosting


@pytest.mark.parametrize(
    "cv_text,github_username,expected_nodes",
    [
        (
            "Python developer",
            None,
            {"analyze_cv"},
        ),
        (
            None,
            "exampleuser",
            {"analyze_github"},
        ),
        (
            "Python developer",
            "exampleuser",
            {"analyze_cv", "analyze_github"},
        ),
    ],
)
def test_candidate_source_routing(
    cv_text,
    github_username,
    expected_nodes,
):
    graph = build_workflow(
        checkpointer=create_checkpointer(),
        github_analyzer=FakeGitHubAnalyzer(),
    )

    initial_state = {
        "cv_text": cv_text,
        "github_username": github_username,
        "preferences_text": None,
        "job_postings": [
            JobPosting(
                id="job-001",
                title="ML Engineer",
                description="Python and machine learning",
            )
        ],
        "candidate_profile": None,
        "results": [],
    }

    events = list(
        graph.stream(
            initial_state,
            config={"configurable": {"thread_id": "routing-test"}},
            stream_mode="updates",
        )
    )

    executed_nodes = {node_name for event in events for node_name in event}

    assert expected_nodes.issubset(executed_nodes)

    if cv_text is None:
        assert "analyze_cv" not in executed_nodes

    if github_username is None:
        assert "analyze_github" not in executed_nodes

    assert "build_candidate_profile" in executed_nodes


class FakeGitHubAnalyzer:
    def analyze(self, username: str) -> GitHubAnalysis:
        return GitHubAnalysis(
            username=username,
            repositories=[
                RepositoryAnalysis(
                    repository_name="example-project",
                    repository_url=("https://github.com/exampleuser/example-project"),
                    skills=[],
                    analyzed_files=["src/main.py"],
                )
            ],
        )
