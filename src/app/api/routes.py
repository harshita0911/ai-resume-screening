
import os

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    CandidateInput,
    PreviewFilesResponse,
    UploadProfilePreview,
)

from app.services.resume_parser import (
    ResumeParsingError,
    extract_candidate_profile,
    parse_resume_bytes,
)

from app.services.scoring import rank_candidates
from app.services.skill_taxonomy import extract_skills


router = APIRouter(prefix="/v1", tags=["screening"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _parse_csv_field(raw_value: str) -> list[str]:
    if not raw_value.strip():
        return []

    return [
        item.strip()
        for item in raw_value.split(",")
        if item.strip()
    ]


def _get_role_family(
    job_title: str,
    role_family: str | None
) -> str:

    if role_family and role_family.strip():
        return role_family.strip()

    return job_title.strip()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:

    role = _get_role_family(
        request.job_title,
        request.role_family,
    )

    must_have = _parse_csv_field(
        ", ".join(request.must_have_skills)
    )

    nice_to_have = _parse_csv_field(
        ", ".join(request.nice_to_have_skills)
    )

    required = sorted(
        extract_skills(request.job_description)
    )

    ranked = rank_candidates(
        request.candidates,
        role,
        required,
        must_have,
        nice_to_have,
    )

    top_limit = int(
        os.getenv("TOP_CANDIDATES_LIMIT", "5")
    )

    return AnalyzeResponse(
        job_title=request.job_title,
        role_family=role,
        required_skills=required,
        must_have_skills=must_have,
        nice_to_have_skills=nice_to_have,
        ranked_candidates=ranked[:top_limit],
    )


@router.post(
    "/preview-files",
    response_model=PreviewFilesResponse,
)
async def preview_files(
    resumes: list[UploadFile] = File(...),
) -> PreviewFilesResponse:

    previews: list[UploadProfilePreview] = []

    for idx, resume in enumerate(resumes):

        file_name = (
            resume.filename
            or f"candidate-{idx + 1}.txt"
        )

        try:
            content = await resume.read()

            resume_text = parse_resume_bytes(
                file_name,
                content,
            )

            if not resume_text.strip():
                raise ResumeParsingError(
                    "No readable resume text found."
                )

            candidate_name, years = (
                extract_candidate_profile(
                    resume_text,
                    file_name,
                )
            )

            detected = sorted(
                extract_skills(resume_text)
            )

            previews.append(
                UploadProfilePreview(
                    file_name=file_name,
                    status="ok",
                    candidate_name=candidate_name,
                    years_experience=years,
                    detected_skills=detected,
                    message=(
                        "Profile parsed successfully."
                        if detected
                        else "Resume parsed, but no known skills were detected."
                    ),
                )
            )

        except ResumeParsingError as exc:

            previews.append(
                UploadProfilePreview(
                    file_name=file_name,
                    status="error",
                    message=str(exc),
                )
            )

    return PreviewFilesResponse(
        previews=previews
    )


@router.post(
    "/analyze-files",
    response_model=AnalyzeResponse,
)
async def analyze_files(
    job_title: str = Form(...),
    job_description: str = Form(...),
    role_family: str | None = Form(default=None),
    must_have_skills: str = Form(default=""),
    nice_to_have_skills: str = Form(default=""),
    resumes: list[UploadFile] = File(...),
) -> AnalyzeResponse:

    candidates: list[CandidateInput] = []

    for idx, resume in enumerate(resumes):

        file_name = (
            resume.filename
            or f"candidate-{idx + 1}.txt"
        )

        try:
            content = await resume.read()

            resume_text = parse_resume_bytes(
                file_name,
                content,
            )

            if len(resume_text.strip()) < 30:
                raise ResumeParsingError(
                    "Resume contains too little readable text."
                )

        except ResumeParsingError as exc:
            raise HTTPException(
                status_code=400,
                detail=str(exc),
            ) from exc

        candidate_name, years = (
            extract_candidate_profile(
                resume_text,
                file_name,
            )
        )

        candidates.append(
            CandidateInput(
                name=candidate_name,
                resume_text=resume_text,
                years_experience=years,
            )
        )

    role = _get_role_family(
        job_title,
        role_family,
    )

    must_have = _parse_csv_field(
        must_have_skills
    )

    nice_to_have = _parse_csv_field(
        nice_to_have_skills
    )

    required = sorted(
        extract_skills(job_description)
    )

    ranked = rank_candidates(
        candidates,
        role,
        required,
        must_have,
        nice_to_have,
    )

    top_limit = int(
        os.getenv("TOP_CANDIDATES_LIMIT", "5")
    )

    return AnalyzeResponse(
        job_title=job_title,
        role_family=role,
        required_skills=required,
        must_have_skills=must_have,
        nice_to_have_skills=nice_to_have,
        ranked_candidates=ranked[:top_limit],
    )
