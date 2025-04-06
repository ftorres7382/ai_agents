@echo off
mypy --strict main.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR! mypy found type issues. Aborting execution of the Python file.
    exit /b %ERRORLEVEL%
)
python main.py
