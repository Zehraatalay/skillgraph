"""Read-only, deterministic project health signals. Not a proof of functionality."""
from __future__ import annotations
import re
from pathlib import PurePosixPath

DOC_NAMES = {'readme.md', 'readme.rst', 'readme.txt'}
TEST_PATTERNS = (re.compile(r'(^|/)tests?/test_[^/]+\.py$'), re.compile(r'(^|/)__tests__/'), re.compile(r'(^|/)[^/]+\.test\.[jt]sx?$'))
MANIFESTS = {'pyproject.toml', 'requirements.txt', 'package.json', 'pom.xml', 'build.gradle', 'cargo.toml', 'go.mod'}
CI_PREFIXES = ('.github/workflows/', '.gitlab-ci.yml')
EXCLUDED_PARTS = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build'}

def audit_project(files: dict[str, str]) -> dict:
    """Analyze a bounded {relative_path: UTF-8 content} mapping; never execute code."""
    if len(files) > 300:
        raise ValueError('Too many files')
    normalized = {}
    for path, content in files.items():
        if not isinstance(path, str) or not isinstance(content, str):
            raise ValueError('Paths and contents must be strings')
        p = PurePosixPath(path)
        if not path or p.is_absolute() or '..' in p.parts or '\\' in path:
            raise ValueError('Unsafe path')
        if len(content.encode('utf-8')) > 1_048_576:
            raise ValueError('File too large')
        if not any(part in EXCLUDED_PARTS for part in p.parts):
            normalized[path] = content
    names = set(normalized)
    readmes = sorted(n for n in names if PurePosixPath(n).name.lower() in DOC_NAMES)
    manifests = sorted(n for n in names if PurePosixPath(n).name.lower() in MANIFESTS)
    tests = sorted(n for n in names if any(pattern.search(n) for pattern in TEST_PATTERNS))
    ci = sorted(n for n in names if n.startswith(CI_PREFIXES))
    source = sorted(n for n in names if n.endswith(('.py','.js','.ts','.tsx','.jsx','.java','.go','.rs','.cs','.cpp','.c','.h','.vue')) and n not in tests)
    readme_text = '\n'.join(normalized[n][:20000] for n in readmes)
    headings = re.findall(r'^#{1,4}\s+(.+)$', readme_text, flags=re.M)
    install = bool(re.search(r'\b(install|installation|setup|kurulum)\b', readme_text, flags=re.I))
    run = bool(re.search(r'\b(usage|quickstart|run|getting started|kullanım|çalıştır)\b', readme_text, flags=re.I))
    signals = {'readme': bool(readmes), 'installation_instructions': install, 'usage_instructions': run,
               'dependency_manifest': bool(manifests), 'test_files': bool(tests), 'ci_config': bool(ci), 'source_files': bool(source)}
    missing = [key for key, present in signals.items() if not present]
    return {'assessment': 'static_signals_only', 'signals': signals,
            'files': {'readme': readmes[:5], 'manifests': manifests[:10], 'tests': tests[:10], 'ci': ci[:10]},
            'source_file_count': len(source), 'test_file_count': len(tests), 'readme_headings': headings[:15],
            'missing_signals': missing, 'limitations': [
                'Project completion cannot be inferred from file presence.',
                'Runtime functionality has not been tested.',
                'Code quality, security and authorship have not been established.',
                'README claims are unverified until checked against code and tests.'
            ], 'code_executed': False, 'llm_calls': False, 'neo4j_writes': False}
