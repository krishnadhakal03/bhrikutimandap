@echo off
setlocal

REM Run from this script's directory (project root)
cd /d "%~dp0"

set "VENV_PYTHON=%~dp0.venv\Scripts\python.exe"

if exist "%VENV_PYTHON%" (
    echo Using virtual environment Python: %VENV_PYTHON%
    "%VENV_PYTHON%" manage.py createsuperuser
) else (
    echo [WARN] .venv Python not found. Falling back to system python.
    python manage.py createsuperuser
)

if errorlevel 1 (
    echo.
    echo Superuser creation failed or was cancelled.
    exit /b 1
)

echo.
echo Superuser creation completed.
exit /b 0
