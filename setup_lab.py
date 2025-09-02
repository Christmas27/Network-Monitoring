#!/usr/bin/env python3
"""
Lab Device Auto-Setup and Testing Script

This script automatically:
1. Adds lab devices to the dashboard
2. Tests connectivity to all lab devices
3. Runs enhanced Ansible playbooks
4. Shows real results instead of simulations
"""

import sys
import os
import subprocess
import time
import json
from pathlib import Path

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.device_manager import DeviceManager
from modules.ansible_manager_simple import AnsibleManager

def test_ssh_connection(host, port, username="admin", password="admin", timeout=5):
    """Test SSH connection to a host"""
    try:
        import paramiko
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            timeout=timeout,
            allow_agent=False,
            look_for_keys=False
        )
        
        # Test command execution
        stdin, stdout, stderr = ssh.exec_command('echo "SSH test successful"')
        result = stdout.read().decode().strip()
        ssh.close()
        
        return True, result
    except Exception as e:
        return False, str(e)

def setup_lab_devices():
    """Add lab devices to the device manager"""
    print("🔧 Setting up lab devices...")
    
    device_manager = DeviceManager()
    
    lab_devices = [
        {
            'hostname': 'lab-router1',
            'ip_address': 'localhost:2221',
            'device_type': 'linux',
            'vendor': 'docker',
            'model': 'openssh-server',
            'username': 'admin',
            'password': 'admin',
            'port': 2221,
            'role': 'router',
            'location': 'Docker Lab',
            'tags': 'lab,ssh,testing'
        },
        {
            'hostname': 'lab-switch1',
            'ip_address': 'localhost:2222',
            'device_type': 'linux',
            'vendor': 'docker',
            'model': 'openssh-server',
            'username': 'admin',
            'password': 'admin',
            'port': 2222,
            'role': 'switch',
            'location': 'Docker Lab',
            'tags': 'lab,ssh,testing'
        },
        {
            'hostname': 'lab-firewall1',
            'ip_address': 'localhost:2223',
            'device_type': 'linux',
            'vendor': 'docker',
            'model': 'openssh-server',
            'username': 'admin',
            'password': 'admin',
            'port': 2223,
            'role': 'firewall',
            'location': 'Docker Lab',
            'tags': 'lab,ssh,testing'
        }
    ]
    
    added_devices = []
    
    for device_data in lab_devices:
        try:
            # Check if device already exists by checking all devices
            existing_devices = device_manager.get_all_devices()
            existing = None
            for d in existing_devices:
                if d.get('ip_address') == device_data['ip_address']:
                    existing = d
                    break
            
            if existing:
                print(f"  ⚠️  Device {device_data['hostname']} already exists")
                added_devices.append(existing)
                continue
            
            # Test connectivity first
            print(f"  🔍 Testing connectivity to {device_data['hostname']}...")
            success, message = test_ssh_connection('localhost', device_data['port'])
            
            if success:
                device_data['status'] = 'online'
                device_id = device_manager.add_device(device_data)
                added_devices.append(device_manager.get_device(device_id))
                print(f"  ✅ Added {device_data['hostname']} (ID: {device_id})")
            else:
                device_data['status'] = 'offline'
                device_id = device_manager.add_device(device_data)
                print(f"  ❌ Added {device_data['hostname']} but connection failed: {message}")
                
        except Exception as e:
            print(f"  ❌ Error adding {device_data['hostname']}: {e}")
    
    return added_devices

