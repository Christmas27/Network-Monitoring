# Simple PowerShell script for managing Network Dashboard
# Always ensures virtual environment is activated before running commands

Write-Host "🌐 Network Monitoring Dashboard Manager" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Gray

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "🔄 Activating virtual environment..." -ForegroundColor Yellow
    & "D:\DevOps\DevOps Project - Local\network_dashboard_env\Scripts\Activate.ps1"
    Write-Host "✅ Virtual environment activated!" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already active: $env:VIRTUAL_ENV" -ForegroundColor Green
}

Write-Host ""
Write-Host "📊 Project Status:" -ForegroundColor Cyan

# Check Python
Write-Host "🐍 Python:" -ForegroundColor Yellow -NoNewline
python --version

# Check key files
Write-Host "📁 Files:" -ForegroundColor Yellow
$files = @("streamlit_app.py", "requirements.txt", "docker-compose.yml")
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file" -ForegroundColor Red
    }
}

# Check lab setup
if (Test-Path "lab\docker\docker-compose.yml") {
    Write-Host "  ✅ Docker lab configured" -ForegroundColor Green
} else {
    Write-Host "  ⭕ Docker lab not configured" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Available Commands:" -ForegroundColor Cyan
Write-Host "  python streamlit_app.py              - Run main dashboard" -ForegroundColor White
Write-Host "  streamlit run streamlit_app.py       - Run Streamlit dashboard" -ForegroundColor White
Write-Host "  python lab_setup.py                  - Setup lab environment" -ForegroundColor White
Write-Host "  docker-compose up -d                 - Start Docker lab" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Quick Start:" -ForegroundColor Yellow
Write-Host "  streamlit run streamlit_app.py --server.port 8503" -ForegroundColor Cyan
