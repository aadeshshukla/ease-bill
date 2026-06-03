import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.auth import router as auth_router
from routers.upload import router as upload_router

app = FastAPI(title="Ease Bill API")


def _cors_origins() -> list[str]:
    configured = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000",
    )
    return [origin.strip() for origin in configured.split(",") if origin.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(upload_router, prefix="/upload", tags=["upload"])
