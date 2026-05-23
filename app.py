import json
import re
import streamlit as st
from modules.llm_router import ModelRouter
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
    page_title="AI Job Portal",
    page_icon="🚀",
    layout="wide"
)


def _application_signature(job_description: str, company: str, position: str) -> str:
    return "|".join([
        (job_description or "").strip(),
        (company or "Unknown Company").strip(),
        (position or "").strip(),
    ])


def _generate_application_assets(
    resume_data,
    job_description: str,
    company: str,
    position: str,
    api_key,
    selected_model: str,
    model_provider,
):
    if resume_data is None:
        raise ValueError("Please upload a resume before generating applications.")

    if not job_description or not job_description.strip():
        raise ValueError("Please enter a job description before generating applications.")

    matcher = AIJobMatcher(api_key=api_key, model=selected_model, llm=model_provider)
    requirements = matcher.extract_job_requirements(job_description)

    generator = DocumentGenerator(api_key=api_key, model=selected_model, llm=model_provider)

    cover_letter = generator.generate_cover_letter(
        resume_data,
        job_description,
        company,
        position or company,
    )
    resume_tips = generator.tailor_resume(resume_data, requirements)
    revised_resume = generator.revise_resume(resume_data, requirements)

    cover_letter_filename = f"cover_letter_{company.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    resume_filename = f"revised_resume_{company.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"

    cover_letter_path = generator.save_as_docx(cover_letter, cover_letter_filename)
    revised_resume_path = generator.save_as_docx(revised_resume, resume_filename)

    return {
        "requirements": requirements,
        "cover_letter": cover_letter,
        "cover_letter_path": cover_letter_path,
        "resume_tips": resume_tips,
        "revised_resume": revised_resume,
        "revised_resume_path": revised_resume_path,
        "email_body": cover_letter,
    }


def _create_email_draft(recipient_email: str, subject: str, body: str, resume_path: str, cover_letter_path: str) -> str:
    gmail = GmailHandler()
    attachments = [resume_path, cover_letter_path]
    attachments = [attachment for attachment in attachments if attachment and os.path.exists(attachment)]
    return gmail.create_draft_with_attachments(
        to=recipient_email,
        subject=subject,
        body=body,
        attachments=attachments,
    )


def _build_resume_summary(resume_data) -> str:
    if resume_data is None:
        return "No resume attached."

    skills = ", ".join(resume_data.get('skills', [])[:20])
    summary = resume_data.get('summary', '')
    experience = resume_data.get('experience', '')
    education = resume_data.get('education', '')

    return (
        f"Summary: {summary}\n"
        f"Skills: {skills}\n"
        f"Experience: {experience[:1500]}\n"
        f"Education: {education}"
    )


def _parse_question_list(raw_text: str) -> list[str]:
    questions = []
    for line in raw_text.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        cleaned = re.sub(r'^[\-\*•]+\s*', '', cleaned)
        cleaned = re.sub(r'^\d+[\).\-\s]+', '', cleaned)
        if cleaned.lower().startswith('questions:'):
            cleaned = cleaned.split(':', 1)[1].strip()
        if cleaned:
            questions.append(cleaned)

    unique = []
    for question in questions:
        if question and question not in unique:
            unique.append(question)
    return unique


def _build_question_fallback(resume_data, role: str, company: str, count: int) -> list[str]:
    skills = resume_data.get('skills', []) if resume_data else []
    summary = resume_data.get('summary', '') if resume_data else ''
    experience = resume_data.get('experience', '') if resume_data else ''

    skill_reference = skills[0] if skills else 'your main skill'
    fallback_questions = [
        f"Can you tell me about a time you used {skill_reference} to solve a real work problem?",
        f"How would you describe your approach to working with a {role.lower()} team?",
        f"What results are you most proud of in your recent work experience?",
        f"How do you manage competing priorities and deadlines in a professional setting?",
        f"Tell me about a situation where you improved a process or delivered a better outcome.",
        f"How do you communicate clearly with managers, clients, or stakeholders?",
        f"What makes you a strong fit for this role at {company}?",
        f"How do you handle feedback when a manager or teammate gives you a different view?",
        f"Can you walk me through one challenge in your previous role and how you handled it?",
        f"What would you do first in your first 30 days in this role?",
        f"How do you keep learning and improving in your current field?",
        f"Describe a moment when you took ownership and led a project to completion.",
        f"How do you balance teamwork with independent work?",
        f"What skills from your resume are most relevant to this opportunity?",
        f"How would your previous manager describe your working style?",
        f"What would success look like to you in this role at {company}?",
        f"How do you stay organized when you have multiple priorities at once?",
        f"Can you give an example of when you adapted quickly to change?",
        f"How do you make sure your work is accurate and professional?",
        f"What do you want to learn next in your career?",
        f"Why are you interested in this position, and how does your background support it?",
    ]

    if summary:
        fallback_questions.append(f"Can you connect your background to the goals of this role at {company} using one example from your resume?")
    if experience:
        fallback_questions.append("Tell me about the most important responsibility you had in your previous role and the outcome.")

    return fallback_questions[:count]


def _generate_interview_question_batch(
    model_provider,
    resume_data,
    job_description: str,
    company: str,
    interviewer_role: str,
    target_count: int = 20,
) -> list[str]:
    all_questions = []
    attempts = 0

    while len(all_questions) < target_count and attempts < 3:
        remaining = target_count - len(all_questions)
        prompt = f"""
You are a professional interview coach and recruiter. Create {remaining} unique, professional, simple-English interview questions for {interviewer_role} at {company}.

Use only the candidate's real resume details and the job description. Do not invent skills, achievements, company history, or experience that is not in the resume.

Candidate resume:
{_build_resume_summary(resume_data)}

Job description:
{job_description}

Return only a numbered list of {remaining} questions. Each question should be short, realistic, and suitable for a spoken answer.
"""

        with st.spinner(f"Preparing {remaining} interview questions for {interviewer_role}..."):
            raw_output = model_provider.generate(prompt, temperature=0.7, max_tokens=1800).strip()

        parsed = _parse_question_list(raw_text=raw_output)
        for question in parsed:
            if question and question not in all_questions:
                all_questions.append(question)

        attempts += 1

    if len(all_questions) < target_count:
        fallback_questions = _build_question_fallback(resume_data, interviewer_role, company, target_count - len(all_questions))
        for question in fallback_questions:
            if question and question not in all_questions:
                all_questions.append(question)

    return all_questions[:target_count]


def _generate_model_answer_for_question(
    model_provider,
    resume_data,
    job_description: str,
    company: str,
    interviewer_role: str,
    question: str,
) -> str:
    prompt = f"""
You are the candidate. Answer this interview question using only the facts in the resume and job description.

Interviewer role: {interviewer_role}
Company: {company}
Job description: {job_description}
Candidate resume:
{_build_resume_summary(resume_data)}

Question:
{question}

Rules:
- Use simple, professional English.
- Answer in first person.
- Use only experience and skills that are actually in the resume.
- If the resume does not show a direct example, say so briefly and connect the answer to the closest relevant skill or experience.
- Keep it concise: 2 to 4 sentences.
"""

    with st.spinner("Preparing model answer..."):
        return model_provider.generate(prompt, temperature=0.55, max_tokens=400).strip()


def _assess_interview_answer(
    model_provider,
    resume_data,
    job_description: str,
    company: str,
    interviewer_role: str,
    question: str,
    answer: str,
) -> str:
    interview_prep_generator = InterviewPrepGenerator(llm=model_provider)
    with st.spinner("Assessing your response..."):
        return interview_prep_generator.get_answer_feedback(
            question=question,
            candidate_answer=answer
        )


def _interview_mic_component(question: str) -> str:
    current_question = (question or "").replace("'", "\\'")
    html = f"""
<div class="interview-mic-card">
  <style>
    .interview-mic-card {{
      border: 1px solid #d1d5db;
      border-radius: 16px;
      padding: 16px;
      background: linear-gradient(180deg, #f8fafc, #ffffff);
      font-family: Arial, sans-serif;
    }}
    .interview-mic-card textarea {{
      width: 100%;
      min-height: 110px;
      border-radius: 12px;
      border: 1px solid #cbd5e1;
      padding: 12px;
      font-size: 14px;
      box-sizing: border-box;
      margin-top: 12px;
      resize: vertical;
    }}
    .interview-mic-actions {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 12px;
    }}
    .interview-mic-actions button {{
      border: 0;
      border-radius: 999px;
      padding: 10px 14px;
      cursor: pointer;
      font-weight: 700;
    }}
    .interview-mic-primary {{ background: #0f172a; color: white; }}
    .interview-mic-secondary {{ background: #e2e8f0; color: #0f172a; }}
    .interview-mic-status {{
      margin-top: 10px;
      color: #334155;
      font-size: 14px;
    }}
    .interview-mic-note {{
      margin-top: 10px;
      color: #475569;
      font-size: 13px;
    }}
  </style>
  <div><strong>🎤 Speak your answer</strong></div>
  <div class="interview-mic-note">Use your browser microphone to capture a spoken reply. Your speech will be written into the answer box below.</div>
  <textarea id="interview-mic-transcript" placeholder="Your spoken reply will appear here."></textarea>
  <div class="interview-mic-actions">
    <button id="start-btn" class="interview-mic-primary">Start Mic</button>
    <button id="stop-btn" class="interview-mic-secondary">Stop Mic</button>
    <button id="clear-btn" class="interview-mic-secondary">Clear</button>
    <button id="speak-btn" class="interview-mic-secondary">Read Question Aloud</button>
  </div>
  <div class="interview-mic-status" id="interview-mic-status">Click Start Mic to begin speaking.</div>
</div>
<script>
let recognition = null;
let currentTranscript = '';
const transcriptBox = document.getElementById('interview-mic-transcript');
const status = document.getElementById('interview-mic-status');
const questionText = {json.dumps(current_question)};

function updateStatus(message) {{
  status.textContent = message;
}}

function sendComponentValue(value) {{
  try {{
    if (window.parent && window.parent.postMessage) {{
      window.parent.postMessage({{type: 'streamlit:setComponentValue', value: value}}, '*');
    }}
  }} catch (error) {{
    console.warn('Unable to send transcript to Streamlit:', error);
  }}
}}

if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {{
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.lang = 'en-US';

  recognition.onstart = function() {{
    updateStatus('Listening... speak clearly and pause when done.');
  }};

  recognition.onresult = function(event) {{
    let interim = '';
    let finalText = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {{
      const result = event.results[i];
      if (result.isFinal) {{
        finalText += result[0].transcript + ' ';
      }} else {{
        interim += result[0].transcript;
      }}
    }}
    currentTranscript = (finalText || interim).trim();
    transcriptBox.value = currentTranscript;
    sendComponentValue(currentTranscript);
    if (finalText) {{
      updateStatus('Transcript captured. Review and submit your answer.');
    }} else {{
      updateStatus('Listening...');
    }}
  }};

  recognition.onerror = function(event) {{
    updateStatus('Microphone error: ' + (event.error || 'unknown error'));
  }};

  recognition.onend = function() {{
    if (!currentTranscript) {{
      updateStatus('Microphone stopped.');
    }}
  }};
}} else {{
  updateStatus('Speech recognition is not supported in this browser.');
}}

const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const clearBtn = document.getElementById('clear-btn');
const speakBtn = document.getElementById('speak-btn');

startBtn.addEventListener('click', function() {{
  if (recognition) {{
    currentTranscript = '';
    transcriptBox.value = '';
    recognition.start();
  }}
}});

stopBtn.addEventListener('click', function() {{
  if (recognition) {{
    recognition.stop();
  }}
}});

clearBtn.addEventListener('click', function() {{
  currentTranscript = '';
  transcriptBox.value = '';
  updateStatus('Answer cleared.');
  sendComponentValue('');
}});

speakBtn.addEventListener('click', function() {{
  if ('speechSynthesis' in window) {{
    const utterance = new SpeechSynthesisUtterance(questionText);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    speechSynthesis.cancel();
    speechSynthesis.speak(utterance);
    updateStatus('Question is being read aloud.');
  }} else {{
    updateStatus('Text-to-speech is not supported in this browser.');
  }}
}});
</script>
</div>
"""
    component_value = st.components.v1.html(html, height=320)
    if isinstance(component_value, str):
        st.session_state.interview_spoken_reply = component_value
    return st.session_state.interview_spoken_reply


def main():
    st.title("🚀 AI-Powered Job Application Portal")
    st.markdown("### AI-powered job application assistant 🤖")

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
    if 'generated_application_signature' not in st.session_state:
        st.session_state.generated_application_signature = ''
    if 'interview_job_description' not in st.session_state:
        st.session_state.interview_job_description = ''
    if 'interview_company_name' not in st.session_state:
        st.session_state.interview_company_name = ''
    if 'interview_job_url' not in st.session_state:
        st.session_state.interview_job_url = ''
    if 'interview_role_1' not in st.session_state:
        st.session_state.interview_role_1 = 'Hiring Manager'
    if 'interview_role_2' not in st.session_state:
        st.session_state.interview_role_2 = 'HR Manager'
    if 'interview_role_3' not in st.session_state:
        st.session_state.interview_role_3 = 'Department Head'
    if 'interview_questions' not in st.session_state:
        st.session_state.interview_questions = []
    if 'interview_simulation_messages' not in st.session_state:
        st.session_state.interview_simulation_messages = []
    if 'interview_simulation_active' not in st.session_state:
        st.session_state.interview_simulation_active = False
    if 'interview_current_question_index' not in st.session_state:
        st.session_state.interview_current_question_index = 0
    if 'interview_spoken_reply' not in st.session_state:
        st.session_state.interview_spoken_reply = ''
    if 'interview_last_comparison' not in st.session_state:
        st.session_state.interview_last_comparison = None
    if 'generated_cover_letter' not in st.session_state:
        st.session_state.generated_cover_letter = ''
    if 'generated_cover_letter_path' not in st.session_state:
        st.session_state.generated_cover_letter_path = None
    if 'generated_resume_draft' not in st.session_state:
        st.session_state.generated_resume_draft = ''
    if 'generated_resume_tips' not in st.session_state:
        st.session_state.generated_resume_tips = ''
    if 'generated_resume_path' not in st.session_state:
        st.session_state.generated_resume_path = None
    if 'generated_email_body' not in st.session_state:
        st.session_state.generated_email_body = ''
    if 'generated_email_draft_path' not in st.session_state:
        st.session_state.generated_email_draft_path = None
    if 'generated_email_draft_signature' not in st.session_state:
        st.session_state.generated_email_draft_signature = ''

    # Sidebar Configuration
    with st.sidebar:
        st.header("📋 Configuration")

        model_choice = st.selectbox(
            "AI Model",
            [
                "Gemini 2.5 Flash",
                "Ollama llama3.1:8b",
            ],
            index=0,
            help="Choose the model used across the job portal workflows."
        )

        if model_choice == "Gemini 2.5 Flash":
            selected_provider = "gemini"
            selected_model = "gemini-2.5-flash"
            st.caption("Uses Gemini 2.5 Flash. Requires a Gemini API key.")
        else:
            selected_provider = "ollama"
            selected_model = "llama3.1:8b"
            st.caption("Uses local Ollama at http://localhost:11434. Make sure llama3.1:8b is pulled.")

        st.subheader("🔑 Gemini API")

        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            help="Get free key at: https://aistudio.google.com/app/apikey"
        )

        if api_key:
            os.environ['GEMINI_API_KEY'] = api_key

        model_provider = ModelRouter(
            provider=selected_provider,
            model_name=selected_model,
            api_key=api_key,
        )

        if st.button("🧪 Test Connection"):
            try:
                with st.spinner("Testing..."):
                    response = model_provider.generate("Say hello", max_tokens=20)
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
        
        if selected_provider == "gemini" and not api_key:
            st.warning("⚠️ Please enter Gemini API key in sidebar")

        if st.session_state.resume_data is not None:
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
        can_use_gemini_grounding = selected_provider == "gemini" and bool(api_key)
        use_gemini_grounding = st.checkbox(
            "Use Gemini Google Search Grounding (requires Gemini API Key)",
            value=False,
            disabled=not can_use_gemini_grounding,
            help="Enable to let Gemini run live Google searches and aggregate results."
        )
        if selected_provider == "ollama":
            st.caption("Google Search Grounding is only available when Gemini is selected.")
        elif not api_key:
            st.caption("Enter a Gemini API key to enable Google Search Grounding.")

        scraper = JobScraper(
            use_gemini_search=bool(use_gemini_grounding and can_use_gemini_grounding),
            gemini_api_key=api_key if selected_provider == "gemini" else None,
            gemini_model=selected_model,
        )
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
            if st.session_state.resume_data is None:
                st.warning("⚠️ Upload a resume first before analyzing a job.")
            elif not job_description or len(job_description) < 50:
                st.error("❌ Please paste a complete job description")
            else:
                try:
                    matcher = AIJobMatcher(api_key=api_key, model=selected_model, llm=model_provider)

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

        if selected_provider == "gemini" and not api_key:
            st.warning("⚠️ Please enter API key in sidebar")

        job = st.session_state.current_job or {}
        company = st.session_state.selected_job_company or job.get('company', 'Unknown Company')
        position = st.session_state.selected_job_position or job.get('position', '')
        job_description = st.session_state.selected_job_description or job.get('description', '')
        application_signature = _application_signature(job_description, company, position)

        has_job_description = bool(job_description.strip())
        has_resume = st.session_state.resume_data is not None
        can_generate_applications = has_job_description and has_resume and not (selected_provider == "gemini" and not api_key)

        if not has_job_description:
            st.warning("⚠️ Paste or select a job description in Tab 2 before generating applications.")

        if not has_resume:
            st.warning("⚠️ Upload a resume before generating applications.")

        if can_generate_applications and st.session_state.generated_application_signature != application_signature:
            try:
                assets = _generate_application_assets(
                    st.session_state.resume_data,
                    job_description,
                    company,
                    position,
                    api_key,
                    selected_model,
                    model_provider,
                )

                st.session_state.generated_application_signature = application_signature
                st.session_state.generated_cover_letter = assets['cover_letter']
                st.session_state.generated_cover_letter_path = assets['cover_letter_path']
                st.session_state.generated_resume_draft = assets['revised_resume']
                st.session_state.generated_resume_tips = assets['resume_tips']
                st.session_state.generated_resume_path = assets['revised_resume_path']
                st.session_state.generated_email_body = assets['email_body']
                st.session_state.cover_letter_path = assets['cover_letter_path']
                st.session_state.generated_email_draft_path = None
                st.session_state.generated_email_draft_signature = ''
                st.session_state.current_job = {
                    **job,
                    'description': job_description,
                    'company': company,
                    'position': position,
                    'requirements': assets['requirements'],
                }
                st.success("✅ Personalized cover letter and resume draft generated automatically.")
            except Exception as e:
                st.error(f"❌ Error generating applications: {e}")
                st.code(traceback.format_exc())

        if company:
            st.success(f"✅ Working on: **{company}**")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📝 Cover Letter")
            st.text_area(
                "Cover Letter",
                value=st.session_state.generated_cover_letter,
                height=400,
                key="cover_letter_display",
            )

            if st.session_state.generated_cover_letter_path:
                with open(st.session_state.generated_cover_letter_path, 'rb') as f:
                    st.download_button(
                        "📥 Download Cover Letter",
                        f,
                        file_name=os.path.basename(st.session_state.generated_cover_letter_path),
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="download_cover_letter",
                    )

            if st.button("🔄 Regenerate Cover Letter", use_container_width=True):
                try:
                    assets = _generate_application_assets(
                        st.session_state.resume_data,
                        job_description,
                        company,
                        position,
                        api_key,
                        selected_model,
                        model_provider,
                    )
                    st.session_state.generated_cover_letter = assets['cover_letter']
                    st.session_state.generated_cover_letter_path = assets['cover_letter_path']
                    st.session_state.generated_email_body = assets['email_body']
                    st.session_state.cover_letter_path = assets['cover_letter_path']
                    st.session_state.generated_email_draft_path = None
                    st.session_state.generated_email_draft_signature = ''
                    st.session_state.generated_application_signature = application_signature
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error regenerating cover letter: {e}")
                    st.code(traceback.format_exc())

        with col2:
            st.subheader("🎯 Resume Tips")
            st.markdown("### ✅ Resume Improvement Suggestions")
            st.markdown(st.session_state.generated_resume_tips)

            st.markdown("### ✍️ Revised Resume Draft")
            st.text_area(
                "Revised Resume",
                value=st.session_state.generated_resume_draft,
                height=340,
                key="revised_resume_output",
            )

            if st.session_state.generated_resume_path:
                with open(st.session_state.generated_resume_path, 'rb') as f:
                    st.download_button(
                        "📥 Download Revised Resume",
                        f,
                        file_name=os.path.basename(st.session_state.generated_resume_path),
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="download_revised_resume",
                    )

            if st.button("🔄 Regenerate Resume Draft", use_container_width=True):
                try:
                    assets = _generate_application_assets(
                        st.session_state.resume_data,
                        job_description,
                        company,
                        position,
                        api_key,
                        selected_model,
                        model_provider,
                    )
                    st.session_state.generated_resume_draft = assets['revised_resume']
                    st.session_state.generated_resume_tips = assets['resume_tips']
                    st.session_state.generated_resume_path = assets['revised_resume_path']
                    st.session_state.generated_email_body = assets['email_body']
                    st.session_state.generated_email_draft_path = None
                    st.session_state.generated_email_draft_signature = ''
                    st.session_state.generated_application_signature = application_signature
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error regenerating resume draft: {e}")
                    st.code(traceback.format_exc())

        st.divider()

        st.subheader("📧 Create Email Draft")

        col1, col2 = st.columns(2)

        with col1:
            recipient_email = st.text_input(
                "Recipient Email",
                value=st.session_state.get("application_recipient_email", ""),
                key="recipient_email",
            )
            st.session_state.application_recipient_email = recipient_email

        with col2:
            email_subject = st.text_input(
                "Subject",
                value=f"Application for {company}",
                key="email_subject",
            )

        email_body = st.text_area(
            "Email Body",
            value=st.session_state.generated_email_body or f"""Dear Hiring Manager,

I am writing to express my interest in the position at {company}. Please find attached my resume and cover letter.

With over 10 years of IT leadership experience, I am confident I can contribute to your team.

Best regards""",
            height=200,
            key="email_body",
        )
        st.session_state.generated_email_body = email_body

        draft_signature = f"{application_signature}::{recipient_email.strip()}"
        if recipient_email and st.session_state.generated_email_draft_signature != draft_signature:
            try:
                draft_path = _create_email_draft(
                    recipient_email,
                    email_subject,
                    email_body,
                    st.session_state.resume_path,
                    st.session_state.cover_letter_path,
                )
                st.session_state.generated_email_draft_path = draft_path
                st.session_state.generated_email_draft_signature = draft_signature
                st.success("✅ Email draft created automatically.")
            except Exception as e:
                st.error(f"❌ Error creating email draft: {e}")
                st.code(traceback.format_exc())

        if st.session_state.generated_email_draft_path:
            with open(st.session_state.generated_email_draft_path, 'rb') as f:
                st.download_button(
                    "📥 Download Email Draft",
                    f,
                    file_name=os.path.basename(st.session_state.generated_email_draft_path),
                    mime="message/rfc822",
                    key="download_email_draft",
                )

        if st.button("📧 Recreate Email Draft", type="primary", key="create_draft_button"):
            if not recipient_email:
                st.error("❌ Please enter recipient email")
            elif st.session_state.cover_letter_path is None:
                st.error("❌ Please generate cover letter first")
            else:
                try:
                    draft_path = _create_email_draft(
                        recipient_email,
                        email_subject,
                        email_body,
                        st.session_state.resume_path,
                        st.session_state.cover_letter_path,
                    )
                    st.session_state.generated_email_draft_path = draft_path
                    st.session_state.generated_email_draft_signature = draft_signature
                    st.success("✅ Email draft recreated!")
                    st.info(f"📁 Saved to: `{draft_path}`")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error creating email draft: {e}")
                    st.code(traceback.format_exc())
    
    with tab4:
        st.header("💼 Interview Preparation")

        current_job = st.session_state.current_job or {}

        if st.session_state.current_job is None:
            st.info("👈 Analyze a job first to auto-fill the details, or enter the job description and company manually below.")

        if selected_provider == "gemini" and not api_key:
            st.warning("⚠️ Please enter API key in sidebar")

        default_job_description = st.session_state.selected_job_description or current_job.get('description', '')
        default_company_name = st.session_state.selected_job_company or current_job.get('company', 'Unknown Company')
        default_job_url = st.session_state.selected_job_url or current_job.get('url', '')

        st.session_state.interview_job_description = st.text_area(
            "Job Description",
            value=st.session_state.interview_job_description or default_job_description,
            height=180,
            key="interview_job_description_input",
        )
        st.session_state.interview_company_name = st.text_input(
            "Company Name",
            value=st.session_state.interview_company_name or default_company_name,
            key="interview_company_name_input",
        )
        st.session_state.interview_job_url = st.text_input(
            "Job URL",
            value=st.session_state.interview_job_url or default_job_url,
            key="interview_job_url_input",
        )

        role_cols = st.columns(3)
        with role_cols[0]:
            st.session_state.interview_role_1 = st.text_input(
                "Interviewer Role 1",
                value=st.session_state.interview_role_1,
                key="interviewer_role_1",
            )
        with role_cols[1]:
            st.session_state.interview_role_2 = st.text_input(
                "Interviewer Role 2",
                value=st.session_state.interview_role_2,
                key="interviewer_role_2",
            )
        with role_cols[2]:
            st.session_state.interview_role_3 = st.text_input(
                "Interviewer Role 3",
                value=st.session_state.interview_role_3,
                key="interviewer_role_3",
            )

        st.success(f"✅ Preparing for: **{st.session_state.interview_company_name}**")

        if st.button("🎯 Generate Interview Q&A", type="primary", use_container_width=True):
            if not st.session_state.interview_job_description.strip():
                st.warning("⚠️ Please enter a job description before generating interview Q&A.")
            elif not st.session_state.interview_company_name.strip():
                st.warning("⚠️ Please enter a company name before generating interview Q&A.")
            else:
                try:
                    interview_roles = [
                        st.session_state.interview_role_1,
                        st.session_state.interview_role_2,
                        st.session_state.interview_role_3,
                    ]

                    generated_questions = []
                    with st.spinner("Generating interview questions and model answers..."):
                        for role in interview_roles:
                            questions = _generate_interview_question_batch(
                                model_provider,
                                st.session_state.resume_data,
                                st.session_state.interview_job_description,
                                st.session_state.interview_company_name,
                                role,
                                target_count=20,
                            )
                            for question in questions:
                                answer = _generate_model_answer_for_question(
                                    model_provider,
                                    st.session_state.resume_data,
                                    st.session_state.interview_job_description,
                                    st.session_state.interview_company_name,
                                    role,
                                    question,
                                )
                                generated_questions.append(
                                    {"role": role, "question": question, "answer": answer}
                                )

                    st.session_state.interview_questions = generated_questions
                    st.session_state.interview_simulation_messages = []
                    st.session_state.interview_simulation_active = False
                    st.session_state.interview_current_question_index = 0
                    st.session_state.interview_spoken_reply = ''
                    st.session_state.interview_last_comparison = None

                    qa_output = []
                    for item in generated_questions:
                        qa_output.append(
                            f"**{item['role']}**\n"
                            f"**Question:** {item['question']}\n"
                            f"**Model answer:** {item['answer']}"
                        )

                    qa_text = "\n\n".join(qa_output)
                    st.success(f"✅ Generated {len(generated_questions)} interview questions across {len(interview_roles)} interviewer roles.")
                    with st.expander("View all generated questions and model answers", expanded=False):
                        st.markdown(qa_text)

                    st.download_button(
                        "📥 Download Interview Prep",
                        qa_text,
                        file_name=f"interview_prep_{st.session_state.interview_company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain",
                        key="download_interview_prep",
                    )
                except Exception as e:
                    st.error(f"❌ Error generating interview prep: {e}")
                    st.code(traceback.format_exc())

        if st.session_state.interview_questions:
            st.divider()
            st.subheader("🧪 Interview Simulation")
            st.info("Use the microphone below to speak your answer. The coach will assess your reply and give practical feedback.")

            if not st.session_state.interview_simulation_active:
                if st.button("▶ Start Simulation", type="primary", use_container_width=True):
                    st.session_state.interview_simulation_active = True
                    st.session_state.interview_current_question_index = 0
                    st.session_state.interview_simulation_messages = []
                    st.session_state.interview_spoken_reply = ''
                    st.session_state.interview_last_comparison = None
                    st.rerun()

            if st.session_state.interview_simulation_active:
                current_question = st.session_state.interview_questions[st.session_state.interview_current_question_index]
                interviewer_role = current_question['role']
                question_text = current_question['question']
                model_answer = current_question.get('answer', '')

                with st.container(border=True):
                    st.markdown(f"### {interviewer_role}")
                    st.markdown(question_text)

                    if model_answer:
                        with st.expander("View model answer example", expanded=False):
                            st.markdown(model_answer)

                    spoken_reply = _interview_mic_component(question_text)
                    if isinstance(spoken_reply, str) and spoken_reply:
                        st.session_state.interview_spoken_reply = spoken_reply

                    st.text_area(
                        "Your answer",
                        value=st.session_state.interview_spoken_reply,
                        height=140,
                        key="interview_reply_text_area",
                    )

                    if st.button("📤 Submit Response", use_container_width=True):
                        typed_answer = st.session_state.get("interview_reply_text_area", "")
                        if not typed_answer.strip():
                            st.warning("⚠️ Capture or type your answer before submitting.")
                        else:
                            feedback = _assess_interview_answer(
                                model_provider,
                                st.session_state.resume_data,
                                st.session_state.interview_job_description,
                                st.session_state.interview_company_name,
                                interviewer_role,
                                question_text,
                                typed_answer,
                            )
                            st.session_state.interview_simulation_messages.append(
                                {"role": "Interviewee", "content": typed_answer}
                            )
                            st.session_state.interview_simulation_messages.append(
                                {"role": "Coach", "content": feedback}
                            )
                            st.session_state.interview_last_comparison = {
                                "question": question_text,
                                "your_answer": st.session_state.interview_spoken_reply,
                                "model_answer": model_answer,
                                "feedback": feedback,
                            }
                            st.session_state.interview_spoken_reply = ''
                            if st.session_state.interview_current_question_index < len(st.session_state.interview_questions) - 1:
                                st.session_state.interview_current_question_index += 1
                                st.rerun()
                            else:
                                st.session_state.interview_simulation_active = False
                                st.success("✅ Simulation complete. Review the feedback above.")

                for message in st.session_state.interview_simulation_messages:
                    if message['role'] == 'Interviewee':
                        st.markdown(f"**You:** {message['content']}")
                    else:
                        st.markdown(f"**Coach:** {message['content']}")

                if st.session_state.interview_last_comparison:
                    with st.container(border=True):
                        st.subheader("📊 Comparison")
                        st.markdown("**Question**")
                        st.markdown(st.session_state.interview_last_comparison["question"])
                        st.markdown("**Your answer**")
                        st.markdown(st.session_state.interview_last_comparison["your_answer"])
                        st.markdown("**Model answer**")
                        st.markdown(st.session_state.interview_last_comparison["model_answer"])
                        st.markdown("**Coach feedback**")
                        st.markdown(st.session_state.interview_last_comparison["feedback"])

                if st.session_state.interview_current_question_index == len(st.session_state.interview_questions) - 1 and not st.session_state.interview_simulation_active:
                    st.info("Simulation complete. You can generate a new set of questions if you want to practice again.")

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
                            if selected_provider == "gemini" and not api_key:
                                st.error("⚠️ Gemini API key required for job matching.")
                            else:
                                st.success("✅ Running job matching skill...")
                                matcher = AIJobMatcher(api_key=api_key, model=selected_model, llm=model_provider)
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
                        elif selected_provider == "gemini" and not api_key:
                            st.error("⚠️ Gemini API key required for cover letter generation.")
                        else:
                            st.success("✅ Running cover letter generation skill...")
                            generator = DocumentGenerator(api_key=api_key, model=selected_model, llm=model_provider)
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
                        elif selected_provider == "gemini" and not api_key:
                            st.error("⚠️ Gemini API key required for interview prep.")
                        else:
                            st.success("✅ Running mock interview skill...")
                            prep = InterviewPrepGenerator(api_key=api_key, model=selected_model, llm=model_provider)
                            qa = prep.generate_interview_qa(
                                st.session_state.resume_data,
                                st.session_state.current_job['description']
                            )
                            st.markdown(qa)

                    else:
                        st.info(f"🔧 Running a general AI tool skill using {model_choice}.")
                        if selected_provider == "gemini" and not api_key:
                            st.error("⚠️ Gemini API key required for general AI tool execution.")
                        else:
                            prompt = (
                                f"You are an AI engineering assistant. Provide a concise Python plan for how to implement the following AI agent skill: {ai_skill_query}. "
                                "Include a short code sketch and the main steps."
                            )
                            result = model_provider.generate(prompt, temperature=0.6)
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
