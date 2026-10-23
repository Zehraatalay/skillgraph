"""Public repository discovery and explicit-selection analysis endpoints."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from app.ai.profile_discovery_v102 import discover, analyze_selected
from app.repositories.github_repository import GitHubRepository, GitHubAPIError

router = APIRouter(prefix='/api/profile-analysis', tags=['Profile Analysis V10.2'])

class AnalyzeRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    repositories: list[str] = Field(min_length=1, max_length=5)
    max_files: int = Field(default=40, ge=1, le=40)

@router.get('/{username}/repositories')
def repositories(username: str, include_forks: bool = Query(False)):
    github = GitHubRepository()
    try:
        return discover(github, username, include_forks=include_forks)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except GitHubAPIError as exc:
        raise HTTPException(502, str(exc)) from exc
    finally:
        github.close()

@router.post('/analyze')
def analyze(request: AnalyzeRequest):
    github = GitHubRepository()
    try:
        return analyze_selected(github, request.username, request.repositories, max_files=request.max_files)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except GitHubAPIError as exc:
        raise HTTPException(502, str(exc)) from exc
    finally:
        github.close()
