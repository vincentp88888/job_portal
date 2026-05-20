from modules.gemini_llm import GeminiLLM
from docx import Document
from pathlib import Path
from typing import Dict

class DocumentGenerator:
    """Generate documents using Google Gemini"""
    
    def __init__(self, api_key=None, model="gemini-1.5-flash"):
        """
        Initialize with Gemini
        gemini-1.5-flash is best for creative writing
        """
        self.llm = GeminiLLM(api_key=api_key, model_name=model)
    
    def generate_cover_letter(
        self,
        resume_data: Dict,
        job_description: str,
        company_name: str
    ) -> str:
        """Generate tailored cover letter"""
        
        system_prompt = """You are an expert cover letter writer for IT professionals in Singapore.
You write compelling, professional cover letters that get interviews."""
        
        prompt = f"""
Write a professional cover letter for this Singapore IT job application.

CANDIDATE BACKGROUND:
{resume_data.get('summary', '')}

KEY ACHIEVEMENTS:
- 10+ years IT leadership experience
- Led US\$400M business value delivery through supply chain improvements
- SAP/ERP expert (SAP APO, SAP MM, S/4HANA)
- Managed APAC-wide projects
- PMP & ITIL certified

SKILLS: {', '.join(resume_data.get('skills', [])[:20])}

JOB DESCRIPTION:
{job_description}

COMPANY: {company_name}

REQUIREMENTS:
- Address to "Dear Hiring Manager,"
- Professional but warm and engaging tone
- 3-4 paragraphs (300-350 words total)
- Opening: Express interest and highlight key qualification
- Body: 2-3 specific achievements that match job requirements
- Closing: Express enthusiasm, mention salary expectation (SGD 15,000/month), call to action
- End with "Sincerely,"
- NO placeholder brackets like [Your Name]

Make it specific to this role and compelling. Show genuine interest.
"""
        
        return self.llm.generate(
            prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=1500
        )
    
    def tailor_resume(self, resume_data: Dict, job_requirements: str) -> str:
        """Suggest resume modifications to match job"""
        
        system_prompt = """You are an expert resume optimizer and ATS specialist."""
        
        prompt = f"""
Optimize this resume to better match the job requirements.

CURRENT RESUME:
Summary: {resume_data.get('summary', '')}
Skills: {', '.join(resume_data.get('skills', []))}
Experience: {resume_data.get('experience', '')[:1000]}

JOB REQUIREMENTS:
{job_requirements}

Provide specific recommendations:

1. PROFESSIONAL SUMMARY REWRITE:
   - New version optimized for this role
   - Include key terms

2. SKILLS SECTION:
   - Which skills to emphasize
   - New skills to add (if applicable)
   - Order/grouping strategy

3. EXPERIENCE BULLETS:
   - Specific bullets to add/modify
   - Achievement quantification
   - Keywords to include

4. ATS OPTIMIZATION:
   - Critical keywords to add
   - Formatting tips
   - Section ordering

5. QUICK WINS:
   - 3 immediate changes for maximum impact

Be specific with exact wording suggestions.
"""
        
        return self.llm.generate(
            prompt,
            system_prompt=system_prompt,
            temperature=0.6,
            max_tokens=2000
        )
    
    def enhance_professional_summary(
        self,
        current_summary: str,
        target_role: str
    ) -> str:
        """Rewrite professional summary for target role"""
        
        prompt = f"""
Rewrite this professional summary to target this specific role:

CURRENT SUMMARY:
{current_summary}

TARGET ROLE: {target_role}

Create 3 versions:
1. Standard (50-60 words) - For general applications
2. ATS-optimized (60-70 words) - Keyword-rich
3. LinkedIn (80-100 words) - More conversational

Each should:
- Lead with years of experience
- Highlight relevant expertise
- Quantify achievements
- Include target role keywords
- End with value proposition
"""
        
        return self.llm.generate(prompt, temperature=0.7)
    
    def save_as_docx(self, content: str, filename: str) -> str:
        """Save content as DOCX file"""
        
        doc = Document()
        
        # Add content paragraph by paragraph
        for paragraph in content.split('\n\n'):
            if paragraph.strip():
                doc.add_paragraph(paragraph.strip())
        
        # Ensure drafts directory exists
        Path("drafts").mkdir(exist_ok=True)
        
        filepath = f"drafts/{filename}"
        doc.save(filepath)
        
        return filepath
