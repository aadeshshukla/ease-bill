from fastapi import FastAPI

from routers.auth import router as auth_router
from routers.upload import router as upload_router

app = FastAPI(title="Ease Bill API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(upload_router, prefix="/upload", tags=["upload"])
