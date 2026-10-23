"""V10.3: bounded, ephemeral, local-only ZIP source analysis. Never executes files."""
from __future__ import annotations
import hashlib
import io
import re
import stat
import tempfile
import zipfile
from pathlib import Path
from app.ai.project_source import ProjectSource, SourceType, Visibility, private_project_id, validate_relative_source_path
from app.ai.source_context import scan_local_directory
from app.ai.technology_usage_v103 import detect_usage

MAX_ARCHIVE_BYTES = 6 * 1024 * 1024
MAX_UNCOMPRESSED = 15 * 1024 * 1024
MAX_ENTRIES = 300
MAX_ENTRY_BYTES = 1 * 1024 * 1024
MAX_RATIO = 100
SAFE_NAME = re.compile(r"^[^\x00-\x1f]{1,150}$")


def _check_archive(blob: bytes):
    if not blob or len(blob) > MAX_ARCHIVE_BYTES:
        raise ValueError('ZIP exceeds upload limit (6 MiB) or is empty')
    try:
        archive = zipfile.ZipFile(io.BytesIO(blob))
    except (zipfile.BadZipFile, OSError) as exc:
        raise ValueError('Invalid ZIP archive') from exc
    entries = archive.infolist()
    if len(entries) > MAX_ENTRIES:
        archive.close(); raise ValueError('Too many ZIP entries')
    total = 0
    seen_paths = set()
    for item in entries:
        name = item.filename
        if name.startswith('/') or '\\' in name or '\x00' in name:
            archive.close(); raise ValueError('Unsafe ZIP path')
        try:
            validate_relative_source_path(name.rstrip('/'))
        except ValueError as exc:
            archive.close(); raise ValueError('Unsafe ZIP path') from exc
        canonical = name.rstrip('/').casefold()
        if canonical in seen_paths:
            archive.close(); raise ValueError('Duplicate ZIP entry')
        seen_paths.add(canonical)
        mode = (item.external_attr >> 16) & 0xFFFF
        if stat.S_IFMT(mode) and not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
            archive.close(); raise ValueError('Unsupported ZIP entry type')
        if item.flag_bits & 1:
            archive.close(); raise ValueError('Encrypted ZIP is unsupported')
        if item.file_size > MAX_ENTRY_BYTES:
            archive.close(); raise ValueError('ZIP entry exceeds 1 MiB')
        if item.file_size and (item.compress_size == 0 or item.file_size / item.compress_size > MAX_RATIO):
            archive.close(); raise ValueError('Suspicious ZIP compression ratio')
        total += item.file_size
        if total > MAX_UNCOMPRESSED:
            archive.close(); raise ValueError('Uncompressed ZIP exceeds limit')
    return archive


def analyze_zip(blob: bytes, *, filename: str = 'private-project.zip') -> dict:
    """Ephemeral local-only analysis; no DB, remote model, or persistent disk writes."""
    if not SAFE_NAME.fullmatch(filename) or not filename.lower().endswith('.zip'):
        raise ValueError('A valid .zip filename is required')
    archive = _check_archive(blob)
    storage_key = hashlib.sha256(blob).hexdigest()
    project_id = private_project_id('local-session', storage_key)
    source = ProjectSource(project_id=project_id, owner_id='local-session',
                           display_name='Private ZIP project', source_type=SourceType.ZIP_UPLOAD,
                           visibility=Visibility.PRIVATE, storage_key=storage_key,
                           source_revision=storage_key)
    try:
        with tempfile.TemporaryDirectory(prefix='skillgraph-zip-') as directory:
            root = Path(directory)
            for entry in archive.infolist():
                if entry.is_dir():
                    continue
                dest = root.joinpath(*entry.filename.split('/'))
                dest.parent.mkdir(parents=True, exist_ok=True)
                # Stream bounded data. Never use extractall, never execute extracted content.
                with archive.open(entry) as reader, dest.open('wb') as writer:
                    data = reader.read(MAX_ENTRY_BYTES + 1)
                    if len(data) > MAX_ENTRY_BYTES:
                        raise ValueError('ZIP entry exceeds limit')
                    writer.write(data)
            context = scan_local_directory(source, root, max_files=100,
                                           max_file_bytes=30_000, max_total_chars=500_000)
            skills = detect_usage(context)
            return {'project_id': project_id, 'source_type': 'zip_upload', 'visibility': 'private',
                    'analysis_type': 'ast_technology_usage', 'files_scanned': len(context.files),
                    'skipped_files': context.skipped_files,
                    'skills': [{'name': s.name, 'evidence_count': s.evidence_count,
                                'evidence_samples': [e.model_dump() for e in s.evidence[:3]]}
                               for s in skills], 'neo4j_writes': False,
                    'note': 'Local-only, temporary source analysis. No proficiency inference, LLM calls, or graph writes.'}
    finally:
        archive.close()
