@echo off

echo === Simple Banking System Setup ===

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Please install Python 3.6 or higher.
    exit /b 1
)

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment. Please install venv package.
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    exit /b 1
)

if not exist logs (
    echo Creating logs directory...
    mkdir logs
)

echo Setup complete! Starting Simple Banking System...
python main.py %*
