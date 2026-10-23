"""V9.2.3: conservative, explainable behavioral candidates from Python AST.

Candidates are NOT verified skills. Rules use combinations of structural signals,
not names of functions, classes, or files as sufficient evidence.
"""
from __future__ import annotations

import ast
from dataclasses import asdict, dataclass

from app.ai.schemas import RepositoryContext


@dataclass(frozen=True)
class BehaviorCandidate:
    concept: str
    repository: str
    file: str
    function: str
    line: int
    quote: str
    signals: tuple[str, ...]
    status: str = 'needs_review'


def _attr(node: ast.AST) -> str | None:
    return node.attr if isinstance(node, ast.Attribute) else node.id if isinstance(node, ast.Name) else None


def _snippet(src: str, node: ast.AST, *, limit: int = 420) -> str:
    text = ast.get_source_segment(src, node) or ''
    return text[:limit] + ('…' if len(text) > limit else '')


def _local_nodes(fn: ast.AST):
    """Exclude nested function/class bodies to avoid attributing their logic to parent."""
    stack = list(reversed(getattr(fn, 'body', [])))
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            continue
        yield node
        stack.extend(reversed(list(ast.iter_child_nodes(node))))


def _function_candidates(fn: ast.AST, src: str, repository: str, path: str) -> list[BehaviorCandidate]:
    nodes = list(_local_nodes(fn))
    calls = [n for n in nodes if isinstance(n, ast.Call)]
    names = {_attr(c.func) for c in calls}
    loops = [n for n in nodes if isinstance(n, (ast.For, ast.While))]
    branches = [n for n in nodes if isinstance(n, ast.If)]
    returns = [n for n in nodes if isinstance(n, ast.Return)]
    yields = [n for n in nodes if isinstance(n, (ast.Yield, ast.YieldFrom))]
    comparisons = [n for n in nodes if isinstance(n, ast.Compare)]
    results: list[BehaviorCandidate] = []

    def emit(concept: str, signals: tuple[str, ...], anchor: ast.AST):
        results.append(BehaviorCandidate(concept, repository, path, getattr(fn, 'name', '<anonymous>'),
                                         anchor.lineno, _snippet(src, anchor), signals))

    # Candidate move enumeration: a loop, condition, and collection of accepted
    # items. We do NOT call this a game skill without manual review.
    collection = [c for c in calls if _attr(c.func) in {'append', 'add'}]
    if loops and branches and collection and (returns or yields):
        # Require append/add within a loop (not merely elsewhere in function).
        loop_calls = [c for loop in loops for c in ast.walk(loop)
                      if isinstance(c, ast.Call) and _attr(c.func) in {'append', 'add'}]
        if loop_calls:
            emit('Conditional candidate enumeration', ('loop', 'conditional_filter', 'collection_add', 'result_return'), loop_calls[0])

    # Greedy candidate selection: an explicit best-so-far update gated by a
    # comparison inside a loop. No algorithm name is inferred from identifiers.
    if loops and branches and comparisons:
        for loop in loops:
            for branch in (n for n in ast.walk(loop) if isinstance(n, ast.If)):
                if not isinstance(branch.test, (ast.Compare, ast.BoolOp)):
                    continue
                assigns = [n for stmt in branch.body for n in ast.walk(stmt)
                           if isinstance(n, (ast.Assign, ast.AnnAssign))]
                if assigns and returns:
                    emit('Iterative best-candidate selection', ('loop', 'comparison', 'conditional_update', 'result_return'), branch)
                    break
            else:
                continue
            break

    # State transformation: explicit copying/replacement of input state followed
    # by a mutation and return. This is NOT sufficient to infer game state management.
    copy_calls = [c for c in calls if _attr(c.func) in {'copy', 'deepcopy', 'replace'}]
    mutation = [n for n in nodes if isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign)) and
                any(isinstance(t, (ast.Subscript, ast.Attribute)) for t in
                    (n.targets if isinstance(n, ast.Assign) else [n.target]))]
    if copy_calls and mutation and returns:
        emit('Copy-and-update state transformation', ('copy_or_replace', 'attribute_or_index_update', 'result_return'), mutation[0])

    # Tests: require assertions, not a test_* function name alone.
    asserts = [n for n in nodes if isinstance(n, ast.Assert)]
    pytest_raises = [c for c in calls if isinstance(c.func, ast.Attribute)
                     and isinstance(c.func.value, ast.Name) and c.func.value.id == 'pytest'
                     and c.func.attr == 'raises']
    if asserts or pytest_raises:
        anchor = (asserts or pytest_raises)[0]
        emit('Executable behavioral assertions', ('assert_or_pytest_raises',), anchor)

    # Explicit memoization: check a cache lookup and write in same function.
    # This is deliberately more stringent than merely finding a cache variable.
    indexed_reads = [n for n in nodes if isinstance(n, ast.Subscript) and isinstance(n.ctx, ast.Load)]
    indexed_writes = [n for n in nodes if isinstance(n, ast.Subscript) and isinstance(n.ctx, ast.Store)]
    read_roots = {ast.dump(n.value) for n in indexed_reads}
    matching = [n for n in indexed_writes if ast.dump(n.value) in read_roots]
    if matching and branches and returns:
        emit('Explicit cache lookup and update', ('indexed_read', 'indexed_write_same_object', 'branch', 'return'), matching[0])

    return results


def behavior_report(context: RepositoryContext) -> dict:
    repository = f'{context.owner}/{context.repository}'
    items: list[BehaviorCandidate] = []
    parse_errors = []
    for file in context.files:
        if not file.path.endswith('.py'):
            continue
        try:
            tree = ast.parse(file.content)
        except (SyntaxError, ValueError) as exc:
            parse_errors.append({'file': file.path, 'error': type(exc).__name__})
            continue
        for fn in (n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))):
            items.extend(_function_candidates(fn, file.content, repository, file.path))
    items.sort(key=lambda x: (x.file, x.line, x.concept))
    return {'repository': repository, 'assessment_type': 'ast_behavior_candidates',
            'status': 'review_required', 'candidate_count': len(items),
            'items': [asdict(i) for i in items], 'parse_errors': parse_errors,
            'warning': 'Behavior candidates are NOT verified skills and are NOT imported or used for matching.'}
