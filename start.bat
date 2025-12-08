@echo off
echo Checking for virtual environment 'venv'...

if not exist venv (
    echo Virtual environment 'venv' not found. Creating it...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Error creating virtual environment. Please ensure Python is installed and in your PATH.
        goto :eof
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Checking for Flask installation...
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo Flask not found in venv. Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Error installing dependencies. Please check requirements.txt and your internet connection.
        call venv\Scripts\deactivate.bat
        goto :eof
    )
)

echo Setting domain for QR codes...
set SPRITZQUIZ_DOMAIN=https://quiz.satoshispritz.it

echo Starting SpritzQuiz Flask application...
set FLASK_APP=app.py
set FLASK_DEBUG=True
set FLASK_RUN_PORT=5005
flask run --port=5005

