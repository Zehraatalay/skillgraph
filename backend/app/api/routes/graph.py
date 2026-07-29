from fastapi import APIRouter, HTTPException, Path, status

from app.schemas.graph import DeveloperGraphResponse
from app.services.graph_service import GraphService

router = APIRouter(
    prefix="/graphs",
    tags=["Graphs"],
)


@router.get(
    "/developers/{username}",
    response_model=DeveloperGraphResponse,
)
def get_developer_graph(
    username: str = Path(
        min_length=1,
        max_length=39,
        pattern=(
            r"^[A-Za-z0-9]"
            r"(?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$"
        ),
    ),
) -> DeveloperGraphResponse:
    service = GraphService()

    try:
        result = service.get_developer_graph(username)

        return DeveloperGraphResponse.model_validate(
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