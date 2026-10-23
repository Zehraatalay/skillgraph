"""Private ZIP endpoint deliberately restricted to loopback clients until auth exists."""
from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from app.ai.private_zip_v103 import MAX_ARCHIVE_BYTES, analyze_zip

router = APIRouter(prefix='/api/private-project', tags=['Private ZIP V10.3'])

@router.post('/analyze-zip')
async def analyze_private_zip(request: Request, file: UploadFile = File(...)):
    host = request.client.host if request.client else None
    if host not in {'127.0.0.1', '::1'}:
        raise HTTPException(403, 'Private ZIP analysis is localhost-only until authentication is implemented')
    try:
        blob = await file.read(MAX_ARCHIVE_BYTES + 1)
        if len(blob) > MAX_ARCHIVE_BYTES:
            raise HTTPException(413, 'ZIP exceeds 6 MiB upload limit')
        return analyze_zip(blob, filename=file.filename or '')
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    finally:
        await file.close()
