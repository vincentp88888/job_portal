from modules.llm_router import ModelRouter
from typing import Dict


class InterviewPrepGenerator:
    """Generate interview prep using the selected model backend."""

    def __init__(self, api_key=None, model="gemini-2.5-flash", llm=None):
        self.llm = llm or ModelRouter(provider="gemini", model_name=model, api_key=api_key)
    
    # Rest of the code stays the same...

    
    def generate_interview_qa(
        self,
        resume_data: Dict,
        job_description: str
    ) -> str:
        """Generate comprehensive interview preparation"""
        
        system_prompt = """You are an expert interview coach for IT professionals in Singapore.
You prepare candidates with realistic questions and strong STAR-method answers."""
        
        prompt = f"""
Create comprehensive interview preparation for this candidate and role.

CANDIDATE PROFILE:
Experience Summary: {resume_data.get('experience', '')[:2000]}

Key Skills: {', '.join(resume_data.get('skills', []))}

Major Achievements:
- Contributed to US\$400M annual business value (Asia Center of Excellence)
- Reduced US\$17M NWI in one year
- Led multiple APAC SAP deployments
- Managed 3PL migrations across Singapore, Thailand, Australia
- 10+ years IT leadership

JOB DESCRIPTION:
{job_description}

Generate detailed interview preparation:

━━━━━━━━━━━━━━━━━━━━━━━━
TECHNICAL QUESTIONS (10)
━━━━━━━━━━━━━━━━━━━━━━━━

[For each question:]
Q: [Question]
A: [Professional answer using STAR method, referencing specific experience]

━━━━━━━━━━━━━━━━━━━━━━━━
BEHAVIORAL QUESTIONS (5)
━━━━━━━━━━━━━━━━━━━━━━━━

[For each question:]
Q: [Question]
A: [STAR-method answer with real examples]

━━━━━━━━━━━━━━━━━━━━━━━━
ACHIEVEMENT DEEP-DIVES (3)
━━━━━━━━━━━━━━━━━━━━━━━━

1. US\$400M Business Value Delivery
   - How to explain
   - Key metrics
   - Your specific role

2. SAP/ERP Expertise
   - How to demonstrate
   - Technical depth
   - Business impact

3. Leadership & Stakeholder Management
   - Examples to use
   - Challenges overcome
   - Results achieved

━━━━━━━━━━━━━━━━━━━━━━━━
QUESTIONS TO ASK (8)
━━━━━━━━━━━━━━━━━━━━━━━━

About Role: [3 questions]
About Team: [2 questions]
About Technology: [2 questions]
About Growth: [1 question]

━━━━━━━━━━━━━━━━━━━━━━━━
SALARY NEGOTIATION
━━━━━━━━━━━━━━━━━━━━━━━━

Target: SGD 15,000 monthly
Strategy: [How to discuss and negotiate]

Make answers sound natural, confident, and specific. Use real examples from the candidate's experience.
"""
        
        return self.llm.generate(
            prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=4096
        )
    
    def generate_questions_to_ask(
        self,
        company_name: str,
        job_role: str
    ) -> str:
        """Generate smart questions candidate should ask"""
        
        prompt = f"""
Generate insightful questions a senior IT professional should ask when interviewing for:

Company: {company_name}
Role: {job_role}
Location: Singapore

Create 10 thoughtful questions across these categories:

1. ROLE & RESPONSIBILITIES (3 questions):
   - Day-to-day expectations
   - Success metrics
   - Team structure

2. TECHNOLOGY & PROJECTS (3 questions):
   - Tech stack
   - Current initiatives
   - Innovation priorities

3. CULTURE & TEAM (2 questions):
   - Team dynamics
   - Work environment

4. GROWTH & DEVELOPMENT (2 questions):
   - Career progression
   - Learning opportunities

Make questions show:
- Deep industry knowledge
- Strategic thinking
- Genuine interest
- Leadership mindset

Avoid generic questions like "What's the culture like?"
"""
        
        return self.llm.generate(prompt, temperature=0.7)
    
    def prepare_for_weakness_question(self) -> str:
        """Prepare answer for "What's your weakness?" question"""
        
        prompt = """
For an IT Project Manager with 10+ years experience, create a professional answer to:
"What is your biggest weakness?"

Requirements:
- Choose a real but non-critical weakness
- Show self-awareness
- Demonstrate how you're addressing it
- Turn it into a positive
- Keep to 1-2 minutes

Provide 3 different approaches the candidate can choose from.
"""
        
        return self.llm.generate(prompt, temperature=0.7)

    def get_answer_feedback(
        self,
        question: str,
        candidate_answer: str
    ) -> str:
        """Generate feedback on a candidate's interview answer."""

        system_prompt = """You are an expert interview coach for IT professionals in Singapore.
You provide constructive and actionable feedback on interview answers, focusing on the STAR method, relevance, clarity, and professionalism."""

        prompt = f"""
I am preparing for an interview. Here is a question and my answer. Please provide feedback on my answer.

INTERVIEW QUESTION:
{question}

MY ANSWER:
{candidate_answer}

Please evaluate my answer based on the following criteria:
1.  **Relevance and Directness:** Does the answer directly address the question?
2.  **STAR Method (if applicable):** If the question is behavioral, does the answer follow the Situation, Task, Action, Result (STAR) method effectively?
3.  **Clarity and Conciseness:** Is the answer easy to understand and free of jargon? Is it concise enough?
4.  **Professionalism:** Is the tone professional and confident?
5.  **Specific Examples:** Does the answer include specific and relevant examples from your experience?

Provide detailed and actionable feedback, suggesting improvements where necessary.
"""
        return self.llm.generate(
            prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1024
        )
