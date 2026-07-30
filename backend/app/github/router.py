from fastapi import APIRouter, HTTPException

from app.github.schemas import (
    RepositoryAnalysisRequest,
    RepositoryAnalysisResponse,
)
from app.github.service import (
    GitHubRepositoryError,
    analyze_repository,
)


router = APIRouter(
    prefix="/github",
    tags=["GitHub"],
)


@router.post(
    "/analyze",
    response_model=RepositoryAnalysisResponse,
)
async def analyze_github_repository(
    request: RepositoryAnalysisRequest,
) -> RepositoryAnalysisResponse:
    try:
        result = await analyze_repository(
            str(request.repository_url)
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
    except GitHubRepositoryError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    return RepositoryAnalysisResponse(
        **result
    )