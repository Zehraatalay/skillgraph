"""V10.1 adapter: normalize a bounded, trusted local directory into V9 RepositoryContext.

The local root is supplied by trusted backend code only; NEVER pass arbitrary
HTTP user paths to this adapter. ZIP extraction and auth belong to V10.3.
"""
from __future__ import annotations

from pathlib import Path
from app.ai.schemas import RepositoryContext, SourceFile
from app.ai.project_source import ProjectSource, SourceType, validate_relative_source_path

_ALLOWED = {".py", ".js", ".ts", ".tsx", ".jsx", ".vue", ".java", ".cpp", ".c", ".h", ".cs", ".go", ".rs", ".md", ".toml", ".yml", ".yaml", ".json"}
_EXCLUDED = {".git", ".venv", "venv", "node_modules", "dist", "build", "__pycache__", ".next", ".idea"}


def scan_local_directory(source: ProjectSource, root: Path, *, max_files: int = 40,
                         max_file_bytes: int = 30_000, max_total_chars: int = 250_000) -> RepositoryContext:
    if source.source_type not in {SourceType.LOCAL_DIRECTORY, SourceType.ZIP_UPLOAD}:
        raise ValueError("Expected a local or extracted upload source")
    if not 1 <= max_files <= 100 or max_file_bytes < 1 or max_total_chars < 1:
        raise ValueError("Invalid scan limits")
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Source root must be a directory")
    files = []
    remaining = max_total_chars
    skipped = 0
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in _EXCLUDED or part.startswith(".") for part in relative.parts):
            continue
        if path.is_symlink() or not path.is_file():
            continue
        if path.suffix.lower() not in _ALLOWED:
            continue
        if len(files) >= max_files or remaining <= 0:
            skipped += 1
            continue
        # Reject symlinked ancestor directories as well as symlink files.
        if not path.resolve().is_relative_to(root):
            skipped += 1
            continue
        if path.stat().st_size > max_file_bytes:
            skipped += 1
            continue
        relative_name = validate_relative_source_path(relative.as_posix())
        try:
            raw = path.read_bytes()
            if b"\x00" in raw:
                skipped += 1
                continue
            content = raw.decode("utf-8")
        except (OSError, UnicodeDecodeError):
            skipped += 1
            continue
        if len(content) > remaining:
            skipped += 1  # Never truncate Python files into invalid AST.
            continue
        files.append(SourceFile(path=relative_name, content=content, size=len(raw)))
        remaining -= len(content)
    owner, repo = source.repository_key.split("/", 1)
    return RepositoryContext(owner=owner, repository=repo, files=files,
                             skipped_files=skipped, total_characters=max_total_chars - remaining)
