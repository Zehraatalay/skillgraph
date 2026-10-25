from typing import Protocol

from agents.graph.state import SkillGraphState
from agents.schemas.cv import CVAnalysis


class CVExtractorProtocol(Protocol):
    def extract(self, cv_text: str) -> CVAnalysis: ...


def create_cv_analysis_node(extractor: CVExtractorProtocol):
    def analyze_cv(state: SkillGraphState) -> dict:
        cv_text = (state.get("cv_text") or "").strip()

        if not cv_text:
            raise ValueError("CV analysis requires non-empty CV text.")

        analysis = extractor.extract(cv_text)

        return {"cv_analysis": analysis.model_dump(mode="json")}

    return analyze_cv
