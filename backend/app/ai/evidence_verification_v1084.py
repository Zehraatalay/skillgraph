"""V10.8.4 conservative, read-only verification of narrowly recognizable claims.

A supported check proves only the stated syntactic property, never runtime correctness.
"""
from __future__ import annotations

import ast
import re
from copy import deepcopy

STATUSES = {'supported', 'contradicted', 'insufficient_evidence', 'not_machine_verifiable'}


def _parse(source: str):
    try:
        return ast.parse(source)
    except (SyntaxError, ValueError, TypeError):
        return None


def _find_method(tree: ast.AST, cls: str, method: str):
    for node in getattr(tree, 'body', []):
        if isinstance(node, ast.ClassDef) and node.name == cls:
            return next((n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == method), None)
    return None


def _test_assertions(tree: ast.AST, name: str):
    for node in getattr(tree, 'body', []):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return [n.test for n in ast.walk(node) if isinstance(n, ast.Assert)]
    return None


def _result(status: str, method: str, reason: str, *, file: str | None = None, line: int | None = None):
    return {'status': status, 'method': method, 'reason': reason, 'file': file, 'line': line,
            'runtime_verified': False}


def verify_finding(finding: dict, packet: dict, files: dict[str, str]) -> dict:
    """Check only explicitly recognized claims; otherwise abstain.

    Never treat the presence of an evidence ID as proof that its claim is true.
    """
    explanation = finding.get('explanation', '')
    if not isinstance(explanation, str):
        return _result('not_machine_verifiable', 'none', 'No textual claim to inspect')
    evidence = {e.get('id'): e for e in packet.get('evidence', []) if isinstance(e, dict)}
    refs = finding.get('evidence_ids', [])
    if not isinstance(refs, list) or not refs or any(r not in evidence for r in refs):
        return _result('insufficient_evidence', 'evidence_reference', 'Missing or invalid evidence reference')
    cited = [evidence[r] for r in refs]
    if any(e.get('complete_function') is not True for e in cited):
        return _result('insufficient_evidence', 'context_completeness', 'At least one cited function is incomplete')

    # Narrow rule: claim that missing/undefined max_cascades permits an infinite loop.
    if re.search(r'\bmax_cascades\b', explanation, re.I) and re.search(r'\b(not set|undefined|no default|not defined|infinite loop)\b', explanation, re.I):
        target = packet.get('target', {})
        path = target.get('file')
        tree = _parse(files.get(path, ''))
        if tree is None:
            return _result('insufficient_evidence', 'constructor_ast', 'Target source unavailable or unparsable', file=path)
        cls = target.get('symbol', '').split('.')[0]
        init = _find_method(tree, cls, '__init__')
        if init is None:
            return _result('insufficient_evidence', 'constructor_ast', 'Constructor unavailable', file=path)
        args = init.args.posonlyargs + init.args.args
        defaults = dict(zip((a.arg for a in args[-len(init.args.defaults):]), init.args.defaults)) if init.args.defaults else {}
        if 'max_cascades' in defaults:
            value = defaults['max_cascades']
            if isinstance(value, ast.Constant) and isinstance(value.value, int) and value.value > 0:
                return _result('contradicted', 'constructor_ast',
                               f'max_cascades has a positive default ({value.value}); missing-default premise is false. This does not prove termination.',
                               file=path, line=init.lineno)
        return _result('insufficient_evidence', 'constructor_ast', 'No simple positive default found; termination cannot be inferred', file=path, line=init.lineno)

    # Narrow rule: claim a named test does not assert ANY final no-match check.
    if 'test_valid_swap_resolves_matches' in explanation and re.search(r'(does not|doesn.t|only checks|not verify)', explanation, re.I):
        return _check_test(cited, files, 'test_valid_swap_resolves_matches', 'patterns')

    # Narrow rule: claim a named test does not compare the state at all.
    if 'test_invalid_swap_does_not_change_state' in explanation and re.search(r'(does not|doesn.t|only checks|not verify)', explanation, re.I):
        return _check_test(cited, files, 'test_invalid_swap_does_not_change_state', 'state')

    # No general-purpose natural language verifier: these are unproven hypotheses.
    if 'clear_board_matches' in explanation and 'empty' in explanation.lower():
        return _result('insufficient_evidence', 'call_path', 'Empty-match call reachability is not established')
    if 'apply_board_gravity' in explanation and 'playable_rows' in explanation:
        return _result('insufficient_evidence', 'control_flow', 'Copy is outside the column loop; whether an empty column makes the copy unnecessary is not established')
    return _result('not_machine_verifiable', 'none', 'No safe deterministic rule matches this claim')


def _check_test(cited: list[dict], files: dict[str, str], name: str, kind: str) -> dict:
    for ev in cited:
        if ev.get('symbol') != name:
            continue
        path = ev.get('file')
        tree = _parse(files.get(path, ''))
        if tree is None:
            return _result('insufficient_evidence', 'test_ast', 'Test source unavailable', file=path)
        assertions = _test_assertions(tree, name)
        if assertions is None:
            return _result('insufficient_evidence', 'test_ast', 'Named test not found', file=path)
        for assertion in assertions:
            if kind == 'patterns' and isinstance(assertion, ast.Compare):
                expr = ast.unparse(assertion)
                if 'detect_patterns(' in expr and ('== []' in expr or '[] ==' in expr):
                    return _result('contradicted', 'test_assertion_ast', 'Test explicitly asserts no patterns remain after the step', file=path, line=assertion.lineno)
            if kind == 'state':
                expr = ast.unparse(assertion)
                if 'array_equal(' in expr and 'result.state.' in expr and 'state.' in expr:
                    return _result('contradicted', 'test_assertion_ast', 'Test compares a result-state array with an input-state array; full state equality is not proven', file=path, line=assertion.lineno)
        return _result('insufficient_evidence', 'test_assertion_ast', 'Specific assertion pattern not found; absence of coverage is not proven', file=path)
    return _result('insufficient_evidence', 'test_evidence', 'Named test is not among cited evidence')


def verify_review(report: dict, files: dict[str, str]) -> dict:
    """Annotate a V10.8.3 report without changing model findings or making LLM calls."""
    result = deepcopy(report)
    packet = result.get('evidence_packet', {})
    counts = {s: 0 for s in sorted(STATUSES)}
    for finding in result.get('findings', []):
        verdict = verify_finding(finding, packet, files)
        finding['evidence_verification'] = verdict
        counts[verdict['status']] += 1
    result['verification_counts'] = counts
    result['verification_policy'] = 'conservative_syntactic_checks_only; no execution; unsupported claims are not confirmed'
    return result


def review_function_verified(files: dict[str, str], **kwargs) -> dict:
    """Run the opt-in V10.8.3 local review, then attach deterministic verification."""
    from app.ai.context_review_v1083 import review_function_with_ollama
    return verify_review(review_function_with_ollama(files, **kwargs), files)
