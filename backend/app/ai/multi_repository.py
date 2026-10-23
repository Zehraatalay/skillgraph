"""Multi-repository deterministic skill extraction with explicit review before import."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from app.ai.repository_scanner import RepositoryScanner
from app.ai.skill_profile import ValidatedSkillProfile
from app.ai.technology_detector import detect_technology_skills

_REPO = re.compile(r'^[A-Za-z0-9_.-]+$')


def analyze_repositories(github, owner: str, repositories: list[str], output_dir: Path, *, max_files: int = 40) -> dict:
    """Write one profile per repository; do not modify Neo4j.

    Explicit repository allowlist only. Failures are reported without interrupting
    other repositories. Existing output files are never silently overwritten.
    """
    if not owner or not _REPO.fullmatch(owner):
        raise ValueError('Invalid GitHub owner')
    if not 1 <= max_files <= 100:
        raise ValueError('max_files must be between 1 and 100')
    if not repositories:
        raise ValueError('At least one repository is required')
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    seen = set()
    scanner = RepositoryScanner(github, max_files=max_files, max_total_chars=250_000)
    for repo in repositories:
        if not _REPO.fullmatch(repo):
            raise ValueError(f'Invalid repository name: {repo!r}')
        if repo.casefold() in seen:
            continue
        seen.add(repo.casefold())
        target = output_dir / f'{owner}__{repo}.json'
        if target.exists():
            results.append({'repository': f'{owner}/{repo}', 'status': 'skipped_existing', 'profile': str(target)})
            continue
        try:
            context = scanner.scan(owner, repo)
            skills = detect_technology_skills(context)
            profile = ValidatedSkillProfile(
                developer=owner,
                repository=f'{owner}/{repo}',
                skills=skills,
                accepted_evidence_count=sum(s.evidence_count for s in skills),
                excluded_findings_count=0,
                excluded_by_decision={},
            )
            # A scan with no source files is not proof that a repository has no skills.
            if not context.files:
                results.append({'repository': f'{owner}/{repo}', 'status': 'empty_scan'})
                continue
            target.write_text(profile.model_dump_json(indent=2), encoding='utf-8')
            results.append({'repository': profile.repository, 'status': 'ok',
                            'files_scanned': len(context.files),
                            'skills': [s.name for s in skills],
                            'evidence_count': profile.accepted_evidence_count,
                            'profile': str(target)})
        except Exception as exc:
            results.append({'repository': f'{owner}/{repo}', 'status': 'error',
                            'error': f'{type(exc).__name__}: {exc}'})
    return {'developer': owner, 'results': results}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner', required=True)
    parser.add_argument('--repos', nargs='+', required=True, help='Explicit GitHub repository names')
    parser.add_argument('--output-dir', default='profiles-v9')
    parser.add_argument('--max-files', type=int, default=40)
    args = parser.parse_args()
    from app.repositories.github_repository import GitHubRepository
    github = GitHubRepository()
    try:
        report = analyze_repositories(github, args.owner, args.repos, Path(args.output_dir), max_files=args.max_files)
    finally:
        github.close()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print('DRY RUN ONLY: Review profiles; import selected profiles with app.ai.import_profile --apply.')


if __name__ == '__main__':
    main()
