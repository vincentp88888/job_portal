import openai

class InterviewPrepGenerator:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
    
    def generate_interview_qa(self, resume_data, job_description):
        """Generate likely interview questions and answers"""
        
        prompt = f"""
        Based on this candidate's background and job description, generate:
        1. 10 likely technical interview questions
        2. 5 behavioral interview questions
        3. Professional answers with examples from candidate's experience
        
        CANDIDATE EXPERIENCE:
        {resume_data.get('experience', '')}
        
        CANDIDATE SKILLS:
        {resume_data.get('skills', [])}
        
        JOB DESCRIPTION:
        {job_description}
        
        For each answer:
        - Use STAR method (Situation, Task, Action, Result)
        - Reference specific examples from resume
        - Keep answers concise (2-3 minutes speaking time)
        - Show enthusiasm for Singapore IT market
        """
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices.message.content
    
    def generate_questions_to_ask(self, company_name, job_role):
        """Generate smart questions candidate should ask"""
        
        prompt = f"""
        Generate 10 insightful questions a candidate should ask when interviewing for:
        - Company: {company_name}
        - Role: {job_role}
        - Location: Singapore
        
        Focus on:
        1. Team structure and culture
        2. Growth opportunities
        3. Technology stack and projects
        4. Success metrics
        5. Work-life balance in Singapore context
        """
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices.message.content
