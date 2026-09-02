from pydantic import BaseModel, Field


class CandidateInput(BaseModel):
    name: str = Field(..., min_length=1)
    resume_text: str = Field(..., min_length=30)
    years_experience: float = Field(0, ge=0)


class AnalyzeRequest(BaseModel):
    job_title: str = Field(..., min_length=2)
    role_family: str | None = None
    job_description: str = Field(..., min_length=10)
    must_have_skills: list[str] = Field(default_factory=list)
    nice_to_have_skills: list[str] = Field(default_factory=list)
    candidates: list[CandidateInput] = Field(..., min_length=1)


class CandidateScore(BaseModel):
    name: str
    total_score: float
    role_family: str
    skill_score: float
    must_have_match_rate: float
    nice_to_have_match_rate: float
    experience_score: float
    hard_constraint_passed: bool
    matched_skills: list[str]
    missing_skills: list[str]
    semantic_matches: dict[str, list[str]]
    strengths: list[str]
    concerns: list[str]


class AnalyzeResponse(BaseModel):
    job_title: str
    role_family: str
    required_skills: list[str]
    must_have_skills: list[str]
    nice_to_have_skills: list[str]
    ranked_candidates: list[CandidateScore]


class UploadProfilePreview(BaseModel):
    file_name: str
    status: str
    candidate_name: str | None = None
    years_experience: float | None = None
    detected_skills: list[str] = Field(default_factory=list)
    message: str | None = None


class PreviewFilesResponse(BaseModel):
    previews: list[UploadProfilePreview]