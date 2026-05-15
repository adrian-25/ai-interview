@echo off
REM Quick start script for backend (Windows)

echo 🚀 Starting AI Interview Coach Backend...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -q -r requirements.txt

REM Run setup validation
echo.
echo 🔍 Validating setup...
python setup.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Starting server...
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
) else (
    echo.
    echo ❌ Setup validation failed. Please fix the issues above.
    exit /b 1
)
