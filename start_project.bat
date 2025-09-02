@echo off
echo ========================================
echo 🚀 Starting Network Monitoring Dashboard
echo ========================================

echo 📁 Navigating to project directory...
cd /d "D:\DevOps\DevOps Project - Local"

echo 🐍 Activating Python virtual environment...
call .\network_dashboard_env\Scripts\activate

echo 🐳 Starting lab environment (Docker containers)...
cd portfolio\local-testing
docker-compose -f docker-compose-simple.yml up -d

echo ⏳ Waiting for containers to start...
timeout /t 5 /nobreak >nul

echo 🔍 Checking lab device status...
docker ps --filter name=lab-

echo 📡 Returning to project root...
cd "D:\DevOps\DevOps Project - Local"

echo ✅ Lab environment started successfully!
echo 🌐 Lab devices available at:
echo    - lab-router1:   127.0.0.1:2221
echo    - lab-switch1:   127.0.0.1:2222  
echo    - lab-firewall1: 127.0.0.1:2223

echo.
echo 🚀 Starting Streamlit dashboard...
echo 📖 Dashboard will open at: http://localhost:8501
echo.
echo ⚠️  Press Ctrl+C to stop the dashboard
echo ========================================

streamlit run streamlit_app.py

pause
