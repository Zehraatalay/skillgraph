from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.github import router as github_router
from app.api.routes.health import router as health_router
from app.core.config import get_settings

from app.api.routes.analysis import router as analysis_router

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
app.include_router(github_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")