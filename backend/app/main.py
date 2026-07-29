from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router

app = FastAPI(
    title="SkillGraph API",
    description="GitHub developer skill analysis and recommendation API",
    version="0.1.0",
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


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "SkillGraph API is running",
    }