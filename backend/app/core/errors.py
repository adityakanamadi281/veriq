"""Application-level error types and FastAPI exception handlers.

These give the frontend predictable, explainable error states instead of raw
provider or framework noise. No secrets are ever included in messages.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base error carrying an HTTP status and a user-safe message."""

    status_code: int = 400
    code: str = "app_error"

    def __init__(self, message: str, *, code: str | None = None, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code


class AuthRequiredError(AppError):
    status_code = 401
    code = "auth_required"


class ForbiddenError(AppError):
    status_code = 403
    code = "forbidden"


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"


class ValidationError(AppError):
    status_code = 422
    code = "validation_error"


class ResumeError(AppError):
    status_code = 422
    code = "resume_error"


class GeminiError(AppError):
    status_code = 502
    code = "gemini_error"


class AssessmentStateError(AppError):
    status_code = 409
    code = "assessment_state_error"


class DuplicateSubmissionError(AppError):
    status_code = 409
    code = "duplicate_submission"


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(GeminiError)
    async def _handle_gemini_error(_: Request, exc: GeminiError) -> JSONResponse:
        # Never leak provider details upstream.
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )
