from agents.graph.state import SkillGraphState
from agents.schemas.github import GitHubAnalysis


def analyze_github(state: SkillGraphState) -> dict:
    username = (state.get("github_username") or "").strip()

    return {"github_analysis": GitHubAnalysis(username=username)}
