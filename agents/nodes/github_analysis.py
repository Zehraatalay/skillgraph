from agents.schemas.github import GitHubAnalysis
from agents.services.github_analyzer import GitHubAnalyzer


def analyze_github(
    state: dict,
    analyzer: GitHubAnalyzer | None = None,
) -> dict:
    username = state.get("github_username")

    if not username:
        return {"github_analysis": None}

    if analyzer is None:
        raise RuntimeError("GitHubAnalyzer is not configured")

    result = analyzer.analyze(username)

    if not isinstance(result, GitHubAnalysis):
        raise TypeError("GitHubAnalyzer must return GitHubAnalysis")

    return {"github_analysis": result.model_dump(mode="json")}
