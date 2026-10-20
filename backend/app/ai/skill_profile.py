"""Build a read-only, evidence-backed skill profile from AIAnalysis.

Only accepted findings are eligible. This module performs no database writes.
"""
from collections import defaultdict
from pydantic import BaseModel, Field

from app.ai.analyzer import AIAnalysis


class SkillEvidence(BaseModel):
    repository: str
    file: str
    quote: str
    evidence_type: str
    decision_reason: str
    explanation: str


class ProfileSkill(BaseModel):
    name: str
    category: str
    evidence_count: int
    evidence: list[SkillEvidence]


class ValidatedSkillProfile(BaseModel):
    developer: str
    repository: str
    skills: list[ProfileSkill]
    accepted_evidence_count: int
    excluded_findings_count: int
    excluded_by_decision: dict[str, int] = Field(default_factory=dict)


def build_skill_profile(analysis: AIAnalysis) -> ValidatedSkillProfile:
    """Aggregate accepted findings by normalized name, retaining file-level provenance.

    An accepted finding is evidence of code usage, not proof of proficiency.
    """
    if '/' not in analysis.repository:
        raise ValueError('Expected repository in owner/repository format')
    developer, _ = analysis.repository.split('/', 1)
    if not developer:
        raise ValueError('Repository owner must not be empty')

    groups = defaultdict(list)
    categories = {}
    excluded = defaultdict(int)
    seen = set()
    for finding in analysis.skills:
        if finding.decision != 'accept':
            excluded[finding.decision] += 1
            continue
        # Keep separate evidence from different files; dedupe identical source quotes.
        key = (finding.name.casefold(), finding.file, finding.quote)
        if key in seen:
            continue
        seen.add(key)
        canonical = finding.name.strip()
        groups[canonical].append(SkillEvidence(
            repository=analysis.repository,
            file=finding.file,
            quote=finding.quote,
            evidence_type=finding.evidence_type,
            decision_reason=finding.decision_reason,
            explanation=finding.explanation,
        ))
        categories.setdefault(canonical, finding.category)

    skills = [
        ProfileSkill(
            name=name,
            category=categories[name],
            evidence_count=len(evidences),
            evidence=sorted(evidences, key=lambda e: (e.file, e.quote)),
        )
        for name, evidences in sorted(groups.items(), key=lambda item: item[0].casefold())
    ]
    return ValidatedSkillProfile(
        developer=developer,
        repository=analysis.repository,
        skills=skills,
        accepted_evidence_count=sum(s.evidence_count for s in skills),
        excluded_findings_count=sum(excluded.values()),
        excluded_by_decision=dict(sorted(excluded.items())),
    )
