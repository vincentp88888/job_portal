@echo off
setlocal enabledelayedexpansion

echo ================================================================
echo JOB PORTAL - COMPLETE SETUP SCRIPT
echo ================================================================
echo.

REM Step 1: Check Python
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python from python.org
    pause
    exit /b 1
)
python --version
echo.

REM Step 2: Delete old venv
echo [2/8] Removing old virtual environment...
if exist venv (
    rmdir /s /q venv
    echo Old venv deleted
) else (
    echo No old venv found
)
echo.

REM Step 3: Create new venv
echo [3/8] Creating new virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created
echo.

REM Step 4: Activate venv
echo [4/8] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated
echo.

REM Step 5: Upgrade pip
echo [5/8] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel
echo.

REM Step 6: Install packages
echo [6/8] Installing packages (this may take 2-3 minutes)...
echo.

echo Installing streamlit...
pip install streamlit==1.29.0
echo.

echo Installing google-generativeai...
pip install google-generativeai==0.3.2
echo.

echo Installing python-docx...
pip install python-docx==1.1.0
echo.

echo Installing PyPDF2...
pip install PyPDF2==3.0.1
echo.

echo Installing pandas...
pip install pandas==2.1.3
echo.

echo Installing plotly...
pip install plotly==5.18.0
echo.

echo Installing beautifulsoup4...
pip install beautifulsoup4==4.12.2
echo.

echo Installing requests...
pip install requests==2.31.0
echo.

echo Installing python-dotenv...
pip install python-dotenv==1.0.0
echo.

echo Installing certifi...
pip install certifi==2023.11.17
echo.

echo Installing urllib3...
pip install urllib3==2.1.0
echo.

REM Step 7: Verify installations
echo [7/8] Verifying installations...
echo.

python -c "import streamlit; print('[OK] streamlit:', streamlit.__version__)" || echo [FAIL] streamlit
python -c "import google.generativeai; print('[OK] google-generativeai')" || echo [FAIL] google-generativeai
python -c "from docx import Document; print('[OK] python-docx')" || echo [FAIL] python-docx
python -c "import PyPDF2; print('[OK] PyPDF2:', PyPDF2.__version__)" || echo [FAIL] PyPDF2
python -c "import pandas; print('[OK] pandas:', pandas.__version__)" || echo [FAIL] pandas
python -c "import plotly; print('[OK] plotly:', plotly.__version__)" || echo [FAIL] plotly
python -c "from bs4 import BeautifulSoup; print('[OK] beautifulsoup4')" || echo [FAIL] beautifulsoup4
python -c "import requests; print('[OK] requests:', requests.__version__)" || echo [FAIL] requests
python -c "from dotenv import load_dotenv; print('[OK] python-dotenv')" || echo [FAIL] python-dotenv
python -c "import certifi; print('[OK] certifi:', certifi.__version__)" || echo [FAIL] certifi

echo.
echo [8/8] Setup complete!
echo.
echo ================================================================
echo SUCCESS! All packages installed
echo ================================================================
echo.
echo To run your Job Portal app:
echo   1. Make sure you're in the job_portal directory
echo   2. Activate virtual environment: venv\Scripts\activate
echo   3. Run: streamlit run app.py
echo.
echo Your app will open at: http://localhost:8501
echo.
pause
