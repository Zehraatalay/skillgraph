import pytest

from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.services.github_evidence_validator import (
    validate_github_evidence,
)
from agents.services.research_collector import CollectedFile


def make_evidence(
    reference="src/engine.py",
    snippet="import numpy as np",
    source=EvidenceSource.GITHUB,
    evidence_type=EvidenceType.IMPLEMENTATION,
):
    return SkillEvidence(
        skill="NumPy",
        source=source,
        evidence_type=evidence_type,
        reference=reference,
        code_snippet=snippet,
    )


def test_valid_github_evidence():
    files = [
        CollectedFile(
            path="src/engine.py",
            category="source",
            content="import numpy as np\n",
        )
    ]

    validate_github_evidence(
        [make_evidence()],
        files,
    )


def test_rejects_fabricated_snippet():
    files = [
        CollectedFile(
            path="src/engine.py",
            category="source",
            content="print('hello')",
        )
    ]

    with pytest.raises(ValueError, match="Code snippet not found"):
        validate_github_evidence(
            [make_evidence()],
            files,
        )


def test_rejects_unknown_file():
    with pytest.raises(ValueError, match="Unknown evidence file"):
        validate_github_evidence(
            [make_evidence()],
            [],
        )


def test_rejects_cv_source():
    files = [
        CollectedFile(
            path="src/engine.py",
            category="source",
            content="import numpy as np",
        )
    ]

    with pytest.raises(ValueError, match="Invalid evidence source"):
        validate_github_evidence(
            [
                make_evidence(
                    source=EvidenceSource.CV,
                )
            ],
            files,
        )


def test_rejects_test_file_as_implementation():
    files = [
        CollectedFile(
            path="tests/test_engine.py",
            category="test",
            content="import numpy as np",
        )
    ]

    with pytest.raises(ValueError, match="Implementation evidence"):
        validate_github_evidence(
            [
                make_evidence(
                    reference="tests/test_engine.py",
                )
            ],
            files,
        )


def test_rejects_tested_evidence_for_now():
    files = [
        CollectedFile(
            path="src/engine.py",
            category="source",
            content="import numpy as np",
        )
    ]

    with pytest.raises(ValueError, match="Unsupported evidence type"):
        validate_github_evidence(
            [
                make_evidence(
                    evidence_type=EvidenceType.TESTED,
                )
            ],
            files,
        )


def test_rejects_missing_reference():
    with pytest.raises(
        ValueError,
        match="Missing reference",
    ):
        validate_github_evidence(
            [make_evidence(reference=None)],
            [],
        )


def test_rejects_missing_code_snippet():
    files = [
        CollectedFile(
            path="src/engine.py",
            category="source",
            content="import numpy as np",
        )
    ]

    with pytest.raises(
        ValueError,
        match="Missing code snippet",
    ):
        validate_github_evidence(
            [make_evidence(snippet=None)],
            files,
        )
