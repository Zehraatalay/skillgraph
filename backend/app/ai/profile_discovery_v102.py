"""V10.2: public GitHub discovery and bounded, read-only profile analysis.

This stage intentionally runs V9 AST technology extraction, NOT the V9.4
repository-specific curated behavior finalizer. No LLM/Neo4j writes.
"""
from __future__ import annotations
import re
from collections import defaultdict
from app.ai.repository_scanner import RepositoryScanner
from app.ai.technology_usage_v103 import detect_usage

_NAME = re.compile(r"^[A-Za-z0-9_.-]{1,100}$")


def validate_name(value: str) -> str:
    if not _NAME.fullmatch(value) or value in {'.', '..'}:
        raise ValueError('Invalid GitHub username or repository name')
    return value


def discover(github, username: str, *, include_forks: bool = False, max_results: int = 100) -> dict:
    validate_name(username)
    if not 1 <= max_results <= 100:
        raise ValueError('max_results must be 1..100')
    raw = github.get_user_repositories(username)
    # Public profile endpoint: never expose private repositories here.
    eligible = []
    for repo in raw:
        if not isinstance(repo, dict) or repo.get('private') is not False:
            continue
        if repo.get('fork') and not include_forks:
            continue
        name = repo.get('name', '')
        try:
            validate_name(name)
        except (ValueError, TypeError):
            continue
        eligible.append({'name': name, 'description': repo.get('description') or '',
                         'language': repo.get('language'), 'fork': bool(repo.get('fork')),
                         'size_kb': repo.get('size', 0), 'updated_at': repo.get('updated_at'),
                         'html_url': repo.get('html_url')})
    return {'username': username, 'total_public_eligible': len(eligible),
            'repositories': eligible[:max_results], 'truncated': len(eligible) > max_results}


def analyze_selected(github, username: str, repositories: list[str], *, max_files: int = 40) -> dict:
    validate_name(username)
    if not repositories or len(repositories) > 5:
        raise ValueError('Select between 1 and 5 repositories per request')
    if not 1 <= max_files <= 40:
        raise ValueError('max_files must be 1..40')
    # Selection must come from the public profile; do not accept arbitrary
    # repo names that could be accessible through a privileged GitHub token.
    allowed = {r['name'].casefold(): r['name'] for r in discover(github, username, include_forks=True, max_results=100)['repositories']}
    selected = []
    seen = set()
    for name in repositories:
        validate_name(name)
        if name.casefold() not in allowed:
            raise ValueError(f'Repository not present in public discovery: {name}')
        if name.casefold() not in seen:
            selected.append(allowed[name.casefold()]); seen.add(name.casefold())
    scanner = RepositoryScanner(github, max_files=max_files, max_total_chars=250_000)
    results = []
    combined = defaultdict(list)
    for repo in selected:
        try:
            context = scanner.scan(username, repo)
            if not context.files:
                results.append({'repository': f'{username}/{repo}', 'status': 'empty_scan', 'skills': []})
                continue
            skills = detect_usage(context)
            results.append({'repository': f'{username}/{repo}', 'status': 'ok',
                            'files_scanned': len(context.files), 'skipped_files': context.skipped_files,
                            'skills': [{'name': s.name, 'evidence_count': s.evidence_count} for s in skills]})
            for skill in skills:
                combined[skill.name].extend(e.model_dump() for e in skill.evidence)
        except Exception as exc:
            # Do not expose exception internals (may contain credentials/paths).
            results.append({'repository': f'{username}/{repo}', 'status': 'error',
                            'error_type': type(exc).__name__, 'skills': []})
    summary = [{'name': name, 'repositories': sorted({e['repository'] for e in evidence}),
                'evidence_count': len(evidence), 'evidence_samples': evidence[:3]}
               for name, evidence in sorted(combined.items())]
    return {'username': username, 'analysis_type': 'ast_technology_usage',
            'note': 'Source-backed technology usage only; not a proficiency assessment. Repository-specific V9.4 semantic finalization is not run.',
            'repositories': results, 'skills': summary, 'neo4j_writes': False}
