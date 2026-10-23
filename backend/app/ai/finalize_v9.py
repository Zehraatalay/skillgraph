"""V9 final: explicitly curated, source-backed semantic skill additions. No DB writes."""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

from app.ai.profile_merger import merge_profile_skills
from app.ai.skill_profile import ProfileSkill, SkillEvidence, ValidatedSkillProfile

RULES = {
    'Legal Move Enumeration': [('src/match3_ai/games/match3/moves.py', 'find_valid_moves', 'Conditional candidate enumeration')],
    'Game State Transformation': [
        ('src/match3_ai/games/match3/mechanics.py', 'clear_matches', 'Copy-and-update state transformation'),
        ('src/match3_ai/games/match3/mechanics.py', 'apply_gravity', 'Copy-and-update state transformation'),
        ('src/match3_ai/games/match3/mechanics.py', 'refill_board', 'Copy-and-update state transformation'),
    ],
}


def _function(root: Path, rel: str, name: str):
    base = root.resolve()
    path = (base / rel).resolve()
    if not path.is_relative_to(base) or path.suffix != '.py':
        raise ValueError('Unsafe source path')
    source = path.read_text(encoding='utf-8')
    tree = ast.parse(source)
    funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name]
    if len(funcs) != 1:
        raise ValueError(f'Expected one function {rel}:{name}, found {len(funcs)}')
    return source, funcs[0]


def _structural_check(skill: str, fn: ast.AST) -> bool:
    nodes = list(ast.walk(fn))
    if skill == 'Legal Move Enumeration':
        calls = [n for n in nodes if isinstance(n, ast.Call)]
        return (any(isinstance(n, (ast.For, ast.While)) for n in nodes)
                and any(isinstance(n, ast.If) for n in nodes)
                and any(isinstance(c.func, ast.Name) and c.func.id == 'is_valid_swap' for c in calls)
                and any(isinstance(c.func, ast.Attribute) and c.func.attr == 'append' for c in calls))
    if skill == 'Game State Transformation':
        from app.ai.validate_behaviors import _same_returned_copy
        return _same_returned_copy(fn)
    if skill == 'Automated Testing':
        from app.ai.validate_behaviors import _assertions
        return _assertions(fn)
    return False


def _evidence(repository: str, rel: str, source: str, fn: ast.AST, skill: str) -> SkillEvidence:
    # Signature is exact, auditable source evidence. Structural behavior checked separately.
    quote = source.splitlines()[fn.lineno - 1].strip()
    return SkillEvidence(repository=repository, file=rel, quote=quote,
                         evidence_type='ast_semantic_curated',
                         decision_reason=f'V9 curated rule for {skill}; function AST revalidated against local source.',
                         explanation='Conservative implementation evidence; not a proficiency rating.')


def finalize(profile: ValidatedSkillProfile, reviewed: dict, source_root: Path):
    if profile.repository != reviewed.get('repository') or not reviewed.get('source_validation'):
        raise ValueError('Profile/review repository mismatch or review lacks source validation')
    if profile.repository != 'Zehraatalay/match3-ai-lab':
        raise ValueError('V9 final curated rules currently cover only Zehraatalay/match3-ai-lab')
    verified = {(x.get('file'), x.get('function'), x.get('concept')) for x in reviewed.get('items', [])
                if x.get('status') == 'verified'}
    additions = []
    audit = []
    for skill, requirements in RULES.items():
        ev = []
        checks = []
        for rel, fn_name, concept in requirements:
            report_ok = (rel, fn_name, concept) in verified
            try:
                source, fn = _function(source_root, rel, fn_name)
                ast_ok = _structural_check(skill, fn)
            except (OSError, ValueError, SyntaxError):
                ast_ok = False
            checks.append({'file': rel, 'function': fn_name, 'review_verified': report_ok, 'ast_valid': ast_ok})
            if report_ok and ast_ok:
                ev.append(_evidence(profile.repository, rel, source, fn, skill))
        # All rule components required; no partial promotion.
        accepted = len(ev) == len(requirements)
        audit.append({'skill': skill, 'status': 'accepted' if accepted else 'review_required', 'checks': checks})
        if accepted:
            additions.append(ProfileSkill(name=skill, category='concept', evidence_count=len(ev), evidence=ev))

    # Tests are consolidated: require >=2 distinct verified test functions with actual assertions.
    test_evidence = []
    seen = set()
    for item in reviewed.get('items', []):
        rel, name = item.get('file', ''), item.get('function', '')
        if (item.get('status') != 'verified' or item.get('concept') != 'Executable behavioral assertions'
                or (rel, name) in seen or not (Path(rel).name.startswith('test_') or '/tests/' in '/' + rel)):
            continue
        seen.add((rel, name))
        try:
            source, fn = _function(source_root, rel, name)
            if _structural_check('Automated Testing', fn):
                test_evidence.append(_evidence(profile.repository, rel, source, fn, 'Automated Testing'))
        except (OSError, ValueError, SyntaxError):
            continue
    test_evidence.sort(key=lambda e: (e.file, e.quote))
    test_accepted = len(test_evidence) >= 2
    audit.append({'skill': 'Automated Testing', 'status': 'accepted' if test_accepted else 'review_required',
                  'verified_distinct_test_functions': len(test_evidence)})
    if test_accepted:
        additions.append(ProfileSkill(name='Automated Testing', category='concept',
                                      evidence_count=len(test_evidence), evidence=test_evidence))
    merged = merge_profile_skills(profile, additions)
    return merged, {'repository': profile.repository, 'accepted_skills': [s.name for s in additions],
                    'audit': audit, 'neo4j_writes': False,
                    'warning': 'Source-backed narrow skills; no algorithm expertise/proficiency claim.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ('input', 'reviewed', 'source_dir', 'output', 'audit'):
        p.add_argument('--' + arg.replace('_', '-'), required=True)
    args = p.parse_args()
    output, audit_path = Path(args.output), Path(args.audit)
    if output.exists() or audit_path.exists():
        p.error('Output or audit already exists; use new paths to preserve prior results')
    profile = ValidatedSkillProfile.model_validate_json(Path(args.input).read_text(encoding='utf-8'))
    reviewed = json.loads(Path(args.reviewed).read_text(encoding='utf-8'))
    merged, report = finalize(profile, reviewed, Path(args.source_dir))
    output.parent.mkdir(parents=True, exist_ok=True)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(merged.model_dump_json(indent=2), encoding='utf-8')
    audit_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({'output': str(output), 'audit': str(audit_path),
                      'accepted_skills': report['accepted_skills'],
                      'total_skills': len(merged.skills), 'total_evidence': merged.accepted_evidence_count,
                      'neo4j_writes': False}, indent=2))


if __name__ == '__main__':
    main()
