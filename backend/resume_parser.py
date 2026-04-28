import re
from collections import Counter
from pathlib import Path
from typing import BinaryIO

SKILL_GROUPS: dict[str, list[str]] = {
    "core_skills": [
        "python",
        "java",
        "c++",
        "javascript",
        "typescript",
        "machine learning",
        "deep learning",
        "data analysis",
        "data structures",
        "algorithms",
        "sql",
        "statistics",
        "legal research",
        "contract law",
        "accounting",
        "financial modeling",
        "biology",
        "anatomy",
        "writing",
        "editing",
    ],
    "tools": [
        "git",
        "docker",
        "kubernetes",
        "aws",
        "excel",
        "tableau",
        "figma",
        "jira",
        "linux",
        "bash",
        "autocad",
        "sketchup",
        "crm",
    ],
    "technologies": [
        "react",
        "node",
        "fastapi",
        "django",
        "html",
        "css",
        "tensorflow",
        "pytorch",
        "apis",
        "databases",
        "networking",
        "seo",
        "analytics",
    ],
    "soft_skills": [
        "communication",
        "public speaking",
        "mentoring",
        "patience",
        "leadership",
        "teamwork",
        "negotiation",
        "recruitment",
        "onboarding",
        "conflict resolution",
    ],
}

ALIASES = {
    "ml": ["machine learning", "deep learning"],
    "ai": ["machine learning", "deep learning"],
    "backend": ["apis", "databases"],
    "frontend": ["html", "css", "javascript", "react"],
    "web dev": ["html", "css", "javascript", "react"],
    "devops": ["docker", "kubernetes", "linux", "aws"],
}


def extract_text_from_upload(file: BinaryIO, filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf_text(file)

    content = file.read()
    if isinstance(content, bytes):
        return content.decode("utf-8", errors="ignore")
    return str(content)


def _extract_pdf_text(file: BinaryIO) -> str:
    try:
        import pdfplumber
    except ImportError as error:
        raise RuntimeError("PDF parsing needs pdfplumber. Install backend requirements.") from error

    text_parts = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts).strip()


def extract_structured_skills(text: str) -> dict[str, list[str]]:
    normalized = normalize_text(text)
    extracted: dict[str, list[str]] = {}

    for group, skills in SKILL_GROUPS.items():
        matches = []
        for skill in skills:
            pattern = r"(?<![a-z0-9+#.])" + re.escape(skill) + r"(?![a-z0-9+#.])"
            if re.search(pattern, normalized):
                matches.append(skill)
        extracted[group] = sorted(set(matches))

    for alias, expansions in ALIASES.items():
        if re.search(r"\b" + re.escape(alias) + r"\b", normalized):
            extracted["core_skills"].extend(expansions)

    for group in extracted:
        extracted[group] = sorted(set(extracted[group]))

    return extracted


def flatten_skills(structured_skills: dict[str, list[str]]) -> list[str]:
    flattened = []
    for skills in structured_skills.values():
        flattened.extend(skills)
    return sorted(set(skill.strip().lower() for skill in flattened if skill.strip()))


def expand_skills(skills: list[str]) -> list[str]:
    expanded = set(skill.strip().lower() for skill in skills if skill.strip())
    for skill in list(expanded):
        expanded.update(ALIASES.get(skill, []))
    return sorted(expanded)


def weighted_skill_scores(structured_skills: dict[str, list[str]]) -> dict[str, float]:
    weights = {
        "core_skills": 1.0,
        "tools": 0.7,
        "technologies": 0.8,
        "soft_skills": 0.3,
    }
    scores = {}
    for group, skills in structured_skills.items():
        for skill in skills:
            scores[skill] = max(scores.get(skill, 0.0), weights.get(group, 0.5))
    return scores


def skill_frequency(text: str, skills: list[str]) -> dict[str, int]:
    normalized = normalize_text(text)
    counter = Counter()
    for skill in skills:
        counter[skill] = len(re.findall(r"\b" + re.escape(skill) + r"\b", normalized))
    return dict(counter)


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#.\s-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()
