from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.api.routes.health import router as health_router
from app.core.config import get_settings

from app.api.routes.analysis import router as analysis_router

from app.api.routes.skill import router as skill_router
from app.api.routes.github import router as github_preview_router
from app.api.routes.recommendation import (
    router as recommendation_router,
)

from app.api.routes.graph import router as graph_router

from app.api.routes.similarity import (
    router as similarity_router,
)

from app.api.routes.github import router as github_router
from app.matching.router import (
    router as matching_router,
)
from app.matching.evidence_router import router as evidence_matching_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="GitHub developer skill analysis and recommendation API",
    version=settings.app_version,
    debug=settings.debug,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(github_router)
app.include_router(analysis_router, prefix="/api")
app.include_router(skill_router, prefix="/api")
app.include_router(recommendation_router, prefix="/api")
app.include_router(graph_router, prefix="/api")
app.include_router(similarity_router, prefix="/api")
app.include_router(
    matching_router,
    prefix="/api",
)
app.include_router(github_preview_router, prefix="/api")
# V10 evidence-backed matching; separate from legacy developer matching.
app.include_router(evidence_matching_router, prefix="/api/matching", tags=["Evidence Matching"])

# V10.2 public profile discovery
from app.api.routes.profile_discovery_v102 import router as profile_discovery_router
app.include_router(profile_discovery_router)

# V10.3 private ZIP upload: localhost-only until authenticated user isolation exists.
from app.api.routes.private_zip_v103 import router as private_zip_router
app.include_router(private_zip_router)

# V10.4 ephemeral public + private profile (localhost only).
from app.api.routes.unified_profile_v104 import router as unified_profile_router
app.include_router(unified_profile_router)
