"""Shared V9 AST usage detector for public GitHub and private ZIP inputs."""
from app.ai.technology_detector import detect_technology_skills
from app.ai.evidence_intelligence import detect_additional_technologies
from app.ai.skill_profile import ProfileSkill


def detect_usage(context) -> list[ProfileSkill]:
    grouped = {}
    for skill in [*detect_technology_skills(context), *detect_additional_technologies(context)]:
        key = skill.name.casefold()
        if key not in grouped:
            grouped[key] = (skill.name, skill.category, {})
        evidence = grouped[key][2]
        for item in skill.evidence:
            evidence.setdefault((item.repository, item.file, item.quote), item)
    return [ProfileSkill(name=name, category=category, evidence_count=len(items),
                         evidence=sorted(items.values(), key=lambda x:(x.file,x.quote)))
            for _,(name,category,items) in sorted(grouped.items())]
