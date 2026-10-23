"""Local-only V10.4 endpoint: server performs both analyses, then aggregates."""
from __future__ import annotations
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from app.ai.private_zip_v103 import MAX_ARCHIVE_BYTES, analyze_zip
from app.ai.profile_discovery_v102 import analyze_selected
from app.ai.unified_profile_v104 import combine_analysis
from app.repositories.github_repository import GitHubRepository

router = APIRouter(prefix='/api/unified-profile', tags=['Unified Profile V10.4'])

@router.post('/analyze')
async def analyze_unified(
    request: Request,
    username: str = Form(default=''),
    repositories: str = Form(default=''),
    file: UploadFile | None = File(default=None),
):
    if request.client is None or request.client.host not in {'127.0.0.1', '::1'}:
        raise HTTPException(403, 'Unified analysis is localhost-only until authentication is implemented')
    names = [name.strip() for name in repositories.split(',') if name.strip()]
    if len(names) > 5:
        raise HTTPException(422, 'At most 5 public repositories per request')
    if bool(names) != bool(username.strip()):
        raise HTTPException(422, 'Provide both username and repositories, or neither')
    if not names and file is None:
        raise HTTPException(422, 'Select public repositories and/or upload a ZIP')
    public = None
    if names:
        github = GitHubRepository()
        try:
            public = analyze_selected(github, username.strip(), names)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        except Exception as exc:
            # Avoid leaking credentials or internal HTTP details.
            raise HTTPException(502, f'GitHub analysis failed: {type(exc).__name__}') from exc
        finally:
            github.close()
    private = []
    if file is not None:
        try:
            blob = await file.read(MAX_ARCHIVE_BYTES + 1)
            if len(blob) > MAX_ARCHIVE_BYTES:
                raise HTTPException(413, 'ZIP exceeds 6 MiB upload limit')
            private.append(analyze_zip(blob, filename=file.filename or ''))
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        finally:
            await file.close()
    return combine_analysis(public, private)
