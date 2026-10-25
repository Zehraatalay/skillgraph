"""Evidence-only, weighted job coverage. No LLM or network calls in scoring."""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.jobs.skill_registry import normalize_skill, normalize_skill_text

MAX_EVIDENCE_PER_SKILL = 3


def canonical(value: str) -> str:
    return normalize_skill(value) or normalize_skill_text(value)


def fetch_verified_evidence(db: Any, username: str) -> list[dict]:
    """Read only evidence connected to repositories owned by the developer."""
    return db.run_query('''
        MATCH (d:Developer)-[:OWNS]->(r:Repository)-[:HAS_EVIDENCE]->
              (e:SkillEvidence)-[:SUPPORTS]->(s:Skill)
        WHERE toLower(d.login) = toLower($username)
          AND e.repository = r.full_name
        RETURN s.name AS skill, r.full_name AS repository,
               e.evidence_id AS evidence_id, e.file AS file,
               e.quote AS quote, e.evidence_type AS evidence_type,
               e.explanation AS explanation
        ORDER BY s.name, r.full_name, e.file, e.evidence_id
    ''', {'username': username})


def _group_evidence(rows: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    seen: set[tuple[str, str]] = set()
    for row in rows:
        name = row.get('skill')
        if not isinstance(name, str) or not name.strip():
            continue
        key = canonical(name)
        evidence_id = row.get('evidence_id')
        if not evidence_id or (key, evidence_id) in seen:
            continue
        seen.add((key, evidence_id))
        grouped[key].append({field: row.get(field) for field in (
            'evidence_id', 'repository', 'file', 'quote', 'evidence_type', 'explanation'
        )})
    for items in grouped.values():
        items.sort(key=lambda e: (str(e['repository']), str(e['file']), str(e['evidence_id'])))
    return dict(grouped)


def _requirements(items: list[dict]) -> dict[str, float]:
    result: dict[str, float] = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get('name'), str) or not item['name'].strip():
            raise ValueError('Invalid job skill entry')
        name = canonical(item['name'])
        weight = float(item.get('weight', 1.0))
        if not 0 < weight <= 1:
            raise ValueError(f'Invalid skill weight for {name}')
        result[name] = max(weight, result.get(name, 0.0))
    return result


def _evidence_priority(item: dict) -> tuple:
    """Prefer attributable API usage and meaningful Python definitions over constants."""
    kind = item.get('evidence_type')
    quote = str(item.get('quote') or '').strip()
    if kind == 'ast_api_usage':
        tier = 0
    elif kind == 'ast_source_usage':
        tier = 1 if quote.startswith(('def ', 'async def ', 'class ')) else 2
    else:
        tier = 0  # Already validated AI evidence; do not demote it.
    return (tier, str(item.get('repository') or ''), str(item.get('file') or ''),
            str(item.get('evidence_id') or ''))


def score_job(job: dict, evidence: dict[str, list[dict]]) -> dict:
    required = _requirements(job.get('required_skills') or [])
    preferred = _requirements(job.get('preferred_skills') or [])

    def coverage(group: dict[str, float]) -> float | None:
        if not group:
            return None
        return sum(w for name, w in group.items() if evidence.get(name)) / sum(group.values())

    cr, cp = coverage(required), coverage(preferred)
    if cr is None and cp is None:
        score = 0.0
    elif cr is None:
        score = 100 * cp
    elif cp is None:
        score = 100 * cr
    else:
        score = 100 * (0.8 * cr + 0.2 * cp)

    def details(group: dict[str, float]) -> tuple[list[dict], list[str]]:
        verified = []
        for name, weight in sorted(group.items()):
            if not evidence.get(name):
                continue
            items = evidence[name]
            verified.append({
                'name': name,
                'weight': weight,
                'evidence_count': len(items),
                'evidence': sorted(items, key=_evidence_priority)[:MAX_EVIDENCE_PER_SKILL],
            })
        unverified = sorted(name for name in group if not evidence.get(name))
        return verified, unverified

    vr, ur = details(required)
    vp, up = details(preferred)
    return {
        'job_id': job['job_id'], 'title': job['title'],
        'role_family': job['role_family'], 'seniority': job['seniority'],
        'technology_stack_id': job['technology_stack_id'],
        'verified_skill_coverage_score': round(score, 2),
        'required_coverage': None if cr is None else round(cr, 4),
        'preferred_coverage': None if cp is None else round(cp, 4),
        'verified_required_skills': vr, 'unverified_required_skills': ur,
        'verified_preferred_skills': vp, 'unverified_preferred_skills': up,
    }


def rank_jobs(jobs: list[dict], rows: list[dict], limit: int) -> dict:
    evidence = _group_evidence(rows)
    matches = [score_job(job, evidence) for job in jobs]
    matches.sort(key=lambda m: (-m['verified_skill_coverage_score'],
                                -len(m['verified_required_skills']), m['job_id']))
    return {'verified_skills': sorted(evidence), 'verified_skill_count': len(evidence),
            'total_jobs_evaluated': len(jobs), 'matches': matches[:limit]}
