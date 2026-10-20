"""CLI: scan public GitHub code, add deterministic technology evidence to V6 profile.

Example: python -m app.ai.augment_profile --input skill-profile.json --output skill-profile-v8-1.json
"""
import argparse
from pathlib import Path

from app.ai.profile_merger import merge_profile_skills
from app.ai.repository_scanner import RepositoryScanner
from app.ai.skill_profile import ValidatedSkillProfile
from app.ai.technology_detector import detect_technology_skills
from app.repositories.github_repository import GitHubRepository


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--max-files', type=int, default=40)
    args = parser.parse_args()
    profile = ValidatedSkillProfile.model_validate_json(Path(args.input).read_text(encoding='utf-8'))
    owner, repo = profile.repository.split('/', 1)
    github = GitHubRepository()
    try:
        context = RepositoryScanner(github, max_files=args.max_files, max_total_chars=250_000).scan(owner, repo)
    finally:
        github.close()
    additions = detect_technology_skills(context)
    merged = merge_profile_skills(profile, additions)
    Path(args.output).write_text(merged.model_dump_json(indent=2), encoding='utf-8')
    print(f'Scanned {len(context.files)} files; detected {[s.name for s in additions]}')
    print(f'Profile: {len(merged.skills)} skills, {merged.accepted_evidence_count} evidence -> {args.output}')


if __name__ == '__main__':
    main()
