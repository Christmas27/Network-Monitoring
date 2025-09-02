#!/usr/bin/env python3
"""
Debug WSL Ansible Detection
"""

import subprocess

def debug_wsl_ansible():
    print("🔍 Debug WSL Ansible Detection")
    print("=" * 40)
    
    # Test 1: Basic WSL check
    print("1. Testing basic WSL...")
    try:
        result = subprocess.run(["wsl", "--list", "--verbose"], 
                              capture_output=True, text=True, timeout=10)
        print(f"WSL Return Code: {result.returncode}")
        print(f"WSL Output: {result.stdout[:200]}...")
        print(f"WSL Errors: {result.stderr}")
    except Exception as e:
        print(f"WSL Error: {e}")
    
    # Test 2: Check Ubuntu distro
    print("\n2. Testing Ubuntu distro...")
    try:
        result = subprocess.run(["wsl", "-d", "Ubuntu", "--", "echo", "Hello from Ubuntu"], 
                              capture_output=True, text=True, timeout=10)
        print(f"Ubuntu Return Code: {result.returncode}")
        print(f"Ubuntu Output: {result.stdout}")
        print(f"Ubuntu Errors: {result.stderr}")
    except Exception as e:
        print(f"Ubuntu Error: {e}")
    
    # Test 3: Check which ansible-playbook
    print("\n3. Testing which ansible-playbook...")
    try:
        result = subprocess.run(["wsl", "-d", "Ubuntu", "--", "which", "ansible-playbook"], 
                              capture_output=True, text=True, timeout=10)
        print(f"Which Return Code: {result.returncode}")
        print(f"Which Output: '{result.stdout.strip()}'")
        print(f"Which Errors: '{result.stderr.strip()}'")
    except Exception as e:
        print(f"Which Error: {e}")
    
    # Test 4: Check ansible-playbook version
    print("\n4. Testing ansible-playbook version...")
    try:
        result = subprocess.run(["wsl", "-d", "Ubuntu", "--", "ansible-playbook", "--version"], 
                              capture_output=True, text=True, timeout=10)
        print(f"Version Return Code: {result.returncode}")
        print(f"Version Output: {result.stdout[:200]}...")
        print(f"Version Errors: {result.stderr}")
    except Exception as e:
        print(f"Version Error: {e}")

if __name__ == "__main__":
    debug_wsl_ansible()
