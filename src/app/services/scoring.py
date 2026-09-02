from app.schemas import CandidateInput, CandidateScore


def normalize(text: str) -> str:
    return text.lower().strip()


def get_skills(text: str) -> set[str]:
    skills = {
        "communication",
        "classroom management",
        "lesson planning",
        "teaching",
        "subject knowledge",
        "educational technology",
        "microsoft office",
        "leadership",
        "presentation",
        "creativity",
        "python",
        "java",
        "javascript",
        "sql",
        "machine learning",
        "data analysis",
        "excel",
    }

    text = normalize(text)
    return {skill for skill in skills if skill in text}


def score_candidate(
    candidate: CandidateInput,
    must_have: list[str],
    nice_to_have: list[str],
    role_family: str,
) -> CandidateScore:

    resume_skills = get_skills(candidate.resume_text)

    must = {normalize(skill) for skill in must_have}
    nice = {normalize(skill) for skill in nice_to_have}

    matched_must = sorted(resume_skills.intersection(must))
    matched_nice = sorted(resume_skills.intersection(nice))

    missing = sorted(must - resume_skills)

    must_rate = (
        len(matched_must) / len(must) * 100
        if must else 100
    )

    nice_rate = (
        len(matched_nice) / len(nice) * 100
        if nice else 0
    )

    skill_score = (must_rate * 0.7) + (nice_rate * 0.3)

    experience_score = min(candidate.years_experience * 20, 100)

    total_score = (
        skill_score * 0.7
        + experience_score * 0.3
    )

    matched = sorted(resume_skills.intersection(must.union(nice)))

    strengths = []
    concerns = []

    if matched_must:
        strengths.append(f"Matched {len(matched_must)} must-have skills")

    if matched_nice:
        strengths.append(f"Matched {len(matched_nice)} nice-to-have skills")

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
        key=lambda candidate: candidate.total_score,
        reverse=True,
    )