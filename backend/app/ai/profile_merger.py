"""Merge validated profiles and deterministic technology evidence without graph writes."""
from __future__ import annotations

from app.ai.skill_profile import ProfileSkill, ValidatedSkillProfile


def merge_profile_skills(profile: ValidatedSkillProfile, additions: list[ProfileSkill]) -> ValidatedSkillProfile:
    grouped: dict[str, tuple[str, str, dict[tuple[str, str], object]]] = {}
    for skill in [*profile.skills, *additions]:
        key = skill.name.strip().casefold()
        if not key:
            raise ValueError('Blank skill name')
        if key not in grouped:
            grouped[key] = (skill.name.strip(), skill.category, {})
        name, category, evidence_map = grouped[key]
        for evidence in skill.evidence:
            if evidence.repository != profile.repository:
                raise ValueError('Cannot merge evidence from another repository')
            evidence_map.setdefault((evidence.file, evidence.quote), evidence)
    skills = [ProfileSkill(name=name, category=category, evidence_count=len(evidence_map),
                           evidence=sorted(evidence_map.values(), key=lambda e: (e.file, e.quote)))
              for _, (name, category, evidence_map) in sorted(grouped.items())]
    return profile.model_copy(update={
        'skills': skills,
        'accepted_evidence_count': sum(s.evidence_count for s in skills),
    })
