"""Preview a validated skill profile; --apply explicitly writes to Neo4j."""
import argparse
import json
from pathlib import Path

from app.ai.graph_import import apply_import_plan, make_import_plan
from app.ai.skill_profile import ValidatedSkillProfile


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, help='Path to V6 skill-profile.json')
    parser.add_argument('--apply', action='store_true', help='Write to the configured Neo4j database')
    args = parser.parse_args()
    profile = ValidatedSkillProfile.model_validate_json(Path(args.input).read_text(encoding='utf-8'))
    plan = make_import_plan(profile)
    print(json.dumps({'developer': plan.developer, 'repository': plan.repository,
                      'skills': [row['name'] for row in plan.skills],
                      'skill_count': len(plan.skills), 'evidence_count': len(plan.evidence),
                      'mode': 'APPLY' if args.apply else 'DRY_RUN'}, ensure_ascii=False, indent=2))
    if not args.apply:
        print('Dry run: no Neo4j connection or writes. Use --apply only after reviewing this output.')
        return
    from app.repositories.neo4j_repository import Neo4jRepository
    db = Neo4jRepository()
    try:
        print('Import result:', apply_import_plan(plan, db))
    finally:
        db.close()


if __name__ == '__main__':
    main()
