from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.schemas.semantic_matching import (
    SemanticMatchBatch,
    SemanticMatchDecision,
)
from agents.schemas.support_level import SupportLevel
from agents.services.semantic_skill_matcher import (
    SemanticSkillMatcher,
)


class FakeStructuredModel:
    def __init__(self, result):
        self.result = result
        self.calls = 0

    def invoke(self, prompt):
        self.calls += 1
        return self.result


class FakeModelWrapper:
    def __init__(self, result):
        self.structured_model = FakeStructuredModel(result)

    def with_structured_output(self, schema, **kwargs):
        assert schema is SemanticMatchBatch
        return self.structured_model


def make_evidence(skill, reference):
    return SkillEvidence(
        skill=skill,
        source=EvidenceSource.CV,
        evidence_type=EvidenceType.SELF_REPORTED,
        reference=reference,
    )


def test_semantic_matcher_supports_equivalent_skill():
    model = FakeModelWrapper(
        SemanticMatchBatch(
            decisions=[
                SemanticMatchDecision(
                    required_skill="data analytics",
                    support_level=SupportLevel.FULL,
                    supporting_evidence_indices=[0],
                    reasoning="Python data analysis supports data analytics.",
                )
            ]
        )
    )

    matcher = SemanticSkillMatcher(model)

    result = matcher.match(
        requirements=[
            {
                "skill": "data analytics",
                "context": "Experience with data analytics",
            }
        ],
        candidate_evidence=[
            make_evidence(
                "Data Analysis",
                "Python (data analysis)",
            )
        ],
    )

    assert result.decisions[0].support_level == SupportLevel.FULL
    assert result.decisions[0].supporting_evidence_indices == [0]


def test_semantic_matcher_supports_partial_relationship():
    model = FakeModelWrapper(
        SemanticMatchBatch(
            decisions=[
                SemanticMatchDecision(
                    required_skill="MS Office",
                    support_level=SupportLevel.PARTIAL,
                    supporting_evidence_indices=[0],
                    reasoning="Excel is part of Microsoft Office.",
                )
            ]
        )
    )

    matcher = SemanticSkillMatcher(model)

    result = matcher.match(
        requirements=[
            {
                "skill": "MS Office",
                "context": "Experience with MS Office tools",
            }
        ],
        candidate_evidence=[
            make_evidence(
                "Excel",
                "Excel/Google Sheets",
            )
        ],
    )

    assert result.decisions[0].support_level == SupportLevel.PARTIAL


def test_semantic_matcher_rejects_invalid_evidence_index():
    model = FakeModelWrapper(
        SemanticMatchBatch(
            decisions=[
                SemanticMatchDecision(
                    required_skill="PowerBI",
                    support_level=SupportLevel.FULL,
                    supporting_evidence_indices=[999],
                    reasoning="Supported.",
                )
            ]
        )
    )

    matcher = SemanticSkillMatcher(model)

    result = matcher.match(
        requirements=[
            {
                "skill": "PowerBI",
                "context": "PowerBI experience",
            }
        ],
        candidate_evidence=[
            make_evidence("Python", "Python"),
        ],
    )

    assert result.decisions[0].support_level == SupportLevel.NONE
    assert result.decisions[0].supporting_evidence_indices == []


def test_semantic_matcher_handles_missing_decisions():
    model = FakeModelWrapper(SemanticMatchBatch(decisions=[]))

    matcher = SemanticSkillMatcher(model)

    result = matcher.match(
        requirements=[
            {
                "skill": "SQL",
                "context": "SQL experience",
            }
        ],
        candidate_evidence=[
            make_evidence("Python", "Python"),
        ],
    )

    assert len(result.decisions) == 1
    assert result.decisions[0].support_level == SupportLevel.NONE


def test_semantic_matcher_skips_llm_without_requirements():
    model = FakeModelWrapper(SemanticMatchBatch(decisions=[]))

    matcher = SemanticSkillMatcher(model)

    result = matcher.match(
        requirements=[],
        candidate_evidence=[
            make_evidence("Python", "Python"),
        ],
    )

    assert result.decisions == []
    assert model.structured_model.calls == 0


def test_semantic_matcher_skips_llm_without_evidence():
    model = FakeModelWrapper(SemanticMatchBatch(decisions=[]))

    matcher = SemanticSkillMatcher(model)

    result = matcher.match(
        requirements=[
            {
                "skill": "PowerBI",
                "context": "PowerBI experience",
            }
        ],
        candidate_evidence=[],
    )

    assert result.decisions[0].support_level == SupportLevel.NONE
    assert model.structured_model.calls == 0
