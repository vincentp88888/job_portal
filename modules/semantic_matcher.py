from typing import Optional

try:
    from sentence_transformers import SentenceTransformer, util
except ImportError:
    SentenceTransformer = None
    util = None

class SemanticMatcher:
    """Semantic resume to job matching using sentence embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if SentenceTransformer is None:
            raise ImportError(
                "sentence-transformers is required for semantic matching. Install it with 'pip install sentence-transformers'"
            )
        self.model = SentenceTransformer(model_name)

    def calculate_match_score(self, resume_text: str, job_text: str) -> float:
        resume_text = resume_text.strip()
        job_text = job_text.strip()
        if not resume_text or not job_text:
            return 0.0

        embeddings = self.model.encode([resume_text, job_text], convert_to_tensor=True)
        score = util.cos_sim(embeddings[0], embeddings[1]).item()
        return round(float(score) * 100, 1)

    def extract_top_skill_matches(self, resume_skills: list[str], job_text: str, limit: int = 8) -> list[str]:
        if not resume_skills:
            return []

        text = job_text.lower()
        matches = [skill for skill in resume_skills if skill.lower() in text]
        if not matches:
            return resume_skills[:limit]
        return matches[:limit]
