Write-Host "Network Monitoring Dashboard Manager" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Gray

if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "D:\DevOps\DevOps Project - Local\network_dashboard_env\Scripts\Activate.ps1"
    Write-Host "Virtual environment activated!" -ForegroundColor Green
} else {
    Write-Host "Virtual environment already active" -ForegroundColor Green
}

Write-Host ""
Write-Host "Python version:" -ForegroundColor Yellow
python --version

Write-Host ""
Write-Host "Quick commands:" -ForegroundColor Cyan
Write-Host "  streamlit run streamlit_app.py --server.port 8503" -ForegroundColor White
