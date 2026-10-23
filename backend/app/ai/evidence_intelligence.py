"""V9.2.1: conservative AST technology evidence and source-backed quality ranking.

No LLM, DB writes or inferred proficiency. A call must resolve to an imported API.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass

from app.ai.skill_profile import ProfileSkill, SkillEvidence
from app.ai.schemas import RepositoryContext

# Canonical skill -> exact import prefixes. Keep intentionally small and auditable.
TECHNOLOGIES = {
    'OpenCV': ('cv2',),
    'NumPy': ('numpy',),
    'Pandas': ('pandas',),
    'scikit-learn': ('sklearn',),
    'Pygame': ('pygame',),
    'FastAPI': ('fastapi',),
    'Pytest': ('pytest',),
}


def _imports(tree: ast.Module) -> dict[str, str]:
    result = {}
    # Only module-level imports: nested conditional imports are not always executed.
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                result[alias.asname or alias.name.split('.')[0]] = alias.name if alias.asname else alias.name.split('.')[0]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            for alias in node.names:
                if alias.name != '*':
                    result[alias.asname or alias.name] = f'{node.module}.{alias.name}'
    return result


def _resolve(node: ast.AST, bindings: dict[str, str]) -> str | None:
    if isinstance(node, ast.Name):
        return bindings.get(node.id)
    if isinstance(node, ast.Attribute):
        parent = _resolve(node.value, bindings)
        return f'{parent}.{node.attr}' if parent else None
    return None


def _shadowed(tree: ast.Module) -> set[str]:
    """Conservatively ignore aliases reassigned anywhere in the module.

    Also excludes imports with aliases shadowed in nested scopes (safe false negatives).
    """
    shadowed = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                for sub in ast.walk(target):
                    if isinstance(sub, ast.Name):
                        shadowed.add(sub.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            shadowed.add(node.name)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                shadowed.update(a.arg for a in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs))
    return shadowed


def _line(source: str, lineno: int) -> str:
    lines = source.splitlines()
    return lines[lineno - 1].strip() if 0 < lineno <= len(lines) else ''


def detect_additional_technologies(context: RepositoryContext) -> list[ProfileSkill]:
    """Detect *usage*, not mere imports. At most one evidence per technology per file."""
    repository = f'{context.owner}/{context.repository}'
    evidence: dict[str, list[SkillEvidence]] = {name: [] for name in TECHNOLOGIES}
    for source in context.files:
        if not source.path.endswith('.py'):
            continue
        try:
            tree = ast.parse(source.content)
        except (SyntaxError, ValueError):
            continue
        bindings = _imports(tree)
        for alias in _shadowed(tree):
            bindings.pop(alias, None)
        calls = sorted((n for n in ast.walk(tree) if isinstance(n, ast.Call)),
                       key=lambda n: (n.lineno, n.col_offset))
        for name, prefixes in TECHNOLOGIES.items():
            for call in calls:
                target = _resolve(call.func, bindings)
                if target and any(target.startswith(prefix + '.') for prefix in prefixes):
                    quote = _line(source.content, call.lineno)
                    if quote:
                        evidence[name].append(SkillEvidence(
                            repository=repository, file=source.path, quote=quote,
                            evidence_type='ast_api_usage',
                            decision_reason=f'Call target {target} resolves to an imported {name} API; usage only.',
                            explanation=f'{name} API call identified from Python AST imports.',
                        ))
                    break
    return [ProfileSkill(name=name, category='technology', evidence_count=len(items),
                         evidence=sorted(items, key=lambda e: (e.file, e.quote)))
            for name, items in evidence.items() if items]


@dataclass(frozen=True)
class EvidenceAssessment:
    quality: str
    reason: str
    snippet: str


def assess_evidence(evidence: SkillEvidence, source: str) -> EvidenceAssessment:
    """Source-backed presentation quality, NOT developer proficiency.

    A quote must exist in the file. The snippet is a short, verbatim source excerpt.
    """
    lines = source.splitlines()
    indexes = [i for i, line in enumerate(lines) if evidence.quote.strip() in line]
    if not indexes:
        return EvidenceAssessment('unverified', 'Quote not present in source', '')
    i = indexes[0]
    snippet = '\n'.join(lines[i:min(i + 6, len(lines))])[:650]
    stripped = evidence.quote.lstrip()
    if evidence.evidence_type == 'ast_api_usage':
        return EvidenceAssessment('strong', 'Imported API call, AST-resolved', snippet)
    if stripped.startswith(('def ', 'async def ', 'class ')):
        return EvidenceAssessment('medium', 'Function/class declaration; behavior not validated', snippet)
    return EvidenceAssessment('weak', 'Generic source statement', snippet)


def build_quality_report(profile, context: RepositoryContext) -> dict:
    files = {file.path: file.content for file in context.files}
    result = []
    for skill in profile.skills:
        for evidence in skill.evidence:
            if evidence.file not in files:
                assessment = EvidenceAssessment('unverified', 'Source not available in scan', '')
            else:
                assessment = assess_evidence(evidence, files[evidence.file])
            result.append({'skill': skill.name, 'repository': evidence.repository,
                           'file': evidence.file, 'quote': evidence.quote,
                           'quality': assessment.quality, 'reason': assessment.reason,
                           'snippet': assessment.snippet})
    order = {'strong': 0, 'medium': 1, 'weak': 2, 'unverified': 3}
    result.sort(key=lambda r: (order[r['quality']], r['skill'].casefold(), r['file'], r['quote']))
    return {'repository': profile.repository, 'assessment_type': 'evidence_presentation_quality',
            'items': result, 'total': len(result)}
