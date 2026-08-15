"""Resume routes: upload+parse, and re-parse an existing resume."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile

from ...core.deps import get_current_user, get_datastore
from ...core.errors import NotFoundError, ResumeError
from ...core.security import AuthUser
from ...repositories.base import Store
from ...schemas.profile import ProfileOut
from ...schemas.resume import ResumeParseResult
from ...services.assessment_service import assessment_service
from ...services.resume_parser import resume_parser

router = APIRouter(prefix="/resume", tags=["resume"])


def _extracted_fields(extraction) -> list[str]:
    fields = []
    for name in (
        "name",
        "education",
        "graduation_year",
        "experience",
        "target_role",
        "technical_skills",
        "projects",
        "ai_tools",
        "github",
        "linkedin",
        "professional_links",
        "background",
    ):
        value = getattr(extraction, name, None)
        if value:
            fields.append(name)
    return fields


@router.post("", response_model=ResumeParseResult)
async def upload_resume(
    file: UploadFile = File(...),
    user: AuthUser = Depends(get_current_user),
    store: Store = Depends(get_datastore),
):
    data = await file.read()
    resume_parser.validate(file.filename or "resume.pdf", file.content_type or "", len(data))
    text = resume_parser.extract_text(data)
    path = resume_parser.upload(user.id, file.filename or "resume.pdf", data)
    extraction = await resume_parser.parse(text)

    profile = assessment_service.get_profile(store, user.id)
    profile.resume_path = path
    profile = resume_parser.apply_extraction(profile, extraction)
    profile = store.upsert_profile(profile)

    return ResumeParseResult(
        profile=ProfileOut(**profile.model_dump()),
        extracted_fields=_extracted_fields(extraction),
    )


@router.post("/parse", response_model=ResumeParseResult)
async def reparse_resume(
    user: AuthUser = Depends(get_current_user),
    store: Store = Depends(get_datastore),
):
    """Re-extract from the resume stored in Supabase Storage."""
    profile = assessment_service.get_profile(store, user.id)
    if not profile.resume_path:
        raise NotFoundError("No resume found. Please upload one first.")

    from ...core.supabase import get_supabase_admin
    from ...services.resume_parser import _BUCKET

    client = get_supabase_admin()
    try:
        data = client.storage.from_(_BUCKET).download(profile.resume_path)
    except Exception as exc:
        raise ResumeError("Could not retrieve your stored resume.") from exc
    text = resume_parser.extract_text(bytes(data))

    extraction = await resume_parser.parse(text)
    profile = resume_parser.apply_extraction(profile, extraction)
    profile = store.upsert_profile(profile)

    return ResumeParseResult(
        profile=ProfileOut(**profile.model_dump()),
        extracted_fields=_extracted_fields(extraction),
    )
