@echo off
REM ========================================
REM Bhrikutimandap Development Setup
REM ========================================

echo.
echo Bhrikutimandap Development Setup
echo.

REM Get the directory where this script is located
cd /d "%~dp0"

REM Activate virtual environment
call .venv\Scripts\activate.bat

if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    exit /b 1
)

echo [OK] Virtual environment activated
echo.

REM Run migrations
echo Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo [WARN] Migration had issues
) else (
    echo [OK] Migrations completed
)

echo.

REM Collect static files (optional)
echo Collecting static files...
python manage.py collectstatic --noinput
if errorlevel 1 (
    echo [WARN] Static files collection had issues
) else (
    echo [OK] Static files collected
)

echo.
echo ========================================
echo Setup completed!
echo.
echo To start the server, run: run_server.bat
echo ========================================
echo.

pause
