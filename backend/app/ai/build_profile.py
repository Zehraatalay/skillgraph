"""Convert a saved AI analysis JSON into a validated skill profile JSON.

Usage: python -m app.ai.build_profile --input ai-analysis-v5.json --output skill-profile.json
"""
import argparse
from pathlib import Path
from app.ai.analyzer import AIAnalysis
from app.ai.skill_profile import build_skill_profile


def main():
    parser = argparse.ArgumentParser(description='Build a validated skill profile from an AI analysis')
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    analysis = AIAnalysis.model_validate_json(args.input.read_text(encoding='utf-8'))
    profile = build_skill_profile(analysis)
    args.output.write_text(profile.model_dump_json(indent=2) + '\n', encoding='utf-8')
    print(f'{profile.developer}: {len(profile.skills)} unique skills, '
          f'{profile.accepted_evidence_count} accepted evidence, '
          f'{profile.excluded_findings_count} excluded findings. Output: {args.output}')


if __name__ == '__main__':
    main()
