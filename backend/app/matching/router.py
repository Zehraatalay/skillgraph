from fastapi import (
    APIRouter,
    HTTPException,
)

from app.github.service import (
    GitHubRepositoryError,
)
from app.matching.schemas import (
    RepositoryMatchRequest,
    RepositoryMatchResponse,
    DeveloperMatchRequest,
    DeveloperMatchResponse,
)
from app.matching.service import (
    match_repository_to_jobs,
    match_developer_to_jobs,
)


router = APIRouter(
    prefix="/matching",
    tags=["Matching"],
)


@router.post(
    "/repository",
    response_model=RepositoryMatchResponse,
)
async def match_repository(
    request: RepositoryMatchRequest,
) -> RepositoryMatchResponse:
    try:
        result = await match_repository_to_jobs(
            repository_url=str(
                request.repository_url
            ),
            limit=request.limit,
        )

    except GitHubRepositoryError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return RepositoryMatchResponse(
        **result
    )

@router.post("/developer", response_model=DeveloperMatchResponse)
def match_developer(request: DeveloperMatchRequest) -> DeveloperMatchResponse:
    try:
        result = match_developer_to_jobs(request.username, request.limit)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail="Curated job dataset is unavailable") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Developer not found in Neo4j. Analyze the GitHub profile first.",
        )
    return DeveloperMatchResponse(**result)


from app.matching.evidence_router import router as evidence_router

router.include_router(evidence_router)