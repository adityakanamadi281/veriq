"""Profile API schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..models.profile import Project


class ProfileUpdate(BaseModel):
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
    background: str | None = None


class ProfileOut(BaseModel):
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
    background: str | None = None
    resume_parsed: bool = False
    resume_path: str | None = None
