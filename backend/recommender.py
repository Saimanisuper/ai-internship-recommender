import json
import logging
import pathlib
from typing import List, Dict, Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging for better readability and debugging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Define the absolute path to the mock dataset
DATA_PATH = pathlib.Path(__file__).parent / "data" / "internships.json"

class InternshipRecommender:
    """
    A unified Machine Learning engine to rank internships for a student profile
    using TF-IDF Vectorization and Cosine Similarity.
    """

    def __init__(self):
        """Initializes the recommender by loading data and training the TF-IDF model."""
        self.internships = self._load_dataset()
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self._train_tfidf_model()

    def _load_dataset(self) -> List[Dict[str, Any]]:
        """
        Loads the static JSON dataset containing internship postings.

        Returns:
            List[Dict]: A list of internship dictionary objects.
        """
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as error:
            logging.error(f"Error loading {DATA_PATH}: {error}")
            return []

    def _train_tfidf_model(self):
        """
        Prepares the document corpus based on required skills and trains the TF-IDF model.

        Returns:
            sparse matrix or None: The fitted TF-IDF matrix representing the corpus.
        """
        self.documents = []
        for internship in self.internships:
            # Normalize the skills and join them into a single String "document"
            skills_list = internship.get("skills_required", [])
            skills_string = " ".join([skill.lower().strip() for skill in skills_list])
            self.documents.append(skills_string)
            
        if self.documents:
            return self.vectorizer.fit_transform(self.documents)
        return None

    def _normalize_user_skills(self, profile) -> set:
        """
        Extracts, cleans, and deduplicates the skills from the user's profile.

        Args:
            profile: Pydantic model representing the student profile.
            
        Returns:
            set: A set of normalized, lowercase skill strings.
        """
        user_skills_raw = getattr(profile, 'skills', [])
        cleaned_skills = [skill.strip().lower() for skill in user_skills_raw if skill.strip()]
        return set(cleaned_skills)

    def _generate_explanation(self, matched: List[str], missing: List[str]) -> str:
        """
        Generates a human-readable explanation based on matched and missing skills.

        Args:
            matched: A list of matched valid skills.
            missing: A list of skills lacking in the user's profile.

        Returns:
            str: The generated explanation.
        """
        if matched:
            matched_formatted = ", ".join([m.title() for m in matched])
            explanation = f"You match this role due to {matched_formatted}."
            
            if missing:
                missing_formatted = ", ".join([m.title() for m in missing])
                explanation += f" Learning {missing_formatted} will improve your chances."
        else:
            missing_formatted = ", ".join([m.title() for m in missing]) if missing else "the required skills"
            explanation = f"While you don't have exact technical matches, your profile loosely aligns with this role. Learning {missing_formatted} is recommended."
        
        return explanation

    def recommend(self, profile) -> List[Dict[str, Any]]:
        """
        Recommends ranked internships based on a user's profile.

        Args:
            profile: Pydantic model containing the user's skills and interests.

        Returns:
            List[Dict]: A list of sorted and evaluated internships.
        """
        # 1. Normalize user's input skills
        user_skills_set = self._normalize_user_skills(profile)
        if not user_skills_set or self.tfidf_matrix is None:
            return []
            
        # 2. Vectorize the user's search query and compute cosine similarities
        user_query = " ".join(user_skills_set)
        query_vector = self.vectorizer.transform([user_query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        results = []
        
        # 3. Evaluate each internship listing against the user's similarity rating
        for idx, similarity_score in enumerate(similarities):
            internship = self.internships[idx]
            
            req_skills = [s.strip().lower() for s in internship.get("skills_required", [])]
            req_skills_set = set(req_skills)
            
            # Identify intersections to feed our explainable AI response
            matched = list(user_skills_set.intersection(req_skills_set))
            missing = list(req_skills_set.difference(user_skills_set))
            
            # Compute a hybrid score bridging pure ML string similarity with explicit keyword matching
            basic_match_ratio = len(matched) / len(req_skills_set) if req_skills_set else 0.0
            hybrid_score = (similarity_score * 0.7) + (basic_match_ratio * 0.3)
            
            # Ignore listings where the score is negligibly low
            if hybrid_score <= 0.01:
                continue
                
            # Synthesize the explanation
            explanation = self._generate_explanation(matched, missing)
                
            results.append({
                "role": internship["role"],
                "company": internship["company"],
                "location": internship.get("location", "N/A"),
                "match_score": hybrid_score,
                "matched_skills": matched,
                "missing_skills": missing,
                "explanation": explanation
            })
            
        # 4. Sort descending by match_score and return to the Frontend
        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results

# Singleton instance to expose directly to FastAPI endpoint
recommender_instance = InternshipRecommender()
