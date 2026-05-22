<<<<<<< HEAD
import google.generativeai as genai
import os
from typing import Optional, Dict, List
from dotenv import load_dotenv
import time

load_dotenv()

class GeminiLLM:
    """
    Google Gemini API wrapper
    FREE tier: 60 requests/min, 1500 requests/day
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        """
        Initialize Gemini client
        
        Models:
        - gemini-1.5-flash (RECOMMENDED) - Fast, free, 1M context
        - gemini-1.5-pro - Highest quality, 2M context
        - gemini-1.0-pro - Legacy, 32K context
        
        Args:
            api_key: Gemini API key (or from env)
            model_name: Model to use
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Gemini API key required. Get free key at: "
                "https://aistudio.google.com/app/apikey"
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
        # Safety settings (moderate)
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        # Generation config
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        self._test_connection()
    
    def _test_connection(self):
        """Test if API key is valid"""
        try:
            # Quick test
            response = self.model.generate_content("Say 'OK'")
            print(f"✅ Gemini {self.model_name} connected successfully!")
        except Exception as e:
            print(f"❌ Gemini connection error: {e}")
            raise
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8192
    ) -> str:
        """
        Generate text using Gemini
        
        Args:
            prompt: User prompt
            system_prompt: System instructions (prepended to prompt)
            temperature: Creativity (0.0-1.0)
            max_tokens: Max response length
        
        Returns:
            Generated text
        """
        
        # Combine system prompt and user prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt
        
        # Update config
        config = self.generation_config.copy()
        config['temperature'] = temperature
        config['max_output_tokens'] = max_tokens
        
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=config,
                safety_settings=self.safety_settings
            )
            
            return response.text
        
        except Exception as e:
            error_msg = str(e)
            
            if "quota" in error_msg.lower():
                return "⚠️ Quota exceeded. Please wait a moment or upgrade to paid tier."
            elif "safety" in error_msg.lower():
                return "⚠️ Content blocked by safety filters. Try rephrasing."
            else:
                return f"Error: {error_msg}"
    
    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        Stream response for real-time display
        
        Yields chunks of text as they're generated
        """
        
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt
        
        config = self.generation_config.copy()
        config['temperature'] = temperature
        
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=config,
                safety_settings=self.safety_settings,
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        except Exception as e:
            yield f"Error: {e}"
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Multi-turn conversation
        
        Args:
            messages: List of {'role': 'user'/'model', 'content': 'text'}
        
        Returns:
            Response text
        """
        
        chat = self.model.start_chat(history=[])
        
        for msg in messages:
            if msg['role'] == 'user':
                response = chat.send_message(msg['content'])
        
        return response.text
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            result = self.model.count_tokens(text)
            return result.total_tokens
        except:
            # Rough estimate: 1 token ≈ 4 characters
            return len(text) // 4

# Convenience functions for job portal

def analyze_job_match_gemini(
    resume_data: Dict,
    job_description: str,
    model: str = "gemini-1.5-flash"
) -> str:
    """Analyze job match using Gemini"""
    
    llm = GeminiLLM(model_name=model)
    
    system_prompt = """You are an expert career advisor and recruiter specializing in Singapore's IT market.
You provide detailed, actionable advice for job seekers."""
    
    prompt = f"""
Analyze the match between this resume and job description.

CANDIDATE PROFILE:
Summary: {resume_data.get('summary', '')}
Skills: {', '.join(resume_data.get('skills', []))}
Experience Highlights: {resume_data.get('experience', '')[:1000]}

JOB DESCRIPTION:
{job_description}

Provide a comprehensive analysis:

1. MATCH PERCENTAGE: Give an overall match score (e.g., "75% match")

2. MATCHING SKILLS:
   - List skills from resume that match job requirements
   - Highlight strongest matches

3. MISSING SKILLS:
   - Critical skills required but not in resume
   - Nice-to-have skills

4. RELEVANT EXPERIENCE:
   - Which experiences are most relevant
   - How to emphasize them

5. RESUME IMPROVEMENTS:
   - Specific changes to make
   - Keywords to add for ATS

6. SALARY INSIGHTS:
   - Appropriate range for Singapore market
   - Negotiation strategy

Be specific and actionable. Consider the candidate has 10+ years experience and targets SGD 15,000 monthly.
"""
    
    return llm.generate(prompt, system_prompt=system_prompt, temperature=0.7)

