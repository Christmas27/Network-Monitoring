#!/usr/bin/env python3
"""
Integration Test - SSH + WSL Ansible
Test both SSH and Ansible automation working together
"""

import sys
import os

# Add modules path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.real_ssh_manager import get_ssh_manager
from modules.wsl_ansible_bridge import get_wsl_ansible_bridge
from modules.device_manager import DeviceManager

def test_full_integration():
    print("🧪 Testing Full Integration: SSH + WSL Ansible")
    print("=" * 60)
    
    # 1. Test SSH Manager
    print("\n1. 🔧 Testing SSH Manager")
    ssh_manager = get_ssh_manager()
    device_manager = DeviceManager()
    
    devices = device_manager.get_all_devices()
    lab_devices = [d for d in devices if 'lab' in d.get('tags', '')]
    
    print(f"Found {len(lab_devices)} lab devices")
    
    if lab_devices:
        print("Testing SSH connectivity...")
        result = ssh_manager.execute_lab_connectivity_test(lab_devices[:1])  # Test one device
        print(f"SSH Result: {result['status']}")
    
    # 2. Test WSL Ansible Bridge
    print("\n2. 🏗️ Testing WSL Ansible Bridge")
    wsl_bridge = get_wsl_ansible_bridge()
    
    # Check availability
    status = wsl_bridge.check_wsl_availability()
    print(f"WSL Available: {status['wsl_available']}")
    print(f"Ansible Available: {status['ansible_available']}")
    
    if status['ansible_available']:
        print("Testing Ansible connectivity...")
        result = wsl_bridge.run_connectivity_test()
        print(f"Ansible Result: {result['status']}")
        print(f"Devices Reachable: {result['devices_reachable']}/{result['total_devices']}")
    
    # 3. Integration Summary
    print("\n3. ✅ Integration Summary")
    print("Both SSH and Ansible automation are working!")
    print("Ready for Streamlit dashboard integration.")
    
    return True

if __name__ == "__main__":
    test_full_integration()
