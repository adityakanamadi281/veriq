"""v1 API router aggregating all route modules."""

from __future__ import annotations

from fastapi import APIRouter

from . import assessments, profile, reports, resumes

api_router = APIRouter()
api_router.include_router(profile.router)
api_router.include_router(resumes.router)
api_router.include_router(assessments.router)
api_router.include_router(reports.router)
