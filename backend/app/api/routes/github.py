from fastapi import APIRouter, HTTPException, Path, status

from app.repositories.github_repository import GitHubAPIError
from app.schemas.github import GitHubAnalysisPreviewResponse
from app.services.github_service import GitHubService

router = APIRouter(
    prefix="/github",
    tags=["GitHub"],
)


@router.get(
    "/users/{username}/preview",
    response_model=GitHubAnalysisPreviewResponse,
)
def get_github_analysis_preview(
    username: str = Path(
        min_length=1,
        max_length=39,
        pattern=r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$",
    ),
) -> GitHubAnalysisPreviewResponse:
    service = GitHubService()

    try:
        result = service.get_analysis_preview(username)
        return GitHubAnalysisPreviewResponse.model_validate(result)

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

    finally:
        service.close()