"""Report routes (alias to the assessment report)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ...core.deps import get_current_user, get_datastore
from ...core.security import AuthUser
from ...repositories.base import Store
from .mappers import to_report_out

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{assessment_id}")
async def get_report(
    assessment_id: str,
    user: AuthUser = Depends(get_current_user),
    store: Store = Depends(get_datastore),
):
    from ...services.assessment_service import assessment_service

    report = assessment_service.get_report(store, user.id, assessment_id)
    return to_report_out(report)
