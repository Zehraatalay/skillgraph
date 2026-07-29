from fastapi import APIRouter, HTTPException, Path, status

from app.schemas.recommendation import (
    DeveloperRecommendationResponse,
)
from app.services.recommendation_service import (
    RecommendationService,
)

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


@router.get(
    "/developers/{username}",
    response_model=DeveloperRecommendationResponse,
)
def get_developer_recommendations(
    username: str = Path(
        min_length=1,
        max_length=39,
        pattern=r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$",
    ),
) -> DeveloperRecommendationResponse:
    service = RecommendationService()

    try:
        result = service.get_developer_recommendations(username)

        return DeveloperRecommendationResponse.model_validate(
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