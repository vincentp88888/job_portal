import re
from typing import Dict, Optional
from modules.gemini_llm import GeminiLLM

class JobParser:
    """Job description parser for structured job intelligence."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.llm = GeminiLLM(api_key=api_key, model_name=model)

    def parse_job_description(self, text: str) -> Dict[str, str]:
        text = text.strip()

        return {
            "title": self._extract_title(text),
            "location": self._extract_location(text),
            "salary": self._extract_salary(text),
            "experience_years": self._extract_experience_years(text),
            "skills": self._extract_skills(text),
            "responsibilities": self._extract_responsibilities(text),
            "summary": self._generate_summary(text),
        }

    def _extract_title(self, text: str) -> str:
        match = re.search(r"(Senior|Lead|Principal|Manager|Specialist|Engineer|Developer|Analyst|Consultant)[^\n]{1,80}", text, re.IGNORECASE)
        return match.group(0).strip() if match else "Not found"

    def _extract_location(self, text: str) -> str:
        match = re.search(r"(Singapore|Remote|Hybrid|[A-Z][a-z]+,\s*[A-Z][a-z]+|APAC|Asia|Australia)", text)
        return match.group(0).strip() if match else "Not specified"

    def _extract_salary(self, text: str) -> str:
        match = re.search(r"(SGD\s*[0-9,.]+|USD\s*[0-9,.]+|\$[0-9,.]+|\bRM\b[0-9,.]+)", text)
        return match.group(0).strip() if match else "Not specified"

    def _extract_experience_years(self, text: str) -> str:
        match = re.search(r"(\d+\+?\s*(?:years|yrs|year))", text, re.IGNORECASE)
        return match.group(0).strip() if match else "Not specified"

    def _extract_skills(self, text: str) -> str:
        skills = re.findall(
            r"\b(SAP|Python|Java|SQL|Agile|Scrum|Project Management|ERP|DevOps|AWS|Azure|GCP|Data Analytics|Power BI|Tableau|Kubernetes|JIRA|Confluence)\b",
            text,
            re.IGNORECASE,
        )
        unique = []
        for value in skills:
            normalized = value.strip().title()
            if normalized not in unique:
                unique.append(normalized)
        return ", ".join(unique) if unique else "Not specified"

    def _extract_responsibilities(self, text: str) -> str:
        match = re.search(r"(Responsibilities|Role Responsibilities|What you will do|You will be responsible for)(.*?)(Qualifications|Requirements|Skills|About the Role|What we look for)", text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(2).strip()
        return "Not specified"

    def _generate_summary(self, job_description: str) -> str:
        prompt = f"""
Read this job description and provide a concise summary of the role, key skills, experience level, and why it is a good fit for a senior IT professional.

Job Description:
{job_description}

Write the summary in 4 short bullet points.
"""
        return self.llm.generate(prompt, temperature=0.4)
