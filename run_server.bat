@echo off
REM ========================================
REM Bhrikutimandap Django Development Server
REM ========================================

echo.
echo Starting Bhrikutimandap Development Server...
echo.

REM Get the directory where this script is located
cd /d "%~dp0"

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check if activation was successful
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    exit /b 1
)

echo Virtual environment activated
echo.

REM Run Django development server
echo Starting Django server on http://127.0.0.1:5000
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver 127.0.0.1:5000

pause
