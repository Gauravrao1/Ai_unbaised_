from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routes.bias import router as bias_router
from app.routes.explain import router as explain_router
from app.routes.mitigation import router as mitigation_router
from app.routes.upload import router as upload_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="BiasLens AI detects, explains, and mitigates bias in ML systems.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(bias_router)
app.include_router(mitigation_router)
app.include_router(explain_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.app_name}


@app.get("/")
def root():
    return {
        "message": "BiasLens AI backend is running.",
        "endpoints": ["/upload", "/analyze-bias", "/mitigate", "/explain", "/health"],
    }

