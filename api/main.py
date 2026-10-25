from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from langchain_google_genai.chat_models import (
    GoogleAPIError,
    GoogleRateLimitError,
)

from agents.services.document_text_extractor import (
    DocumentExtractionError,
    DocumentTextExtractor,
)
from api.dependencies import get_workflow
from api.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
)

app = FastAPI(
    title="SkillGraph API",
    description=("Evidence-backed AI skill analysis and explainable job matching"),
    version="0.1.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "skillgraph",
    }


@app.post(
    "/analyze",
    response_model=AnalyzeResponse,
)
def analyze(
    request: AnalyzeRequest,
    workflow=Depends(get_workflow),
):
    try:
        result = workflow.invoke(
            {
                "cv_text": request.cv_text,
                "github_username": request.github_username,
                "job_postings": [job.model_dump() for job in request.job_postings],
            }
        )
    except GoogleRateLimitError as exc:
        raise HTTPException(
            status_code=429,
            detail=(
                "Gemini API request quota has been exceeded. "
                "Please try again after the quota resets."
            ),
        ) from exc
    except GoogleAPIError as exc:
        message = str(exc).lower()

        if "503" in message or "unavailable" in message:
            raise HTTPException(
                status_code=503,
                detail=(
                    "The AI model is temporarily unavailable. Please try again shortly."
                ),
            ) from exc

        if "429" in message or "resource_exhausted" in message:
            raise HTTPException(
                status_code=429,
                detail=(
                    "The AI service rate limit or quota "
                    "has been reached. Please try again later."
                ),
            ) from exc

        raise HTTPException(
            status_code=502,
            detail="The AI service returned an error.",
        ) from exc

    return AnalyzeResponse(
        candidate_profile=result["candidate_profile"],
        job_analyses=result.get("job_analyses", []),
        results=result.get("results", []),
    )


MAX_DOCUMENT_SIZE = 5 * 1024 * 1024  # 5 MB


@app.post("/documents/extract")
async def extract_document(
    file: UploadFile = File(...),
):
    filename = file.filename or ""

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    content = await file.read(MAX_DOCUMENT_SIZE + 1)

    if len(content) > MAX_DOCUMENT_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Document exceeds the 5 MB limit.",
        )

    extractor = DocumentTextExtractor()

    try:
        text = extractor.extract(
            filename=filename,
            content=content,
        )
    except DocumentExtractionError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
    finally:
        await file.close()

    return {
        "filename": filename,
        "text": text,
        "character_count": len(text),
    }
