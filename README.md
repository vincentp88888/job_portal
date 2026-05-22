# AI Job Portal

A Python Streamlit job portal enhanced with Google Gemini 2.5 flash AI, resume parsing, job matching, ATS scoring, interview preparation, and application tracking.

## What is included

- Resume parsing for PDF and DOCX
- Job description parsing and skill extraction
- Semantic resume-to-job match scoring
- ATS keyword gap analysis and resume improvement guidance
- Cover letter generation and interview prep using Gemini
- Application tracker saved to `data/applications.json`
- Deployment-ready for AWS Ubuntu with Streamlit on port `8501`

## Python compatibility

- Tested for Python `3.13.13`
- Compatible with Python `3.14`

## Setup locally

1. Install Python 3.13 or 3.14 on Ubuntu.
2. Create and activate a virtual environment:

```bash
python3.14 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a local `.env` file from the example:

```bash
cp .env.example .env
```

5. Add your Gemini API key to `.env`:

```text
GEMINI_API_KEY=your_gemini_api_key_here
```

6. Run the app:

```bash
streamlit run app.py
```

7. Open the portal in Chrome or Edge at:

```
http://127.0.0.1:8501
```

## Deploy on AWS Ubuntu

### 1. Launch an EC2 instance

- Ubuntu 22.04 or 24.04 LTS
- t3.small or larger
- Open port 8501 in the security group

### 2. SSH into the instance

```bash
ssh -i job_portal_key.pem ubuntu@<your_ec2_ip>
```

### 3. Update packages and install Python

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3.14 python3.14-venv python3.14-distutils git
```

### 4. Clone repository and install requirements

```bash
git clone <your-github-repo-url> job_portal
cd job_portal
python3.14 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure environment variables

```bash
cp .env.example .env
nano .env
```

Set `GEMINI_API_KEY` to your Gemini key.

### 6. Start Streamlit as a background service

```bash
nohup streamlit run app.py --server.port=8501 --server.address=0.0.0.0 &
```

### 7. Configure DuckDNS

- Set `aijobportal.duckdns.org` to your EC2 public IP
- Use port `8501`

### 8. Optional: Use Nginx as a reverse proxy

For a browser-friendly address and HTTPS, install Nginx and proxy traffic to `localhost:8501`.

## Important browser note

Streamlit is best experienced in modern browsers: Chrome, Edge, Firefox, and mobile Chrome. Internet Explorer is not supported by Streamlit and is not recommended for modern AI web apps.

## Marketing suggestions

- Highlight Gemini 2.5 AI in landing page copy
- Publish career coaching, ATS score, and interview prep as core benefits
- Add a simple landing page at `http://aijobportal.duckdns.org:8501` that explains your AI agent capabilities
- Use Google Play account `vincentp88888@gmail.com` to publish a companion Android PWA or APK later
- Share the portal in LinkedIn groups, IT hiring communities, and local Singapore career forums
- Create a short product demo video and pin it to your GitHub README

## Files to review

- `app.py`
- `modules/resume_parser.py`
- `modules/job_parser.py`
- `modules/semantic_matcher.py`
- `modules/ats_optimizer.py`
- `modules/application_tracker.py`
- `requirements.txt`
