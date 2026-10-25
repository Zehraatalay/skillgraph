import pytest

from agents.nodes.cv_analysis import create_cv_analysis_node
from agents.schemas.cv import CVAnalysis
from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)


class FakeCVExtractor:
    def __init__(self):
        self.calls = []

    def extract(self, cv_text: str) -> CVAnalysis:
        self.calls.append(cv_text)

        return CVAnalysis(
            skills=[
                SkillEvidence(
                    skill="Python",
                    source=EvidenceSource.CV,
                    evidence_type=EvidenceType.SELF_REPORTED,
                    reference="Python",
                )
            ]
        )


def test_cv_node_uses_injected_extractor():
    extractor = FakeCVExtractor()

    node = create_cv_analysis_node(extractor)

    result = node(
        {
            "cv_text": "Skills: Python",
        }
    )

    assert extractor.calls == ["Skills: Python"]

    assert isinstance(
        result["cv_analysis"],
        dict,
    )

    assert result["cv_analysis"]["skills"][0]["skill"] == "Python"


@pytest.mark.parametrize(
    "cv_text",
    [None, "", "   "],
)
def test_cv_node_rejects_empty_text(cv_text):
    extractor = FakeCVExtractor()

    node = create_cv_analysis_node(extractor)

    with pytest.raises(ValueError):
        node(
            {
                "cv_text": cv_text,
            }
        )

    assert extractor.calls == []