def generate_cover_letter_gemini(
    resume_data: Dict,
    job_description: str,
    company_name: str,
    model: str = "gemini-1.5-flash"
) -> str:
    """Generate cover letter using Gemini"""
    
    llm = GeminiLLM(model_name=model)
    
    system_prompt = """You are an expert cover letter writer specializing in IT roles in Singapore.
You write professional, engaging cover letters that get interviews."""
    
    prompt = f"""
Write a professional cover letter for this job application.

CANDIDATE BACKGROUND:
{resume_data.get('summary', '')}

KEY ACHIEVEMENTS:
- 10+ years IT leadership
- Led US\$400M business value delivery
- SAP/ERP expert
- APAC project management

SKILLS: {', '.join(resume_data.get('skills', [])[:15])}

JOB DESCRIPTION:
{job_description}

COMPANY: {company_name}

Requirements:
- Start with "Dear Hiring Manager,"
- Professional but warm tone
- 3-4 paragraphs (300-350 words)
- Highlight 2-3 specific achievements
- Show enthusiasm for Singapore IT market
- Mention salary expectation: SGD 15,000 monthly
- End with "Sincerely,"

Make it compelling and specific to this role.
"""
    
    return llm.generate(prompt, system_prompt=system_prompt, temperature=0.8)

def generate_interview_qa_gemini(
    resume_data: Dict,
    job_description: str,
    model: str = "gemini-1.5-flash"
) -> str:
    """Generate interview Q&A using Gemini"""
    
    llm = GeminiLLM(model_name=model)
    
    system_prompt = """You are an expert interview coach for IT professionals in Singapore.
You prepare candidates with realistic questions and strong STAR-method answers."""
    
    prompt = f"""
Generate comprehensive interview preparation for this candidate and role.

CANDIDATE PROFILE:
Experience: {resume_data.get('experience', '')[:2000]}
Key Skills: {', '.join(resume_data.get('skills', []))}

KEY ACHIEVEMENTS:
- US\$400M business value delivery
- 10+ years IT leadership
- SAP deployments across APAC
- 3PL migrations

JOB DESCRIPTION:
{job_description}

Generate:

1. TECHNICAL QUESTIONS (10):
   For each question provide:
   - The question
   - Professional answer using STAR method
   - Reference specific examples from candidate's background

2. BEHAVIORAL QUESTIONS (5):
   - Question
   - STAR-method answer with real examples
   
3. ACHIEVEMENT QUESTIONS (3):
   - How to discuss US\$400M value delivery
   - How to explain SAP expertise
   - How to position leadership experience

4. QUESTIONS TO ASK INTERVIEWER (5):
   - Thoughtful questions about role, team, technology

Format clearly with headers. Make answers sound natural and confident.
"""
    
    return llm.generate(prompt, system_prompt=system_prompt, temperature=0.7, max_tokens=4096)
=======
import google.generativeai as genai
import os
from typing import Optional, Dict, List
from dotenv import load_dotenv
import time

load_dotenv()

class GeminiLLM:
    """
    Google Gemini API wrapper
    FREE tier: 60 requests/min, 1500 requests/day
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        """
        Initialize Gemini client
        
        Models:
        - gemini-1.5-flash (RECOMMENDED) - Fast, free, 1M context
        - gemini-1.5-pro - Highest quality, 2M context
        - gemini-1.0-pro - Legacy, 32K context
        
        Args:
            api_key: Gemini API key (or from env)
            model_name: Model to use
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Gemini API key required. Get free key at: "
                "https://aistudio.google.com/app/apikey"
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
        # Safety settings (moderate)
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        # Generation config
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        self._test_connection()
    
    def _test_connection(self):
        """Test if API key is valid"""
        try:
            # Quick test
            response = self.model.generate_content("Say 'OK'")
            print(f"✅ Gemini {self.model_name} connected successfully!")
        except Exception as e:
            print(f"❌ Gemini connection error: {e}")
            raise
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8192
    ) -> str:
        """
        Generate text using Gemini
        
        Args:
            prompt: User prompt
            system_prompt: System instructions (prepended to prompt)
            temperature: Creativity (0.0-1.0)
            max_tokens: Max response length
        
        Returns:
            Generated text
        """
        
        # Combine system prompt and user prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt
        
        # Update config
        config = self.generation_config.copy()
        config['temperature'] = temperature
        config['max_output_tokens'] = max_tokens
        
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=config,
                safety_settings=self.safety_settings
            )
            
            return response.text
        
        except Exception as e:
            error_msg = str(e)
            
            if "quota" in error_msg.lower():
                return "⚠️ Quota exceeded. Please wait a moment or upgrade to paid tier."
            elif "safety" in error_msg.lower():
                return "⚠️ Content blocked by safety filters. Try rephrasing."
            else:
                return f"Error: {error_msg}"
    
    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        Stream response for real-time display
        
        Yields chunks of text as they're generated
        """
        
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt
        
        config = self.generation_config.copy()
        config['temperature'] = temperature
        
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=config,
                safety_settings=self.safety_settings,
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        except Exception as e:
            yield f"Error: {e}"
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Multi-turn conversation
        
        Args:
            messages: List of {'role': 'user'/'model', 'content': 'text'}
        
        Returns:
            Response text
        """
        
        chat = self.model.start_chat(history=[])
        
        for msg in messages:
            if msg['role'] == 'user':
                response = chat.send_message(msg['content'])
        
        return response.text
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            result = self.model.count_tokens(text)
            return result.total_tokens
        except:
            # Rough estimate: 1 token ≈ 4 characters
            return len(text) // 4

