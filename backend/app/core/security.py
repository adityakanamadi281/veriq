"""Authentication: resolve the authenticated candidate from a request.

The frontend holds a Supabase access token (email/password auth) and sends it
as `Authorization: Bearer <token>`. We verify it server-side by asking Supabase
to resolve the user from the JWT. The authenticated user id always comes from
the verified token — never from the request body.
"""

from __future__ import annotations

from dataclasses import dataclass

from .config import get_settings
from .errors import AuthRequiredError
from .supabase import get_supabase_admin


@dataclass(frozen=True)
class AuthUser:
    id: str
    email: str


def _bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise AuthRequiredError("Sign in to continue.")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise AuthRequiredError("Invalid authentication token.")
    return token


def resolve_user(authorization: str | None) -> AuthUser:
    """Resolve the authenticated user from a Bearer header.

    Raises AuthRequiredError (HTTP 401) when no/invalid/expired token is supplied.
    """
    settings = get_settings()
    token = _bearer_token(authorization)

    if not settings.supabase_configured:
        raise AuthRequiredError(
            "Authentication is not configured. Set Supabase credentials in .env."
        )

    client = get_supabase_admin()
    try:
        response = client.auth.get_user(token)
    except Exception as exc:
        raise AuthRequiredError("We could not verify your session. Please sign in again.") from exc

    user = getattr(response, "user", None)
    if user is None or not getattr(user, "id", None):
        raise AuthRequiredError("Your session has expired. Please sign in again.")

    email = getattr(user, "email", None) or ""
    return AuthUser(id=str(user.id), email=str(email))
