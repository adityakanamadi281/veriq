"""FastAPI dependencies."""

from __future__ import annotations

from fastapi import Header

from ..repositories.base import Store
from ..repositories.factory import get_store
from .config import Settings, get_settings
from .security import AuthUser, resolve_user


def get_current_user(authorization: str | None = Header(default=None)) -> AuthUser:
    return resolve_user(authorization)


def get_current_settings() -> Settings:
    return get_settings()


def get_datastore() -> Store:
    return get_store()
