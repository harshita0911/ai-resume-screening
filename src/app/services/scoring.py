
from app.schemas import CandidateInput, CandidateScore

from app.services.skill_taxonomy import (
    extract_skills,
    normalize_skill_list,
)


def score_candidate(
    candidate: CandidateInput,
    must_have: list[str],
    nice_to_have: list[str],
    role_family: str,
) -> CandidateScore:

    # Extract skills from resume
    resume_skills = extract_skills(candidate.resume_text)

    # Normalize job requirements
    must = set(normalize_skill_list(must_have))
    nice = set(normalize_skill_list(nice_to_have))

    # Find matching skills
    matched_must = sorted(resume_skills & must)
    matched_nice = sorted(resume_skills & nice)

    # Find missing must-have skills
    missing = sorted(must - resume_skills)

    # Calculate match percentage
    must_rate = (
        len(matched_must) / len(must) * 100
        if must else 100
    )

    nice_rate = (
        len(matched_nice) / len(nice) * 100
        if nice else 0
    )

    skill_score = (
        must_rate * 0.7 + nice_rate * 0.3
    )

    # Experience score
    experience_score = min(
        candidate.years_experience * 20, 100
    )

    # Overall score
    total_score = (
        skill_score * 0.7 +
        experience_score * 0.3
    )

    matched = sorted(
        resume_skills & (must | nice)
    )

    strengths = []
    concerns = []

    if matched_must:
        strengths.append(
            f"Matched {len(matched_must)} must-have skills"
        )

    if matched_nice:
        strengths.append(
            f"Matched {len(matched_nice)} nice-to-have skills"
        )

    if missing:
        concerns.append(
            f"Missing skills: {', '.join(missing)}"
        )

    return CandidateScore(
        name=candidate.name,
        total_score=round(total_score, 2),
        role_family=role_family,
        skill_score=round(skill_score, 2),
        must_have_match_rate=round(must_rate, 2),
        nice_to_have_match_rate=round(nice_rate, 2),
        experience_score=round(experience_score, 2),
        hard_constraint_passed=must_rate >= 60,
        matched_skills=matched,
        missing_skills=missing,
        semantic_matches={},
        strengths=strengths,
        concerns=concerns,
    )


def rank_candidates(
    candidates: list[CandidateInput],
    role_family: str,
    required_skills: list[str],
    must_have_skills: list[str],
    nice_to_have_skills: list[str],
) -> list[CandidateScore]:

    scored = [
        score_candidate(
            candidate,
            must_have_skills,
            nice_to_have_skills,
            role_family,
        )
        for candidate in candidates
    ]

    return sorted(
        scored,
        key=lambda candidate: (
            -candidate.total_score,
            candidate.name.lower(),
        ),
    )
