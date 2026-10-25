"""Deterministic, source-backed technology usage detection (no LLM)."""
from __future__ import annotations

import ast
from dataclasses import dataclass

from app.ai.schemas import RepositoryContext
from app.ai.skill_profile import SkillEvidence, ProfileSkill


@dataclass(frozen=True)
class _Binding:
    module: str
    origin: str


def _resolve(expr: ast.AST, bindings: dict[str, _Binding]) -> str | None:
    if isinstance(expr, ast.Name):
        bound = bindings.get(expr.id)
        return bound.module if bound else None
    if isinstance(expr, ast.Attribute):
        base = _resolve(expr.value, bindings)
        return f'{base}.{expr.attr}' if base else None
    return None


def _binding_map(tree: ast.Module) -> dict[str, _Binding]:
    bindings: dict[str, _Binding] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name.split('.')[0]
                resolved = alias.name if alias.asname else alias.name.split('.')[0]
                bindings[local] = _Binding(resolved, 'import')
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            for alias in node.names:
                if alias.name != '*':
                    bindings[alias.asname or alias.name] = _Binding(f'{node.module}.{alias.name}', 'from')
    return bindings


def detect_technology_skills(context: RepositoryContext) -> list[ProfileSkill]:
    """Return Python/PyTorch usage supported by a quoted source line.

    Python: parsed .py source containing executable statements (not just imports).
    PyTorch: a call resolved through an imported torch symbol. Merely importing
    torch or declaring it as a dependency is insufficient.

    This is *usage* evidence, not a claim of proficiency. Files that cannot be
    parsed (including truncated scanner output) are skipped.
    """
    repository = f'{context.owner}/{context.repository}'
    found: dict[str, list[SkillEvidence]] = {'Python': [], 'PyTorch': []}
    for source in context.files:
        if not source.path.endswith('.py'):
            continue
        try:
            tree = ast.parse(source.content)
        except (SyntaxError, ValueError):
            continue
        lines = source.content.splitlines()
        bindings = _binding_map(tree)
        executable = [n for n in tree.body if not isinstance(n, (ast.Import, ast.ImportFrom, ast.Expr)) or (isinstance(n, ast.Expr) and not isinstance(n.value, ast.Constant))]
        if executable:
            node = executable[0]
            quote = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ''
            if quote:
                found['Python'].append(SkillEvidence(
                    repository=repository, file=source.path, quote=quote,
                    evidence_type='ast_source_usage',
                    decision_reason='Python source parsed with executable statements; evidence of usage, not proficiency.',
                    explanation='Python code found in a repository source file.',
                ))
        calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                resolved = _resolve(node.func, bindings)
                if resolved and resolved.startswith('torch.'):
                    calls.append(node)
        if calls:
            node = sorted(calls, key=lambda n: (n.lineno, n.col_offset))[0]
            quote = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ''
            if quote:
                found['PyTorch'].append(SkillEvidence(
                    repository=repository, file=source.path, quote=quote,
                    evidence_type='ast_api_usage',
                    decision_reason='Call target resolves to an imported torch API; evidence of usage, not proficiency.',
                    explanation='PyTorch API call identified using Python AST import resolution.',
                ))
    return [ProfileSkill(name=name, category='programming_language' if name == 'Python' else 'ml_framework',
                         evidence_count=len(found[name]), evidence=sorted(found[name], key=lambda e: (e.file, e.quote)))
            for name in ('Python', 'PyTorch') if found[name]]
