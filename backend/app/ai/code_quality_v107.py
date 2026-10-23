"""V10.7 static Python quality and technical-depth signals.

Conservative evidence: observations, not overall quality or runtime correctness.
Never executes user code or sends source to a model.
"""
from __future__ import annotations

import ast
from collections import Counter
from pathlib import PurePosixPath
from app.ai.project_audit_v105 import audit_project

_MAX_FINDINGS = 150


def review_code_quality(files: dict[str, str]) -> dict:
    """Review bounded file mapping already acquired from an approved source."""
    audit = audit_project(files)  # validates file count, safe paths and per-file limits
    excluded = {'.git', '.venv', 'venv', 'node_modules', '__pycache__', 'dist', 'build'}
    findings = []
    parsed = 0
    syntax_errors = 0
    functions = 0
    classes = 0
    test_functions = 0
    for path in sorted(files):
        if not path.endswith('.py') or any(part in excluded for part in PurePosixPath(path).parts):
            continue
        content = files[path]
        try:
            tree = ast.parse(content, filename=path)
        except (SyntaxError, ValueError) as exc:
            syntax_errors += 1
            findings.append({'category': 'parseability', 'signal': 'python_parse_failed',
                             'file': path, 'line': getattr(exc, 'lineno', None),
                             'detail': 'Python AST parsing failed; runtime status unknown.'})
            continue
        parsed += 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions += 1
                if node.name.startswith('test_') and ('test' in PurePosixPath(path).parts or PurePosixPath(path).name.startswith('test_')):
                    test_functions += 1
                span = (node.end_lineno or node.lineno) - node.lineno + 1
                if span > 80:
                    findings.append({'category': 'maintainability', 'signal': 'long_function',
                                     'file': path, 'line': node.lineno, 'symbol': node.name,
                                     'detail': f'{span} source lines; review decomposition in context.'})
                if not node.returns and not node.name.startswith('_'):
                    findings.append({'category': 'typing', 'signal': 'missing_return_annotation',
                                     'file': path, 'line': node.lineno, 'symbol': node.name,
                                     'detail': 'No return annotation; not necessarily a defect.'})
            elif isinstance(node, ast.ClassDef):
                classes += 1
            elif isinstance(node, ast.ExceptHandler) and node.type is None:
                findings.append({'category': 'error_handling', 'signal': 'bare_except',
                                 'file': path, 'line': node.lineno,
                                 'detail': 'Bare except catches BaseException; inspect intent.'})
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {'eval', 'exec'}:
                findings.append({'category': 'review_required', 'signal': 'dynamic_execution_call',
                                 'file': path, 'line': node.lineno,
                                 'detail': 'eval/exec call present; context and trust boundary require review.'})
            elif isinstance(node, (ast.For, ast.While)):
                if any(isinstance(child, (ast.For, ast.While)) for child in ast.walk(node) if child is not node):
                    findings.append({'category': 'technical_depth', 'signal': 'nested_iteration',
                                     'file': path, 'line': node.lineno,
                                     'detail': 'Nested loop structure present; algorithmic purpose/complexity not established.'})
            elif isinstance(node, ast.With):
                findings.append({'category': 'technical_depth', 'signal': 'context_manager',
                                 'file': path, 'line': node.lineno,
                                 'detail': 'Context manager used; resource-safety not established.'})
    findings = sorted(findings, key=lambda f: (f['file'], f['line'] or 0, f['signal']))
    total = len(findings)
    return {'analysis_type': 'static_code_quality_signals',
            'summary': {'python_files_parsed': parsed, 'python_parse_failures': syntax_errors,
                        'function_definitions': functions, 'class_definitions': classes,
                        'test_function_definitions': test_functions, 'findings_total': total,
                        'findings_returned': min(total, _MAX_FINDINGS)},
            'finding_counts': dict(sorted(Counter(f['signal'] for f in findings).items())),
            'findings': findings[:_MAX_FINDINGS],
            'coverage': {'files_supplied': len(files), 'source_files_in_audit': audit['source_file_count'],
                         'scan_completeness': 'unknown_without_ingestion_manifest'},
            'limitations': ['Static signals do not establish code quality or proficiency.',
                            'README claims and functional behavior are not verified.',
                            'Tests and application were not executed.',
                            'Results cover only the files supplied by the scanner.',
                            'No quality score is inferred from raw finding counts.'],
            'code_executed': False, 'llm_calls': False, 'neo4j_writes': False}
