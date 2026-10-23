"""V9.3: conservative, source-backed review of V9.2.3 behavioral candidates.

No network calls, model inference, Neo4j writes or skill-profile mutations.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Any

LABELS = {
    'Conditional candidate enumeration': 'Conditional enumeration',
    'Copy-and-update state transformation': 'Copy-and-update transformation',
    'Executable behavioral assertions': 'Automated assertions',
    'Iterative best-candidate selection': 'Best-candidate selection',
    'Explicit cache lookup and update': 'Caching / memoization',
}


def _functions(tree: ast.AST):
    return [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def _nodes(fn: ast.AST):
    for stmt in fn.body:
        for node in ast.walk(stmt):
            if node is stmt or not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                yield node


def _call_name(call: ast.Call) -> str:
    return call.func.attr if isinstance(call.func, ast.Attribute) else call.func.id if isinstance(call.func, ast.Name) else ''


def _same_returned_copy(fn: ast.AST) -> bool:
    """Require a named copied object, its mutation, and its return."""
    copied = set()
    nodes = list(_nodes(fn))
    for node in nodes:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) and _call_name(node.value) in {'copy', 'deepcopy', 'replace'}:
            copied.update(t.id for t in node.targets if isinstance(t, ast.Name))
    if not copied:
        return False
    modified = set()
    for node in nodes:
        targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, (ast.AugAssign, ast.AnnAssign)) else []
        for target in targets:
            if isinstance(target, (ast.Subscript, ast.Attribute)) and isinstance(target.value, ast.Name):
                modified.add(target.value.id)
    returned = {node.value.id for node in nodes if isinstance(node, ast.Return) and isinstance(node.value, ast.Name)}
    return bool(copied & modified & returned)


def _conditional_collection(fn: ast.AST) -> bool:
    for loop in (n for n in _nodes(fn) if isinstance(n, (ast.For, ast.While))):
        for branch in (n for n in ast.walk(loop) if isinstance(n, ast.If)):
            if any(isinstance(c, ast.Call) and _call_name(c) in {'append', 'add'}
                   for stmt in branch.body for c in ast.walk(stmt)):
                return True
    return False


def _assertions(fn: ast.AST) -> bool:
    return any(isinstance(n, ast.Assert) or (isinstance(n, ast.Call) and _call_name(n) == 'raises') for n in _nodes(fn))


def _verify(concept: str, fn: ast.AST, path: str) -> tuple[str, str, str, str]:
    """Returns status, confidence, depth, explanation. Confidence is not proficiency."""
    if concept == 'Executable behavioral assertions':
        if _assertions(fn) and (Path(path).name.startswith('test_') or '/tests/' in '/' + path):
            return 'verified', 'high', 'basic', 'Executable assertion in a test module; does not establish test quality.'
        return 'review_required', 'medium', 'unknown', 'Assertion found, but test-module context is insufficient.'
    if concept == 'Copy-and-update state transformation':
        if _same_returned_copy(fn):
            return 'verified', 'high', 'basic', 'A copied object is modified and returned; domain-specific state semantics not proven.'
        return 'review_required', 'low', 'unknown', 'Copy, mutation, and return may refer to different objects.'
    if concept == 'Conditional candidate enumeration':
        if _conditional_collection(fn):
            return 'verified', 'high', 'basic', 'Conditional collection insertion occurs within iteration; legal-move semantics not proven.'
        return 'review_required', 'low', 'unknown', 'Loop/branch/append signals do not establish a filtered collection.'
    if concept == 'Explicit cache lookup and update':
        return 'rejected', 'low', 'unknown', 'Indexed reads and writes alone do not demonstrate reuse of previously computed results.'
    if concept == 'Iterative best-candidate selection':
        return 'review_required', 'low', 'unknown', 'Comparison and assignment alone do not establish argmax/argmin candidate tracking.'
    return 'review_required', 'low', 'unknown', 'Unknown behavior category.'


def review_report(report: dict[str, Any], source_root: Path | None = None) -> dict[str, Any]:
    if not isinstance(report.get('items'), list) or not isinstance(report.get('repository'), str):
        raise ValueError('Expected V9.2.3 report with repository and items.')
    results = []
    cache: dict[str, tuple[str, ast.AST] | None] = {}
    for item in report['items']:
        path = item.get('file', '')
        concept = item.get('concept', '')
        status, confidence, depth, reason = 'review_required', 'unassessed', 'unknown', 'Local source was not provided; cannot revalidate AST.'
        if source_root is not None:
            root = source_root.resolve()
            target = (root / path).resolve()
            if not path or not target.is_relative_to(root) or target.suffix != '.py':
                status, confidence, reason = 'rejected', 'low', 'Unsafe or non-Python source path.'
            else:
                if path not in cache:
                    try:
                        src = target.read_text(encoding='utf-8')
                        cache[path] = (src, ast.parse(src))
                    except (OSError, UnicodeError, SyntaxError, ValueError):
                        cache[path] = None
                entry = cache[path]
                if entry is None:
                    status, confidence, reason = 'review_required', 'unassessed', 'Source unavailable or unparseable.'
                else:
                    src, tree = entry
                    # The remote scan's line number is advisory: local checkouts may
                    # differ by comments/blank lines. Anchor the quote to the
                    # *named function body*, never just anywhere in the file.
                    quote = item.get('quote', '').strip()
                    anchor = quote.splitlines()[0].strip() if quote else ''
                    named = [f for f in _functions(tree) if f.name == item.get('function')]
                    matches = []
                    for f in named:
                        segment = ast.get_source_segment(src, f) or ''
                        if anchor and anchor in segment:
                            matches.append(f)
                    if len(matches) == 1:
                        fn = matches[0]
                        status, confidence, depth, reason = _verify(concept, fn, path)
                    elif len(matches) > 1:
                        status, confidence, reason = 'review_required', 'low', 'Ambiguous evidence: quote occurs in multiple same-named functions.'
                    elif not named:
                        status, confidence, reason = 'review_required', 'low', 'Named function absent from source.'
                    else:
                        status, confidence, reason = 'review_required', 'low', 'Evidence quote absent from the named function body.'
        results.append({**item, 'status': status, 'evidence_confidence': confidence,
                        'implementation_depth': depth, 'reason': reason,
                        'validated_concept': LABELS.get(concept, concept)})
    groups: dict[str, list[dict]] = defaultdict(list)
    for result in results:
        groups[result['validated_concept']].append(result)
    consolidated = []
    for concept, members in sorted(groups.items()):
        counts = Counter(m['status'] for m in members)
        consolidated.append({'concept': concept, 'status': 'verified' if counts['verified'] else 'review_required' if counts['review_required'] else 'rejected',
                             'candidate_count': len(members), 'verified_evidence_count': counts['verified'],
                             'files': sorted({m['file'] for m in members}),
                             'note': 'Verified here means a narrow AST behavior, NOT a domain skill or proficiency.'})
    return {'version': '9.3', 'repository': report['repository'], 'source_validation': source_root is not None,
            'counts': dict(Counter(r['status'] for r in results)), 'candidate_count': len(results),
            'concepts': consolidated, 'items': results, 'neo4j_writes': False,
            'warning': 'Do not import behavioral concepts into skill profiles or Neo4j automatically.'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--source-dir', help='Local checkout root of the analyzed repository (optional).')
    args = parser.parse_args()
    src, dst = Path(args.input), Path(args.output)
    if dst.exists():
        parser.error(f'Output exists: {dst}')
    data = review_report(json.loads(src.read_text(encoding='utf-8')), Path(args.source_dir) if args.source_dir else None)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open('x', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    print(json.dumps({'repository': data['repository'], 'candidate_count': data['candidate_count'],
                      'counts': data['counts'], 'source_validation': data['source_validation'],
                      'output': str(dst), 'neo4j_writes': False}, indent=2))


if __name__ == '__main__':
    main()
