from dataclasses import dataclass
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from .database import list_jobs
    from .resume_parser import expand_skills, flatten_skills, weighted_skill_scores
except ImportError:
    from database import list_jobs
    from resume_parser import expand_skills, flatten_skills, weighted_skill_scores


@dataclass
class RecommendationProfile:
    skills: list[str]
    interests: list[str]
    education: str = ""
    structured_skills: dict[str, list[str]] | None = None


class JobRecommender:
    def __init__(self) -> None:
        self.jobs: list[dict[str, Any]] = []
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        self.tfidf_matrix = None

    def refresh(self) -> None:
        self.jobs = list_jobs(limit=1000)
        documents = [self._job_document(job) for job in self.jobs]
        self.tfidf_matrix = self.vectorizer.fit_transform(documents) if documents else None

    def recommend(self, profile: Any, limit: int = 8) -> list[dict[str, Any]]:
        normalized_profile = self._coerce_profile(profile)
        user_skills = set(expand_skills(normalized_profile.skills))
        if not user_skills or self.tfidf_matrix is None:
            return []

        weights = weighted_skill_scores(normalized_profile.structured_skills or {})
        query = " ".join(
            list(user_skills)
            + normalized_profile.interests
            + [normalized_profile.education]
        )
        query_vector = self.vectorizer.transform([query])
        tfidf_scores = cosine_similarity(query_vector, self.tfidf_matrix).flatten()

        results = []
        for index, job in enumerate(self.jobs):
            required = [skill.lower().strip() for skill in job.get("skills_required", [])]
            required_set = set(required)
            matched = sorted(user_skills.intersection(required_set))
            missing = sorted(required_set.difference(user_skills))

            weighted_overlap = self._weighted_overlap(required, user_skills, weights)
            plain_overlap = len(matched) / len(required_set) if required_set else 0.0
            embedding_proxy = tfidf_scores[index]
            final_score = (0.5 * embedding_proxy) + (0.3 * tfidf_scores[index]) + (0.2 * weighted_overlap)

            if final_score <= 0.01 and plain_overlap == 0:
                continue

            results.append(
                {
                    "id": job["id"],
                    "role": job["role"],
                    "company": job["company"],
                    "location": job.get("location", "remote"),
                    "date_posted": job.get("date_posted"),
                    "match_score": round(float(final_score), 4),
                    "tfidf_score": round(float(tfidf_scores[index]), 4),
                    "overlap_score": round(float(plain_overlap), 4),
                    "matched_skills": matched,
                    "missing_skills": missing[:6],
                    "skills_required": required,
                    "explanation": self._explain(job, matched, missing),
                }
            )

        results.sort(key=lambda item: item["match_score"], reverse=True)
        return results[:limit]

    def _coerce_profile(self, profile: Any) -> RecommendationProfile:
        if isinstance(profile, dict):
            structured = profile.get("structured_skills") or {}
            skills = profile.get("skills") or flatten_skills(structured)
            return RecommendationProfile(
                skills=[str(skill).lower().strip() for skill in skills if str(skill).strip()],
                interests=profile.get("interests") or [],
                education=profile.get("education") or "",
                structured_skills=structured,
            )

        structured = getattr(profile, "structured_skills", None) or {}
        skills = getattr(profile, "skills", None) or flatten_skills(structured)
        return RecommendationProfile(
            skills=[str(skill).lower().strip() for skill in skills if str(skill).strip()],
            interests=getattr(profile, "interests", []) or [],
            education=getattr(profile, "education", "") or "",
            structured_skills=structured,
        )

    def _job_document(self, job: dict[str, Any]) -> str:
        return " ".join(
            [
                job.get("role", ""),
                job.get("company", ""),
                job.get("description", ""),
                " ".join(job.get("skills_required", [])),
                job.get("location", ""),
            ]
        ).lower()

    def _weighted_overlap(
        self,
        required: list[str],
        user_skills: set[str],
        weights: dict[str, float],
    ) -> float:
        if not required:
            return 0.0
        possible = sum(weights.get(skill, 0.5) for skill in required)
        actual = sum(weights.get(skill, 0.5) for skill in required if skill in user_skills)
        return actual / possible if possible else 0.0

    def _explain(self, job: dict[str, Any], matched: list[str], missing: list[str]) -> str:
        if matched:
            matched_text = ", ".join(skill.title() for skill in matched[:4])
            if missing:
                missing_text = ", ".join(skill.title() for skill in missing[:3])
                return (
                    f"{job['role']} at {job['company']} matches because of {matched_text}. "
                    f"Learning {missing_text} would make this a stronger fit."
                )
            return f"{job['role']} at {job['company']} is a strong fit across the listed skills."

        missing_text = ", ".join(skill.title() for skill in missing[:3]) or "the listed skills"
        return f"This role is adjacent to your profile. Start with {missing_text} to close the gap."


recommender_instance = JobRecommender()
