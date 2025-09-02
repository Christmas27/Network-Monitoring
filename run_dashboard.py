#!/usr/bin/env python3
"""
Network Monitoring Dashboard Launcher
Simplified launcher for the Python-only dashboard
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🌐 Network Monitoring Dashboard")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("streamlit_app.py").exists():
        print("❌ Error: streamlit_app.py not found")
        print("Please run this script from the project root directory")
        return 1
    
    # Check if virtual environment is activated
    if not os.environ.get('VIRTUAL_ENV'):
        print("⚠️  Warning: Virtual environment not detected")
        print("Consider activating your virtual environment:")
        print("   network_dashboard_env\\Scripts\\activate  # Windows")
        print("   source network_dashboard_env/bin/activate  # Linux/Mac")
        print()
    
    # Check if Streamlit is installed
    try:
        import streamlit
        print("✅ Streamlit found")
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit", "plotly", "pandas"])
    
    print()
    print("🚀 Starting Network Monitoring Dashboard...")
    print("📱 Dashboard will open at: http://localhost:8501")
    print("🔄 Press Ctrl+C to stop")
    print()
    
    # Start Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.headless", "false",
            "--server.port", "8501"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
