"""Generate a review-only behavioral analysis report for one GitHub repository."""
import argparse
import json
import re
from pathlib import Path

from app.ai.behavior_detector import behavior_report
from app.ai.repository_scanner import RepositoryScanner
from app.repositories.github_repository import GitHubRepository


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner', required=True)
    parser.add_argument('--repo', required=True)
    parser.add_argument('--report', required=True)
    parser.add_argument('--max-files', type=int, default=80)
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9-]{1,39}', args.owner):
        parser.error('Invalid GitHub owner')
    if not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}', args.repo) or args.repo in {'.', '..'}:
        parser.error('Invalid repository')
    if not 1 <= args.max_files <= 100:
        parser.error('--max-files must be between 1 and 100')
    path = Path(args.report)
    if path.exists():
        parser.error(f'Report already exists: {path}')
    github = GitHubRepository()
    try:
        context = RepositoryScanner(github, max_files=args.max_files, max_total_chars=350_000).scan(args.owner, args.repo)
    finally:
        github.close()
    report = behavior_report(context)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as out:
        json.dump(report, out, ensure_ascii=False, indent=2)
    print(json.dumps({'repository': report['repository'], 'files_scanned': len(context.files),
                      'candidates': report['candidate_count'], 'report': str(path),
                      'status': 'REVIEW_REQUIRED', 'neo4j_writes': False}, indent=2))


if __name__ == '__main__':
    main()
