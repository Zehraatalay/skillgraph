"""V9.2.1 CLI: create an augmented profile and a separate evidence quality report."""
import argparse
import json
from pathlib import Path

from app.ai.evidence_intelligence import build_quality_report, detect_additional_technologies
from app.ai.profile_merger import merge_profile_skills
from app.ai.repository_scanner import RepositoryScanner
from app.ai.skill_profile import ValidatedSkillProfile
from app.repositories.github_repository import GitHubRepository


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--report', required=True)
    parser.add_argument('--max-files', type=int, default=40)
    args = parser.parse_args()
    if args.max_files < 1:
        parser.error('--max-files must be positive')
    destinations = [Path(args.input).resolve(), Path(args.output).resolve(), Path(args.report).resolve()]
    if len(set(destinations)) != 3:
        parser.error('Input, output and report must be different paths')
    profile = ValidatedSkillProfile.model_validate_json(Path(args.input).read_text(encoding='utf-8'))
    owner, repo = profile.repository.split('/', 1)
    github = GitHubRepository()
    try:
        context = RepositoryScanner(github, max_files=args.max_files, max_total_chars=250_000).scan(owner, repo)
    finally:
        github.close()
    additions = detect_additional_technologies(context)
    merged = merge_profile_skills(profile, additions)
    report = build_quality_report(merged, context)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(merged.model_dump_json(indent=2), encoding='utf-8')
    Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'repository': profile.repository, 'files_scanned': len(context.files),
                      'new_technologies': [s.name for s in additions],
                      'skills': len(merged.skills), 'evidence': merged.accepted_evidence_count,
                      'profile': args.output, 'report': args.report}, indent=2))
    print('DRY RUN: No Neo4j writes. Quality report does not affect matching scores.')


if __name__ == '__main__':
    main()
