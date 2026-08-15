"""Profile routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ...core.deps import get_current_user, get_datastore
from ...core.security import AuthUser
from ...repositories.base import Store
from ...schemas.profile import ProfileOut, ProfileUpdate
from ...services.assessment_service import assessment_service

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileOut)
async def get_profile(
    user: AuthUser = Depends(get_current_user),
    store: Store = Depends(get_datastore),
):
    profile = assessment_service.get_profile(store, user.id)
    return ProfileOut(**profile.model_dump())


@router.put("", response_model=ProfileOut)
async def update_profile(
    body: ProfileUpdate,
    user: AuthUser = Depends(get_current_user),
    store: Store = Depends(get_datastore),
):
    profile = assessment_service.upsert_profile(store, user.id, body.model_dump(exclude_unset=True))
    return ProfileOut(**profile.model_dump())
