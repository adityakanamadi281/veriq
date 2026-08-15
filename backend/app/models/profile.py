"""Candidate profile / candidate context.

This is the structured context passed into the assessment engine. It is also
the schema Gemini must produce when parsing a resume. Facts that cannot be
supported by the resume are left null/empty — never fabricated.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import Dimension


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Project(BaseModel):
    name: str
    description: str = ""
    technologies: list[str] = Field(default_factory=list)
    url: str | None = None


class CandidateProfile(BaseModel):
    """The candidate's structured context."""

    user_id: str
    name: str | None = None
    education: str | None = None
    graduation_year: int | None = None
    experience: str | None = None
    target_role: str | None = None
    technical_skills: list[str] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    ai_tools: list[str] = Field(default_factory=list)
    github: str | None = None
    linkedin: str | None = None
    professional_links: list[str] = Field(default_factory=list)
    background: str | None = None  # concise professional background

    # Resume storage reference (private object path in Supabase Storage).
    resume_path: str | None = None
    resume_parsed: bool = False

    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)

    def context_for_assessment(self) -> dict[str, Any]:
        """A trimmed dict suitable for inclusion in Gemini prompts."""
        return {
            "name": self.name,
            "education": self.education,
            "graduation_year": self.graduation_year,
            "experience": self.experience,
            "target_role": self.target_role,
            "technical_skills": self.technical_skills,
            "projects": [p.model_dump() for p in self.projects],
            "ai_tools": self.ai_tools,
            "github": self.github,
            "linkedin": self.linkedin,
            "professional_links": self.professional_links,
            "background": self.background,
        }

    def completeness(self) -> dict[Dimension, float]:
        """Heuristic coverage of context — not a capability score."""
        filled = 0
        total = 0
        for field in (
            "name",
            "education",
            "experience",
            "target_role",
            "technical_skills",
            "projects",
            "ai_tools",
            "background",
        ):
            total += 1
            value = getattr(self, field)
            if value:
                filled += 1
        ratio = filled / total if total else 0.0
        return {d: ratio for d in Dimension}
