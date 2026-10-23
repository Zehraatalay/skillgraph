"""V10.6: conservative README-to-source traceability review.

Static, read-only. A referenced symbol is evidence of presence, not correct behavior.
No code execution, external LLM, persistence or graph writes.
"""
from __future__ import annotations

import ast
import re
from pathlib import PurePosixPath

from app.ai.project_audit_v105 import audit_project

_READMES = {'readme.md', 'readme.rst', 'readme.txt'}
_SOURCE_SUFFIXES = {'.py', '.js', '.jsx', '.ts', '.tsx', '.vue', '.java', '.go', '.rs', '.cpp', '.cs'}
_LINK = re.compile(r'\[([^\]\n]{1,100})\]\(([^)\n]{1,300})\)')
_CODE = re.compile(r'`([A-Za-z_][A-Za-z0-9_]{2,80})`')
_HEADING = re.compile(r'^#{1,4}\s+(.+)$', re.M)
_MAX_CLAIMS = 60


def _normalize_target(target: str, readme_path: str) -> str | None:
    """Accept only local relative paths that cannot escape the project root."""
    target = target.split('#', 1)[0].split('?', 1)[0].strip()
    if not target or target.startswith(('/', '\\')) or '://' in target or '\\' in target:
        return None
    base = list(PurePosixPath(readme_path).parent.parts)
    if base == ['.']:
        base = []
    for part in PurePosixPath(target).parts:
        if part in ('', '.'):
            continue
        if part == '..':
            if not base:
                return None
            base.pop()
        else:
            base.append(part)
    return '/'.join(base)


def _python_symbols(path: str, content: str) -> set[str]:
    if not path.endswith('.py'):
        return set()
    try:
        tree = ast.parse(content)
    except (SyntaxError, ValueError):
        return set()
    return {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}


def review_readme_against_code(files: dict[str, str]) -> dict:
    """Inspect README links and backticked Python symbols against supplied source.

    Only explicit traceable references are assessed; free-text feature claims
    remain unverified and require later semantic/agent review.
    """
    audit = audit_project(files)  # enforces bounded content and safe relative paths
    excluded = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build'}
    safe_files = {p: content for p, content in files.items()
                  if not any(part in excluded for part in PurePosixPath(p).parts)}
    source_paths = sorted(p for p in safe_files if PurePosixPath(p).suffix.lower() in _SOURCE_SUFFIXES)
    python_symbols = {p: _python_symbols(p, safe_files[p]) for p in source_paths if p.endswith('.py')}
    readmes = sorted(p for p in safe_files if PurePosixPath(p).name.lower() in _READMES)
    findings: list[dict] = []
    seen: set[tuple] = set()
    for readme in readmes[:5]:
        content = safe_files[readme][:20_000]
        for match in _LINK.finditer(content):
            target = _normalize_target(match.group(2), readme)
            if target is None or PurePosixPath(target).suffix.lower() not in _SOURCE_SUFFIXES:
                continue
            key = ('file_reference', readme, target)
            if key in seen:
                continue
            seen.add(key)
            found = target in safe_files and target in source_paths
            findings.append({'kind': 'file_reference', 'claim': match.group(1), 'readme': readme,
                             'target': target, 'status': 'source_present' if found else 'not_found_in_scanned_files',
                             'evidence': [{'file': target, 'type': 'path_exists'}] if found else [],
                             'caveat': 'File presence does not prove described functionality.'})
        for match in _CODE.finditer(content):
            symbol = match.group(1)
            key = ('python_symbol', readme, symbol)
            if key in seen:
                continue
            seen.add(key)
            paths = [p for p, symbols in python_symbols.items() if symbol in symbols][:5]
            findings.append({'kind': 'python_symbol', 'claim': symbol, 'readme': readme,
                             'target': symbol, 'status': 'source_present' if paths else 'not_found_in_scanned_files',
                             'evidence': [{'file': p, 'type': 'ast_definition'} for p in paths],
                             'caveat': 'AST definition does not prove behavior, quality, or runtime success.'})
        if len(findings) >= _MAX_CLAIMS:
            break
    findings = findings[:_MAX_CLAIMS]
    return {'assessment': 'readme_source_traceability_only', 'project_audit': audit,
            'readme_files': readmes[:5], 'readme_headings': [h for r in readmes[:5] for h in _HEADING.findall(safe_files[r][:20_000])][:20],
            'source_files_scanned': len(source_paths), 'findings': findings,
            'counts': {'source_present': sum(f['status'] == 'source_present' for f in findings),
                       'not_found_in_scanned_files': sum(f['status'] == 'not_found_in_scanned_files' for f in findings)},
            'limitations': ['README free-text feature claims are not verified by this version.',
                            'Missing references may be caused by bounded file selection.',
                            'No test suite or application was executed; completion and correctness are unknown.',
                            'Source presence is not evidence of authorship or proficiency.'],
            'code_executed': False, 'llm_calls': False, 'neo4j_writes': False}
