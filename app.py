<<<<<<< HEAD
import streamlit as st
from modules.gemini_llm import GeminiLLM
from modules.ai_matcher import AIJobMatcher
from modules.document_generator import DocumentGenerator
from modules.interview_prep import InterviewPrepGenerator
from modules.resume_parser import ResumeParser
from modules.gmail_handler import GmailHandler
from modules.job_scraper import JobScraper
from modules.ai_tool import AIToolSearch
import os
import math
from datetime import datetime
import traceback

# Ensure folders exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("drafts", exist_ok=True)
os.makedirs("email_drafts", exist_ok=True)

# Page config
st.set_page_config(
    page_title="AI Job Portal - Powered by Gemini",
    page_icon="🚀",
    layout="wide"
)

def main():
    st.title("🚀 AI-Powered Job Application Portal")
    st.markdown("### Powered by Google Gemini 2.5 🤖")
    
    # Initialize session state
    if 'resume_data' not in st.session_state:
        st.session_state.resume_data = None
    if 'resume_path' not in st.session_state:
        st.session_state.resume_path = None
    if 'current_job' not in st.session_state:
        st.session_state.current_job = None
    if 'cover_letter_path' not in st.session_state:
        st.session_state.cover_letter_path = None
    if 'job_search_results' not in st.session_state:
        st.session_state.job_search_results = []
    if 'job_search_page' not in st.session_state:
        st.session_state.job_search_page = 1
    if 'selected_job_title' not in st.session_state:
        st.session_state.selected_job_title = ''
    if 'selected_job_company' not in st.session_state:
        st.session_state.selected_job_company = ''
    if 'selected_job_url' not in st.session_state:
        st.session_state.selected_job_url = ''
    if 'selected_job_description' not in st.session_state:
        st.session_state.selected_job_description = ''
    if 'selected_job_position' not in st.session_state:
        st.session_state.selected_job_position = ''

    # Sidebar Configuration
    with st.sidebar:
        st.header("📋 Configuration")
        
        st.subheader("🔑 Google Gemini API")
        
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            help="Get free key at: https://aistudio.google.com/app/apikey"
        )
        
        if api_key:
            os.environ['GEMINI_API_KEY'] = api_key
        
        model = st.selectbox(
            "Model",
            [
                "gemini-2.5-flash",
                "gemini-flash-latest",
                "gemini-2.5-pro",
                "gemini-pro-latest",
            ],
            index=0,
            help="gemini-2.5-flash is recommended"
        )
        
        if st.button("🧪 Test Connection"):
            if not api_key:
                st.error("Please enter API key first!")
            else:
                try:
                    with st.spinner("Testing..."):
                        test_llm = GeminiLLM(api_key=api_key, model_name=model)
                        response = test_llm.generate("Say hello", max_tokens=20)
                        st.success(f"✅ Working! Response: {response}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

        if st.button("📌 How to get Gemini Free / Pro Key"):
            st.info(
                "To apply for Gemini Free or Pro key, open Google Gemini Studio or Google Cloud Generative AI Studio. "
                "Sign in with your Google account, choose a free key/credits plan, or upgrade to Gemini Pro if available in your region. "
                "For Pro access, look for Gemini Pro or Workspace plans and request access from Google if you do not see it yet."
            )
            st.markdown(
                "- Free key: https://studio.google.ai/\n"
                "- Pro key: https://developers.generativeai.google/studio/\n"
                "- If you already have a Google Cloud project, enable the Generative AI API and create an API key."
            )

        st.divider()
        
        st.subheader("💼 Preferences")
        job_title = st.text_input("Job Title", "IT Project Manager", key="job_title")
        job_location = st.text_input("Location", "Singapore", key="job_location")
        min_salary = st.number_input("Min Salary (SGD/month)", value=15000, step=1000, key="min_salary")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📄 Upload Resume",
        "🔍 Analyze Jobs",
        "✉️ Generate Applications",
        "💼 Interview Prep",
        "🤖 AI Tool",
        "💖 Donate & Feedback"
    ])
    
    with tab1:
        st.header("📄 Upload Your Resume")
        
        uploaded_file = st.file_uploader(
            "Choose your resume (DOCX or PDF)",
            type=['docx', 'pdf']
        )
        
        if uploaded_file:
            try:
                file_path = f"uploads/{uploaded_file.name}"
                
                with open(file_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                parser = ResumeParser()
                
                with st.spinner("Parsing resume..."):
                    if uploaded_file.name.endswith('.docx'):
                        resume_data = parser.parse_docx(file_path)
                    else:
                        resume_data = parser.parse_pdf(file_path)
                
                st.success("✅ Resume uploaded and parsed!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📋 Skills Found:**")
                    for skill in resume_data.get('skills', [])[:10]:
                        st.write(f"• {skill}")
                
                with col2:
                    st.markdown("**📝 Summary:**")
                    st.write(resume_data.get('summary', '')[:200] + "...")
                
                st.session_state.resume_data = resume_data
                st.session_state.resume_path = file_path
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.code(traceback.format_exc())
    
    with tab2:
        st.header("🔍 Job Analysis")
        
        if st.session_state.resume_data is None:
            st.warning("⚠️ Please upload your resume first (Tab 1)")
            st.stop()
        
        if not api_key:
            st.warning("⚠️ Please enter Gemini API key in sidebar")
            st.stop()
        
        st.success("✅ Resume loaded")
        
        st.subheader("🔎 Search Jobs from Popular Portals")
        selected_sites = st.multiselect(
            "Job sites to search",
            ["LinkedIn", "Google", "Indeed", "JobStreet", "JobsDB", "Foundit", "MyFutureCareer"],
            default=["LinkedIn", "Google", "Indeed", "JobStreet", "JobsDB", "Foundit", "MyFutureCareer"],
        )

        search_title = st.text_input("Search Title", job_title, key="search_title")
        search_location = st.text_input("Search Location", job_location, key="search_location")

        st.info("Job search uses only job title, location, and your salary preference. It does not search by job description or company name.")
        use_gemini_grounding = st.checkbox(
            "Use Gemini Google Search Grounding (requires Gemini API Key)",
            value=False,
            help="Enable to let Gemini run live Google searches and aggregate results."
        )

        scraper = JobScraper(use_gemini_search=use_gemini_grounding, gemini_api_key=api_key, gemini_model=model)
        if st.button("🔎 Search Job Listings", key="search_jobs_button"):
            if not search_title:
                st.error("❌ Enter a search title to query job sites.")
            else:
                try:
                    with st.spinner("Searching jobs from selected portals..."):
                        job_results = scraper.search(
                            title=search_title,
                            location=search_location,
                            sites=selected_sites,
                            per_site_limit=20,
                            overall_limit=100,
                        )

                    st.session_state.job_search_results = job_results
                    st.session_state.job_search_page = 1

                    if job_results:
                        st.success(f"✅ Found {len(job_results)} job results")
                    else:
                        st.info("No results found. Try changing the title, location, or selected job boards.")
                except Exception as e:
                    st.error(f"❌ Job search error: {e}")
                    st.code(traceback.format_exc())

        job_results = st.session_state.job_search_results or []
        if job_results:
            total = len(job_results)
            pages = max(1, math.ceil(total / 20))
            st.markdown(f"**Showing {total} matching jobs across selected portals.**")
            st.session_state.job_search_page = st.number_input(
                "Page",
                min_value=1,
                max_value=pages,
                value=st.session_state.job_search_page,
                step=1,
                key="job_search_page_input"
            )

            start = (st.session_state.job_search_page - 1) * 20
            end = min(start + 20, total)
            for index, job in enumerate(job_results[start:end], start=start):
                with st.expander(f"{job['title']} at {job['company']} ({job['source']})"):
                    st.markdown(
                        f"**Company:** {job['company']}  \\n**Location:** {job['location']}  \\n**Source:** {job['source']}  \\n**Link:** [{job['url']}]({job['url']})"
                    )
                    if job.get('summary'):
                        st.write(job['summary'])

                    if st.button("Select this job", key=f"select_job_{index}"):
                        job_description_from_page = scraper.fetch_job_description(job['url']) or job.get('summary', '')
                        st.session_state.selected_job_title = job['title']
                        st.session_state.selected_job_company = job['company']
                        st.session_state.selected_job_url = job['url']
                        st.session_state.selected_job_description = job_description_from_page
                        st.session_state.selected_job_position = job['title']
                        st.success("✅ Selected job saved. Scroll down to continue with analysis.")

            st.markdown(f"Page {st.session_state.job_search_page} of {pages}")

        st.divider()
        st.subheader("📄 Job Selection for Analysis")
        col1, col2 = st.columns([2, 1])
        with col1:
            position_name = st.text_input(
                "Position / Job Title",
                st.session_state.selected_job_position or job_title,
                key="position_name"
            )
            job_url = st.text_input("Job URL (optional)", st.session_state.selected_job_url or "", key="job_url")
        with col2:
            company_name = st.text_input(
                "Company Name",
                st.session_state.selected_job_company or "",
                key="company_name"
            )

        job_description = st.text_area(
            "Paste Job Description",
            value=st.session_state.selected_job_description or "",
            height=300,
            placeholder="Paste the full job description here...",
            key="job_description"
        )

        if st.button("🎯 Analyze Job Match", type="primary"):
            if not job_description or len(job_description) < 50:
                st.error("❌ Please paste a complete job description")
            else:
                try:
                    matcher = AIJobMatcher(api_key=api_key, model=model)
                    
                    with st.spinner("Analyzing..."):
                        match_analysis = matcher.analyze_job_match(
                            st.session_state.resume_data,
                            job_description
                        )
                    
                    st.success("✅ Analysis Complete!")
                    st.markdown(match_analysis)
                    
                    with st.spinner("Extracting requirements..."):
                        requirements = matcher.extract_job_requirements(job_description)
                    
                    with st.expander("📋 Detailed Requirements"):
                        st.markdown(requirements)
                    
                    st.session_state.current_job = {
                        'url': job_url,
                        'description': job_description,
                        'company': company_name if company_name else 'Unknown Company',
                        'position': position_name,
                        'requirements': requirements,
                        'match_analysis': match_analysis
                    }
                    
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    st.code(traceback.format_exc())
    
    with tab3:
        st.header("✉️ Generate Applications")
        
        if st.session_state.current_job is None:
            st.warning("⚠️ Please analyze a job first (Tab 2)")
            st.info("👈 Go to 'Analyze Jobs' tab and click 'Analyze Job Match'")
            st.stop()
        
        if not api_key:
            st.warning("⚠️ Please enter API key in sidebar")
            st.stop()
        
        job = st.session_state.current_job
        company = job.get('company', 'Unknown Company')
        
        st.success(f"✅ Working on: **{company}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Cover Letter")
            
            if st.button("✨ Generate Cover Letter", use_container_width=True):
                try:
                    generator = DocumentGenerator(api_key=api_key, model=model)
                    
                    with st.spinner("Writing cover letter..."):
                        cover_letter = generator.generate_cover_letter(
                            st.session_state.resume_data,
                            job['description'],
                            company,
                            job.get('position', '') or company
                        )
                    
                    st.text_area("Cover Letter", cover_letter, height=400, key="cover_letter_display")
                    
                    filename = f"cover_letter_{company.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.docx"
                    filepath = generator.save_as_docx(cover_letter, filename)
                    
                    st.success(f"✅ Saved as {filename}")
                    
                    with open(filepath, 'rb') as f:
                        st.download_button(
                            "📥 Download Cover Letter",
                            f,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key="download_cover_letter"
                        )
                    
                    st.session_state.cover_letter_path = filepath
                    
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    st.code(traceback.format_exc())
        
        with col2:
            st.subheader("🎯 Resume Tips")
            
            if st.button("🔧 Get Suggestions", use_container_width=True):
                try:
                    generator = DocumentGenerator(api_key=api_key, model=model)
                    
                    with st.spinner("Analyzing..."):
                        suggestions = generator.tailor_resume(
                            st.session_state.resume_data,
                            job.get('requirements', '')
                        )
                        revised_resume = generator.revise_resume(
                            st.session_state.resume_data,
                            job.get('requirements', '')
                        )
                    
                    st.markdown("### ✅ Resume Improvement Suggestions")
                    st.markdown(suggestions)
                    
                    st.markdown("### ✍️ Revised Resume Draft")
                    st.text_area("Revised Resume", revised_resume, height=340, key="revised_resume_output")

                    filename = f"revised_resume_{company.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.docx"
                    filepath = generator.save_as_docx(revised_resume, filename)
                    st.success(f"✅ Revised resume draft saved as {filename}")

                    with open(filepath, 'rb') as f:
                        st.download_button(
                            "📥 Download Revised Resume",
                            f,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key="download_revised_resume"
                        )
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    st.code(traceback.format_exc())
        
        st.divider()
        
        st.subheader("📧 Create Email Draft")
        
        col1, col2 = st.columns(2)
        
        with col1:
            recipient_email = st.text_input("Recipient Email", key="recipient_email")
        
        with col2:
            email_subject = st.text_input(
                "Subject",
                value=f"Application for {company}",
                key="email_subject"
            )
        
        email_body = st.text_area(
            "Email Body",
            value=f"""Dear Hiring Manager,

I am writing to express my interest in the position at {company}. Please find attached my resume and cover letter.

With over 10 years of IT leadership experience, I am confident I can contribute to your team.

Best regards""",
            height=200,
            key="email_body"
        )
        
        if st.button("📧 Create Email Draft", type="primary", key="create_draft_button"):
            if not recipient_email:
                st.error("❌ Please enter recipient email")
            elif st.session_state.cover_letter_path is None:
                st.error("❌ Please generate cover letter first")
            else:
                try:
                    gmail = GmailHandler()
                    
                    attachments = [
                        st.session_state.get('resume_path'),
                        st.session_state.get('cover_letter_path')
                    ]
                    attachments = [a for a in attachments if a and os.path.exists(a)]
                    
                    with st.spinner("Creating email draft..."):
                        draft_path = gmail.create_draft_with_attachments(
                            to=recipient_email,
                            subject=email_subject,
                            body=email_body,
                            attachments=attachments
                        )
                    
                    st.success("✅ Email draft created!")
                    st.info(f"📁 Saved to: `{draft_path}`")
                    st.write("Download the .eml file and open it in your local email client (Outlook, Windows Mail, Thunderbird) to save it as a draft with attachments.")
                    
                    with open(draft_path, 'rb') as f:
                        st.download_button(
                            "📥 Download Email Draft",
                            f,
                            file_name=os.path.basename(draft_path),
                            mime="message/rfc822",
                            key="download_email_draft"
                        )
                    
                except Exception as e:
                    st.error(f"❌ Error creating email draft: {e}")
                    st.code(traceback.format_exc())
    
    with tab4:
        st.header("💼 Interview Preparation")
        
        if st.session_state.current_job is None:
            st.warning("⚠️ Please analyze a job first (Tab 2)")
            st.info("👈 Go to 'Analyze Jobs' tab and click 'Analyze Job Match'")
            st.stop()
        
        if not api_key:
            st.warning("⚠️ Please enter API key in sidebar")
            st.stop()
        
        job = st.session_state.current_job
        company = job.get('company', 'Unknown Company')
        
        st.success(f"✅ Preparing for: **{company}**")
        
        if st.button("🎯 Generate Interview Q&A", type="primary", use_container_width=True):
            try:
                prep = InterviewPrepGenerator(api_key=api_key, model=model)
                
                with st.spinner("Generating interview preparation... This may take 30-60 seconds"):
                    qa = prep.generate_interview_qa(
                        st.session_state.resume_data,
                        job['description']
                    )
                
                st.markdown(qa)
                
                st.download_button(
                    "📥 Download Interview Prep",
                    qa,
                    file_name=f"interview_prep_{company.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    key="download_interview_prep"
                )
                
            except Exception as e:
                st.error(f"❌ Error generating interview prep: {e}")
                st.code(traceback.format_exc())

    with tab5:
        st.header("🤖 AI Tool")
        st.markdown("Search AI agent skills on the internet, then run a helpful AI action using your portal data.")

        ai_skill_query = st.text_input(
            "AI Agent Skill Query",
            placeholder="e.g. resume parsing, ATS optimization, interview coach, cover letter generation",
            key="ai_skill_query"
        )

        if st.button("🔍 Search AI Skill", key="search_ai_skill"):
            if not ai_skill_query.strip():
                st.error("❌ Please enter an AI skill query.")
            else:
                try:
                    tool_search = AIToolSearch()
                    with st.spinner("Searching the internet for AI skill references..."):
                        search_results = tool_search.search_skill(ai_skill_query, limit=8)

                    if search_results:
                        st.success(f"✅ Found {len(search_results)} references")
                        for index, item in enumerate(search_results, start=1):
                            st.markdown(f"**{index}. [{item['title']}]({item['url']})**")
                            if item.get('summary'):
                                st.write(item['summary'])
                            st.divider()
                    else:
                        st.info("No AI skill references found. Try a broader query.")
                except Exception as e:
                    st.error(f"❌ Search failed: {e}")
                    st.code(traceback.format_exc())

        if st.button("▶ Run AI Tool", key="run_ai_tool"):
            if not ai_skill_query.strip():
                st.error("❌ Please enter an AI skill query first.")
            else:
                skill_text = ai_skill_query.lower()
                try:
                    if "resume" in skill_text:
                        if st.session_state.resume_data is None:
                            st.warning("📄 Upload a resume first in Tab 1 to run resume parsing.")
                        else:
                            st.success("✅ Running resume parsing skill...")
                            parser = ResumeParser()
                            parsed = st.session_state.resume_data
                            st.markdown("**Skills:**")
                            st.write(parsed.get('skills', []))
                            st.markdown("**Experience:**")
                            st.write(parsed.get('experience', ''))
                            st.markdown("**Education:**")
                            st.write(parsed.get('education', ''))

                    elif "job" in skill_text and ("match" in skill_text or "matching" in skill_text):
                        if st.session_state.current_job is None:
                            st.warning("🔎 Analyze a job first in Tab 2 to run job matching.")
                        else:
                            if not api_key:
                                st.error("⚠️ Gemini API key required for job matching.")
                            else:
                                st.success("✅ Running job matching skill...")
                                matcher = AIJobMatcher(api_key=api_key, model=model)
                                analysis = matcher.analyze_job_match(
                                    st.session_state.resume_data,
                                    st.session_state.current_job['description'],
                                )
                                st.markdown(analysis)

                    elif "cover" in skill_text or "letter" in skill_text:
                        if st.session_state.current_job is None:
                            st.warning("✉️ Analyze a job first in Tab 2 to generate a cover letter.")
                        elif st.session_state.resume_data is None:
                            st.warning("📄 Upload a resume first in Tab 1.")
                        elif not api_key:
                            st.error("⚠️ Gemini API key required for cover letter generation.")
                        else:
                            st.success("✅ Running cover letter generation skill...")
                            generator = DocumentGenerator(api_key=api_key, model=model)
                            cover_letter = generator.generate_cover_letter(
                                st.session_state.resume_data,
                                st.session_state.current_job['description'],
                                st.session_state.current_job.get('company', 'Company'),
                                st.session_state.current_job.get('position', '') or st.session_state.current_job.get('company', 'Company')
                            )
                            st.text_area("Cover Letter Output", cover_letter, height=320)

                    elif "interview" in skill_text:
                        if st.session_state.current_job is None:
                            st.warning("💼 Analyze a job first in Tab 2 to prepare interview questions.")
                        elif not api_key:
                            st.error("⚠️ Gemini API key required for interview prep.")
                        else:
                            st.success("✅ Running mock interview skill...")
                            prep = InterviewPrepGenerator(api_key=api_key, model=model)
                            qa = prep.generate_interview_qa(
                                st.session_state.resume_data,
                                st.session_state.current_job['description']
                            )
                            st.markdown(qa)

                    else:
                        st.info("🔧 Running a general AI tool skill using Gemini.")
                        if not api_key:
                            st.error("⚠️ Gemini API key required for general AI tool execution.")
                        else:
                            tool = GeminiLLM(api_key=api_key, model_name=model)
                            prompt = (
                                f"You are an AI engineering assistant. Provide a concise Python plan for how to implement the following AI agent skill: {ai_skill_query}. "
                                "Include a short code sketch and the main steps."
                            )
                            result = tool.generate(prompt, temperature=0.6)
                            st.markdown(result)
                except Exception as e:
                    st.error(f"❌ AI tool execution failed: {e}")
                    st.code(traceback.format_exc())

    with tab6:
        st.header("💖 Donate & Feedback")
        st.markdown(
            "Support the project and share feedback with Vincent at `vincentp88888@gmail.com`."
        )
        st.markdown(
            "- Email: `vincentp88888@gmail.com`\n"
            "- Send feedback about job search, cover letters, or app improvements.\n"
            "- Donations are welcome to help maintain the service and keep Gemini integrations up to date."
        )
        st.info(
            "Thank you for your support! Your feedback helps make the portal better and more reliable."
        )

if __name__ == "__main__":
    main()
=======
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
>>>>>>> 1567d1cc7060c3393434b99c0f195ebd24a1f3c1
