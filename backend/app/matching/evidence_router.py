"""Opt-in evidence-based matching API; existing matching endpoints remain unchanged."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.matching.evidence_matching import fetch_verified_evidence, rank_jobs
from app.matching.service import _load_jobs
from app.repositories.graph_repository import GraphRepository

router = APIRouter()


class EvidenceMatchRequest(BaseModel):
    username: str = Field(min_length=1, max_length=39,
                          pattern=r'^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$')
    limit: int = Field(default=10, ge=1, le=50)


@router.post('/developer/evidence')
def match_developer_evidence(request: EvidenceMatchRequest) -> dict:
    graph = GraphRepository()
    try:
        if not graph.developer_exists(request.username):
            raise HTTPException(status_code=404, detail='Developer not found in Neo4j')
        rows = fetch_verified_evidence(graph._neo4j, request.username)
    finally:
        graph.close()
    try:
        result = rank_jobs(_load_jobs(), rows, request.limit)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail='Curated job dataset unavailable') from exc
    return {'username': request.username, 'score_type': 'verified_skill_coverage', **result}
