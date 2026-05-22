import openai
import os
from dotenv import load_dotenv

load_dotenv()

class AIJobMatcher:
    def __init__(self):
        # Use Claude or OpenAI
        self.api_key = os.getenv('OPENAI_API_KEY')
        openai.api_key = self.api_key
    
    def analyze_job_match(self, resume_data, job_description):
        """Analyze how well resume matches job requirements"""
        
        prompt = f"""
        Analyze the match between this resume and job description.
        
        RESUME SKILLS: {resume_data.get('skills', [])}
        RESUME EXPERIENCE: {resume_data.get('experience', '')}
        
        JOB DESCRIPTION:
        {job_description}
        
        Provide:
        1. Matching skills (%)
        2. Missing skills
        3. Relevant experience highlights
        4. Recommended resume improvements
        5. Suggested salary range for Singapore market
        """
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert career advisor and recruiter in Singapore's IT market."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.choices.message.content
    
    def extract_job_requirements(self, job_description):
        """Extract structured requirements from job posting"""
        prompt = f"""
        Extract from this job description:
        1. Required skills
        2. Preferred skills
        3. Years of experience
        4. Education requirements
        5. Salary range (if mentioned)
        6. Key responsibilities
        
        JOB DESCRIPTION:
        {job_description}
        
        Return as structured JSON.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return response.choices.message.content
    
    def suggest_salary(self, job_title, experience_years, location="Singapore"):
        """Suggest competitive salary"""
        prompt = f"""
        Suggest competitive salary for:
        - Position: {job_title}
        - Experience: {experience_years} years
        - Location: {location}
        - Target: SGD 15,000 monthly (SGD 200,000 annually)
        
        Consider:
        1. Current Singapore IT market rates
        2. Candidate experience level
        3. Industry standards
        4. Negotiation strategy
        """
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        
        return response.choices.message.content
