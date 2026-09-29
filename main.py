"""
main.py — JURIS FastAPI application entry point.

Start the server:
    uv run uvicorn main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.chat import router as chat_router
from core.config import settings

app = FastAPI(
    title="JURIS",
    description="The AI/backend layer for Lawyer's E-Diary (LED).",
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ───────────────────────────────────────────────────────────────────────
# Allows LED Flutter web builds to reach JURIS during development.
# origins are controlled by JURIS_ALLOWED_ORIGINS in .env.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
if settings.api_prefix:
    app.include_router(chat_router, prefix=settings.api_prefix)
else:
    app.include_router(chat_router)


# ── Root routes ───────────────────────────────────────────────────────────────

@app.get("/")
async def root() -> dict:
    return {
        "message": "JURIS is online",
        "version": settings.version,
        "env": settings.env,
    }


@app.get("/health")
async def health() -> dict:
    return {
        "status": "healthy",
        "gateway": settings.gateway,
    }