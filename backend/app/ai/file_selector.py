"""Deterministic, budgeted source-file selection."""
from pathlib import PurePosixPath

ALLOWED_SUFFIXES = {'.py', '.js', '.jsx', '.ts', '.tsx', '.vue', '.cs', '.java', '.go', '.rs', '.sql', '.md', '.toml', '.yaml', '.yml', '.json', '.txt'}
EXCLUDED_PARTS = {'.git', '.venv', 'venv', 'node_modules', 'dist', 'build', '__pycache__', '.next', 'coverage', 'vendor', 'generated'}
EXCLUDED_NAMES = {'.env', '.env.local', '.env.production', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'poetry.lock', 'uv.lock', 'composer.lock'}
SENSITIVE_PARTS = ('secret', 'credential', 'private_key', 'token', 'password', 'id_rsa', '.pem', '.key')


def is_candidate(path: str, size: int, max_file_bytes: int = 30_000) -> bool:
    p = PurePosixPath(path)
    if path.startswith('/') or '..' in p.parts or size <= 0 or size > max_file_bytes:
        return False
    parts = {part.lower() for part in p.parts}
    if parts & EXCLUDED_PARTS or p.name.lower() in EXCLUDED_NAMES:
        return False
    if any(marker in p.name.lower() for marker in SENSITIVE_PARTS):
        return False
    return p.suffix.lower() in ALLOWED_SUFFIXES or p.name.lower() in {'dockerfile', 'makefile'}


def select_files(tree: list[dict], max_files: int = 16, max_file_bytes: int = 30_000) -> list[dict]:
    files = [item for item in tree if item.get('type') == 'blob' and isinstance(item.get('path'), str) and is_candidate(item['path'], item.get('size', 0), max_file_bytes)]

    def priority(item: dict) -> tuple[int, int, str]:
        path = item['path']
        name = PurePosixPath(path).name.lower()
        if name.startswith('readme'): rank = 0
        elif name in {'pyproject.toml', 'requirements.txt', 'package.json', 'dockerfile'}: rank = 1
        elif name in {'main.py', 'app.py', 'train.py', 'model.py', 'agent.py'}: rank = 2
        elif '/test' in path.lower() or name.startswith('test_'): rank = 5
        elif name.endswith(('.py', '.cs', '.java', '.ts', '.vue')): rank = 3
        else: rank = 4
        return (rank, len(PurePosixPath(path).parts), path)

    return sorted(files, key=priority)[:max_files]
