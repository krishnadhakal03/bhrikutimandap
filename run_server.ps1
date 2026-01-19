# ========================================
# Bhrikutimandap Django Development Server
# ========================================

Write-Host "`n" -ForegroundColor Green
Write-Host "Starting Bhrikutimandap Development Server..." -ForegroundColor Green
Write-Host "`n"

# Get the directory where this script is located
$scriptPath = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
Set-Location $scriptPath

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Check if activation was successful
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

Write-Host "Virtual environment activated" -ForegroundColor Green
Write-Host "`n"

# Run Django development server
Write-Host "Starting Django server on http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Cyan
Write-Host "`n"

python manage.py runserver 127.0.0.1:5000
