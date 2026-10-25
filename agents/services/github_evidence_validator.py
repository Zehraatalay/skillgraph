from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.services.research_collector import CollectedFile


def validate_github_evidence(
    evidence: list[SkillEvidence],
    collected_files: list[CollectedFile],
) -> None:
    files_by_path = {file.path: file for file in collected_files}

    for item in evidence:
        if item.source != EvidenceSource.GITHUB:
            raise ValueError(f"Invalid evidence source: {item.source}")

        if item.evidence_type != EvidenceType.IMPLEMENTATION:
            raise ValueError(f"Unsupported evidence type: {item.evidence_type}")

        if not item.reference:
            raise ValueError(f"Missing reference for skill: {item.skill}")

        file = files_by_path.get(item.reference)

        if file is None:
            raise ValueError(f"Unknown evidence file: {item.reference}")

        if file.category != "source":
            raise ValueError(
                f"Implementation evidence must reference source code: {item.reference}"
            )

        if not item.code_snippet:
            raise ValueError(f"Missing code snippet for skill: {item.skill}")

        if item.code_snippet not in file.content:
            raise ValueError(f"Code snippet not found for skill: {item.skill}")
