"""Resume API schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .profile import ProfileOut


class ResumeParseResult(BaseModel):
    """Returned after upload+parse so the candidate can review extracted fields."""

    profile: ProfileOut
    extracted_fields: list[str] = Field(
        default_factory=list,
        description="Names of fields that were populated from the resume.",
    )
