import streamlit as st
from modules.resume_parser import ResumeParser
from modules.ai_matcher import AIJobMatcher
from modules.document_generator import DocumentGenerator
from modules.gmail_handler import GmailHandler
from modules.interview_prep import InterviewPrepGenerator
import os
from datetime import datetime

import streamlit as st
from modules.gemini_llm import GeminiLLM
from modules.ai_matcher import AIJobMatcher
from modules.document_generator import DocumentGenerator
from modules.interview_prep import InterviewPrepGenerator
from modules.resume_parser import ResumeParser
from modules.gmail_handler import GmailHandler
import os
from datetime import datetime

st.set_page_config(page_title="AI Job Application Portal", layout="wide")

def main():
    st.title("🚀 AI-Powered Job Application Portal")
    st.markdown("### Automate your job search in Singapore")
    
    # Sidebar
with st.sidebar:
    st.header("📋 Configuration")
    
    # Gemini API Key
    st.subheader("🔑 Google Gemini API")
    
    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        help="Get free key at: https://aistudio.google.com/app/apikey"
    )
    
    if api_key:
        os.environ['GEMINI_API_KEY'] = api_key
    
    # Model Selection - UPDATED WITH 2025 MODELS
    model = st.selectbox(
        "Model",
        [
            "gemini-2.5-flash",          # ⭐ RECOMMENDED - Stable, fast, 1M tokens
            "gemini-flash-latest",       # Always latest flash version
            "gemini-2.5-pro",            # Best quality
            "gemini-pro-latest",         # Always latest pro
            "gemini-2.0-flash",          # Older but stable
            "gemini-2.5-flash-lite",     # Lightest/fastest
        ],
        index=0,
        help="gemini-2.5-flash is recommended: fast, stable, 1M token context"
    )
    
    # Test Connection
    if st.button("🧪 Test Gemini Connection"):
        if not api_key:
            st.error("Please enter API key first!")
        else:
            try:
                from modules.gemini_llm import GeminiLLM
                
                with st.spinner(f"Testing {model}..."):
                    test_llm = GeminiLLM(api_key=api_key, model_name=model)
                    response = test_llm.generate("Say hello in one sentence", max_tokens=20)
                    
                    st.success(f"✅ {model} working!")
                    st.info(f"Response: {response}")
                    
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.code(str(e))
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📄 Upload Resume", 
        "🔍 Search Jobs", 
        "✉️ Generate Applications",
        "💼 Interview Prep",
        "📊 Track Applications"
    ])
    
    # Tab 1: Upload Resume
    with tab1:
        st.header("Upload Your Resume")
        uploaded_file = st.file_uploader(
            "Choose your resume (DOCX or PDF)", 
            type=['docx', 'pdf']
        )
        
        if uploaded_file:
            # Save file
            file_path = f"uploads/{uploaded_file.name}"
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # Parse resume
            parser = ResumeParser()
            if uploaded_file.name.endswith('.docx'):
                resume_data = parser.parse_docx(file_path)
            else:
                resume_data = parser.parse_pdf(file_path)
            
            st.success("✅ Resume uploaded and parsed!")
            
            # Display parsed data
            st.subheader("Extracted Information")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Skills Found:**")
                st.write(resume_data.get('skills', []))
            
            with col2:
                st.markdown("**Summary:**")
                st.write(resume_data.get('summary', '')[:200] + "...")
            
            # Store in session
            st.session_state['resume_data'] = resume_data
            st.session_state['resume_path'] = file_path
    
    # Tab 2: Job Search
    with tab2:
        st.header("Job Search")
        
        # Manual job input (since scraping is limited)
        st.info("⚠️ Automated scraping violates most job site ToS. Please paste job descriptions manually.")
        
        job_url = st.text_input("Job Posting URL")
        job_description = st.text_area("Paste Job Description", height=300)
        company_name = st.text_input("Company Name")
        
        if st.button("Analyze Job Match"):
            if 'resume_data' not in st.session_state:
                st.error("Please upload resume first!")
            else:
                matcher = AIJobMatcher()
                
                with st.spinner("Analyzing job match..."):
                    # Analyze match
                    match_analysis = matcher.analyze_job_match(
                        st.session_state['resume_data'],
                        job_description
                    )
                    
                    st.success("Analysis Complete!")
                    st.markdown(match_analysis)
                    
                    # Extract requirements
                    requirements = matcher.extract_job_requirements(job_description)
                    
                    # Store job data
                    st.session_state['current_job'] = {
                        'url': job_url,
                        'description': job_description,
                        'company': company_name,
                        'requirements': requirements,
                        'match_analysis': match_analysis
                    }
    
    # Tab 3: Generate Applications
    with tab3:
        st.header("Generate Application Materials")
        
        if 'current_job' not in st.session_state:
            st.warning("Please analyze a job first!")
        else:
            job = st.session_state['current_job']
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📝 Generate Cover Letter"):
                    generator = DocumentGenerator()
                    
                    with st.spinner("Generating cover letter..."):
                        cover_letter = generator.generate_cover_letter(
                            st.session_state['resume_data'],
                            job['description'],
                            job['company']
                        )
                        
                        st.text_area("Cover Letter", cover_letter, height=400)
                        
                        # Save as DOCX
                        filename = f"cover_letter_{job['company']}_{datetime.now().strftime('%Y%m%d')}.docx"
                        file_path = generator.save_as_docx(cover_letter, filename)
                        
                        st.success(f"✅ Saved as {filename}")
                        st.session_state['cover_letter_path'] = file_path
            
            with col2:
                if st.button("📄 Tailor Resume"):
                    generator = DocumentGenerator()
                    
                    with st.spinner("Generating tailored resume suggestions..."):
                        suggestions = generator.tailor_resume(
                            st.session_state['resume_data'],
                            job['requirements']
                        )
                        
                        st.text_area("Resume Suggestions", suggestions, height=400)
            
            st.divider()
            
            # Gmail Draft
            st.subheader("Create Gmail Draft")
            
            recipient_email = st.text_input("Recipient Email")
            email_subject = st.text_input(
                "Email Subject",
                value=f"Application for {job.get('company', '')}"
            )
            email_body = st.text_area(
                "Email Body",
                value=f"Dear Hiring Manager,\n\nPlease find attached my application for the position at {job.get('company', '')}.\n\nBest regards"
            )
            
            if st.button("📧 Create Gmail Draft"):
                if 'cover_letter_path' not in st.session_state:
                    st.error("Please generate cover letter first!")
                else:
                    gmail = GmailHandler()
                    
                    attachments = [
                        st.session_state.get('resume_path'),
                        st.session_state.get('cover_letter_path')
                    ]
                    
                    draft_id = gmail.create_draft_with_attachments(
                        to=recipient_email,
                        subject=email_subject,
                        body=email_body,
                        attachments=attachments
                    )
                    
                    st.success(f"✅ Draft created! Draft ID: {draft_id}")
                    st.info("Check your Gmail drafts folder")
    
    # Tab 4: Interview Prep
    with tab4:
        st.header("Interview Preparation")
        
        if 'current_job' not in st.session_state:
            st.warning("Please analyze a job first!")
        else:
            if st.button("Generate Interview Q&A"):
                prep = InterviewPrepGenerator()
                
                with st.spinner("Generating interview questions..."):
                    qa = prep.generate_interview_qa(
                        st.session_state['resume_data'],
                        st.session_state['current_job']['description']
                    )
                    
                    st.markdown(qa)
                    
                    # Questions to ask
                    st.subheader("Questions You Should Ask")
                    questions = prep.generate_questions_to_ask(
                        st.session_state['current_job']['company'],
                        job_title
                    )
                    st.markdown(questions)
    
    # Tab 5: Track Applications
    with tab5:
        st.header("Application Tracker")
        st.info("🚧 Coming soon: Track application status automatically")
        
        # Placeholder for tracking functionality
        st.dataframe({
            'Company': [],
            'Position': [],
            'Applied Date': [],
            'Status': [],
            'Last Follow-up': []
        })

if __name__ == "__main__":
    main()
