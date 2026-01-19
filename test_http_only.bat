@echo off
REM Test Django with zero security headers
cd /d "%~dp0"
call .venv\Scripts\activate.bat

REM Set environment to explicitly disable all SSL
set DJANGO_DEBUG=True
set SECURE_SSL_REDIRECT=False
set SESSION_COOKIE_SECURE=False
set CSRF_COOKIE_SECURE=False
set SECURE_HSTS_SECONDS=0

echo.
echo Testing Django on http://127.0.0.1:5000
echo All SSL/HTTPS headers disabled
echo.
echo To test: Open PowerShell and run:
echo   Invoke-WebRequest -Uri "http://127.0.0.1:5000" -UseBasicParsing
echo.

python manage.py runserver 127.0.0.1:5000

pause
