"""
main.py — JURIS FastAPI application entry point.

Start the server:
    uv run uvicorn main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.chat import router as chat_router
from api.finance import router as finance_router
from core.config import settings
from core.errors import JurisError

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
app.include_router(chat_router, prefix=settings.api_prefix)
app.include_router(finance_router, prefix=settings.api_prefix)


@app.exception_handler(JurisError)
async def handle_juris_error(_request: Request, error: JurisError) -> JSONResponse:
    _ = _request
    return JSONResponse(status_code=error.http_status, content=error.to_dict())


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