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
)
from app.matching.service import (
    match_repository_to_jobs,
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