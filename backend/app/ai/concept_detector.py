"""V9.2.2: conservative AST concept *candidates*, not verified skills.

Each rule requires structural evidence. No function-name-only detection, no LLM,
no proficiency claims, no profile/Neo4j mutations.
"""
from __future__ import annotations

import ast
from dataclasses import asdict, dataclass

from app.ai.schemas import RepositoryContext


@dataclass(frozen=True)
class ConceptCandidate:
    concept: str
    repository: str
    file: str
    line: int
    quote: str
    reason: str
    status: str = 'needs_review'


def _calls(node: ast.AST) -> list[ast.Call]:
    return [x for x in ast.walk(node) if isinstance(x, ast.Call)]


def _name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _quoted_line(source: str, lineno: int) -> str:
    lines = source.splitlines()
    return lines[lineno - 1].strip() if 0 < lineno <= len(lines) else ''


def detect_concept_candidates(context: RepositoryContext) -> list[ConceptCandidate]:
    result: list[ConceptCandidate] = []
    repository = f'{context.owner}/{context.repository}'
    for source in context.files:
        if not source.path.endswith('.py'):
            continue
        try:
            tree = ast.parse(source.content)
        except (SyntaxError, ValueError):
            continue
        for fn in (n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))):
            calls = _calls(fn)
            call_names = {_name(c.func) for c in calls}
            method_names = {_name(c.func) for c in calls if isinstance(c.func, ast.Attribute)}
            assigned = {n.id for node in ast.walk(fn) if isinstance(node, (ast.Assign, ast.AnnAssign))
                        for target in (node.targets if isinstance(node, ast.Assign) else [node.target])
                        for n in ast.walk(target) if isinstance(n, ast.Name)}
            loops = any(isinstance(n, (ast.For, ast.While)) for n in ast.walk(fn))
            conditions = any(isinstance(n, ast.If) for n in ast.walk(fn))
            recursion = any(isinstance(c.func, ast.Name) and c.func.id == fn.name for c in calls)
            concepts: list[tuple[str, str]] = []
            # Queue-based graph traversal: actual popleft + append in a loop and visited membership.
            if loops and conditions and 'popleft' in method_names and 'append' in method_names and any(
                isinstance(n, (ast.Compare, ast.If)) and any(isinstance(v, (ast.In, ast.NotIn)) for v in getattr(n, 'ops', []))
                for n in ast.walk(fn)
            ):
                concepts.append(('Queue-based graph traversal', 'Loop with queue dequeue/enqueue and membership test; traversal intent requires review.'))
            # Memoization: explicit Python caching decorator (not just a function called cache).
            if any(_name(d) in ('lru_cache', 'cache') or
                   (isinstance(d, ast.Call) and _name(d.func) in ('lru_cache', 'cache')) for d in fn.decorator_list):
                concepts.append(('Memoization', 'Function uses a caching decorator; caching semantics require review.'))
            # Recursive search with explicit competing min/max branches.
            if recursion and conditions and {'min', 'max'} <= call_names:
                concepts.append(('Minimax-like recursive search', 'Recursive function contains both min() and max(); game-tree semantics require review.'))
            # Priority-queue traversal; usage is not sufficient to claim Dijkstra/A*.
            if loops and {'heappush', 'heappop'} <= call_names:
                concepts.append(('Priority-queue search', 'Loop uses heap push/pop; algorithm identity requires review.'))
            # Iterative state-space search with explicit stack and pop, not necessarily DFS.
            if loops and 'pop' in method_names and 'append' in method_names and conditions:
                concepts.append(('Stack-based search candidate', 'Loop uses pop/append with branching; review whether it traverses states.'))
            for concept, reason in concepts:
                result.append(ConceptCandidate(concept, repository, source.path, fn.lineno,
                                               _quoted_line(source.content, fn.lineno), reason))
    # Stable, duplicate-free report. Do not silently convert candidates into skills.
    return list({(x.concept, x.file, x.line): x for x in sorted(
        result, key=lambda x: (x.file, x.line, x.concept))}.values())


def concept_report(context: RepositoryContext) -> dict:
    items = [asdict(x) for x in detect_concept_candidates(context)]
    return {'repository': f'{context.owner}/{context.repository}',
            'assessment_type': 'ast_concept_candidates', 'status': 'review_required',
            'candidate_count': len(items), 'items': items,
            'warning': 'Candidates are NOT verified skills and are NOT used for job matching.'}
