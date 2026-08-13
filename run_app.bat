@echo off
:: Windows Batch Script to Start the Apple Change Detection Streamlit App
title Apple Change Detection POC - Launcher

echo =========================================================================
echo 🍏 Starting Apple Change Detection & Automated Map Update POC
echo =========================================================================

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your Windows PATH.
    echo Please install Python 3.11+ from python.org before running this app.
    pause
    exit /b 1
)

:: Activate Virtual Environment if exists, otherwise create it
if exist .venv\Scripts\activate.bat (
    echo [INFO] Activating existing Python virtual environment (.venv)...
    call .venv\Scripts\activate.bat
) else (
    echo [INFO] Creating new Python virtual environment (.venv)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [WARNING] Could not create virtual environment automatically.
        echo Attempting to run with system-wide Python...
    ) else (
        echo [INFO] Activating virtual environment...
        call .venv\Scripts\activate.bat
        echo [INFO] Installing required dependencies from requirements.txt...
        pip install -r requirements.txt
    )
)

echo [INFO] Launching Streamlit interface on Localhost...
streamlit run app.py

pause
