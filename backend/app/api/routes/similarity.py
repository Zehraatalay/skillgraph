from fastapi import (
    APIRouter,
    HTTPException,
    Path,
    Query,
    status,
)

from app.schemas.similarity import (
    DeveloperSimilarityResponse,
)
from app.services.similarity_service import (
    SimilarityService,
)

router = APIRouter(
    prefix="/similarity",
    tags=["Similarity"],
)


@router.get(
    "/developers/{username}",
    response_model=DeveloperSimilarityResponse,
)
def get_similar_developers(
    username: str = Path(
        min_length=1,
        max_length=39,
        pattern=(
            r"^[A-Za-z0-9]"
            r"(?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$"
        ),
    ),
    limit: int = Query(
        default=5,
        ge=1,
        le=20,
    ),
) -> DeveloperSimilarityResponse:
    service = SimilarityService()

    try:
        result = service.get_similar_developers(
            username=username,
            limit=limit,
        )

        return DeveloperSimilarityResponse.model_validate(
            result
        )

    except ValueError as exc:
        message = str(exc)

        response_status = (
            status.HTTP_404_NOT_FOUND
            if "no analyzed graph data" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )

        raise HTTPException(
            status_code=response_status,
            detail=message,
        ) from exc

    finally:
        service.close()