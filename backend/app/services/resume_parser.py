"""Resume upload + parsing pipeline.

Validates type/size → extracts text with pypdf → uploads the private object to
Supabase Storage → asks Gemini for structured extraction → validates with
Pydantic → returns the normalized fields for candidate review. Missing facts
are left null; nothing is fabricated.
"""

from __future__ import annotations

import io
import logging
import uuid

from ..core.config import Settings, get_settings
from ..core.errors import ResumeError
from ..core.supabase import get_supabase_admin
from ..models.profile import CandidateProfile, Project
from .ai_contracts import ResumeExtraction
from .gemini_service import gemini_service

logger = logging.getLogger("aura.resume")

_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
_ALLOWED_CONTENT_TYPES = {"application/pdf"}
_BUCKET = "candidate-resumes"


class ResumeParser:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def validate(self, filename: str, content_type: str, size: int) -> None:
        if content_type not in _ALLOWED_CONTENT_TYPES:
            raise ResumeError("Only PDF resumes are supported.")
        if size > _MAX_BYTES:
            raise ResumeError("Resume must be under 5 MB.")
        if not filename.lower().endswith(".pdf"):
            raise ResumeError("The resume file must be a .pdf.")

    def extract_text(self, data: bytes) -> str:
        try:
            from pypdf import PdfReader  # type: ignore[import-not-found]
        except Exception as exc:
            raise ResumeError("Resume processing is unavailable.") from exc
        try:
            reader = PdfReader(io.BytesIO(data))
            pages = [page.extract_text() or "" for page in reader.pages]
        except Exception as exc:
            raise ResumeError("Could not read this PDF. Try exporting it again.") from exc
        text = "\n".join(pages).strip()
        if len(text) < 20:
            raise ResumeError(
                "This PDF appears to be empty or image-only. Upload a text-based PDF."
            )
        return text

    def upload(self, user_id: str, filename: str, data: bytes) -> str:
        """Upload to private Supabase Storage; return the object path."""
        client = get_supabase_admin()  # raises a clear error if Supabase isn't configured
        path = f"{user_id}/{uuid.uuid4()}/{filename}"
        try:
            client.storage.from_(_BUCKET).upload(path, data, {"content-type": "application/pdf"})
        except Exception as exc:
            logger.warning("Resume upload failed: %s", exc)
            raise ResumeError("Could not store your resume. Please try again.") from exc
        return path

    async def parse(self, text: str) -> ResumeExtraction:
        return await gemini_service.parse_resume(text)

    def apply_extraction(
        self, profile: CandidateProfile, extraction: ResumeExtraction
    ) -> CandidateProfile:
        """Merge extracted fields onto a profile without overwriting manual edits."""
        profile.name = extraction.name or profile.name
        profile.education = extraction.education or profile.education
        profile.graduation_year = extraction.graduation_year or profile.graduation_year
        profile.experience = extraction.experience or profile.experience
        profile.target_role = extraction.target_role or profile.target_role
        if extraction.technical_skills:
            profile.technical_skills = extraction.technical_skills
        if extraction.projects:
            profile.projects = [Project(**p.model_dump()) for p in extraction.projects]
        if extraction.ai_tools:
            profile.ai_tools = extraction.ai_tools
        profile.github = extraction.github or profile.github
        profile.linkedin = extraction.linkedin or profile.linkedin
        if extraction.professional_links:
            profile.professional_links = extraction.professional_links
        profile.background = extraction.background or profile.background
        profile.resume_parsed = True
        return profile


resume_parser = ResumeParser()
