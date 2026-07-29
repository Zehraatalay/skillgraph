from fastapi import APIRouter, HTTPException, Path, status

from app.schemas.skill import DeveloperSkillProfileResponse
from app.services.skill_service import SkillService

router = APIRouter(
    prefix="/skills",
    tags=["Skills"],
)


@router.get(
    "/developers/{username}",
    response_model=DeveloperSkillProfileResponse,
)
def get_developer_skill_profile(
    username: str = Path(
        min_length=1,
        max_length=39,
        pattern=r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$",
    ),
) -> DeveloperSkillProfileResponse:
    service = SkillService()

    try:
        result = service.get_developer_skill_profile(username)

        return DeveloperSkillProfileResponse.model_validate(
            result
        )

    except ValueError as exc:
        error_message = str(exc)

        response_status = (
            status.HTTP_404_NOT_FOUND
            if "no analyzed graph data" in error_message.lower()
            else status.HTTP_400_BAD_REQUEST
        )

        raise HTTPException(
            status_code=response_status,
            detail=error_message,
        ) from exc

    finally:
        service.close()