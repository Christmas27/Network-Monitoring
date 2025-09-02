#!/usr/bin/env python3
"""
Quick Test - Connect to Lab Devices
Tests your dashboard integration with lab devices
"""

import paramiko
import json
import subprocess

def test_ansible_connectivity():
    """Test Ansible connectivity to lab devices"""
    print("🔧 Testing Ansible Integration:")
    print("-" * 40)
    
    # Test Ansible ping to lab devices
    try:
        # Use our lab inventory
        result = subprocess.run([
            'ansible', 'all', 
            '-i', 'portfolio/local-testing/inventory.yml',
            '-m', 'ping',
            '--ask-pass'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Ansible connectivity successful!")
            print(result.stdout)
        else:
            print("⚠️ Ansible test with some issues:")
            print(result.stdout)
            print(result.stderr)
    except Exception as e:
        print(f"❌ Ansible test failed: {e}")

def test_device_direct_ssh():
    """Test direct SSH connections to lab devices"""
    print("🔌 Testing Direct SSH Connections:")
    print("-" * 40)
    
    devices = [
        {"name": "Router", "host": "localhost", "port": 2221},
        {"name": "Switch", "host": "localhost", "port": 2222},
        {"name": "Firewall", "host": "localhost", "port": 2223}
    ]
    
    for device in devices:
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                device['host'], 
                port=device['port'], 
                username='admin', 
                password='admin',
                timeout=10
            )
            
            # Test basic commands
            stdin, stdout, stderr = client.exec_command('hostname')
            hostname = stdout.read().decode().strip()
            
            stdin, stdout, stderr = client.exec_command('whoami')
            user = stdout.read().decode().strip()
            
            stdin, stdout, stderr = client.exec_command('uptime')
            uptime = stdout.read().decode().strip()
            
            print(f"✅ {device['name']} (:{device['port']}):")
            print(f"   Hostname: {hostname}")
            print(f"   User: {user}")
            print(f"   Uptime: {uptime[:50]}...")
            
            client.close()
            
        except Exception as e:
            print(f"❌ {device['name']} (:{device['port']}): {e}")
        print()

def show_lab_summary():
    """Show complete lab summary"""
    print("🎯 Your Lab Environment is Ready!")
    print("=" * 50)
    print()
    print("📱 Dashboard Access:")
    print("   • Streamlit App: http://localhost:8503")
    print("   • Prometheus: http://localhost:9090")
    print("   • Grafana: http://localhost:3000 (admin/admin123)")
    print()
    print("🔧 Lab Devices (SSH Access):")
    print("   • Router: ssh admin@localhost -p 2221")
    print("   • Switch: ssh admin@localhost -p 2222")
    print("   • Firewall: ssh admin@localhost -p 2223")
    print("   • Password: admin")
    print()
    print("⚙️ Test Your Automation:")
    print("   • Edit config/devices.yaml to add lab devices")
    print("   • Run Ansible playbooks against lab")
    print("   • Test device discovery in dashboard")
    print("   • Practice network automation scripts")
    print()
    print("🧪 Next Steps:")
    print("   1. Open dashboard at http://localhost:8503")
    print("   2. Go to 'Device Management' tab")
    print("   3. Add lab devices (localhost:2221, 2222, 2223)")
    print("   4. Test connectivity and monitoring")
    print("   5. Run automation scripts")
    print()

if __name__ == "__main__":
    test_device_direct_ssh()
    print()
    show_lab_summary()
