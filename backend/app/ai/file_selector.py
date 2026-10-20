"""Deterministic, diversity-aware selection of repository evidence files."""
from pathlib import PurePosixPath

ALLOWED_SUFFIXES = {'.py', '.js', '.jsx', '.ts', '.tsx', '.vue', '.cs', '.java', '.go', '.rs', '.sql', '.md', '.toml', '.yaml', '.yml', '.json', '.txt'}
EXCLUDED_PARTS = {'.git', '.venv', 'venv', 'node_modules', 'dist', 'build', '__pycache__', '.next', 'coverage', 'vendor', 'generated', '.pytest_cache'}
EXCLUDED_NAMES = {'.env', '.env.local', '.env.production', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'poetry.lock', 'uv.lock', 'composer.lock'}
SENSITIVE_PARTS = ('secret', 'credential', 'private_key', 'token', 'password', 'id_rsa', '.pem', '.key')
SOURCE_SUFFIXES = {'.py', '.js', '.jsx', '.ts', '.tsx', '.vue', '.cs', '.java', '.go', '.rs', '.sql'}
IMPORTANT_NAMES = {'main.py', 'app.py', 'train.py', 'training.py', 'model.py', 'models.py', 'agent.py', 'agents.py', 'policy.py', 'dqn.py', 'ppo.py', 'environment.py'}
IMPORTANT_DIRS = {'agent', 'agents', 'model', 'models', 'training', 'train', 'rl', 'reinforcement_learning', 'algorithms', 'ai', 'ml'}


def is_candidate(path: str, size: int, max_file_bytes: int = 30_000) -> bool:
    p = PurePosixPath(path)
    if not isinstance(size, int) or path.startswith('/') or '..' in p.parts or size <= 0 or size > max_file_bytes:
        return False
    parts = {part.lower() for part in p.parts}
    if parts & EXCLUDED_PARTS or p.name.lower() in EXCLUDED_NAMES:
        return False
    if any(marker in p.name.lower() for marker in SENSITIVE_PARTS):
        return False
    return p.suffix.lower() in ALLOWED_SUFFIXES or p.name.lower() in {'dockerfile', 'makefile'}


def _category(path: str) -> str:
    p = PurePosixPath(path)
    name = p.name.lower()
    dirs = {x.lower() for x in p.parts[:-1]}
    if name.startswith('readme') and p.suffix.lower() == '.md':
        return 'readme'
    if name in {'pyproject.toml', 'requirements.txt', 'package.json', 'dockerfile', 'environment.yml', 'environment.yaml'}:
        return 'manifest'
    if name.startswith('test_') or name.endswith(('.test.js', '.test.ts', '.spec.ts')) or dirs & {'tests', 'test', '__tests__'}:
        return 'test'
    if p.suffix.lower() in SOURCE_SUFFIXES and (name in IMPORTANT_NAMES or dirs & IMPORTANT_DIRS or any(x in name for x in ('agent', 'train', 'model', 'policy', 'ppo', 'dqn'))):
        return 'core'
    if p.suffix.lower() in SOURCE_SUFFIXES:
        return 'source'
    return 'other'


def select_files(tree: list[dict], max_files: int = 16, max_file_bytes: int = 30_000) -> list[dict]:
    """Reserve slots for README, manifests, core algorithms, general source, and tests.

    Selected items retain their original GitHub tree dictionaries. No network access.
    """
    if max_files <= 0:
        return []
    eligible = [item for item in tree if item.get('type') == 'blob' and isinstance(item.get('path'), str) and is_candidate(item['path'], item.get('size', 0), max_file_bytes)]

    def sort_key(item: dict) -> tuple[int, int, str]:
        p = PurePosixPath(item['path'])
        name = p.name.lower()
        # Prefer top-level README and dependency manifests; prioritize named agent/model files.
        important = 0 if name in IMPORTANT_NAMES else 1
        return (important, len(p.parts), item['path'].lower())

    groups = {name: [] for name in ('readme', 'manifest', 'core', 'source', 'test', 'other')}
    for item in eligible:
        groups[_category(item['path'])].append(item)
    for group in groups.values():
        group.sort(key=sort_key)

    chosen: list[dict] = []
    selected_paths: set[str] = set()

    def take(category: str, count: int) -> None:
        for item in groups[category]:
            if count <= 0 or len(chosen) >= max_files:
                break
            if item['path'] not in selected_paths:
                chosen.append(item)
                selected_paths.add(item['path'])
                count -= 1

    # Balanced coverage prevents alphabetically early source/test files from
    # consuming all slots before the actual model/agent implementation.
    for category, quota in [('readme', 1), ('manifest', 2), ('core', max(1, max_files // 2)), ('source', 2), ('test', 1)]:
        take(category, quota)
    for category in ('core', 'source', 'manifest', 'readme', 'test', 'other'):
        take(category, max_files - len(chosen))
    return chosen
