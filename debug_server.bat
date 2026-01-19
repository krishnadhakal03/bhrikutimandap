@echo off
REM Debug script - shows all output
cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo.
echo ========================================
echo Django Debug Test
echo ========================================
echo.

REM Check Python works
echo Testing Python...
python --version
echo.

REM Check Django works
echo Testing Django...
python -m django --version
echo.

REM Try to run server with verbose output
echo Starting Django server with verbose output...
echo URL: http://127.0.0.1:5000
echo.

python manage.py runserver 127.0.0.1:5000 --verbosity 2

pause
