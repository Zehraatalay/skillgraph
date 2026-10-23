"""CLI: scan a GitHub repository and output a non-mutating concept candidate report."""
import argparse
import json
from pathlib import Path

from app.ai.concept_detector import concept_report
from app.ai.repository_scanner import RepositoryScanner
from app.repositories.github_repository import GitHubRepository


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner', required=True)
    parser.add_argument('--repo', required=True)
    parser.add_argument('--report', required=True)
    parser.add_argument('--max-files', type=int, default=60)
    args = parser.parse_args()
    if not 1 <= args.max_files <= 100:
        parser.error('--max-files must be between 1 and 100')
    import re
    if not re.fullmatch(r'[A-Za-z0-9-]{1,39}', args.owner) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}', args.repo):
        parser.error('Invalid GitHub owner/repository')
    github = GitHubRepository()
    try:
        context = RepositoryScanner(github, max_files=args.max_files, max_total_chars=350_000).scan(args.owner, args.repo)
    finally:
        github.close()
    report = concept_report(context)
    target = Path(args.report)
    if target.exists():
        parser.error(f'Report already exists (refusing overwrite): {target}')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'repository': report['repository'], 'files_scanned': len(context.files),
                      'candidates': report['candidate_count'], 'report': str(target),
                      'status': 'REVIEW_REQUIRED', 'neo4j_writes': False}, indent=2))


if __name__ == '__main__':
    main()
