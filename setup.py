#!/usr/bin/env python3
"""
Network Dashboard Setup Script
Automated setup for the Network Automation Dashboard
"""

import os
import sys
import subprocess
import platform

def print_banner():
    print("=" * 60)
    print("🌐 NETWORK AUTOMATION DASHBOARD SETUP")
    print("=" * 60)

def run_command(command, description):
    print(f"🔄 {description}...")
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Error during {description}")
        return False

def main():
    print_banner()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Create virtual environment
    if not run_command("python -m venv network_dashboard_env", "Creating virtual environment"):
        sys.exit(1)
    
    # Install dependencies
    if platform.system() == "Windows":
        pip_cmd = "network_dashboard_env\\Scripts\\pip"
    else:
        pip_cmd = "network_dashboard_env/bin/pip"
    
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        sys.exit(1)
    
    # Create directories
    for directory in ['data', 'logs', 'backups']:
        os.makedirs(directory, exist_ok=True)
    
    # Setup config
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("✅ Created .env from template")
    
    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    if platform.system() == "Windows":
        print("1. network_dashboard_env\\Scripts\\activate")
    else:
        print("1. source network_dashboard_env/bin/activate")
    print("2. python main.py")
    print("3. Open http://localhost:5000")

if __name__ == "__main__":
    main()