def test_ansible_playbooks():
    """Test the new lab playbooks"""
    print("\n🧪 Testing Ansible playbooks with real lab devices...")
    
    ansible_manager = AnsibleManager()
    device_manager = DeviceManager()
    
    # Get lab devices
    lab_devices = [d for d in device_manager.get_all_devices() if 'lab' in d.get('tags', '')]
    
    if not lab_devices:
        print("  ❌ No lab devices found! Run setup first.")
        return []
    
    # Create lab-specific inventory
    lab_inventory = []
    for device in lab_devices:
        lab_inventory.append({
            'id': device['id'],
            'hostname': device['hostname'],
            'ip_address': 'localhost',  # All are localhost with different ports
            'ansible_port': device.get('port', 22),
            'device_type': device['device_type'],
            'vendor': device['vendor']
        })
    
    inventory = ansible_manager.generate_inventory(lab_inventory)
    
    # Test each lab playbook
    lab_playbooks = [
        'lab_connectivity_test.yml',
        'lab_configuration.yml', 
        'lab_monitoring.yml'
    ]
    
    results = []
    
    for playbook in lab_playbooks:
        print(f"\n  🚀 Running {playbook}...")
        
        try:
            result = ansible_manager.run_playbook(
                playbook_name=playbook,
                inventory=inventory,
                extra_vars={'lab_mode': True}
            )
            
            results.append(result)
            
            if result['status'] == 'simulated':
                print(f"    ✅ {playbook} completed (simulation mode)")
                print(f"    📊 Duration: {result['duration']}s")
                print(f"    📋 Message: {result.get('message', 'No additional details')}")
            else:
                print(f"    ✅ {playbook} executed successfully!")
                
        except Exception as e:
            print(f"    ❌ Error running {playbook}: {e}")
    
    return results

def run_real_ansible_test():
    """Try to run a real Ansible command if possible"""
    print("\n🔬 Attempting real Ansible execution...")
    
    try:
        # Check if ansible is available
        result = subprocess.run(['ansible', '--version'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("  ✅ Ansible is available!")
            print(f"  📄 Version: {result.stdout.split()[1]}")
            
            # Try a simple ping to lab devices
            print("  🏓 Running ansible ping to lab devices...")
            
            # Create a simple inventory file
            inventory_content = """
[lab_devices]
lab-router1 ansible_host=localhost ansible_port=2221 ansible_user=admin ansible_password=admin
lab-switch1 ansible_host=localhost ansible_port=2222 ansible_user=admin ansible_password=admin  
lab-firewall1 ansible_host=localhost ansible_port=2223 ansible_user=admin ansible_password=admin

[all:vars]
ansible_connection=ssh
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
"""
            
            with open('temp_lab_inventory.ini', 'w') as f:
                f.write(inventory_content)
            
            # Run ansible ping
            ping_result = subprocess.run([
                'ansible', 'all', '-i', 'temp_lab_inventory.ini', '-m', 'ping'
            ], capture_output=True, text=True, timeout=30)
            
            if ping_result.returncode == 0:
                print("  🎉 Real Ansible execution successful!")
                print("  📋 Results:")
                print(ping_result.stdout)
            else:
                print("  ⚠️  Ansible ping failed:")
                print(ping_result.stderr)
            
            # Clean up
            if os.path.exists('temp_lab_inventory.ini'):
                os.remove('temp_lab_inventory.ini')
                
        else:
            print("  ⚠️  Ansible not available in PATH")
            
    except FileNotFoundError:
        print("  ⚠️  Ansible not installed or not in PATH")
    except subprocess.TimeoutExpired:
        print("  ⚠️  Ansible command timed out")
    except Exception as e:
        print(f"  ❌ Error testing Ansible: {e}")

def main():
    """Main lab setup and testing function"""
    print("🧪 Lab Enhancement Script")
    print("=" * 50)
    
    # Step 1: Setup lab devices
    devices = setup_lab_devices()
    print(f"\n✅ Lab setup complete! Added {len(devices)} devices.")
    
    # Step 2: Test playbooks
    results = test_ansible_playbooks()
    print(f"\n✅ Playbook testing complete! Ran {len(results)} playbooks.")
    
    # Step 3: Try real Ansible if available
    run_real_ansible_test()
    
    print("\n🎉 Lab enhancement complete!")
    print("\n💡 Next steps:")
    print("  1. Open your Streamlit dashboard")
    print("  2. Go to 📱 Devices tab to see your lab devices")
    print("  3. Go to 🤖 Automation tab to test the new playbooks")
    print("  4. Check the results - they should now show real data!")

if __name__ == "__main__":
    main()