# Convenience functions for job portal

def analyze_job_match_gemini(
    resume_data: Dict,
    job_description: str,
    model: str = "gemini-1.5-flash"
) -> str:
    """Analyze job match using Gemini"""
    
    llm = GeminiLLM(model_name=model)
    
    system_prompt = """You are an expert career advisor and recruiter specializing in Singapore's IT market.
You provide detailed, actionable advice for job seekers."""
    
    prompt = f"""
Analyze the match between this resume and job description.

CANDIDATE PROFILE:
Summary: {resume_data.get('summary', '')}
Skills: {', '.join(resume_data.get('skills', []))}
Experience Highlights: {resume_data.get('experience', '')[:1000]}

JOB DESCRIPTION:
{job_description}

Provide a comprehensive analysis:

1. MATCH PERCENTAGE: Give an overall match score (e.g., "75% match")

2. MATCHING SKILLS:
   - List skills from resume that match job requirements
   - Highlight strongest matches

3. MISSING SKILLS:
   - Critical skills required but not in resume
   - Nice-to-have skills

4. RELEVANT EXPERIENCE:
   - Which experiences are most relevant
   - How to emphasize them

5. RESUME IMPROVEMENTS:
   - Specific changes to make
   - Keywords to add for ATS

6. SALARY INSIGHTS:
   - Appropriate range for Singapore market
   - Negotiation strategy

Be specific and actionable. Consider the candidate has 10+ years experience and targets SGD 15,000 monthly.
"""
    
    return llm.generate(prompt, system_prompt=system_prompt, temperature=0.7)

def generate_cover_letter_gemini(
    resume_data: Dict,
    job_description: str,
    company_name: str,
    model: str = "gemini-1.5-flash"
) -> str:
    """Generate cover letter using Gemini"""
    
    llm = GeminiLLM(model_name=model)
    
    system_prompt = """You are an expert cover letter writer specializing in IT roles in Singapore.
You write professional, engaging cover letters that get interviews."""
    
    prompt = f"""
Write a professional cover letter for this job application.

CANDIDATE BACKGROUND:
{resume_data.get('summary', '')}

KEY ACHIEVEMENTS:
- 10+ years IT leadership
- Led US\$400M business value delivery
- SAP/ERP expert
- APAC project management

SKILLS: {', '.join(resume_data.get('skills', [])[:15])}

JOB DESCRIPTION:
{job_description}

COMPANY: {company_name}

Requirements:
- Start with "Dear Hiring Manager,"
- Professional but warm tone
- 3-4 paragraphs (300-350 words)
- Highlight 2-3 specific achievements
- Show enthusiasm for Singapore IT market
- Mention salary expectation: SGD 15,000 monthly
- End with "Sincerely,"

Make it compelling and specific to this role.
"""
    
    return llm.generate(prompt, system_prompt=system_prompt, temperature=0.8)

def generate_interview_qa_gemini(
    resume_data: Dict,
    job_description: str,
    model: str = "gemini-1.5-flash"
) -> str:
    """Generate interview Q&A using Gemini"""
    
    llm = GeminiLLM(model_name=model)
    
    system_prompt = """You are an expert interview coach for IT professionals in Singapore.
You prepare candidates with realistic questions and strong STAR-method answers."""
    
    prompt = f"""
Generate comprehensive interview preparation for this candidate and role.

CANDIDATE PROFILE:
Experience: {resume_data.get('experience', '')[:2000]}
Key Skills: {', '.join(resume_data.get('skills', []))}

KEY ACHIEVEMENTS:
- US\$400M business value delivery
- 10+ years IT leadership
- SAP deployments across APAC
- 3PL migrations

JOB DESCRIPTION:
{job_description}

Generate:

1. TECHNICAL QUESTIONS (10):
   For each question provide:
   - The question
   - Professional answer using STAR method
   - Reference specific examples from candidate's background

2. BEHAVIORAL QUESTIONS (5):
   - Question
   - STAR-method answer with real examples
   
3. ACHIEVEMENT QUESTIONS (3):
   - How to discuss US\$400M value delivery
   - How to explain SAP expertise
   - How to position leadership experience

4. QUESTIONS TO ASK INTERVIEWER (5):
   - Thoughtful questions about role, team, technology

Format clearly with headers. Make answers sound natural and confident.
"""
    
    return llm.generate(prompt, system_prompt=system_prompt, temperature=0.7, max_tokens=4096)
>>>>>>> 1567d1cc7060c3393434b99c0f195ebd24a1f3c1
