import pytest

from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.schemas.github_extraction import (
    GitHubEvidenceExtraction,
)
from agents.services.github_evidence_extractor import (
    GitHubEvidenceExtractor,
)
from agents.services.research_collector import CollectedFile


class FakeStructuredLLM:
    def __init__(self, response):
        self.response = response
        self.messages = None

    def invoke(self, messages):
        self.messages = messages
        return self.response


class FakeLLM:
    def __init__(self, response):
        self.structured = FakeStructuredLLM(response)

    def with_structured_output(self, schema, method):
        assert schema is GitHubEvidenceExtraction
        assert method == "json_schema"
        return self.structured


def make_file(
    path="src/engine.py",
    category="source",
    content="import numpy as np",
):
    return CollectedFile(
        path=path,
        category=category,
        content=content,
    )


def make_skill(
    snippet="import numpy as np",
    reference="src/engine.py",
):
    return SkillEvidence(
        skill="NumPy",
        source=EvidenceSource.GITHUB,
        evidence_type=EvidenceType.IMPLEMENTATION,
        reference=reference,
        code_snippet=snippet,
    )


def test_extracts_valid_github_evidence():
    response = GitHubEvidenceExtraction(skills=[make_skill()])

    extractor = GitHubEvidenceExtractor(FakeLLM(response))

    result = extractor.extract([make_file()])

    assert len(result) == 1
    assert result[0].skill == "NumPy"


def test_rejects_fabricated_code():
    response = GitHubEvidenceExtraction(
        skills=[make_skill(snippet="import tensorflow as tf")]
    )

    extractor = GitHubEvidenceExtractor(FakeLLM(response))

    with pytest.raises(
        ValueError,
        match="Code snippet not found",
    ):
        extractor.extract([make_file()])


def test_returns_empty_for_no_source_files():
    response = GitHubEvidenceExtraction(skills=[make_skill()])

    llm = FakeLLM(response)

    extractor = GitHubEvidenceExtractor(llm)

    result = extractor.extract(
        [
            make_file(
                path="tests/test_engine.py",
                category="test",
            )
        ]
    )

    assert result == []
    assert llm.structured.messages is None


def test_rejects_unexpected_response():
    extractor = GitHubEvidenceExtractor(FakeLLM({"skills": []}))

    with pytest.raises(
        TypeError,
        match="Unexpected GitHub evidence extraction response",
    ):
        extractor.extract([make_file()])


def test_returns_empty_extraction():
    extractor = GitHubEvidenceExtractor(FakeLLM(GitHubEvidenceExtraction(skills=[])))

    result = extractor.extract([make_file()])

    assert result == []
