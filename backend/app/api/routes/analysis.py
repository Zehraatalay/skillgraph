from fastapi import APIRouter, HTTPException, Path, status

from app.repositories.github_repository import GitHubAPIError
from app.schemas.analysis import DeveloperAnalysisResponse
from app.services.analysis_service import AnalysisService

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)


@router.post(
    "/developers/{username}",
    response_model=DeveloperAnalysisResponse,
)
def analyze_developer(
    username: str = Path(
        min_length=1,
        max_length=39,
        pattern=r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$",
    ),
) -> DeveloperAnalysisResponse:
    service = AnalysisService()

    try:
        result = service.analyze_developer(username)
        return DeveloperAnalysisResponse.model_validate(result)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except GitHubAPIError as exc:
        error_message = str(exc)

        response_status = (
            status.HTTP_404_NOT_FOUND
            if "not found" in error_message.lower()
            else status.HTTP_502_BAD_GATEWAY
        )

        raise HTTPException(
            status_code=response_status,
            detail=error_message,
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    finally:
        service.close()