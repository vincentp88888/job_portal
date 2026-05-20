from modules.gemini_llm import GeminiLLM
from typing import Dict, Optional
import time

class AIJobMatcher:
    """Job matching using Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        """
        Initialize with Gemini
        
        Models:
        - gemini-1.5-flash (RECOMMENDED) - Fast, free tier friendly
        - gemini-1.5-pro - Best quality, 2M context
        
        Args:
            api_key: Gemini API key
            model: Model name
        """
        self.llm = GeminiLLM(api_key=api_key, model_name=model)
        self.model = model
    
    def analyze_job_match(self, resume_data: Dict, job_description: str) -> str:
        """Analyze how well resume matches job requirements"""
        
        system_prompt = """You are an expert career advisor and recruiter in Singapore's IT market.
You provide detailed, actionable advice for IT professionals."""
        
        prompt = f"""
Analyze the match between this resume and job description for Singapore IT market.

CANDIDATE PROFILE:
Professional Summary: {resume_data.get('summary', '')}

Key Skills: {', '.join(resume_data.get('skills', []))}

Experience Highlights: {resume_data.get('experience', '')[:1500]}

JOB DESCRIPTION:
{job_description}

Provide comprehensive analysis:

1. MATCH SCORE: Overall percentage (e.g., "78% match")

2. STRONG MATCHES:
   - Skills that align perfectly
   - Relevant experience

3. GAPS TO ADDRESS:
   - Critical missing skills
   - How to address them in application

4. EXPERIENCE RELEVANCE:
   - Which projects to highlight
   - Transferable skills

5. ATS OPTIMIZATION:
   - Keywords to add
   - Phrases to include

6. SALARY GUIDANCE (Singapore market):
   - Appropriate range
   - Negotiation tips
   - Consider candidate's 10+ years experience and SGD 15k target

Be specific and actionable.
"""
        
        return self.llm.generate(
            prompt,
            system_prompt=system_prompt,
            temperature=0.7
        )
    
    def extract_job_requirements(self, job_description: str) -> str:
        """Extract structured requirements from job posting"""
        
        prompt = f"""
Extract and structure the key requirements from this job description:

{job_description}

Format as:

REQUIRED SKILLS:
• [List each skill]

PREFERRED SKILLS:
• [List each skill]

EXPERIENCE REQUIRED:
• Years: [number]
• Type: [specific experience]

EDUCATION:
• [Requirements]

RESPONSIBILITIES:
• [Key duties]

SALARY (if mentioned):
• [Range or indication]

LOCATION/WORK MODE:
• [Details]

Be thorough and specific.
"""
        
        return self.llm.generate(prompt, temperature=0.3)
    
    def suggest_salary(
        self,
        job_title: str,
        experience_years: int,
        location: str = "Singapore"
    ) -> str:
        """Suggest competitive salary for Singapore market"""
        
        prompt = f"""
Provide salary guidance for this position in Singapore (2024):

Position: {job_title}
Experience: {experience_years} years
Location: {location}
Target: SGD 15,000 monthly (SGD 200,000 annually)

Provide:

1. MARKET RANGE:
   - Typical range for this role
   - By experience level

2. FACTORS AFFECTING SALARY:
   - Industry (IT/Tech)
   - Company size
   - Skills premium (SAP, ERP, Project Management)

3. NEGOTIATION STRATEGY:
   - What to ask for
   - How to justify
   - When to negotiate

4. TOTAL COMPENSATION:
   - Base salary
   - Bonus expectations
   - Benefits

Consider Singapore IT market rates, candidate's 10+ years experience, PMP certification, and SAP expertise.
"""
        
        return self.llm.generate(prompt, temperature=0.5)
    
    def compare_multiple_jobs(self, resume_data: Dict, jobs: list) -> str:
        """Compare multiple job opportunities"""
        
        jobs_text = "\n\n".join([
            f"JOB {i+1} - {job.get('company', 'Unknown')}:\n{job.get('description', '')[:500]}"
            for i, job in enumerate(jobs)
        ])
        
        prompt = f"""
Compare these job opportunities for this candidate:

CANDIDATE SKILLS: {', '.join(resume_data.get('skills', []))}

{jobs_text}

For each job, provide:
1. Match score
2. Pros and cons
3. Career growth potential
4. Recommendation

Then rank them by best fit.
"""
        
        return self.llm.generate(prompt, temperature=0.6)
