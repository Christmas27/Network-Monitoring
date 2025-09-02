#!/usr/bin/env python3
"""
Test WSL Ansible Bridge Integration
Simple test script to verify WSL Ansible functionality
"""

import sys
import os

# Add modules path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.wsl_ansible_bridge import get_wsl_ansible_bridge
from modules.real_ssh_manager import get_ssh_manager
from modules.device_manager import DeviceManager

def test_wsl_ansible():
    print("🧪 Testing WSL Ansible Integration...")
    print("=" * 50)
    
    # Test WSL Ansible Bridge
    print("\n1. 🏗️ Testing WSL Ansible Bridge")
    wsl_bridge = get_wsl_ansible_bridge()
    
    # Check WSL availability
    wsl_status = wsl_bridge.check_wsl_availability()
    print(f"WSL Available: {wsl_status['wsl_available']}")
    print(f"Ansible Available: {wsl_status['ansible_available']}")
    if wsl_status['ansible_available']:
        print(f"Ansible Version: {wsl_status.get('ansible_version', 'Unknown')}")
    
    if wsl_status['ansible_available']:
        # Test connectivity
        print("\n2. 🔗 Testing Ansible Connectivity")
        connectivity_result = wsl_bridge.run_connectivity_test()
        print(f"Connectivity Status: {connectivity_result['status']}")
        print(f"Devices Reachable: {connectivity_result.get('devices_reachable', 0)}/{connectivity_result.get('total_devices', 3)}")
        
        if connectivity_result.get('raw_output'):
            print("Raw Output (first 500 chars):")
            print(connectivity_result['raw_output'][:500] + "..." if len(connectivity_result['raw_output']) > 500 else connectivity_result['raw_output'])
    
    # Test SSH Manager
    print("\n3. 🔧 Testing SSH Manager")
    ssh_manager = get_ssh_manager()
    
    # Check for lab devices
    device_manager = DeviceManager()
    devices = device_manager.get_all_devices()
    lab_devices = [d for d in devices if 'lab' in d.get('tags', '')]
    
    print(f"Lab devices found: {len(lab_devices)}")
    for device in lab_devices:
        print(f"  • {device['hostname']} ({device['ip_address']}:{device.get('port', 22)})")
    
    if lab_devices:
        print("\n4. 🔗 Testing SSH Connectivity")
        try:
            # Test first lab device
            test_device = lab_devices[0]
            result = ssh_manager.execute_lab_connectivity_test([test_device])
            print(f"SSH Connectivity: {result['status']}")
            if result.get('results'):
                for device_result in result['results']:
                    print(f"  • {device_result['device']}: {device_result['status']}")
        except Exception as e:
            print(f"SSH Test Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Integration test completed!")

if __name__ == "__main__":
    test_wsl_ansible()
