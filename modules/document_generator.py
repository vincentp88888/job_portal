from modules.llm_router import ModelRouter
from docx import Document
from pathlib import Path
from typing import Dict


class DocumentGenerator:
    """Generate documents using the selected model backend."""

    def __init__(self, api_key=None, model="gemini-2.5-flash", llm=None):
        """Initialize the selected LLM backend."""
        self.llm = llm or ModelRouter(provider="gemini", model_name=model, api_key=api_key)
    
    # Rest of the code stays the same...

    
    def generate_cover_letter(
        self,
        resume_data: Dict,
        job_description: str,
        company_name: str,
        position_name: str
    ) -> str:
        """Generate tailored cover letter"""
        
        system_prompt = """You are an expert cover letter writer for IT professionals in Singapore.
You write compelling, professional cover letters that get interviews."""
        
        prompt = f"""
Write a professional cover letter for this Singapore IT job application.

EMPLOYER: {company_name}
POSITION: {position_name}

CANDIDATE BACKGROUND:
{resume_data.get('summary', '')}

KEY ACHIEVEMENTS:
- 10+ years IT leadership experience
- Led US$400M business value delivery through supply chain improvements
- SAP/ERP expert (SAP APO, SAP MM, S/4HANA)
- Managed APAC-wide projects
- PMP & ITIL certified

SKILLS: {', '.join(resume_data.get('skills', [])[:20])}

JOB DESCRIPTION:
{job_description}

Please include:
- Employer name and position title in the opening paragraph
- A concise summary of why the candidate is a strong match for the role
- Specific examples from the resume that map to the job requirements
- A professional tone and call to action

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

    def revise_resume(self, resume_data: Dict, job_requirements: str) -> str:
        """Create a revised resume draft based on job requirements and original skills."""
        
        system_prompt = """You are an expert resume writer who rewrites candidate resumes for job applications."""
        
        prompt = f"""
Use this candidate's original resume details and the target job requirements to create a revised resume draft.

CURRENT RESUME INFORMATION:
Summary: {resume_data.get('summary', '')}
Skills: {', '.join(resume_data.get('skills', []))}
Experience: {resume_data.get('experience', '')[:1200]}
Education: {resume_data.get('education', '')}

JOB REQUIREMENTS:
{job_requirements}

Produce a revised resume draft with these sections:
- Professional Summary
- Core Skills
- Professional Experience
- Education
- Certifications / Projects (if available)

Use strong achievement language, preserve candidate facts, and add keywords from the target role.
Format the output as plain text with clear headings.
"""
        
        return self.llm.generate(
            prompt,
            system_prompt=system_prompt,
            temperature=0.65,
            max_tokens=2200
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
