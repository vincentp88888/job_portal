import docx
import PyPDF2
from pathlib import Path
import re

class ResumeParser:
    def __init__(self):
        self.skills = []
        self.experience = []
        self.education = []
        
    def parse_docx(self, file_path):
        """Parse DOCX resume"""
        doc = docx.Document(file_path)
        full_text = "\n".join([para.text for para in doc.paragraphs])
        return self._extract_sections(full_text)
    
    def parse_pdf(self, file_path):
        """Parse PDF resume"""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text()
        return self._extract_sections(full_text)
    
    def _extract_sections(self, text):
        """Extract key sections using regex and NLP"""
        return {
            'full_text': text,
            'skills': self._extract_skills(text),
            'experience': self._extract_experience(text),
            'education': self._extract_education(text),
            'summary': self._extract_summary(text)
        }
    
    def _extract_skills(self, text):
        # Basic skill extraction - enhance with NLP
        skills_keywords = ['SAP', 'Python', 'Java', 'SQL', 'Agile', 'Project Management']
        found_skills = [skill for skill in skills_keywords if skill.lower() in text.lower()]
        return found_skills
    
    def _extract_experience(self, text):
        # Extract experience section
        exp_pattern = r'(PROFESSIONAL EXPERIENCE|WORK EXPERIENCE)(.*?)(EDUCATION|CERTIFICATIONS|\$)'
        match = re.search(exp_pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(2).strip() if match else ""
    
    def _extract_education(self, text):
        # Extract education section
        edu_pattern = r'(EDUCATION)(.*?)(CERTIFICATIONS|TECHNICAL SKILLS|\$)'
        match = re.search(edu_pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(2).strip() if match else ""
    
    def _extract_summary(self, text):
        # Extract professional summary
        summary_pattern = r'(PROFESSIONAL SUMMARY|SUMMARY)(.*?)(CORE COMPETENCIES|EXPERIENCE|\$)'
        match = re.search(summary_pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(2).strip() if match else ""
