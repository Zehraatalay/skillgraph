import pytest
from langchain_google_genai.chat_models import GoogleAPIError

from agents.schemas.cv import CVAnalysis
from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.services.cv_extractor import (
    CVExtractor,
    filter_invalid_cv_references,
)

# ============================================================
# Fake models
# ============================================================


class FakeStructuredModel:
    def invoke(self, prompt):
        return CVAnalysis(
            skills=[
                SkillEvidence(
                    skill="Python",
                    source=EvidenceSource.CV,
                    evidence_type=EvidenceType.SELF_REPORTED,
                    reference="Skills: Python",
                )
            ],
            education=["BSc Computer Engineering"],
        )


class FakeGeminiModel:
    def with_structured_output(self, schema, **kwargs):
        assert schema is CVAnalysis
        return FakeStructuredModel()


class FakeModelWrapper:
    def __init__(self, structured_model):
        self.structured_model = structured_model

    def with_structured_output(self, schema, **kwargs):
        assert schema is CVAnalysis
        return self.structured_model


class InvalidSourceModel:
    def invoke(self, prompt):
        return CVAnalysis(
            skills=[
                SkillEvidence(
                    skill="Python",
                    source=EvidenceSource.GITHUB,
                    evidence_type=EvidenceType.SELF_REPORTED,
                )
            ]
        )


class InvalidEvidenceTypeModel:
    def invoke(self, prompt):
        return CVAnalysis(
            skills=[
                SkillEvidence(
                    skill="Python",
                    source=EvidenceSource.CV,
                    evidence_type=EvidenceType.TESTED,
                )
            ]
        )


class PromptCaptureModel:
    def __init__(self):
        self.last_prompt = None

    def invoke(self, prompt):
        self.last_prompt = prompt
        return CVAnalysis()


class TemporarilyUnavailableModel:
    def __init__(self):
        self.attempts = 0

    def invoke(self, prompt):
        self.attempts += 1

        if self.attempts < 3:
            raise GoogleAPIError(
                503,
                {
                    "error": {
                        "code": 503,
                        "message": (
                            "This model is currently experiencing high demand."
                        ),
                        "status": "UNAVAILABLE",
                    }
                },
            )

        return CVAnalysis()


# ============================================================
# CV extraction tests
# ============================================================


def test_cv_extraction():
    extractor = CVExtractor(FakeGeminiModel())

    result = extractor.extract("Computer Engineering graduate. Skills: Python.")

    assert isinstance(result, CVAnalysis)
    assert len(result.skills) == 1
    assert result.skills[0].skill == "Python"
    assert result.skills[0].source == EvidenceSource.CV
    assert result.skills[0].evidence_type == EvidenceType.SELF_REPORTED
    assert result.education == ["BSc Computer Engineering"]


def test_empty_cv_rejected():
    extractor = CVExtractor(FakeGeminiModel())

    with pytest.raises(
        ValueError,
        match="CV text cannot be empty",
    ):
        extractor.extract("   ")


# ============================================================
# Evidence provenance validation
# ============================================================


def test_rejects_github_evidence_in_cv():
    extractor = CVExtractor(FakeModelWrapper(InvalidSourceModel()))

    with pytest.raises(
        ValueError,
        match="Invalid evidence source",
    ):
        extractor.extract("Skills: Python")


def test_rejects_tested_evidence_in_cv():
    extractor = CVExtractor(FakeModelWrapper(InvalidEvidenceTypeModel()))

    with pytest.raises(
        ValueError,
        match="CV evidence must be self-reported",
    ):
        extractor.extract("Skills: Python")


# ============================================================
# CV reference filtering tests
# ============================================================


def test_keeps_valid_cv_reference():
    cv_text = "Developed a forecasting model using LightGBM."

    analysis = CVAnalysis(
        skills=[
            SkillEvidence(
                skill="LightGBM",
                source=EvidenceSource.CV,
                evidence_type=EvidenceType.SELF_REPORTED,
                reference=("Developed a forecasting model using LightGBM."),
            )
        ]
    )

    result = filter_invalid_cv_references(
        analysis,
        cv_text,
    )

    assert len(result.skills) == 1
    assert result.skills[0].skill == "LightGBM"


def test_filters_missing_cv_reference():
    analysis = CVAnalysis(
        skills=[
            SkillEvidence(
                skill="Python",
                source=EvidenceSource.CV,
                evidence_type=EvidenceType.SELF_REPORTED,
                reference=None,
            )
        ]
    )

    result = filter_invalid_cv_references(
        analysis,
        "Skills: Python",
    )

    assert result.skills == []


def test_filters_fabricated_cv_reference():
    analysis = CVAnalysis(
        skills=[
            SkillEvidence(
                skill="PyTorch",
                source=EvidenceSource.CV,
                evidence_type=EvidenceType.SELF_REPORTED,
                reference="Experienced with PyTorch",
            )
        ]
    )

    result = filter_invalid_cv_references(
        analysis,
        "Skills: Python and SQL",
    )

    assert result.skills == []


def test_filters_invalid_cv_reference():
    analysis = CVAnalysis(
        skills=[
            SkillEvidence(
                skill="Retention Analysis",
                source=EvidenceSource.CV,
                evidence_type=EvidenceType.SELF_REPORTED,
                reference="A sentence that does not exist.",
            )
        ]
    )

    result = filter_invalid_cv_references(
        analysis,
        "Skills: Python",
    )

    assert result.skills == []


def test_preserves_valid_skills_when_one_reference_is_invalid():
    analysis = CVAnalysis(
        skills=[
            SkillEvidence(
                skill="Python",
                source=EvidenceSource.CV,
                evidence_type=EvidenceType.SELF_REPORTED,
                reference="Python",
            ),
            SkillEvidence(
                skill="Retention Analysis",
                source=EvidenceSource.CV,
                evidence_type=EvidenceType.SELF_REPORTED,
                reference="Nonexistent CV sentence",
            ),
        ],
        education=["BSc Computer Engineering"],
    )

    result = filter_invalid_cv_references(
        analysis,
        "BSc Computer Engineering. Skills: Python",
    )

    assert len(result.skills) == 1
    assert result.skills[0].skill == "Python"

    # Filtering must not remove unrelated CV information.
    assert result.education == ["BSc Computer Engineering"]

    # Filtering must not mutate the original analysis.
    assert len(analysis.skills) == 2


# ============================================================
# Prompt tests
# ============================================================


def test_cv_prompt_includes_all_relevant_sections():
    structured_model = PromptCaptureModel()

    extractor = CVExtractor(FakeModelWrapper(structured_model))

    extractor.extract("Relevant Coursework: Machine Learning, Data Mining")

    prompt = structured_model.last_prompt

    assert prompt is not None
    assert "Relevant Coursework" in prompt
    assert "Work Experience" in prompt
    assert "Projects" in prompt
    assert "Certifications" in prompt
    assert "high recall" in prompt.lower()


# ============================================================
# Gemini retry tests
# ============================================================


def test_cv_extractor_retries_temporary_gemini_errors():
    structured_model = TemporarilyUnavailableModel()

    extractor = CVExtractor(FakeModelWrapper(structured_model))

    result = extractor.extract("Skills: Python")

    assert isinstance(result, CVAnalysis)
    assert structured_model.attempts == 3
