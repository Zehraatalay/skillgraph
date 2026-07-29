from fastapi import APIRouter, HTTPException, status

from app.repositories.neo4j_repository import Neo4jRepository

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "SkillGraph API",
    }


@router.get("/database")
def database_health_check() -> dict[str, str]:
    repository = Neo4jRepository()

    try:
        repository.verify_connection()

        result = repository.run_query(
            """
            RETURN
                'connected' AS status,
                'Neo4j' AS database
            """
        )

        return {
            "status": result[0]["status"],
            "database": result[0]["database"],
        }

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Neo4j connection failed: {exc}",
        ) from exc

    finally:
        repository.close()