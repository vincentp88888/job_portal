import re
from typing import Dict

class ATSOptimizer:
    """ATS optimization helper for resume and job matching."""

    def detect_missing_keywords(self, resume_data: Dict, job_description: str) -> str:
        resume_text = " ".join([
esume_data.get('summary', ''), resume_data.get('skills', ''), resume_data.get('experience', ''), resume_data.get('education', '')]).lower()
        required_skills = re.findall(r"\b(SAP|Python|Java|SQL|Agile|Scrum|Project Management|ERP|AWS|Azure|GCP|DevOps|Power BI|Tableau|Kubernetes|JIRA|Confluence|Leadership)\b", job_description, re.IGNORECASE)
        required_unique = []
        for skill in required_skills:
            normalized = skill.strip().title()
            if normalized not in required_unique:
                required_unique.append(normalized)

        missing = [skill for skill in required_unique if skill.lower() not in resume_text]
        if not missing:
            return "✅ No obvious keyword gaps were detected. Your resume text already includes the main job keywords."

        return (
            "⚠️ Missing important keywords for ATS and job-match scoring:\n"
            + "\n".join([f"- {skill}" for skill in missing])
            + "\n\nAdd these skills exactly as they appear in the job description if they truly match your experience."
        )

    def suggest_resume_improvements(self, job_description: str) -> str:
        bullets = [
            "Use standard headings: Summary, Skills, Experience, Education, Certifications.",
            "Avoid text in headers/footers and avoid complex tables or graphics.",
            "Keep bullet points short and action-oriented with measurable results.",
            "Include the exact job title and major skills from the posting early in your summary.",
            "Use consistent formatting and plain text so ATS can read the file correctly.",
        ]
        return "\n".join(bullets)

    def analyze_format(self, resume_data: Dict) -> str:
        warnings = []
        if len(resume_data.get('experience', '')) < 30:
            warnings.append("Experience section appears short. Add 3–4 strong achievement bullets.")
        if len(resume_data.get('summary', '')) < 40:
            warnings.append("Professional summary is short. Add 2–3 sentences that highlight your career story.")
        if not resume_data.get('skills'):
            warnings.append("No skills section was detected. Add a skills list with 8-12 keywords.")
        return "\n".join(warnings) if warnings else "No formatting warnings detected."
