
import re

SKILLS = {
    # Programming languages
    "python", "java", "javascript", "typescript",
    "c++", "c#", "php", "ruby", "go", "swift",
    "kotlin", "r",

    # Web development
    "html", "css", "react", "node.js", "angular",
    "vue", "next.js", "django", "flask", "fastapi",
    "express.js", "bootstrap", "tailwind css",

    # Data and AI
    "machine learning", "deep learning",
    "artificial intelligence",
    "natural language processing",
    "data analysis", "data science",
    "pandas", "numpy", "tensorflow", "pytorch",
    "scikit-learn", "computer vision",

    # Database
    "sql", "mysql", "postgresql", "mongodb",
    "sqlite", "oracle",

    # Tools
    "excel", "microsoft office", "microsoft word",
    "power bi", "tableau", "git", "github",
    "docker", "kubernetes", "aws", "azure",

    # Soft skills
    "communication", "leadership", "teamwork",
    "problem solving", "time management",
    "critical thinking", "presentation",

    # Teaching
    "teaching", "classroom management",
    "lesson planning", "subject knowledge",
    "educational technology", "creativity",
}

ALIASES = {
    "ml": "machine learning",
    "machine-learning": "machine learning",
    "ai": "artificial intelligence",
    "nlp": "natural language processing",
    "js": "javascript",
    "react.js": "react",
    "nodejs": "node.js",
    "node js": "node.js",
    "ms office": "microsoft office",
    "ms word": "microsoft word",
    "powerbi": "power bi",
    "scikit learn": "scikit-learn",
    "problem-solving": "problem solving",
    "time-management": "time management",
    "team work": "teamwork",
    "ppt": "presentation",
    "powerpoint": "presentation",
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def normalize_skill_name(skill: str) -> str:
    skill = normalize_text(skill)
    return ALIASES.get(skill, skill)


def _contains_skill(text: str, skill: str) -> bool:
    pattern = (
        rf"(?<![a-z0-9]){re.escape(skill)}(?![a-z0-9])"
    )
    return re.search(pattern, text) is not None


def extract_skills(text: str) -> set[str]:
    text = normalize_text(text)
    found = set()

    for skill in SKILLS:
        if _contains_skill(text, skill):
            found.add(skill)

    for alias, canonical in ALIASES.items():
        if _contains_skill(text, alias):
            found.add(canonical)

    return found


def normalize_skill_list(skills: list[str]) -> list[str]:
    return sorted({
        normalize_skill_name(skill)
        for skill in skills
        if skill and skill.strip()
    })
