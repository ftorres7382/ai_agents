@echo off

:: Check if the .venv folder exists
if not exist .venv (
    echo .venv folder not found. Creating virtual environment...
    python -m venv .venv

    :: Install dependencies from requirements.txt if the virtual environment is created
    if exist requirements.txt (
        echo Installing dependencies from requirements.txt...
        call .venv\Scripts\activate.bat
        pip install -r requirements.txt
        deactivate
    ) else (
        echo requirements.txt not found. Skipping dependency installation.
    )
)
 
:: Activate the virtual environment
call .venv\Scripts\activate.bat

mypy --strict main.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR! mypy found type issues. Aborting execution of the Python file.
    exit /b %ERRORLEVEL%
)
python main.py
