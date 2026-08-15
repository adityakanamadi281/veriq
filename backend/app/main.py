"""VERIQ — FastAPI application entrypoint.

Architecture: React → Supabase Auth → JWT → FastAPI → Supabase Postgres/Storage
→ Gemini SDK → Assessment Engine → FastAPI → React. The browser never calls
Gemini. Service-role and Gemini keys stay server-side.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1.router import api_router
from .core.config import get_settings
from .core.errors import register_error_handlers

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("veriq")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if not settings.supabase_configured:
        logger.warning(
            "Supabase is not configured (SUPABASE_URL / SUPABASE_ANON_KEY). "
            "Auth, persistence, and resume storage will be unavailable until set in .env."
        )
    if not settings.gemini_configured:
        logger.warning(
            "GEMINI_API_KEY not set — resume parsing and assessments will be unavailable "
            "until it is configured in .env."
        )
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="VERIQ — AI Readiness Assessment", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, object]:
        return {
            "status": "ok",
            "service": "veriq",
            "gemini_configured": settings.gemini_configured,
            "supabase_configured": settings.supabase_configured,
        }

    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
