"""V10.4: ephemeral public GitHub + private ZIP profile aggregation.

No persistence, no remote LLM calls, no proficiency inference.
"""
from __future__ import annotations
from collections import defaultdict


def combine_analysis(public: dict | None, private: list[dict] | None = None) -> dict:
    """Aggregate server-generated V10.2/V10.3 responses; never trust client evidence."""
    private = private or []
    if public is not None and public.get('analysis_type') != 'ast_technology_usage':
        raise ValueError('Unsupported public analysis type')
    for item in private:
        if item.get('source_type') != 'zip_upload' or item.get('visibility') != 'private' or item.get('analysis_type') != 'ast_technology_usage':
            raise ValueError('Unsupported private analysis type')
    buckets = defaultdict(dict)
    sources = []
    if public is not None:
        for repo in public.get('repositories', []):
            sources.append({'source_id': repo['repository'], 'source_type': 'github_public', 'visibility': 'public', 'status': repo['status']})
        for skill in public.get('skills', []):
            for evidence in skill.get('evidence_samples', []):
                _add(buckets, skill['name'], evidence)
    for item in private:
        source_id = 'private/' + item['project_id']
        sources.append({'source_id': source_id, 'source_type': 'zip_upload', 'visibility': 'private', 'status': 'ok'})
        for skill in item.get('skills', []):
            for evidence in skill.get('evidence_samples', []):
                _add(buckets, skill['name'], evidence)
    # V10.2 and V10.3 cap evidence samples to 3 per skill. Preserve this
    # distinction: never misreport sample counts as full evidence totals.
    skills = []
    for name, items in sorted(buckets.items()):
        evidence = list(items.values())
        skills.append({'name': name, 'sample_count': len(evidence),
                       'source_count': len({e['repository'] for e in evidence}),
                       'source_ids': sorted({e['repository'] for e in evidence}),
                       'evidence_samples': evidence})
    return {'analysis_type': 'ast_technology_usage', 'skills': skills, 'sources': sources,
            'source_count': len(sources), 'skill_count': len(skills),
            'evidence_scope': 'samples_only_max_3_per_skill_per_source',
            'neo4j_writes': False, 'persisted': False,
            'note': 'Ephemeral source-backed technology usage, not a proficiency assessment. No V9.4 semantic finalization.'}


def _add(buckets, name, evidence):
    if not isinstance(evidence, dict):
        return
    repo = evidence.get('repository')
    path = evidence.get('file')
    quote = evidence.get('quote')
    if not all(isinstance(v, str) and v for v in (repo, path, quote)):
        return
    key = (repo, path, quote, evidence.get('evidence_type', ''))
    buckets[name][key] = evidence
