from agents.graph.state import SkillGraphState
from agents.schemas.cv import CVAnalysis


def analyze_cv(state: SkillGraphState) -> dict:
    return {
        "cv_analysis": CVAnalysis()
    }