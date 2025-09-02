#!/usr/bin/env python3
"""
Lab Environment Test Script
Tests connectivity to Docker lab devices
"""

import socket
import subprocess
import time
import paramiko

def test_port_connectivity(host, port, timeout=5):
    """Test if a port is open and accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Error testing {host}:{port} - {e}")
        return False

def test_ssh_connection(host, port, username, password):
    """Test SSH connection to a device"""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port=port, username=username, password=password, timeout=10)
        
        # Execute a simple command
        stdin, stdout, stderr = client.exec_command('echo "Hello from lab device"')
        output = stdout.read().decode().strip()
        client.close()
        return True, output
    except Exception as e:
        return False, str(e)

def test_lab_environment():
    """Test the complete lab environment"""
    print("🧪 Testing Local Lab Environment")
    print("=" * 50)
    
    # Lab device configurations
    lab_devices = [
        {"name": "lab-router1", "host": "localhost", "port": 2221, "type": "router"},
        {"name": "lab-switch1", "host": "localhost", "port": 2222, "type": "switch"},
        {"name": "lab-firewall1", "host": "localhost", "port": 2223, "type": "firewall"}
    ]
    
    monitoring_services = [
        {"name": "Prometheus", "host": "localhost", "port": 9090},
        {"name": "Grafana", "host": "localhost", "port": 3000}
    ]
    
    print("🔌 Testing Network Device Connectivity:")
    print("-" * 40)
    
    for device in lab_devices:
        print(f"Testing {device['name']} ({device['type']})...")
        
        # Test port connectivity
        port_open = test_port_connectivity(device['host'], device['port'])
        if port_open:
            print(f"  ✅ Port {device['port']} is open")
            
            # Wait a moment for SSH to be ready
            time.sleep(2)
            
            # Test SSH connection
            ssh_success, ssh_result = test_ssh_connection(
                device['host'], device['port'], 'admin', 'admin'
            )
            if ssh_success:
                print(f"  ✅ SSH connection successful")
                print(f"  📝 Response: {ssh_result}")
            else:
                print(f"  ⚠️ SSH connection failed: {ssh_result}")
        else:
            print(f"  ❌ Port {device['port']} is not accessible")
        print()
    
    print("📊 Testing Monitoring Services:")
    print("-" * 40)
    
    for service in monitoring_services:
        print(f"Testing {service['name']}...")
        port_open = test_port_connectivity(service['host'], service['port'])
        if port_open:
            print(f"  ✅ {service['name']} is accessible at http://localhost:{service['port']}")
        else:
            print(f"  ❌ {service['name']} is not accessible")
        print()
    
    print("🌐 Testing Your Dashboard:")
    print("-" * 40)
    dashboard_open = test_port_connectivity("localhost", 8503)
    if dashboard_open:
        print("  ✅ Streamlit Dashboard is running at http://localhost:8503")
    else:
        print("  ⚠️ Streamlit Dashboard is not accessible")
    print()
    
    print("🎯 Lab Environment Summary:")
    print("-" * 40)
    print("📍 Lab Devices:")
    print("  - Router: ssh admin@localhost -p 2221")
    print("  - Switch: ssh admin@localhost -p 2222") 
    print("  - Firewall: ssh admin@localhost -p 2223")
    print()
    print("📍 Monitoring:")
    print("  - Prometheus: http://localhost:9090")
    print("  - Grafana: http://localhost:3000 (admin/admin123)")
    print()
    print("📍 Your Dashboard:")
    print("  - Streamlit: http://localhost:8503")
    print()
    print("🧪 Lab testing completed!")

if __name__ == "__main__":
    test_lab_environment()
