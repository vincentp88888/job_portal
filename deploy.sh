#!/usr/bin/env bash
set -e

# Basic deploy script for Ubuntu + Streamlit
python3.14 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env || true

echo "Update .env with your GEMINI_API_KEY and then run:"
echo "source venv/bin/activate && streamlit run app.py --server.port=8501 --server.address=0.0.0.0"
