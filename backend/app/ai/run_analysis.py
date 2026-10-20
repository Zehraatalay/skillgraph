"""Run locally: python -m app.ai.run_analysis --owner Zehraatalay --repo stylematch"""
import argparse
from pathlib import Path
from app.repositories.github_repository import GitHubRepository
from app.ai.repository_scanner import RepositoryScanner
from app.ai.analyzer import analyze_repository
from app.ai.llm_client import LocalLLMClient


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--owner', default='Zehraatalay')
    parser.add_argument('--repo', default='stylematch')
    parser.add_argument('--model', default='llama3:latest')
    parser.add_argument('--max-files', type=int, default=6)
    parser.add_argument('--output', default='ai-analysis.json')
    parser.add_argument('--semantic-review', action='store_true', help='Run advisory LLM review on uncertain code claims')
    args = parser.parse_args()
    github = GitHubRepository()
    try:
        context = RepositoryScanner(github).scan(args.owner, args.repo)
    finally:
        github.close()
    result = analyze_repository(context, LocalLLMClient(model=args.model), max_files=args.max_files, semantic_review=args.semantic_review)
    output = Path(args.output)
    output.write_text(result.model_dump_json(indent=2), encoding='utf-8')
    print(f'Analyzed {len(result.files_analyzed)} files; {len(result.skills)} verified quotes; {result.rejected_evidence} rejected. Output: {output}')
    for item in result.skills:
        print(f'- {item.name}: {item.file}')
    for note in result.notes:
        print('NOTE:', note)


if __name__ == '__main__':
    main()
