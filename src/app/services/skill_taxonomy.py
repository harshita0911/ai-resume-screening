import re


SKILLS = {
    # Teaching
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

    # Common technical skills
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "sql",
    "html",
    "css",
    "react",
    "node",
    "django",
    "flask",
    "fastapi",
    "machine learning",
    "deep learning",
    "data analysis",
    "pandas",
    "numpy",
    "tensorflow",
    "pytorch",
    "excel",
    "power bi",
    "tableau",
    "aws",
    "azure",
    "docker",
}


ALIASES = {
    "ml": "machine learning",
    "machine-learning": "machine learning",
    "ms office": "microsoft office",
    "microsoft word": "microsoft office",
    "word": "microsoft office",
    "powerpoint": "presentation",
    "ppt": "presentation",
    "communication skills": "communication",
    "classroom-management": "classroom management",
    "lesson-planning": "lesson planning",
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def normalize_skill_name(skill: str) -> str:
    skill = normalize_text(skill)
    return ALIASES.get(skill, skill)


def extract_skills(text: str) -> set[str]:
    text = normalize_text(text)
    found = set()

    for skill in SKILLS:
        pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"

        if re.search(pattern, text):
            found.add(skill)

    for alias, canonical in ALIASES.items():
        pattern = rf"(?<!\w){re.escape(alias)}(?!\w)"

        if re.search(pattern, text):
            found.add(canonical)

    return found


def normalize_skill_list(
    skills: list[str],
) -> list[str]:

    normalized = {
        normalize_skill_name(skill)
        for skill in skills
        if skill.strip()
    }

    return sorted(normalized)