import pytest
from pydantic import ValidationError

from agents.schemas.semantic_matching import (
    SemanticMatchBatch,
    SemanticMatchDecision,
)
from agents.schemas.support_level import SupportLevel


def test_semantic_match_decision_full():
    decision = SemanticMatchDecision(
        required_skill="data analytics",
        support_level=SupportLevel.FULL,
        supporting_evidence_indices=[0],
        reasoning="Data analysis is relevant to data analytics.",
    )

    assert decision.support_level == SupportLevel.FULL
    assert decision.supporting_evidence_indices == [0]


def test_semantic_match_decision_partial():
    decision = SemanticMatchDecision(
        required_skill="MS Office",
        support_level=SupportLevel.PARTIAL,
        supporting_evidence_indices=[2],
        reasoning="Excel supports part of the MS Office requirement.",
    )

    assert decision.support_level == SupportLevel.PARTIAL


def test_semantic_match_decision_none():
    decision = SemanticMatchDecision(
        required_skill="PowerBI",
        support_level=SupportLevel.NONE,
        reasoning="No supporting evidence found.",
    )

    assert decision.supporting_evidence_indices == []


def test_semantic_match_batch():
    batch = SemanticMatchBatch(
        decisions=[
            SemanticMatchDecision(
                required_skill="data analytics",
                support_level=SupportLevel.FULL,
                supporting_evidence_indices=[0],
                reasoning="Supported by Python data analysis.",
            ),
            SemanticMatchDecision(
                required_skill="MS Office",
                support_level=SupportLevel.PARTIAL,
                supporting_evidence_indices=[2],
                reasoning="Supported partially by Excel.",
            ),
        ]
    )

    assert len(batch.decisions) == 2


def test_invalid_support_level_rejected():
    with pytest.raises(ValidationError):
        SemanticMatchDecision(
            required_skill="SQL",
            support_level="unknown",
            reasoning="Invalid support level.",
        )
