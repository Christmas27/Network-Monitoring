#!/usr/bin/env python3
"""
Direct WSL Bridge Test
"""

import sys
import os
import logging

# Configure logging to see debug output
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Add modules path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.wsl_ansible_bridge import WSLAnsibleBridge

def test_bridge_directly():
    print("🧪 Testing WSL Bridge Directly...")
    print("=" * 40)
    
    bridge = WSLAnsibleBridge()
    result = bridge.check_wsl_availability()
    
    print(f"Result: {result}")
    print(f"WSL Available: {result.get('wsl_available')}")
    print(f"Ansible Available: {result.get('ansible_available')}")
    print(f"Ansible Version: {result.get('ansible_version')}")
    print(f"Status: {result.get('status')}")
    
    if result.get('ansible_available'):
        print("\n🔗 Testing connectivity...")
        conn_result = bridge.run_connectivity_test()
        print(f"Connectivity Result: {conn_result}")

if __name__ == "__main__":
    test_bridge_directly()
